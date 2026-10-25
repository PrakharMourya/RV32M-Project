// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: riscv_core.v (Top-Level Pipelined RV32IM Processor Core)
// Work Package: [WP-05][CORE] (Issue #05)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Top-level 3-stage pipelined RV32IM processor core:
//   - Stage 1: Instruction Fetch & Program Counter logic (if_stage.v)
//   - Stage 2: Instruction Decode, ALU & RV32M execution (id_ex_stage.v)
//              * multiplier_rv32m: Single-cycle DSP array (MUL, MULH, MULHSU, MULHU)
//              * divider_rv32m: Non-restoring FSM (DIV, DIVU, REM, REMU)
//   - Stage 3: Memory Access & Writeback Commit (wb_stage.v)
//   - Centralized Hazard Unit: Zero-cycle RAW Forwarding & Multicycle Stall Freeze (hazard_unit.v)
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module riscv_core (
    input  wire        clk,               // Master system clock (50 MHz)
    input  wire        reset_n,           // Active-low asynchronous reset

    // Instruction Memory Bus Interface
    output wire [31:0] imem_addr,         // Byte address sent to Instruction BRAM
    input  wire [31:0] imem_data,         // 32-bit fetched instruction word

    // Data Memory / MMIO Bus Interface
    output wire        dmem_read_req,     // Data memory read strobe
    output wire        dmem_write_req,    // Data memory write strobe
    output wire [3:0]  dmem_byte_enable,  // Byte write enables (4'b0001, 4'b0011, 4'b1111)
    output wire [31:0] dmem_addr,         // Data memory / MMIO target byte address
    output wire [31:0] dmem_wdata,        // Data to write into Data RAM / MMIO
    input  wire [31:0] dmem_rdata,        // Data read response from Data RAM / MMIO

    // Coprocessor Flow Control Interface
    input  wire        coproc_busy,       // External coprocessor stall freeze input

    // Real-Time Telemetry & Verification Retire Interface
    output wire [31:0] debug_pc,          // Architectural retire PC
    output wire [31:0] debug_instruction, // Architectural retire instruction word
    output wire        debug_reg_write,   // High when destination register is written
    output wire [4:0]  debug_rd,          // Destination register index (x0..x31)
    output wire [31:0] debug_wdata        // 32-bit committed value
);

    // -------------------------------------------------------------------------
    // Internal Interconnect Signals
    // -------------------------------------------------------------------------

    // Hazard Unit signals
    wire [1:0]  forward_a;
    wire [1:0]  forward_b;
    wire        stall_pipeline;
    wire        flush_if;

    // Stage 1 (IF) -> Stage 2 (ID/EX) signals
    wire [31:0] if_pc;
    wire [31:0] id_pc;
    wire [31:0] id_instr;

    // Stage 2 (ID/EX) -> Stage 1 & Hazard Unit control signals
    wire [4:0]  id_rs1;
    wire [4:0]  id_rs2;
    wire        div_busy;
    wire        branch_taken;
    wire [31:0] branch_target_pc;
    wire        is_jal;
    wire        is_jalr;

    // Stage 2 (ID/EX) -> Stage 3 (WB) pipeline signals (RegB)
    wire [31:0] ex_wb_pc;
    wire [31:0] ex_wb_instr;
    wire [4:0]  ex_wb_rd;
    wire        ex_wb_reg_write;
    wire        ex_wb_mem_read;
    wire        ex_wb_mem_write;
    wire [2:0]  ex_wb_funct3;
    wire [31:0] ex_wb_result;
    wire [31:0] ex_wb_mem_addr;
    wire [31:0] ex_wb_store_data;

    // Stage 3 (WB) -> Stage 2 (ID/EX) commit & bypass signals
    wire        wb_reg_write;
    wire [4:0]  wb_rd;
    wire [31:0] wb_wdata;
    wire [31:0] wb_forward_data;

    // -------------------------------------------------------------------------
    // Hazard Detection & Forwarding Unit
    // -------------------------------------------------------------------------
    hazard_unit u_hazard_unit (
        .id_rs1         (id_rs1),
        .id_rs2         (id_rs2),
        .wb_reg_write   (wb_reg_write),
        .wb_rd          (wb_rd),
        .div_busy       (div_busy),          // Connected to non-restoring divider FSM
        .coproc_busy    (coproc_busy),
        .branch_taken   (branch_taken),
        .is_jal         (is_jal),
        .is_jalr        (is_jalr),
        .forward_a      (forward_a),
        .forward_b      (forward_b),
        .stall_pipeline (stall_pipeline),
        .flush_if       (flush_if)
    );

    // -------------------------------------------------------------------------
    // Stage 1: Instruction Fetch & Program Counter Unit
    // -------------------------------------------------------------------------
    if_stage u_if_stage (
        .clk              (clk),
        .reset_n          (reset_n),
        .stall_pipeline   (stall_pipeline),
        .flush_if         (flush_if),
        .branch_taken     (branch_taken),
        .branch_target_pc (branch_target_pc),
        .imem_data        (imem_data),
        .imem_addr        (imem_addr),
        .if_pc            (if_pc),
        .id_pc            (id_pc),
        .id_instr         (id_instr)
    );

    // -------------------------------------------------------------------------
    // Stage 2: Instruction Decode, ALU, Multiplier & Divider Execution Unit
    // -------------------------------------------------------------------------
    id_ex_stage u_id_ex_stage (
        .clk              (clk),
        .reset_n          (reset_n),
        .stall_pipeline   (stall_pipeline),
        .id_pc            (id_pc),
        .id_instr         (id_instr),
        .forward_a        (forward_a),
        .forward_b        (forward_b),
        .wb_forward_data  (wb_forward_data),
        .wb_reg_write     (wb_reg_write),
        .wb_rd            (wb_rd),
        .wb_wdata         (wb_wdata),
        .id_rs1           (id_rs1),
        .id_rs2           (id_rs2),
        .div_busy         (div_busy),
        .branch_taken     (branch_taken),
        .branch_target_pc (branch_target_pc),
        .is_jal           (is_jal),
        .is_jalr          (is_jalr),
        .ex_wb_pc         (ex_wb_pc),
        .ex_wb_instr      (ex_wb_instr),
        .ex_wb_rd         (ex_wb_rd),
        .ex_wb_reg_write  (ex_wb_reg_write),
        .ex_wb_mem_read   (ex_wb_mem_read),
        .ex_wb_mem_write  (ex_wb_mem_write),
        .ex_wb_funct3     (ex_wb_funct3),
        .ex_wb_result     (ex_wb_result),
        .ex_wb_mem_addr   (ex_wb_mem_addr),
        .ex_wb_store_data (ex_wb_store_data)
    );

    // -------------------------------------------------------------------------
    // Stage 3: Memory Access & Writeback Commit Unit
    // -------------------------------------------------------------------------
    wb_stage u_wb_stage (
        .clk               (clk),
        .reset_n           (reset_n),
        .ex_wb_pc          (ex_wb_pc),
        .ex_wb_instr       (ex_wb_instr),
        .ex_wb_rd          (ex_wb_rd),
        .ex_wb_reg_write   (ex_wb_reg_write),
        .ex_wb_mem_read    (ex_wb_mem_read),
        .ex_wb_mem_write   (ex_wb_mem_write),
        .ex_wb_funct3      (ex_wb_funct3),
        .ex_wb_result      (ex_wb_result),
        .ex_wb_mem_addr    (ex_wb_mem_addr),
        .ex_wb_store_data  (ex_wb_store_data),
        .dmem_read_req     (dmem_read_req),
        .dmem_write_req    (dmem_write_req),
        .dmem_byte_enable  (dmem_byte_enable),
        .dmem_addr         (dmem_addr),
        .dmem_wdata        (dmem_wdata),
        .dmem_rdata        (dmem_rdata),
        .wb_reg_write      (wb_reg_write),
        .wb_rd             (wb_rd),
        .wb_wdata          (wb_wdata),
        .wb_forward_data   (wb_forward_data),
        .debug_pc          (debug_pc),
        .debug_instruction (debug_instruction),
        .debug_reg_write   (debug_reg_write),
        .debug_rd          (debug_rd),
        .debug_wdata       (debug_wdata)
    );

endmodule
