// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: ram_2p.v (Dual-Port On-Chip Memory Block)
// Work Package: [WP-06][SOC] (Issue #06)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Dual-port synchronous/combinational on-chip RAM block implementing the unified
// 16 KB memory map (0x0000_0000 - 0x0000_3FFF):
//   - Port A: Dedicated Instruction Fetch interface (imem_addr -> imem_data).
//   - Port B: Data Memory load/store interface with 4-byte independent write enables.
//   - Parameterized firmware pre-loading via INIT_FILE ($readmemh).
// ==============================================================================

`timescale 1ns / 1ps

module ram_2p #(
    parameter MEM_SIZE_WORDS = 4096,           // 16 KB (4096 words x 32 bits)
    parameter INIT_FILE      = ""              // Optional hex initialization file path
)(
    input  wire        clk,

    // Port A: Instruction Memory Read Interface
    input  wire [31:0] imem_addr,
    output reg  [31:0] imem_data,

    // Port B: Data Memory Read/Write Interface
    input  wire        dmem_read_req,
    input  wire        dmem_write_req,
    input  wire [3:0]  dmem_byte_enable,
    input  wire [31:0] dmem_addr,
    input  wire [31:0] dmem_wdata,
    output reg  [31:0] dmem_rdata
);

    // 4096 x 32-bit memory array (16 KB)
    reg [31:0] mem [0:MEM_SIZE_WORDS-1];
    integer i;

    // Optional firmware initialization
    initial begin
        for (i = 0; i < MEM_SIZE_WORDS; i = i + 1) begin
            mem[i] = 32'h0000_0013; // Default to NOP (addi x0, x0, 0)
        end
        if (INIT_FILE != "") begin
            $readmemh(INIT_FILE, mem);
        end
    end

    // -------------------------------------------------------------------------
    // Port A: Instruction Fetch (Word-Aligned Address)
    // -------------------------------------------------------------------------
    wire [29:0] imem_word_idx = imem_addr[31:2];
    always @(*) begin
        if (imem_word_idx < MEM_SIZE_WORDS) begin
            imem_data = mem[imem_word_idx];
        end else begin
            imem_data = 32'h0000_0013; // NOP for out-of-bounds fetch
        end
    end

    // -------------------------------------------------------------------------
    // Port B: Data Memory Access (Word-Aligned Address with Byte Strobes)
    // -------------------------------------------------------------------------
    wire [29:0] dmem_word_idx = dmem_addr[31:2];

    always @(posedge clk) begin
        if (dmem_write_req && (dmem_word_idx < MEM_SIZE_WORDS)) begin
            if (dmem_byte_enable[0]) mem[dmem_word_idx][7:0]   <= dmem_wdata[7:0];
            if (dmem_byte_enable[1]) mem[dmem_word_idx][15:8]  <= dmem_wdata[15:8];
            if (dmem_byte_enable[2]) mem[dmem_word_idx][23:16] <= dmem_wdata[23:16];
            if (dmem_byte_enable[3]) mem[dmem_word_idx][31:24] <= dmem_wdata[31:24];
        end
    end

    always @(*) begin
        if (dmem_read_req && (dmem_word_idx < MEM_SIZE_WORDS)) begin
            dmem_rdata = mem[dmem_word_idx];
        end else begin
            dmem_rdata = 32'h0000_0000;
        end
    end

endmodule
