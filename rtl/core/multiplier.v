`timescale 1ns / 1ps
`include "opcodes.vh"

module multiplier (
    input  wire        clk,
    input  wire        reset_n,
    input  wire        enable,
    input  wire [2:0]  funct3,
    input  wire [31:0] operand_a,
    input  wire [31:0] operand_b,
    output reg  [31:0] result,
    output wire        ready
);

    reg sign_a;
    reg sign_b;

    always @(*) begin
        case (funct3)
            `FUNCT3_MUL: begin
                sign_a = operand_a[31];
                sign_b = operand_b[31];
            end
            `FUNCT3_MULH: begin
                sign_a = operand_a[31];
                sign_b = operand_b[31];
            end
            `FUNCT3_MULHSU: begin
                sign_a = operand_a[31];
                sign_b = 1'b0;
            end
            `FUNCT3_MULHU: begin
                sign_a = 1'b0;
                sign_b = 1'b0;
            end
            default: begin
                sign_a = 1'b0;
                sign_b = 1'b0;
            end
        endcase
    end

    assign ready = 1'b1;
    always @(*) result = 32'd0;
    wire _unused_clk = &{clk, reset_n, enable, 1'b0};

endmodule
