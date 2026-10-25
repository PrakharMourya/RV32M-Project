// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: rv32m_soc_top.v (Top-Level RV32IM System-on-Chip Integration)
// Work Package: [WP-06][SOC] (Issue #06)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T, Digilent Nexys A7 / Basys 3)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Complete top-level SoC wrapper integrating the RV32IM pipelined processor core
// with on-chip memory and MMIO peripherals conforming to Section 5:
//   - 0x0000_0000 - 0x0000_3FFF (16 KB): Dual-Port Instruction & Data BRAM (ram_2p.v)
//   - 0x8000_0000 - 0x8000_0017 (24 B): 64-bit Performance Counters (cycle_counter.v)
//   - 0x8000_0020 - 0x8000_0023 (4 B):  7-Segment Display Register (seven_seg_driver.v)
//   - 0x8000_0024 - 0x8000_0027 (4 B):  LED Actuator Register (16 onboard LEDs)
//   - 0x8000_0030 - 0x8000_0037 (8 B):  115200-Baud Serial Transmitter (uart_tx.v)
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module rv32m_soc_top #(
    parameter CLK_DIV   = 2,           // Divides 100 MHz oscillator to 50 MHz core clock
    parameter INIT_FILE = ""           // Firmware hex initialization file
)(
    input  wire        clk,            // 100 MHz master clock (Digilent Nexys A7 / Basys 3)
    input  wire        rst_n,          // Active-low master reset push-button

    // Physical FPGA Peripherals
    output reg  [15:0] led,            // 16 onboard active-high LEDs
    output wire [7:0]  an,             // Active-low 8-digit 7-segment anodes
    output wire [6:0]  seg,            // Active-low 7-segment cathodes (CA..CG)
    output wire        dp,             // Decimal point
    output wire        uart_txd        // 115200-baud serial telemetry TX pin
);

    // -------------------------------------------------------------------------
    // Clock Prescaler (100 MHz -> 50 MHz Core Clock)
    // -------------------------------------------------------------------------
    reg clk_50m;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            clk_50m <= 1'b0;
        end else if (CLK_DIV > 1) begin
            clk_50m <= ~clk_50m;
        end else begin
            clk_50m <= clk;
        end
    end

    wire core_clk = (CLK_DIV == 1) ? clk : clk_50m;

    // -------------------------------------------------------------------------
    // Core Interconnect Buses
    // -------------------------------------------------------------------------
    wire [31:0] imem_addr;
    wire [31:0] imem_data;

    wire        dmem_read_req;
    wire        dmem_write_req;
    wire [3:0]  dmem_byte_enable;
    wire [31:0] dmem_addr;
    wire [31:0] dmem_wdata;
    reg  [31:0] dmem_rdata;

    wire [31:0] debug_pc;
    wire [31:0] debug_instruction;
    wire        debug_reg_write;
    wire [4:0]  debug_rd;
    wire [31:0] debug_wdata;

    // -------------------------------------------------------------------------
    // MMIO Address Decoding
    // -------------------------------------------------------------------------
    wire is_bram_access     = (dmem_addr < 32'h0000_4000);
    wire is_counter_access  = (dmem_addr >= 32'h8000_0000 && dmem_addr <= 32'h8000_0017);
    wire is_7seg_access     = (dmem_addr == 32'h8000_0020);
    wire is_led_access      = (dmem_addr == 32'h8000_0024);
    wire is_uart_access     = (dmem_addr >= 32'h8000_0030 && dmem_addr <= 32'h8000_0037);

    // Peripheral read responses
    wire [31:0] bram_rdata;
    wire [31:0] counter_rdata;
    wire [31:0] uart_rdata;

    always @(*) begin
        if (is_bram_access)         dmem_rdata = bram_rdata;
        else if (is_counter_access) dmem_rdata = counter_rdata;
        else if (is_uart_access)    dmem_rdata = uart_rdata;
        else if (is_led_access)     dmem_rdata = {16'b0, led};
        else                        dmem_rdata = 32'h0000_0000;
    end

    // -------------------------------------------------------------------------
    // Pipelined RV32IM Processor Core Instance
    // -------------------------------------------------------------------------
    rv32m_core u_core (
        .clk               (core_clk),
        .reset_n           (rst_n),
        .imem_addr         (imem_addr),
        .imem_data         (imem_data),
        .dmem_read_req     (dmem_read_req),
        .dmem_write_req    (dmem_write_req),
        .dmem_byte_enable  (dmem_byte_enable),
        .dmem_addr         (dmem_addr),
        .dmem_wdata        (dmem_wdata),
        .dmem_rdata        (dmem_rdata),
        .coproc_busy       (1'b0), // Standalone RV32IM core
        .debug_pc          (debug_pc),
        .debug_instruction (debug_instruction),
        .debug_reg_write   (debug_reg_write),
        .debug_rd          (debug_rd),
        .debug_wdata       (debug_wdata)
    );

    // -------------------------------------------------------------------------
    // 16 KB On-Chip Dual-Port BRAM Block (ram_2p)
    // -------------------------------------------------------------------------
    ram_2p #(
        .MEM_SIZE_WORDS (4096),
        .INIT_FILE      (INIT_FILE)
    ) u_bram (
        .clk              (core_clk),
        .imem_addr        (imem_addr),
        .imem_data        (imem_data),
        .dmem_read_req    (dmem_read_req && is_bram_access),
        .dmem_write_req   (dmem_write_req && is_bram_access),
        .dmem_byte_enable (dmem_byte_enable),
        .dmem_addr        (dmem_addr),
        .dmem_wdata       (dmem_wdata),
        .dmem_rdata       (bram_rdata)
    );

    // -------------------------------------------------------------------------
    // 64-bit Performance Telemetry Counters (cycle_counter)
    // -------------------------------------------------------------------------
    cycle_counter u_counters (
        .clk           (core_clk),
        .rst_n         (rst_n),
        .instr_retired (debug_reg_write && (debug_rd != 5'd0)),
        .core_stalled  (u_core.u_core.u_hazard_unit.stall_pipeline),
        .read_req      (dmem_read_req && is_counter_access),
        .write_req     (dmem_write_req && is_counter_access),
        .addr          (dmem_addr),
        .wdata         (dmem_wdata),
        .rdata         (counter_rdata)
    );

    // -------------------------------------------------------------------------
    // 8-Digit Dynamic Multiplexed 7-Segment Display Driver
    // -------------------------------------------------------------------------
    seven_seg_driver u_seven_seg (
        .clk       (core_clk),
        .rst_n     (rst_n),
        .write_req (dmem_write_req && is_7seg_access),
        .wdata     (dmem_wdata),
        .an        (an),
        .seg       (seg),
        .dp        (dp)
    );

    // -------------------------------------------------------------------------
    // 16-Bit LED Actuator Register (0x8000_0024)
    // -------------------------------------------------------------------------
    always @(posedge core_clk or negedge rst_n) begin
        if (!rst_n) begin
            led <= 16'h0000;
        end else if (dmem_write_req && is_led_access) begin
            led <= dmem_wdata[15:0];
        end
    end

    // -------------------------------------------------------------------------
    // 115200-Baud Serial UART Transmitter
    // -------------------------------------------------------------------------
    uart_tx #(
        .CLK_FREQ_HZ (50_000_000),
        .BAUD_RATE   (115_200)
    ) u_uart (
        .clk       (core_clk),
        .rst_n     (rst_n),
        .read_req  (dmem_read_req && is_uart_access),
        .write_req (dmem_write_req && is_uart_access),
        .addr      (dmem_addr),
        .wdata     (dmem_wdata),
        .rdata     (uart_rdata),
        .tx        (uart_txd)
    );

endmodule
