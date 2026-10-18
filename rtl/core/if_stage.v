// ==============================================================================
// AutoVision-RISC-V: Stage 1 Instruction Fetch & Program Counter Unit
// Module: if_stage.v
// Work Package: [WP-01][CORE] (Issue #1)
// Target FPGA: AMD Xilinx Artix-7 XC7A100T-1CSG324C
// Academic Standard: IIT Guwahati Advanced Computer Architecture (10/10 Target)
//
// Description:
// Stage 1 of the 3-stage RV32IM processor pipeline.
// Manages the Program Counter (PC), sequential +4 incrementing, branch/jump
// target redirection, stall pipeline freezing, and speculative fetch flushing.
// ==============================================================================

`timescale 1ns / 1ps

module if_stage (
    input  wire        clk,              // Master system clock (50 MHz)
    input  wire        reset_n,          // Active-low asynchronous reset
    input  wire        stall_pipeline,   // Freeze PC and IF/ID pipeline registers
    input  wire        flush_if,         // Flush Stage 1 instruction register to NOP
    input  wire        branch_taken,     // Branch or jump condition satisfied in Stage 2
    input  wire [31:0] branch_target_pc, // Target address computed in Stage 2
    input  wire [31:0] imem_data,        // 32-bit instruction word from instruction memory
    output wire [31:0] imem_addr,        // Instruction memory address (byte address)
    output reg  [31:0] if_pc,            // Current PC in Fetch stage
    output reg  [31:0] id_pc,            // Latched PC in Decode/Execute stage
    output reg  [31:0] id_instr          // Latched instruction in Decode/Execute stage
);

    // Instruction memory address is driven by current fetch PC
    assign imem_addr = if_pc;

    // -------------------------------------------------------------------------
    // Program Counter (PC) Update Logic
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            if_pc <= 32'h0000_0000;
        end else if (branch_taken) begin
            // Branch or jump redirection takes highest priority
            if_pc <= branch_target_pc;
        end else if (!stall_pipeline) begin
            // Sequential execution: increment PC by 4 bytes (32-bit word)
            if_pc <= if_pc + 32'd4;
        end
        // If stall_pipeline is active, if_pc maintains its current value
    end

    // -------------------------------------------------------------------------
    // Stage 1 -> Stage 2 Pipeline Registers (RegA)
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            id_pc    <= 32'h0000_0000;
            id_instr <= 32'h0000_0013; // RISC-V NOP (addi x0, x0, 0)
        end else if (flush_if) begin
            // Invalidate speculative instruction on taken branch/jump
            id_pc    <= if_pc;
            id_instr <= 32'h0000_0013; // RISC-V NOP
        end else if (!stall_pipeline) begin
            id_pc    <= if_pc;
            id_instr <= imem_data;
        end
        // If stall_pipeline is active, id_pc and id_instr maintain their values
    end

endmodule
