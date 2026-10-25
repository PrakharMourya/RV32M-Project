// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: multiplier_rv32m.v
// Work Package: [WP-01][CORE] (Issue #01)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Fully synthesizable 32-bit hardware integer multiplier engine compliant with
// the unprivileged RISC-V M-Extension specification. Implements a unified
// 33-bit x 33-bit signed/unsigned multiplication datapath inferring dedicated
// DSP48E1 slices on Xilinx Artix-7 FPGAs.
//
// Instruction Encoding & Operations (funct7 = 7'b0000001, opcode = 7'b0110011):
//   - MUL    (funct3 = 3'b000): Lower 32 bits of signed x signed   (Rd = (Rs1 * Rs2)[31:0])
//   - MULH   (funct3 = 3'b001): Upper 32 bits of signed x signed   (Rd = (Rs1 * Rs2)[63:32])
//   - MULHSU (funct3 = 3'b010): Upper 32 bits of signed x unsigned (Rd = (Rs1 * Rs2)[63:32])
//   - MULHU  (funct3 = 3'b011): Upper 32 bits of unsigned x unsigned (Rd = (Rs1 * Rs2)[63:32])
//
// Microarchitectural Parameterization:
//   - PIPELINED = 0: Single-cycle combinational DSP-assisted execution.
//   - PIPELINED = 1: Registered output slice with 1-cycle active ready flag.
// ==============================================================================

`timescale 1ns / 1ps

module multiplier_rv32m #(
    parameter PIPELINED = 0 // 0: combinational DSP execution, 1: registered output slice
)(
    input  wire        clk,        // System clock (50 MHz - 100 MHz target)
    input  wire        rst_n,      // Active-low reset
    input  wire        start,      // Trigger signal from decode/execute stage
    input  wire [2:0]  funct3,     // 3'b000: MUL, 3'b001: MULH, 3'b010: MULHSU, 3'b011: MULHU
    input  wire [31:0] operand_a,  // rs1 data
    input  wire [31:0] operand_b,  // rs2 data
    output reg  [31:0] result,     // Selected lower or upper 32-bit slice
    output reg         ready       // High when computation is valid
);

    // -------------------------------------------------------------------------
    // funct3 Operation Parameterization
    // -------------------------------------------------------------------------
    localparam [2:0] OP_MUL    = 3'b000;
    localparam [2:0] OP_MULH   = 3'b001;
    localparam [2:0] OP_MULHSU = 3'b010;
    localparam [2:0] OP_MULHU  = 3'b011;

    // -------------------------------------------------------------------------
    // Unified 33-Bit Signed/Unsigned Operand Extension
    // -------------------------------------------------------------------------
    wire sign_a = (funct3 != OP_MULHU) ? operand_a[31] : 1'b0;
    wire sign_b = (funct3 == OP_MUL || funct3 == OP_MULH) ? operand_b[31] : 1'b0;

    wire signed [32:0] ext_a = {sign_a, operand_a};
    wire signed [32:0] ext_b = {sign_b, operand_b};

    // -------------------------------------------------------------------------
    // 66-Bit Internal Product Generation (DSP48E1 Inference)
    // -------------------------------------------------------------------------
    (* use_dsp = "yes" *)
    wire signed [65:0] product_66 = ext_a * ext_b;

    // -------------------------------------------------------------------------
    // Combinational Output Slice Selection
    // -------------------------------------------------------------------------
    wire [31:0] result_slice = (funct3 == OP_MUL) ? product_66[31:0] : product_66[63:32];

    // -------------------------------------------------------------------------
    // Registered Output Stage (for PIPELINED = 1 mode)
    // -------------------------------------------------------------------------
    reg [31:0] reg_result;
    reg        reg_ready;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_result <= 32'h0000_0000;
            reg_ready  <= 1'b0;
        end else if (start) begin
            reg_result <= result_slice;
            reg_ready  <= 1'b1;
        end else begin
            reg_ready  <= 1'b0;
        end
    end

    // -------------------------------------------------------------------------
    // Output Multiplexing (Combinational vs Registered)
    // -------------------------------------------------------------------------
    always @(*) begin
        if (PIPELINED) begin
            result = reg_result;
            ready  = reg_ready;
        end else begin
            result = result_slice;
            ready  = start;
        end
    end

endmodule
