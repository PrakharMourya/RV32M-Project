// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: id_ex_stage.v
// Work Package: [WP-05][CORE] (Issue #05)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Stage 2 of the 3-stage RV32IM processor pipeline:
//   - 32-entry General Purpose Register File with internal same-cycle bypass
//   - Integrated Control Decoder (control_decoder.v) decoding all 37 RV32I + RV32M ops
//   - Zero-cycle RAW Hazard Forwarding Multiplexers (WB -> EX)
//   - Unified Arithmetic Logic Unit (alu_rv32m.v)
//   - Single-Cycle DSP Array Multiplier Coprocessor (multiplier_rv32m.v)
//   - Non-Restoring Sequential Radix-2 Hardware Divider FSM (divider_rv32m.v)
//   - Branch & Jump Target / Condition Evaluator
//   - Stage 2 -> Stage 3 Pipeline Register (RegB) with stall freeze bubble insertion
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module id_ex_stage (
    input  wire        clk,                // Master system clock (50 MHz)
    input  wire        reset_n,            // Active-low asynchronous reset
    input  wire        stall_pipeline,     // Stall pipeline freeze strobe
    input  wire [31:0] id_pc,              // Stage 2 PC
    input  wire [31:0] id_instr,           // Stage 2 Instruction word

    // Forwarding inputs from Hazard Unit & Writeback Stage
    input  wire [1:0]  forward_a,          // Forwarding selector for operand A
    input  wire [1:0]  forward_b,          // Forwarding selector for operand B
    input  wire [31:0] wb_forward_data,    // Committed result from Writeback stage

    // Writeback Commit interface into Register File
    input  wire        wb_reg_write,       // Destination register write strobe
    input  wire [4:0]  wb_rd,              // Destination register address
    input  wire [31:0] wb_wdata,           // Data committed to register file

    // Hazard unit feedback outputs
    output wire [4:0]  id_rs1,             // Source register 1 address
    output wire [4:0]  id_rs2,             // Source register 2 address
    output wire        div_busy,           // Stall signal from divider coprocessor
    output wire        branch_taken,       // Branch / Jump condition satisfied
    output wire [31:0] branch_target_pc,   // Target address for branch / jump
    output wire        is_jal,             // JAL instruction decoded
    output wire        is_jalr,            // JALR instruction decoded

    // Stage 3 Pipeline Outputs (RegB)
    output reg  [31:0] ex_wb_pc,           // Retire PC for telemetry
    output reg  [31:0] ex_wb_instr,        // Retire instruction word for telemetry
    output reg  [4:0]  ex_wb_rd,           // Retire destination register
    output reg         ex_wb_reg_write,    // Retire register write enable
    output reg         ex_wb_mem_read,     // Retire memory read enable
    output reg         ex_wb_mem_write,    // Retire memory write enable
    output reg  [2:0]  ex_wb_funct3,       // Funct3 for memory load/store formatting
    output reg  [31:0] ex_wb_result,       // Computational result (ALU, MUL, DIV, PC+4)
    output reg  [31:0] ex_wb_mem_addr,     // Memory byte address (from ALU)
    output reg  [31:0] ex_wb_store_data    // Store payload data (from forwarded RS2)
);

    // -------------------------------------------------------------------------
    // Control Decoder Instance
    // -------------------------------------------------------------------------
    wire [6:0]  opcode;
    wire [4:0]  rd;
    wire [2:0]  funct3;
    wire [4:0]  rs1;
    wire [4:0]  rs2;
    wire [6:0]  funct7;
    wire [31:0] imm_i;
    wire [31:0] imm_s;
    wire [31:0] imm_b;
    wire [31:0] imm_u;
    wire [31:0] imm_j;
    wire        is_r_type;
    wire        is_i_type;
    wire        is_load;
    wire        is_store;
    wire        is_branch;
    wire        is_lui;
    wire        is_auipc;
    wire        is_m_extension;
    wire        is_mul;
    wire        is_div;
    wire        reg_write;
    wire [3:0]  alu_control;

    control_decoder u_decoder (
        .instr          (id_instr),
        .opcode         (opcode),
        .rd             (rd),
        .funct3         (funct3),
        .rs1            (rs1),
        .rs2            (rs2),
        .funct7         (funct7),
        .imm_i          (imm_i),
        .imm_s          (imm_s),
        .imm_b          (imm_b),
        .imm_u          (imm_u),
        .imm_j          (imm_j),
        .is_r_type      (is_r_type),
        .is_i_type      (is_i_type),
        .is_load        (is_load),
        .is_store       (is_store),
        .is_branch      (is_branch),
        .is_jal         (is_jal),
        .is_jalr        (is_jalr),
        .is_lui         (is_lui),
        .is_auipc       (is_auipc),
        .is_m_extension (is_m_extension),
        .is_mul         (is_mul),
        .is_div         (is_div),
        .reg_write      (reg_write),
        .alu_control    (alu_control)
    );

    assign id_rs1 = rs1;
    assign id_rs2 = rs2;

    // -------------------------------------------------------------------------
    // 32-Entry General Purpose Register File (Dual Read, Same-Cycle Bypass)
    // -------------------------------------------------------------------------
    reg [31:0] regfile [0:31];
    integer idx;

    // Combinational read with internal same-cycle write-through bypass
    wire [31:0] rf_rs1_data = (rs1 == 5'd0) ? 32'd0 :
                              (wb_reg_write && (wb_rd == rs1)) ? wb_wdata : regfile[rs1];

    wire [31:0] rf_rs2_data = (rs2 == 5'd0) ? 32'd0 :
                              (wb_reg_write && (wb_rd == rs2)) ? wb_wdata : regfile[rs2];

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            for (idx = 0; idx < 32; idx = idx + 1)
                regfile[idx] <= 32'h0000_0000;
        end else if (wb_reg_write && (wb_rd != 5'd0)) begin
            regfile[wb_rd] <= wb_wdata;
        end
    end

    // -------------------------------------------------------------------------
    // RAW Hazard Forwarding Multiplexers (WB -> EX)
    // -------------------------------------------------------------------------
    wire [31:0] operand_a = (forward_a == 2'b10) ? wb_forward_data : rf_rs1_data;
    wire [31:0] operand_b = (forward_b == 2'b10) ? wb_forward_data : rf_rs2_data;

    // -------------------------------------------------------------------------
    // ALU Source Multiplexers
    // -------------------------------------------------------------------------
    wire [31:0] alu_op_a = (is_auipc | is_jal) ? id_pc : operand_a;
    reg  [31:0] alu_op_b;
    always @(*) begin
        if (is_r_type) alu_op_b = operand_b;
        else if (is_i_type | is_load | is_jalr) alu_op_b = imm_i;
        else if (is_store) alu_op_b = imm_s;
        else if (is_lui | is_auipc) alu_op_b = imm_u;
        else if (is_jal) alu_op_b = 32'd4;
        else alu_op_b = operand_b;
    end

    // -------------------------------------------------------------------------
    // Multiplier Coprocessor Instance (RV32M Single-Cycle DSP Array)
    // -------------------------------------------------------------------------
    wire [31:0] mul_result;
    wire        mul_ready;

    multiplier_rv32m #(
        .PIPELINED (0) // 1-cycle combinational DSP execution in 3-stage core
    ) u_multiplier (
        .clk       (clk),
        .rst_n     (reset_n),
        .start     (is_mul),
        .funct3    (funct3),
        .operand_a (operand_a),
        .operand_b (operand_b),
        .result    (mul_result),
        .ready     (mul_ready)
    );

    // -------------------------------------------------------------------------
    // Hardware Divider Coprocessor Instance (RV32M Non-Restoring FSM)
    // -------------------------------------------------------------------------
    wire [31:0] div_quotient;
    wire [31:0] div_remainder;
    wire [31:0] div_result;
    wire        internal_div_busy;
    wire        div_done;
    reg         div_active;

    // Generate clean 1-cycle start pulse for divider
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            div_active <= 1'b0;
        end else if (div_done) begin
            div_active <= 1'b0;
        end else if (is_div && !internal_div_busy) begin
            div_active <= 1'b1;
        end
    end

    wire div_start = is_div && !div_active && !div_done;

    divider_rv32m u_divider (
        .clk       (clk),
        .rst_n     (reset_n),
        .start     (div_start),
        .funct3    (funct3),
        .dividend  (operand_a),
        .divisor   (operand_b),
        .quotient  (div_quotient),
        .remainder (div_remainder),
        .result    (div_result),
        .busy      (internal_div_busy),
        .done      (div_done)
    );

    // Assert div_busy to hazard unit immediately from decode until done
    assign div_busy = is_div && !div_done;

    // -------------------------------------------------------------------------
    // Unified ALU & Execution Multiplexer Instance
    // -------------------------------------------------------------------------
    wire [31:0] alu_result;
    wire [31:0] ex_result;
    wire        alu_zero;

    alu_rv32m u_alu (
        .alu_control (alu_control),
        .operand_a   (alu_op_a),
        .operand_b   (alu_op_b),
        .is_mul      (is_mul),
        .mul_result  (mul_result),
        .is_div      (is_div),
        .div_result  (div_result),
        .is_link     (is_jal | is_jalr),
        .link_pc     (id_pc + 32'd4),
        .ex_result   (ex_result),
        .alu_result  (alu_result),
        .zero        (alu_zero)
    );

    // -------------------------------------------------------------------------
    // Branch & Jump Condition & Target Evaluator
    // -------------------------------------------------------------------------
    reg branch_cond;
    always @(*) begin
        case (funct3)
            `FUNCT3_BEQ:  branch_cond = (operand_a == operand_b);
            `FUNCT3_BNE:  branch_cond = (operand_a != operand_b);
            `FUNCT3_BLT:  branch_cond = ($signed(operand_a) < $signed(operand_b));
            `FUNCT3_BGE:  branch_cond = ($signed(operand_a) >= $signed(operand_b));
            `FUNCT3_BLTU: branch_cond = (operand_a < operand_b);
            `FUNCT3_BGEU: branch_cond = (operand_a >= operand_b);
            default:      branch_cond = 1'b0;
        endcase
    end

    assign branch_taken = (is_branch & branch_cond) | is_jal | is_jalr;

    assign branch_target_pc = is_jalr ? ((operand_a + imm_i) & ~32'h1) :
                              is_jal  ? (id_pc + imm_j) :
                                        (id_pc + imm_b);

    // -------------------------------------------------------------------------
    // Stage 2 -> Stage 3 Pipeline Registers (RegB)
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            ex_wb_pc         <= 32'h0000_0000;
            ex_wb_instr      <= 32'h0000_0013; // NOP
            ex_wb_rd         <= 5'd0;
            ex_wb_reg_write  <= 1'b0;
            ex_wb_mem_read   <= 1'b0;
            ex_wb_mem_write  <= 1'b0;
            ex_wb_funct3     <= 3'b000;
            ex_wb_result     <= 32'h0000_0000;
            ex_wb_mem_addr   <= 32'h0000_0000;
            ex_wb_store_data <= 32'h0000_0000;
        end else if (stall_pipeline) begin
            // When stalled, inject a bubble (NOP) into Stage 3 to avoid duplicate commits
            ex_wb_pc         <= id_pc;
            ex_wb_instr      <= 32'h0000_0013; // NOP bubble
            ex_wb_rd         <= 5'd0;
            ex_wb_reg_write  <= 1'b0;
            ex_wb_mem_read   <= 1'b0;
            ex_wb_mem_write  <= 1'b0;
            ex_wb_funct3     <= 3'b000;
            ex_wb_result     <= 32'h0000_0000;
            ex_wb_mem_addr   <= 32'h0000_0000;
            ex_wb_store_data <= 32'h0000_0000;
        end else begin
            ex_wb_pc         <= id_pc;
            ex_wb_instr      <= id_instr;
            ex_wb_rd         <= rd;
            ex_wb_reg_write  <= reg_write;
            ex_wb_mem_read   <= is_load;
            ex_wb_mem_write  <= is_store;
            ex_wb_funct3     <= funct3;
            ex_wb_result     <= ex_result;
            ex_wb_mem_addr   <= alu_result;
            ex_wb_store_data <= operand_b;
        end
    end

endmodule
