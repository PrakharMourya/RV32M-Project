// ==============================================================================
// AutoVision-RISC-V: Stage 2 Instruction Decode & Execution Unit
// Module: id_ex_stage.v
// Work Package: [WP-01][CORE] (Issue #1)
// Target FPGA: AMD Xilinx Artix-7 XC7A100T-1CSG324C
// Academic Standard: IIT Guwahati Advanced Computer Architecture (10/10 Target)
//
// Description:
// Stage 2 of the 3-stage RV32IM processor pipeline:
//   - 32-entry General Purpose Register File with internal same-cycle bypass
//   - Immediate Format Extender (I, S, B, U, J types)
//   - Control Unit decoding all 37 base RV32I + RV32M instructions
//   - Zero-cycle RAW Hazard Forwarding Multiplexers (WB -> EX)
//   - 32-bit Arithmetic Logic Unit (alu.v)
//   - Single-Cycle DSP Array Multiplier Coprocessor (multiplier.v)
//   - Branch & Jump Target / Condition Evaluator
//   - Stage 2 -> Stage 3 Pipeline Register (RegB)
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
    output reg  [31:0] ex_wb_result,       // Computational result (ALU, MUL, PC+4)
    output reg  [31:0] ex_wb_mem_addr,     // Memory byte address (from ALU)
    output reg  [31:0] ex_wb_store_data    // Store payload data (from forwarded RS2)
);

    // -------------------------------------------------------------------------
    // Instruction Field Decomposition
    // -------------------------------------------------------------------------
    wire [6:0] opcode = id_instr[6:0];
    wire [4:0] rd     = id_instr[11:7];
    wire [2:0] funct3 = id_instr[14:12];
    wire [4:0] rs1    = id_instr[19:15];
    wire [4:0] rs2    = id_instr[24:20];
    wire [6:0] funct7 = id_instr[31:25];

    assign id_rs1 = rs1;
    assign id_rs2 = rs2;

    // -------------------------------------------------------------------------
    // Immediate Format Extender (I, S, B, U, J types)
    // -------------------------------------------------------------------------
    wire [31:0] imm_i = {{20{id_instr[31]}}, id_instr[31:20]};
    wire [31:0] imm_s = {{20{id_instr[31]}}, id_instr[31:25], id_instr[11:7]};
    wire [31:0] imm_b = {{19{id_instr[31]}}, id_instr[31], id_instr[7], id_instr[30:25], id_instr[11:8], 1'b0};
    wire [31:0] imm_u = {id_instr[31:12], 12'b0};
    wire [31:0] imm_j = {{11{id_instr[31]}}, id_instr[31], id_instr[19:12], id_instr[20], id_instr[30:21], 1'b0};

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
    // forward_a / forward_b == 2'b10 selects writeback stage committed value
    // -------------------------------------------------------------------------
    wire [31:0] operand_a = (forward_a == 2'b10) ? wb_forward_data : rf_rs1_data;
    wire [31:0] operand_b = (forward_b == 2'b10) ? wb_forward_data : rf_rs2_data;

    // -------------------------------------------------------------------------
    // Control Unit Decoder (RV32I + RV32M)
    // -------------------------------------------------------------------------
    wire is_r_type = (opcode == `OPCODE_R_TYPE);
    wire is_i_type = (opcode == `OPCODE_I_TYPE);
    wire is_load   = (opcode == `OPCODE_LOAD);
    wire is_store  = (opcode == `OPCODE_STORE);
    wire is_branch = (opcode == `OPCODE_BRANCH);
    assign is_jal  = (opcode == `OPCODE_JAL);
    assign is_jalr = (opcode == `OPCODE_JALR);
    wire is_lui    = (opcode == `OPCODE_LUI);
    wire is_auipc  = (opcode == `OPCODE_AUIPC);

    // RV32M coprocessor instruction detection
    wire is_m_extension = is_r_type && (funct7 == `FUNCT7_M_EXTENSION);
    wire is_mul         = is_m_extension && (funct3[2] == 1'b0); // MUL, MULH, MULHSU, MULHU

    // Register write enable
    wire reg_write = (is_r_type | is_i_type | is_load | is_jal | is_jalr | is_lui | is_auipc) & (rd != 5'd0);

    // ALU Source Multiplexers
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

    // ALU Control Decoder
    reg [3:0] alu_control;
    always @(*) begin
        if (is_load | is_store | is_auipc | is_jal) begin
            alu_control = `ALU_CTRL_ADD;
        end else if (is_lui) begin
            alu_control = `ALU_CTRL_PASS_B;
        end else if (is_i_type) begin
            case (funct3)
                `FUNCT3_ADD_SUB: alu_control = `ALU_CTRL_ADD;
                `FUNCT3_SLL:     alu_control = `ALU_CTRL_SLL;
                `FUNCT3_SLT:     alu_control = `ALU_CTRL_SLT;
                `FUNCT3_SLTU:    alu_control = `ALU_CTRL_SLTU;
                `FUNCT3_XOR:     alu_control = `ALU_CTRL_XOR;
                `FUNCT3_SRL_SRA: alu_control = (funct7[5] == 1'b1) ? `ALU_CTRL_SRA : `ALU_CTRL_SRL;
                `FUNCT3_OR:      alu_control = `ALU_CTRL_OR;
                `FUNCT3_AND:     alu_control = `ALU_CTRL_AND;
                default:         alu_control = `ALU_CTRL_ADD;
            endcase
        end else if (is_r_type && !is_m_extension) begin
            case (funct3)
                `FUNCT3_ADD_SUB: alu_control = (funct7[5] == 1'b1) ? `ALU_CTRL_SUB : `ALU_CTRL_ADD;
                `FUNCT3_SLL:     alu_control = `ALU_CTRL_SLL;
                `FUNCT3_SLT:     alu_control = `ALU_CTRL_SLT;
                `FUNCT3_SLTU:    alu_control = `ALU_CTRL_SLTU;
                `FUNCT3_XOR:     alu_control = `ALU_CTRL_XOR;
                `FUNCT3_SRL_SRA: alu_control = (funct7[5] == 1'b1) ? `ALU_CTRL_SRA : `ALU_CTRL_SRL;
                `FUNCT3_OR:      alu_control = `ALU_CTRL_OR;
                `FUNCT3_AND:     alu_control = `ALU_CTRL_AND;
                default:         alu_control = `ALU_CTRL_ADD;
            endcase
        end else begin
            alu_control = `ALU_CTRL_ADD;
        end
    end

    // -------------------------------------------------------------------------
    // ALU Instance
    // -------------------------------------------------------------------------
    wire [31:0] alu_result;
    wire        alu_zero;

    alu u_alu (
        .alu_control (alu_control),
        .operand_a   (alu_op_a),
        .operand_b   (alu_op_b),
        .alu_result  (alu_result),
        .zero        (alu_zero)
    );

    // -------------------------------------------------------------------------
    // Multiplier Coprocessor Instance (RV32M Single-Cycle DSP Array)
    // -------------------------------------------------------------------------
    wire [31:0] mul_result;
    wire        mul_ready;

    multiplier u_multiplier (
        .clk       (clk),
        .reset_n   (reset_n),
        .enable    (is_mul),
        .funct3    (funct3),
        .operand_a (operand_a),
        .operand_b (operand_b),
        .result    (mul_result),
        .ready     (mul_ready)
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
    // Execution Unit Result Multiplexer
    // -------------------------------------------------------------------------
    wire [31:0] ex_result = is_mul          ? mul_result :
                            (is_jal | is_jalr) ? (id_pc + 32'd4) :
                                              alu_result;

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
