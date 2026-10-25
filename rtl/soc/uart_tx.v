// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: uart_tx.v (115200-Baud Hardware Diagnostic Serial Transmitter)
// Work Package: [WP-06][SOC] (Issue #06)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Parameterized serial UART transmitter conforming to Section 5:
//   - Fixed 115200 baud transmission rate at 50 MHz system clock (434 clocks/bit).
//   - Frame: 1 start bit, 8 data bits (LSB first), 1 stop bit (8-N-1).
//   - MMIO 0x8000_0030: TX Data Register (write 8-bit character to transmit).
//   - MMIO 0x8000_0034: TX Status Register (bit 0: tx_ready, bit 1: tx_busy).
// ==============================================================================

`timescale 1ns / 1ps

module uart_tx #(
    parameter CLK_FREQ_HZ = 50_000_000,
    parameter BAUD_RATE   = 115_200
)(
    input  wire        clk,
    input  wire        rst_n,

    // MMIO Interface (0x8000_0030 - 0x8000_0037)
    input  wire        read_req,
    input  wire        write_req,
    input  wire [31:0] addr,
    input  wire [31:0] wdata,
    output reg  [31:0] rdata,

    // Physical Serial Pin
    output reg         tx
);

    localparam CLOCKS_PER_BIT = CLK_FREQ_HZ / BAUD_RATE; // ~434 clocks at 50 MHz

    localparam [1:0] STATE_IDLE  = 2'b00;
    localparam [1:0] STATE_START = 2'b01;
    localparam [1:0] STATE_DATA  = 2'b10;
    localparam [1:0] STATE_STOP  = 2'b11;

    reg [1:0]  state;
    reg [15:0] clk_count;
    reg [2:0]  bit_idx;
    reg [7:0]  tx_data;
    reg        tx_busy;

    wire tx_ready = !tx_busy;

    // -------------------------------------------------------------------------
    // UART Transmitter State Machine
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= STATE_IDLE;
            clk_count <= 16'd0;
            bit_idx   <= 3'd0;
            tx_data   <= 8'h00;
            tx_busy   <= 1'b0;
            tx        <= 1'b1; // Idle line is high
        end else begin
            case (state)
                STATE_IDLE: begin
                    tx <= 1'b1;
                    clk_count <= 16'd0;
                    bit_idx   <= 3'd0;
                    if (write_req && (addr[3:0] == 4'h0)) begin
                        tx_data <= wdata[7:0];
                        tx_busy <= 1'b1;
                        state   <= STATE_START;
                    end else begin
                        tx_busy <= 1'b0;
                    end
                end

                STATE_START: begin
                    tx <= 1'b0; // Start bit is low
                    if (clk_count < CLOCKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 16'd1;
                    end else begin
                        clk_count <= 16'd0;
                        state     <= STATE_DATA;
                    end
                end

                STATE_DATA: begin
                    tx <= tx_data[bit_idx];
                    if (clk_count < CLOCKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 16'd1;
                    end else begin
                        clk_count <= 16'd0;
                        if (bit_idx < 3'd7) begin
                            bit_idx <= bit_idx + 3'd1;
                        end else begin
                            state   <= STATE_STOP;
                        end
                    end
                end

                STATE_STOP: begin
                    tx <= 1'b1; // Stop bit is high
                    if (clk_count < CLOCKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 16'd1;
                    end else begin
                        clk_count <= 16'd0;
                        tx_busy   <= 1'b0;
                        state     <= STATE_IDLE;
                    end
                end

                default: state <= STATE_IDLE;
            endcase
        end
    end

    // -------------------------------------------------------------------------
    // MMIO Read Interface (0x8000_0034 returns status)
    // -------------------------------------------------------------------------
    always @(*) begin
        if (read_req) begin
            case (addr[3:0])
                4'h0:    rdata = {24'b0, tx_data};
                4'h4:    rdata = {30'b0, tx_busy, tx_ready}; // Bit 0: ready, Bit 1: busy
                default: rdata = 32'h0000_0000;
            endcase
        end else begin
            rdata = 32'h0000_0000;
        end
    end

endmodule
