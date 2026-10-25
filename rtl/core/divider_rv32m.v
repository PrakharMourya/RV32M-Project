// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: divider_rv32m.v
// Work Package: [WP-03][CORE] (Issue #03)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Fully synthesizable 32-bit hardware integer division and modulo coprocessor
// compliant with the unprivileged RISC-V M-Extension specification. Implements
// an optimized non-restoring/restoring radix-2 sequential shift-subtract FSM
// with dedicated 1-cycle early-exit bypass for boundary corner cases.
//
// Supported Instructions (funct7 = 7'b0000001, opcode = 7'b0110011):
//   - DIV  (funct3 = 3'b100): Signed integer quotient   (Rd = Rs1 /s Rs2)
//   - DIVU (funct3 = 3'b101): Unsigned integer quotient (Rd = Rs1 /u Rs2)
//   - REM  (funct3 = 3'b110): Signed remainder          (Rd = Rs1 %s Rs2)
//   - REMU (funct3 = 3'b111): Unsigned remainder        (Rd = Rs1 %u Rs2)
//
// Corner-Case Hardware Specifications:
//   1. Division by Zero (Rs2 = 0):
//      - DIV(x, 0)  -> -1 (32'hFFFF_FFFF)
//      - DIVU(x, 0) -> 2^32 - 1 (32'hFFFF_FFFF)
//      - REM(x, 0)  -> x (Original Dividend)
//      - REMU(x, 0) -> x (Original Dividend)
//      - Immediate 1-cycle exit asserted without running 32-cycle FSM.
//   2. Signed Overflow (Rs1 = -2^31 = 32'h8000_0000 and Rs2 = -1 = 32'hFFFF_FFFF):
//      - DIV(-2^31, -1) -> -2^31 (32'h8000_0000)
//      - REM(-2^31, -1) -> 0     (32'h0000_0000)
//      - Immediate 1-cycle exit asserted without running 32-cycle FSM.
//   3. Remainder Sign Rule:
//      - Sign of a non-zero remainder strictly equals the sign of the dividend (Rs1).
//
// Pipeline Interlock Contract:
//   - When start is asserted, busy goes high if multi-cycle calculation is required.
//   - Multi-cycle execution runs in 32 iterations (<= 34 cycles total).
//   - 'done' is pulsed high for exactly 1 cycle upon valid result completion.
//   - Fully synchronous active-low reset (rst_n).
// ==============================================================================

