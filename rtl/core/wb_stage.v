// ==============================================================================
// AutoVision-RISC-V: Stage 3 Memory Access & Writeback Commit Unit
// Module: wb_stage.v
// Work Package: [WP-01][CORE] (Issue #1)
// Target FPGA: AMD Xilinx Artix-7 XC7A100T-1CSG324C
// Academic Standard: IIT Guwahati Advanced Computer Architecture (10/10 Target)
//
// Description:
// Stage 3 of the 3-stage RV32IM processor pipeline.
// Performs memory data bus alignment for byte/halfword loads and stores,
// selects final writeback data (ALU, Multiplier, or Memory Load), commits
// to the architectural register file, and generates real-time telemetry.
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module wb_stage (
    input  wire        clk,                // Master system clock (50 MHz)
    input  wire        reset_n,            // Active-low asynchronous reset

    // Inputs from Stage 2 Pipeline Register (RegB)
    input  wire [31:0] ex_wb_pc,           // Retire PC
    input  wire [31:0] ex_wb_instr,        // Retire instruction word
    input  wire [4:0]  ex_wb_rd,           // Retire destination register
    input  wire        ex_wb_reg_write,    // Retire register write enable
    input  wire        ex_wb_mem_read,     // Retire memory read enable
    input  wire        ex_wb_mem_write,    // Retire memory write enable
    input  wire [2:0]  ex_wb_funct3,       // Memory access formatting funct3
    input  wire [31:0] ex_wb_result,       // Execution unit result (ALU, MUL, PC+4)
    input  wire [31:0] ex_wb_mem_addr,     // Memory byte address
    input  wire [31:0] ex_wb_store_data,   // Raw store payload from RS2

    // Memory Bus Interface (to Data RAM / MMIO Crossbar)
    output wire        dmem_read_req,      // Memory read strobe
    output wire        dmem_write_req,     // Memory write strobe
    output reg  [3:0]  dmem_byte_enable,   // Byte lane write strobes
    output wire [31:0] dmem_addr,          // Byte address to memory
    output reg  [31:0] dmem_wdata,         // Aligned store data
    input  wire [31:0] dmem_rdata,         // Read response from memory

    // Writeback Commit Interface (to Stage 2 RegFile & Hazard Forwarding)
    output wire        wb_reg_write,       // Register write strobe
    output wire [4:0]  wb_rd,              // Destination register index
    output wire [31:0] wb_wdata,           // Committed 32-bit register value
    output wire [31:0] wb_forward_data,    // Zero-cycle RAW bypass bus to Stage 2

    // Architectural Telemetry / Verification Interface
    output wire [31:0] debug_pc,           // Retired PC
    output wire [31:0] debug_instruction,  // Retired instruction word
    output wire        debug_reg_write,    // Active when instruction commits to regfile
    output wire [4:0]  debug_rd,           // Destination register index
    output wire [31:0] debug_wdata         // Written value
);

    assign dmem_read_req  = ex_wb_mem_read;
    assign dmem_write_req = ex_wb_mem_write;
    assign dmem_addr      = ex_wb_mem_addr;

    wire [1:0] byte_offset = ex_wb_mem_addr[1:0];

    // -------------------------------------------------------------------------
    // Store Data Alignment & Byte Enable Generation (SB, SH, SW)
    // -------------------------------------------------------------------------
    always @(*) begin
        if (!ex_wb_mem_write) begin
            dmem_byte_enable = 4'b0000;
            dmem_wdata       = 32'h0000_0000;
        end else begin
            case (ex_wb_funct3)
                `FUNCT3_SB: begin // Store Byte
                    dmem_byte_enable = 4'b0001 << byte_offset;
                    dmem_wdata       = {4{ex_wb_store_data[7:0]}};
                end
                `FUNCT3_SH: begin // Store Halfword
                    dmem_byte_enable = byte_offset[1] ? 4'b1100 : 4'b0011;
                    dmem_wdata       = {2{ex_wb_store_data[15:0]}};
                end
                `FUNCT3_SW: begin // Store Word
                    dmem_byte_enable = 4'b1111;
                    dmem_wdata       = ex_wb_store_data;
                end
                default: begin
                    dmem_byte_enable = 4'b1111;
                    dmem_wdata       = ex_wb_store_data;
                end
            endcase
        end
    end

    // -------------------------------------------------------------------------
    // Load Data Extraction & Sign/Zero Extension (LB, LH, LW, LBU, LHU)
    // -------------------------------------------------------------------------
    reg [7:0]  extracted_byte;
    reg [15:0] extracted_half;
    reg [31:0] formatted_load_data;

    always @(*) begin
        case (byte_offset)
            2'b00: extracted_byte = dmem_rdata[7:0];
            2'b01: extracted_byte = dmem_rdata[15:8];
            2'b10: extracted_byte = dmem_rdata[23:16];
            2'b11: extracted_byte = dmem_rdata[31:24];
        endcase

        extracted_half = byte_offset[1] ? dmem_rdata[31:16] : dmem_rdata[15:0];

        case (ex_wb_funct3)
            `FUNCT3_LB:  formatted_load_data = {{24{extracted_byte[7]}}, extracted_byte};
            `FUNCT3_LH:  formatted_load_data = {{16{extracted_half[15]}}, extracted_half};
            `FUNCT3_LW:  formatted_load_data = dmem_rdata;
            `FUNCT3_LBU: formatted_load_data = {24'b0, extracted_byte};
            `FUNCT3_LHU: formatted_load_data = {16'b0, extracted_half};
            default:     formatted_load_data = dmem_rdata;
        endcase
    end

    // -------------------------------------------------------------------------
    // Final Writeback Multiplexer (Memory Load vs Execution Result)
    // -------------------------------------------------------------------------
    assign wb_wdata        = ex_wb_mem_read ? formatted_load_data : ex_wb_result;
    assign wb_forward_data = wb_wdata;
    assign wb_reg_write    = ex_wb_reg_write;
    assign wb_rd           = ex_wb_rd;

    // Architectural retire telemetry
    assign debug_pc          = ex_wb_pc;
    assign debug_instruction = ex_wb_instr;
    assign debug_reg_write   = ex_wb_reg_write;
    assign debug_rd          = ex_wb_rd;
    assign debug_wdata       = wb_wdata;

endmodule
