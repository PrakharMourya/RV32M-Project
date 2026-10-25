// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: control_decoder.v
// Work Package: [WP-05][CORE] (Issue #05)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Centralized instruction field decomposition, immediate generation, and
// control signal decoder for all 37 RV32I base instructions + RV32M extensions:
//   - RV32I: R-type, I-type (ALU, Load, JALR), S-type, B-type, U-type, J-type.
//   - RV32M: MUL, MULH, MULHSU, MULHU (funct7 = 7'b0000001, funct3[2] = 0).
//   - RV32M: DIV, DIVU, REM, REMU   (funct7 = 7'b0000001, funct3[2] = 1).
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module control_decoder (
    input  wire [31:0] instr,           // 32-bit instruction word from Stage 1

    // Instruction Field Decomposition
    output wire [6:0]  opcode,          // Major opcode [6:0]
    output wire [4:0]  rd,              // Destination register index [11:7]
    output wire [2:0]  funct3,          // 3-bit sub-function [14:12]
    output wire [4:0]  rs1,             // Source register 1 index [19:15]
    output wire [4:0]  rs2,             // Source register 2 index [24:20]
    output wire [6:0]  funct7,          // 7-bit sub-function [31:25]

    // Formatted Immediates
    output wire [31:0] imm_i,           // Sign-extended I-type immediate
    output wire [31:0] imm_s,           // Sign-extended S-type immediate
    output wire [31:0] imm_b,           // Sign-extended B-type branch offset
    output wire [31:0] imm_u,           // Upper 20-bit U-type immediate
    output wire [31:0] imm_j,           // Sign-extended J-type jump target

    // Instruction Classification Flags
    output wire        is_r_type,       // Standard Reg-Reg computational instruction
    output wire        is_i_type,       // Immediate computational instruction
    output wire        is_load,         // Load instruction (LB, LH, LW, LBU, LHU)
    output wire        is_store,        // Store instruction (SB, SH, SW)
    output wire        is_branch,       // Branch instruction (BEQ, BNE, BLT, etc.)
    output wire        is_jal,          // Jump and Link (Unconditional)
    output wire        is_jalr,         // Jump and Link Register (Indirect)
    output wire        is_lui,          // Load Upper Immediate
    output wire        is_auipc,        // Add Upper Immediate to PC

    // RV32M Extension Flags
    output wire        is_m_extension,  // Asserted when funct7 == 7'b0000001 on R-type
    output wire        is_mul,          // MUL, MULH, MULHSU, MULHU
    output wire        is_div,          // DIV, DIVU, REM, REMU

    // Control Unit Signals
    output wire        reg_write,       // High when destination register is to be written
    output reg  [3:0]  alu_control      // 4-bit ALU operation select code
);

    // -------------------------------------------------------------------------
    // Field Slicing
    // -------------------------------------------------------------------------
    assign opcode = instr[6:0];
    assign rd     = instr[11:7];
    assign funct3 = instr[14:12];
    assign rs1    = instr[19:15];
    assign rs2    = instr[24:20];
    assign funct7 = instr[31:25];

    // -------------------------------------------------------------------------
    // Immediate Generation (Sign-extended where required)
    // -------------------------------------------------------------------------
    assign imm_i = {{20{instr[31]}}, instr[31:20]};
    assign imm_s = {{20{instr[31]}}, instr[31:25], instr[11:7]};
    assign imm_b = {{19{instr[31]}}, instr[31], instr[7], instr[30:25], instr[11:8], 1'b0};
    assign imm_u = {instr[31:12], 12'b0};
    assign imm_j = {{11{instr[31]}}, instr[31], instr[19:12], instr[20], instr[30:21], 1'b0};

    // -------------------------------------------------------------------------
    // Opcode Decodes
    // -------------------------------------------------------------------------
    assign is_r_type = (opcode == `OPCODE_R_TYPE);
    assign is_i_type = (opcode == `OPCODE_I_TYPE);
    assign is_load   = (opcode == `OPCODE_LOAD);
    assign is_store  = (opcode == `OPCODE_STORE);
    assign is_branch = (opcode == `OPCODE_BRANCH);
    assign is_jal    = (opcode == `OPCODE_JAL);
    assign is_jalr   = (opcode == `OPCODE_JALR);
    assign is_lui    = (opcode == `OPCODE_LUI);
    assign is_auipc  = (opcode == `OPCODE_AUIPC);

    // -------------------------------------------------------------------------
    // RV32M Extension Decodes
    // -------------------------------------------------------------------------
    assign is_m_extension = is_r_type && (funct7 == `FUNCT7_M_EXTENSION);
    assign is_mul         = is_m_extension && (funct3[2] == 1'b0); // 3'b000..3'b011
    assign is_div         = is_m_extension && (funct3[2] == 1'b1); // 3'b100..3'b111

    // -------------------------------------------------------------------------
    // Architectural Register File Write Enable
    // -------------------------------------------------------------------------
    assign reg_write = (is_r_type | is_i_type | is_load | is_jal | is_jalr | is_lui | is_auipc) && (rd != 5'd0);

    // -------------------------------------------------------------------------
    // ALU Control Matrix Decoder
    // -------------------------------------------------------------------------
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

endmodule
