// ==============================================================================
// AutoVision-RISC-V: Pipeline Hazard Forwarding, Stall Interlock & Flush Unit
// Module: hazard_unit.v
// Work Package: [WP-02][CORE] (Issue #2)
// Target FPGA: AMD Xilinx Artix-7 XC7A100T-1CSG324C
// Academic Standard: IIT Guwahati Advanced Computer Architecture (10/10 Target)
//
// Description:
// Centralized hazard unit resolving data (RAW) and control hazards in the
// 3-stage pipelined RV32IM processor:
//   1. Zero-Cycle RAW Data Forwarding (WB -> EX) for back-to-back operands (0 penalty)
//   2. Multi-Cycle Pipeline Stall Freezing (PC & Stage 1 registers held during coprocessor busy)
//   3. Control Hazard Flushing (1-cycle NOP insertion on branch/jump execution)
// ==============================================================================

`timescale 1ns / 1ps

module hazard_unit (
    input  wire [4:0]  id_rs1,         // Source register 1 address from decode stage
    input  wire [4:0]  id_rs2,         // Source register 2 address from decode stage
    input  wire        wb_reg_write,   // Register write enable signal from writeback stage
    input  wire [4:0]  wb_rd,          // Destination register address from writeback stage
    input  wire        div_busy,       // Stall signal from non-restoring divider FSM
    input  wire        coproc_busy,    // Stall signal from external vision coprocessors
    input  wire        branch_taken,   // Asserted when branch condition is satisfied
    input  wire        is_jal,         // Asserted when JAL instruction is decoded
    input  wire        is_jalr,        // Asserted when JALR instruction is decoded
    output reg  [1:0]  forward_a,      // Forwarding mux select for operand A (2'b00: RegFile, 2'b10: WB)
    output reg  [1:0]  forward_b,      // Forwarding mux select for operand B (2'b00: RegFile, 2'b10: WB)
    output wire        stall_pipeline, // Synchronous freeze enable for PC and Stage 1 registers
    output wire        flush_if        // Synchronous clear for Stage 1 instruction register
);

    // -------------------------------------------------------------------------
    // Zero-Cycle RAW Data Forwarding Logic (WB -> EX)
    // -------------------------------------------------------------------------
    // If the instruction currently committing in Writeback writes to a register
    // (wb_rd != 0) that matches the source operand register in Decode/Execute (id_rs1/id_rs2),
    // forward the commit data directly into the execution unit inputs.
    // -------------------------------------------------------------------------
    always @(*) begin
        if (wb_reg_write && (wb_rd != 5'd0) && (wb_rd == id_rs1)) begin
            forward_a = 2'b10; // Bypass from Writeback stage
        end else begin
            forward_a = 2'b00; // Normal read from Register File
        end

        if (wb_reg_write && (wb_rd != 5'd0) && (wb_rd == id_rs2)) begin
            forward_b = 2'b10; // Bypass from Writeback stage
        end else begin
            forward_b = 2'b00; // Normal read from Register File
        end
    end

    // -------------------------------------------------------------------------
    // Multi-Cycle Coprocessor Stall Freezing
    // -------------------------------------------------------------------------
    // Holds the Program Counter (PC) and Stage 1 (IF/ID) pipeline registers
    // without state modification while divider FSM or vision coprocessor is active.
    // -------------------------------------------------------------------------
    assign stall_pipeline = div_busy | coproc_busy;

    // -------------------------------------------------------------------------
    // Control Hazard Branch / Jump Flushing
    // -------------------------------------------------------------------------
    // Invalidate the speculative instruction fetched into Stage 1 by injecting
    // a synchronous NOP bubble when a branch is taken or jump occurs.
    // -------------------------------------------------------------------------
    assign flush_if = (branch_taken | is_jal | is_jalr) & ~stall_pipeline;

endmodule
