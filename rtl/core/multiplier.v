// ==============================================================================
// AutoVision-RISC-V: Single-Cycle 64-Bit DSP Array Multiplier Coprocessor (RV32M)
// Module: multiplier.v
// Work Package: [WP-03][CORE] (Issue #3)
// Author: Abhishek Kumar Deepak (Roll: 250101002, GitHub: abhiii927)
// Target FPGA: AMD Xilinx Artix-7 XC7A100T-1CSG324C
// Toolchain: AMD Vivado 2025.2 / Icarus Verilog 12+
//
// Description:
// High-throughput, single-cycle integer multiplier coprocessor compliant with
// the RISC-V M-Extension specification. Computes 64-bit products in a single
// clock cycle at 50 MHz by inferring dedicated DSP48E1 hard slices on Artix-7.
//
// Supported Instructions & Arithmetic Semantics:
//   - MUL    (funct3 = 3'b000): Lower 32 bits of signed x signed: (A * B)[31:0]
//   - MULH   (funct3 = 3'b001): Upper 32 bits of signed x signed: (signed(A) * signed(B))[63:32]
//   - MULHSU (funct3 = 3'b010): Upper 32 bits of signed x unsigned: (signed(A) * unsigned(B))[63:32]
//   - MULHU  (funct3 = 3'b011): Upper 32 bits of unsigned x unsigned: (unsigned(A) * unsigned(B))[63:32]
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module multiplier (
    input  wire        clk,        // System clock (50 MHz) - coprocessor interface contract
    input  wire        reset_n,    // Active-low asynchronous reset
    input  wire        enable,     // Active-high multiplier unit enable strobe
    input  wire [2:0]  funct3,     // Instruction funct3 field defining signed/unsigned mode
    input  wire [31:0] operand_a,  // 32-bit multiplicand operand
    input  wire [31:0] operand_b,  // 32-bit multiplier operand
    output reg  [31:0] result,     // Selected 32-bit slice of the 64-bit product
    output wire        ready       // Combinational ready indicator (always 1'b1)
);

    // -------------------------------------------------------------------------
    // Operand Sign Determination (Based on RISC-V M-Extension funct3)
    // -------------------------------------------------------------------------
    // - MUL (3'b000):    A is signed, B is signed (lower 32-bit result is sign-invariant)
    // - MULH (3'b001):   A is signed, B is signed
    // - MULHSU (3'b010): A is signed, B is unsigned (zero-extended)
    // - MULHU (3'b011):  A is unsigned, B is unsigned
    // -------------------------------------------------------------------------
    reg sign_a;
    reg sign_b;

    always @(*) begin
        case (funct3)
            `FUNCT3_MUL: begin
                sign_a = operand_a[31];
                sign_b = operand_b[31];
            end
            `FUNCT3_MULH: begin
                sign_a = operand_a[31];
                sign_b = operand_b[31];
            end
            `FUNCT3_MULHSU: begin
                sign_a = operand_a[31];
                sign_b = 1'b0;
            end
            `FUNCT3_MULHU: begin
                sign_a = 1'b0;
                sign_b = 1'b0;
            end
            default: begin
                sign_a = 1'b0;
                sign_b = 1'b0;
            end
        endcase
    end

    // -------------------------------------------------------------------------
    // 33-bit x 33-bit Unified Signed Multiplication
    // -------------------------------------------------------------------------
    // Sign-extending 32-bit signed/unsigned operands to 33-bit signed values allows
    // a single unified multiplier core to evaluate MUL, MULH, MULHSU, and MULHU
    // with optimal DSP48E1 sharing (exactly 4 cascaded DSP48E1 slices on Artix-7).
    // -------------------------------------------------------------------------
    wire signed [32:0] ext_a = $signed({sign_a, operand_a});
    wire signed [32:0] ext_b = $signed({sign_b, operand_b});
    wire signed [65:0] product_66 = ext_a * ext_b;

    // -------------------------------------------------------------------------
    // Result Slice Selection & Output Multiplexer
    // -------------------------------------------------------------------------
    always @(*) begin
        if (!reset_n || !enable) begin
            result = 32'h0000_0000;
        end else begin
            case (funct3)
                `FUNCT3_MUL:    result = product_66[31:0];   // Lower 32 bits
                `FUNCT3_MULH:   result = product_66[63:32];  // Upper 32 bits (signed x signed)
                `FUNCT3_MULHSU: result = product_66[63:32];  // Upper 32 bits (signed x unsigned)
                `FUNCT3_MULHU:  result = product_66[63:32];  // Upper 32 bits (unsigned x unsigned)
                default:        result = 32'h0000_0000;
            endcase
        end
    end

    // Single-cycle combinational ready strobe (always 1'b1, zero stall penalty)
    assign ready = 1'b1;

    // Clock signal retained for uniform coprocessor socket interface contract
    // Suppress unused signal warning in synthesis
    wire _unused_clk = &{clk, 1'b0};

endmodule
