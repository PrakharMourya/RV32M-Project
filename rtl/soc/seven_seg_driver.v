// ==============================================================================
// RV32M-Core: Master System Architecture & Hardware Extension
// Module: seven_seg_driver.v (8-Digit Multiplexed 7-Segment Display Driver)
// Work Package: [WP-06][SOC] (Issue #06)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// Target FPGA: AMD Xilinx Artix-7 (XC7A100T / XC7A35T, Digilent Nexys A7 / Basys 3)
// Toolchain: AMD Vivado 2024.x/2025.x, Icarus Verilog 12+
//
// Description:
// Dynamic multiplexer driver for 8-digit common-anode 7-segment display on
// Xilinx Artix-7 FPGA boards (Digilent Nexys A7-100T / Basys 3):
//   - MMIO write target: 0x8000_0020 (32-bit hexadecimal numerical value).
//   - Internal 16-bit prescaler generating ~1 kHz digit multiplexing rate.
//   - Active-low digit anodes (an[7:0]) and active-low segment cathodes (seg[6:0]).
// ==============================================================================

`timescale 1ns / 1ps

module seven_seg_driver (
    input  wire        clk,            // System clock (50 MHz)
    input  wire        rst_n,          // Active-low reset

    // MMIO Register Write Interface (0x8000_0020)
    input  wire        write_req,
    input  wire [31:0] wdata,

    // FPGA Physical Display Pins
    output reg  [7:0]  an,             // Active-low 8-digit enable anodes
    output reg  [6:0]  seg,            // Active-low segment cathodes (CA..CG)
    output wire        dp              // Decimal point (active-low, default 1'b1)
);

    assign dp = 1'b1; // Decimal point disabled by default

    // Display data register holding the 32-bit hex word
    reg [31:0] disp_data;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            disp_data <= 32'h0000_0000;
        end else if (write_req) begin
            disp_data <= wdata;
        end
    end

    // -------------------------------------------------------------------------
    // Refresh Clock Divider (16-bit prescaler -> ~762 Hz digit scan rate)
    // -------------------------------------------------------------------------
    reg [15:0] refresh_counter;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            refresh_counter <= 16'd0;
        end else begin
            refresh_counter <= refresh_counter + 16'd1;
        end
    end

    // Active digit selector (3 bits -> 8 digits)
    wire [2:0] digit_sel = refresh_counter[15:13];

    // Current active 4-bit nibble
    reg [3:0] active_nibble;
    always @(*) begin
        case (digit_sel)
            3'b000: begin an = 8'b1111_1110; active_nibble = disp_data[3:0];   end // Digit 0
            3'b001: begin an = 8'b1111_1101; active_nibble = disp_data[7:4];   end // Digit 1
            3'b010: begin an = 8'b1111_1011; active_nibble = disp_data[11:8];  end // Digit 2
            3'b011: begin an = 8'b1111_0111; active_nibble = disp_data[15:12]; end // Digit 3
            3'b100: begin an = 8'b1110_1111; active_nibble = disp_data[19:16]; end // Digit 4
            3'b101: begin an = 8'b1101_1111; active_nibble = disp_data[23:20]; end // Digit 5
            3'b110: begin an = 8'b1011_1111; active_nibble = disp_data[27:24]; end // Digit 6
            3'b111: begin an = 8'b0111_1111; active_nibble = disp_data[31:28]; end // Digit 7
        endcase
    end

    // -------------------------------------------------------------------------
    // Hex-to-7-Segment Cathode Decoder (Active-Low: {g, f, e, d, c, b, a})
    // -------------------------------------------------------------------------
    always @(*) begin
        case (active_nibble)
            4'h0: seg = 7'b100_0000; // 0
            4'h1: seg = 7'b111_1001; // 1
            4'h2: seg = 7'b010_0100; // 2
            4'h3: seg = 7'b011_0000; // 3
            4'h4: seg = 7'b001_1001; // 4
            4'h5: seg = 7'b001_0010; // 5
            4'h6: seg = 7'b000_0010; // 6
            4'h7: seg = 7'b111_1000; // 7
            4'h8: seg = 7'b000_0000; // 8
            4'h9: seg = 7'b001_0000; // 9
            4'hA: seg = 7'b000_1000; // A
            4'hB: seg = 7'b000_0011; // b
            4'hC: seg = 7'b100_0110; // C
            4'hD: seg = 7'b010_0001; // d
            4'hE: seg = 7'b000_0110; // E
            4'hF: seg = 7'b000_1110; // F
            default: seg = 7'b111_1111; // Blank
        endcase
    end

endmodule
