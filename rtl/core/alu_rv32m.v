// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: alu_rv32m.v
// Work Package: [WP-05][CORE] (Issue #05)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Unified 32-bit RV32I ALU & RV32M execution multiplexing engine:
//   1. Full RV32I integer arithmetic, logic, shift, and comparison computations.
//   2. Direct routing and multiplexing of RV32M multiplier (multiplier_rv32m)
//      and divider (divider_rv32m) execution outputs.
//   3. Separate alu_result output for memory effective address generation.
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module alu_rv32m (
    input  wire [3:0]  alu_control,    // 4-bit ALU operation select code
    input  wire [31:0] operand_a,      // 32-bit operand A
    input  wire [31:0] operand_b,      // 32-bit operand B
    input  wire        is_mul,         // High when executing MUL/MULH/MULHSU/MULHU
    input  wire [31:0] mul_result,     // 32-bit product slice from multiplier_rv32m
    input  wire        is_div,         // High when executing DIV/DIVU/REM/REMU
    input  wire [31:0] div_result,     // 32-bit quotient/remainder from divider_rv32m
    input  wire        is_link,        // High for JAL/JALR link address
    input  wire [31:0] link_pc,        // PC + 4
    output reg  [31:0] ex_result,      // Final unified execution result committed to RegB
    output reg  [31:0] alu_result,     // Raw RV32I ALU result (used for memory addresses)
    output wire        zero            // Zero flag asserted when alu_result == 0
);

    wire [4:0] shamt = operand_b[4:0];

    // -------------------------------------------------------------------------
    // RV32I Arithmetic & Logic Unit
    // -------------------------------------------------------------------------
    always @(*) begin
        case (alu_control)
            `ALU_CTRL_ADD:    alu_result = operand_a + operand_b;
            `ALU_CTRL_SUB:    alu_result = operand_a - operand_b;
            `ALU_CTRL_SLL:    alu_result = operand_a << shamt;
            `ALU_CTRL_SLT:    alu_result = ($signed(operand_a) < $signed(operand_b)) ? 32'd1 : 32'd0;
            `ALU_CTRL_SLTU:   alu_result = (operand_a < operand_b) ? 32'd1 : 32'd0;
            `ALU_CTRL_XOR:    alu_result = operand_a ^ operand_b;
            `ALU_CTRL_SRL:    alu_result = operand_a >> shamt;
            `ALU_CTRL_SRA:    alu_result = $signed(operand_a) >>> shamt;
            `ALU_CTRL_OR:     alu_result = operand_a | operand_b;
            `ALU_CTRL_AND:    alu_result = operand_a & operand_b;
            `ALU_CTRL_PASS_B: alu_result = operand_b;
            default:          alu_result = 32'h0000_0000;
        endcase
    end

    assign zero = (alu_result == 32'h0000_0000);

    // -------------------------------------------------------------------------
    // Execution Unit Output Multiplexer (RV32I, RV32M MUL, RV32M DIV, Jumps)
    // -------------------------------------------------------------------------
    always @(*) begin
        if (is_mul) begin
            ex_result = mul_result;
        end else if (is_div) begin
            ex_result = div_result;
        end else if (is_link) begin
            ex_result = link_pc;
        end else begin
            ex_result = alu_result;
        end
    end

endmodule
