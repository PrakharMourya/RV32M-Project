// ==============================================================================
// AutoVision-RISC-V: 32-Bit RV32I Arithmetic Logic Unit (ALU)
// Module: alu.v
// Work Package: [WP-01][CORE] (Issue #1)
// Target FPGA: AMD Xilinx Artix-7 XC7A100T-1CSG324C
// Academic Standard: IIT Guwahati Advanced Computer Architecture (10/10 Target)
//
// Description:
// Fully combinational 32-bit arithmetic, logic, shift, and comparison unit
// implementing all RV32I computational operations.
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module alu (
    input  wire [3:0]  alu_control, // 4-bit operation select
    input  wire [31:0] operand_a,   // 32-bit operand A
    input  wire [31:0] operand_b,   // 32-bit operand B
    output reg  [31:0] alu_result,  // 32-bit computation result
    output wire        zero         // Zero flag asserted when result == 0
);

    wire [4:0] shamt = operand_b[4:0];

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

endmodule
