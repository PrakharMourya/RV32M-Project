// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: rv32m_core.v (Top-Level Pipelined RV32IM Processor Core Wrapper)
// Work Package: [WP-05][CORE] (Issue #05)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Canonical top-level core module wrapper for the 3-stage RV32IM processor core
// conforming to Section 8 of the Master Architecture Brief.
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module rv32m_core (
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

    riscv_core u_core (
        .clk               (clk),
        .reset_n           (reset_n),
        .imem_addr         (imem_addr),
        .imem_data         (imem_data),
        .dmem_read_req     (dmem_read_req),
        .dmem_write_req    (dmem_write_req),
        .dmem_byte_enable  (dmem_byte_enable),
        .dmem_addr         (dmem_addr),
        .dmem_wdata        (dmem_wdata),
        .dmem_rdata        (dmem_rdata),
        .coproc_busy       (coproc_busy),
        .debug_pc          (debug_pc),
        .debug_instruction (debug_instruction),
        .debug_reg_write   (debug_reg_write),
        .debug_rd          (debug_rd),
        .debug_wdata       (debug_wdata)
    );

endmodule
