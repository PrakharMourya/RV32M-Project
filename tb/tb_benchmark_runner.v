// ==============================================================================
// RV32M-Core: Master Benchmark Execution & Telemetry Profiler Testbench
// Module: tb_benchmark_runner.v
// Work Package: [WP-08][BENCH] (Comparative Profiling Engine)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// ==============================================================================

`timescale 1ns / 1ps
`include "opcodes.vh"

module tb_benchmark_runner;

    reg clk;
    reg rst_n;

    wire [15:0] led;
    wire [7:0]  an;
    wire [6:0]  seg;
    wire        dp;
    wire        uart_txd;

    reg [1023:0] hex_file;
    integer max_cycles;
    integer sim_cycles;
    integer halt_detect_count;
    reg     benchmark_done;
    reg [31:0] prev_halt_pc;

    // Instantiate SoC Top with CLK_DIV=1 (single clock domain simulation)
    rv32m_soc_top #(
        .CLK_DIV   (1),
        .INIT_FILE ("")
    ) soc (
        .clk      (clk),
        .rst_n    (rst_n),
        .led      (led),
        .an       (an),
        .seg      (seg),
        .dp       (dp),
        .uart_txd (uart_txd)
    );

    // 50 MHz simulation clock (20 ns period)
    initial clk = 0;
    always #10 clk = ~clk;

    initial begin
        sim_cycles = 0;
        halt_detect_count = 0;
        benchmark_done = 0;
        max_cycles = 500000;
        rst_n = 0;

        if (!$value$plusargs("HEXFILE=%s", hex_file)) begin
            $display("[ERROR] No HEXFILE specified! Use +HEXFILE=<path>");
            $finish;
        end

        if ($value$plusargs("MAX_CYCLES=%d", max_cycles)) begin
            // custom max cycles
        end

        $display("==============================================================================");
        $display("[BENCHMARK RUNNER] Loading Image: %0s", hex_file);
        $display("==============================================================================");

        $readmemh(hex_file, soc.u_bram.mem);

        #40;
        rst_n = 1;
        prev_halt_pc = 32'hFFFFFFFF;

        while (!benchmark_done && sim_cycles < max_cycles) begin
            @(posedge clk);
            sim_cycles = sim_cycles + 1;

            // Detect halt: j _halt (jal x0, 0 -> 32'h0000006F) executed in ID/EX stage
            if (soc.u_core.u_core.u_if_stage.id_instr == 32'h0000006F) begin
                halt_detect_count = halt_detect_count + 1;
                if (halt_detect_count >= 5) begin
                    benchmark_done = 1;
                end
            end
        end

        if (!benchmark_done) begin
            $display("\n[ERROR] Benchmark TIMED OUT after %0d cycles!", max_cycles);
            $display("Last PC: 0x%08h, Last Instr: 0x%08h", soc.u_core.debug_pc, soc.u_core.debug_instruction);
        end else begin
            $display("\n==============================================================================");
            $display(">>> BENCHMARK COMPLETED SUCCESSFULLY <<<");
            $display("CYCLES:        %0d", soc.u_counters.cycle_count);
            $display("INSTRUCTIONS:  %0d", soc.u_counters.instret_count);
            $display("DIV_STALLS:    %0d", soc.u_counters.stall_count);
            $display("FINAL_7SEG:    0x%08h (%0d)", soc.u_seven_seg.disp_data, soc.u_seven_seg.disp_data);
            $display("FINAL_LEDS:    0x%04h (%0d)", led, led);
            $display("RETURN_A0:     0x%08h (%0d)", soc.u_core.u_core.u_id_ex_stage.regfile[10], soc.u_core.u_core.u_id_ex_stage.regfile[10]);
            $display("==============================================================================");
        end

        $finish;
    end

endmodule
