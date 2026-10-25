// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: cycle_counter.v (Hardware Performance Profiling Counters)
// Work Package: [WP-06][SOC] (Issue #06)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// High-precision 64-bit hardware performance profiling counters conforming to
// Section 5 of the Master Architecture Brief:
//   - 0x8000_0000 - 0x8000_0007: 64-bit Core Cycle Counter (mcycle mirror)
//   - 0x8000_0008 - 0x8000_000F: 64-bit Retired Instruction Counter (minstret mirror)
//   - 0x8000_0010 - 0x8000_0017: 64-bit M-Extension Stall Cycle Counter
// Supports 32-bit software reads for lower and upper words, plus software reset.
// ==============================================================================

`timescale 1ns / 1ps

module cycle_counter (
    input  wire        clk,
    input  wire        rst_n,

    // Core Telemetry Inputs
    input  wire        instr_retired,      // High when an instruction commits in WB stage
    input  wire        core_stalled,       // High when pipeline is frozen (div_busy | coproc_busy)

    // MMIO Bus Interface
    input  wire        read_req,
    input  wire        write_req,
    input  wire [31:0] addr,
    input  wire [31:0] wdata,
    output reg  [31:0] rdata
);

    // 64-bit Internal Counters
    reg [63:0] cycle_count;
    reg [63:0] instret_count;
    reg [63:0] stall_count;

    // -------------------------------------------------------------------------
    // Counter Increment & Reset Logic
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cycle_count   <= 64'd0;
            instret_count <= 64'd0;
            stall_count   <= 64'd0;
        end else begin
            // Software clear via MMIO write to 0x8000_0000
            if (write_req && (addr[7:0] == 8'h00)) begin
                cycle_count   <= 64'd0;
                instret_count <= 64'd0;
                stall_count   <= 64'd0;
            end else begin
                cycle_count <= cycle_count + 64'd1;

                if (instr_retired) begin
                    instret_count <= instret_count + 64'd1;
                end

                if (core_stalled) begin
                    stall_count <= stall_count + 64'd1;
                end
            end
        end
    end

    // -------------------------------------------------------------------------
    // MMIO Read Multiplexing
    // -------------------------------------------------------------------------
    always @(*) begin
        if (read_req) begin
            case (addr[7:0])
                8'h00:   rdata = cycle_count[31:0];      // 0x8000_0000: mcycle low
                8'h04:   rdata = cycle_count[63:32];     // 0x8000_0004: mcycle high
                8'h08:   rdata = instret_count[31:0];    // 0x8000_0008: minstret low
                8'h0C:   rdata = instret_count[63:32];   // 0x8000_000C: minstret high
                8'h10:   rdata = stall_count[31:0];      // 0x8000_0010: stall count low
                8'h14:   rdata = stall_count[63:32];     // 0x8000_0014: stall count high
                default: rdata = 32'h0000_0000;
            endcase
        end else begin
            rdata = 32'h0000_0000;
        end
    end

endmodule