`timescale 1ns / 1ps

module divider_rv32m (
    input  wire        clk,        // System clock (50 MHz - 100 MHz target)
    input  wire        rst_n,      // Synchronous active-low reset
    input  wire        start,      // Trigger signal from decode/execute stage
    input  wire [2:0]  funct3,     // 3'b100: DIV, 3'b101: DIVU, 3'b110: REM, 3'b111: REMU
    input  wire [31:0] dividend,   // rs1 data
    input  wire [31:0] divisor,    // rs2 data
    output reg  [31:0] quotient,   // 32-bit quotient
    output reg  [31:0] remainder,  // 32-bit remainder
    output reg  [31:0] result,     // Selected output routed to rd
    output reg         busy,       // High during multi-cycle operation -> stalls pipeline
    output reg         done        // 1-cycle active pulse when execution finishes
);

    // -------------------------------------------------------------------------
    // funct3 Operation Parameterization
    // -------------------------------------------------------------------------
    localparam [2:0] OP_DIV  = 3'b100;
    localparam [2:0] OP_DIVU = 3'b101;
    localparam [2:0] OP_REM  = 3'b110;
    localparam [2:0] OP_REMU = 3'b111;

    // -------------------------------------------------------------------------
    // FSM State Encoding
    // -------------------------------------------------------------------------
    localparam [1:0] S_IDLE = 2'b00;
    localparam [1:0] S_CALC = 2'b01;

    reg [1:0]  state;
    reg [4:0]  count;
    reg [2:0]  op_funct3;
    reg        neg_quot;
    reg        neg_rem;
    reg [31:0] reg_dvr;
    reg [31:0] reg_rem;
    reg [31:0] reg_quot;

    // -------------------------------------------------------------------------
    // Operand Classification & Corner-Case Detection
    // -------------------------------------------------------------------------
    wire is_signed = (funct3 == OP_DIV) || (funct3 == OP_REM);
    wire sign_dvd  = is_signed && dividend[31];
    wire sign_dvr  = is_signed && divisor[31];

    // Absolute magnitude extraction for signed arithmetic
    wire [31:0] abs_dvd = sign_dvd ? (-dividend) : dividend;
    wire [31:0] abs_dvr = sign_dvr ? (-divisor)  : divisor;

    // Corner cases
    wire is_div_by_zero     = (divisor == 32'h0000_0000);
    wire is_signed_overflow = is_signed && (dividend == 32'h8000_0000) && (divisor == 32'hFFFF_FFFF);
    wire early_exit         = is_div_by_zero || is_signed_overflow;

    // -------------------------------------------------------------------------
    // Sequential Radix-2 Shift-Subtract Logic (Combinational Step within S_CALC)
    // -------------------------------------------------------------------------
    wire [31:0] shift_rem  = {reg_rem[30:0], reg_quot[31]};
    wire [32:0] sub_diff   = {1'b0, shift_rem} - {1'b0, reg_dvr};
    wire        sub_ge     = ~sub_diff[32]; // 1 if shift_rem >= reg_dvr

    wire [31:0] step_rem   = sub_ge ? sub_diff[31:0] : shift_rem;
    wire [31:0] step_quot  = {reg_quot[30:0], sub_ge};

    // Sign restoration for final iteration
    wire [31:0] restored_quot = neg_quot ? (-step_quot) : step_quot;
    wire [31:0] restored_rem  = neg_rem  ? (-step_rem)  : step_rem;

    // -------------------------------------------------------------------------
    // Divider State Machine & Datapath Register Control
    // -------------------------------------------------------------------------
    always @(posedge clk) begin
        if (!rst_n) begin
            state     <= S_IDLE;
            count     <= 5'd0;
            op_funct3 <= 3'd0;
            neg_quot  <= 1'b0;
            neg_rem   <= 1'b0;
            reg_dvr   <= 32'h0000_0000;
            reg_rem   <= 32'h0000_0000;
            reg_quot  <= 32'h0000_0000;
            quotient  <= 32'h0000_0000;
            remainder <= 32'h0000_0000;
            result    <= 32'h0000_0000;
            busy      <= 1'b0;
            done      <= 1'b0;
        end else begin
            case (state)
                S_IDLE: begin
                    done <= 1'b0;
                    if (start) begin
                        if (is_div_by_zero) begin
                            // Corner Case 1: Division by Zero (1-cycle early termination)
                            quotient  <= 32'hFFFF_FFFF;
                            remainder <= dividend;
                            result    <= (funct3[1] == 1'b0) ? 32'hFFFF_FFFF : dividend;
                            busy      <= 1'b0;
                            done      <= 1'b1;
                            state     <= S_IDLE;
                        end else if (is_signed_overflow) begin
                            // Corner Case 2: Signed Overflow (-2^31 / -1) (1-cycle early termination)
                            quotient  <= 32'h8000_0000;
                            remainder <= 32'h0000_0000;
                            result    <= (funct3[1] == 1'b0) ? 32'h8000_0000 : 32'h0000_0000;
                            busy      <= 1'b0;
                            done      <= 1'b1;
                            state     <= S_IDLE;
                        end else begin
                            // Initialize 32-cycle sequential shift-subtract FSM
                            reg_dvr   <= abs_dvr;
                            reg_rem   <= 32'h0000_0000;
                            reg_quot  <= abs_dvd;
                            count     <= 5'd31; // 32 steps (31 down to 0)
                            op_funct3 <= funct3;
                            neg_quot  <= is_signed && (sign_dvd ^ sign_dvr);
                            neg_rem   <= is_signed && sign_dvd;
                            busy      <= 1'b1;
                            done      <= 1'b0;
                            state     <= S_CALC;
                        end
                    end else begin
                        busy <= 1'b0;
                    end
                end

                S_CALC: begin
                    if (count == 5'd0) begin
                        // Final 32nd step: apply sign restoration and commit results
                        quotient  <= restored_quot;
                        remainder <= restored_rem;
                        result    <= (op_funct3[1] == 1'b0) ? restored_quot : restored_rem;
                        busy      <= 1'b0;
                        done      <= 1'b1;
                        state     <= S_IDLE;
                    end else begin
                        // Intermediate shift-subtract step
                        reg_rem  <= step_rem;
                        reg_quot <= step_quot;
                        count    <= count - 5'd1;
                        busy     <= 1'b1;
                        done     <= 1'b0;
                    end
                end

                default: begin
                    state <= S_IDLE;
                    busy  <= 1'b0;
                    done  <= 1'b0;
                end
            endcase
        end
    end

endmodule
