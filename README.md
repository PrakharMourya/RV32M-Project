# RV32I Processor Extension with RV32M Instruction Set Architecture

**Group / Academic Standard:** Group 22 — IIT Guwahati Advanced Computer Architecture & FPGA System Design  
**Lead / Author:** Abhishek Kumar Deepak (Roll: 250101002, GitHub: [`abhiii927`](https://github.com/abhiii927))  
**Remote Repository:** [https://github.com/abhiii927/RV32M-Project](https://github.com/abhiii927/RV32M-Project)  
**Target FPGA Device:** AMD Xilinx Artix-7 (`xc7a100tcsg324-1`, Digilent Nexys A7 / Basys 3)  
**Toolchain & Simulation:** AMD Vivado 2024.x/2025.x, Icarus Verilog 12+, GTKWave, RISC-V GNU Toolchain (`riscv64-unknown-elf-gcc` 13.4.0), Python 3.10+

---

## 1. Executive Summary

This repository delivers the complete, standard-compliant implementation of the **RISC-V "M" Standard Extension (RV32M)** for integer multiplication and division integrated into a 3-stage pipelined RV32I processor core.

Baseline RV32I processors emulate multiplication and division through software library subroutines (`__mulsi3`, `__divsi3`, `__udivsi3`, `__modsi3`, `__umodsi3`), incurring hundreds of clock cycles per operation. This design incorporates dedicated hardware-accelerated execution units directly into the CPU decode/execute stage:
- **Single-Cycle DSP-Assisted Multiplier:** Evaluates signed, unsigned, and mixed multiplications (`MUL`, `MULH`, `MULHSU`, `MULHU`) in 1 clock cycle using 4 dedicated DSP48E1 slices on AMD Xilinx Artix-7.
- **32-Step Non-Restoring Divider FSM:** Computes signed/unsigned quotient and remainder (`DIV`, `DIVU`, `REM`, `REMU`) with $\le 33$ cycle execution latency and 1-cycle early termination for division-by-zero ($R_{s2} = 0$) and signed overflow ($-2^{31} / -1$).
- **FPGA SoC Top-Level:** Integrates the RV32IM core with a 16 KB dual-port memory block, 64-bit performance telemetry counters (cycles, retired instructions, multi-cycle stall profiler), 8-digit multiplexed seven-segment display, and a 115200-baud serial UART transmitter.

---

## 2. Microarchitectural Specifications

### 2.1 Instruction Set Architecture (RV32M)
All instructions use R-type format (`opcode = 7'b0110011` / `0x33`, `funct7 = 7'b0000001`):

| Instruction | funct3 | Operation | Mathematical Semantics | Latency |
|:---|:---:|:---|:---|:---:|
| `MUL`    | `3'b000` | Multiply Low | $R_d = (R_{s1} \times R_{s2})[31:0]$ (Signed $\times$ Signed) | 1 cycle |
| `MULH`   | `3'b001` | Multiply High Signed | $R_d = (R_{s1} \times R_{s2})[63:32]$ (Signed $\times$ Signed) | 1 cycle |
| `MULHSU` | `3'b010` | Multiply High Signed-Unsigned | $R_d = (R_{s1} \times R_{s2})[63:32]$ (Signed $\times$ Unsigned) | 1 cycle |
| `MULHU`  | `3'b011` | Multiply High Unsigned | $R_d = (R_{s1} \times R_{s2})[63:32]$ (Unsigned $\times$ Unsigned) | 1 cycle |
| `DIV`    | `3'b100` | Signed Division | $R_d = R_{s1} \,/\, R_{s2}$ | $\le 33$ cycles |
| `DIVU`   | `3'b101` | Unsigned Division | $R_d = R_{s1} \,/\, R_{s2}$ | $\le 33$ cycles |
| `REM`    | `3'b110` | Signed Remainder | $R_d = R_{s1} \pmod{R_{s2}}$, $\text{sign}(R_d) = \text{sign}(R_{s1})$ | $\le 33$ cycles |
| `REMU`   | `3'b111` | Unsigned Remainder | $R_d = R_{s1} \pmod{R_{s2}}$ | $\le 33$ cycles |

### 2.2 Corner-Case Compliance Matrix

| Operation | Condition | Standard RV32M Result | Hardware Implementation Status |
|:---|:---|:---:|:---:|
| `DIV` / `DIVU` | Divide by zero ($R_{s2} = 0$) | All ones (`-1` / `0xFFFFFFFF`) | 1-cycle early exit (Verified) |
| `REM` / `REMU` | Remainder by zero ($R_{s2} = 0$) | Dividend ($R_{s1}$) | 1-cycle early exit (Verified) |
| `DIV` | Signed overflow ($-2^{31} / -1$) | $-2^{31}$ (`0x80000000`) | 1-cycle early exit (Verified) |
| `REM` | Signed overflow ($-2^{31} / -1$) | Zero (`0x00000000`) | 1-cycle early exit (Verified) |
| `REM` | Negative dividend, positive divisor | Negative remainder | Sign match rule enforced (Verified) |
| `REM` | Positive dividend, negative divisor | Positive remainder | Sign match rule enforced (Verified) |

---

## 3. Work Package (WP) Milestone Deliverables

- **WP-01 & WP-02: Multiplier Engine & Standalone Testbench**
  - RTL: [`rtl/core/multiplier_rv32m.v`](rtl/core/multiplier_rv32m.v) with unified 33-bit $\times$ 33-bit signed DSP datapath.
  - Testbench: [`tb/tb_multiplier.v`](tb/tb_multiplier.v) evaluated 40,027 test vectors: **0 errors (100% PASS)**.
- **WP-03 & WP-04: Non-Restoring Divider FSM & Exhaustive Testbench**
  - RTL: [`rtl/core/divider_rv32m.v`](rtl/core/divider_rv32m.v) with 32-step radix-2 shift-subtract FSM and 1-cycle early termination.
  - Testbench: [`tb/tb_divider.v`](tb/tb_divider.v) evaluated 4,048 corner-case and randomized vectors: **0 errors (100% PASS)**.
- **WP-05: Pipelined RV32IM Integration & Hazard Interlocks**
  - Modules: [`control_decoder.v`](rtl/core/control_decoder.v), [`alu_rv32m.v`](rtl/core/alu_rv32m.v), [`id_ex_stage.v`](rtl/core/id_ex_stage.v), [`rv32m_core.v`](rtl/core/rv32m_core.v).
  - Hazard Engine: Combinational stall assertion freezes PC and IF/ID stages while injecting NOP bubbles into Stage 3; zero-cycle forwarding verified across [`tb_rv32m_pipeline.v`](tb/tb_rv32m_pipeline.v).
- **WP-06: SoC Top-Level, Memory & Telemetry Peripherals**
  - RTL: [`ram_2p.v`](rtl/soc/ram_2p.v) (16 KB unified memory), [`cycle_counter.v`](rtl/soc/cycle_counter.v) (64-bit performance counters), [`seven_seg_driver.v`](rtl/soc/seven_seg_driver.v) (8-digit multiplexer), [`uart_tx.v`](rtl/soc/uart_tx.v) (115200-baud TX), [`rv32m_soc_top.v`](rtl/soc/rv32m_soc_top.v), and [`constr/basys3_nexys.xdc`](constr/basys3_nexys.xdc).
- **WP-07: 5 Calculation-Heavy C Benchmarks**
  - Applications: `01_matmul` (4×4 dense matrix multiplication), `02_fir_filter` (8-tap, 32-sample FIR convolution), `03_taylor_series` (Taylor series $e^2$ expansion), `04_gcd_euclidean` (Euclidean GCD batch), `05_newton_raphson` (Integer square root iteration).
- **WP-08: Comparative Profiling Suite**
  - Automated framework: [`scripts/run_benchmarks.py`](scripts/run_benchmarks.py), [`tb/tb_benchmark_runner.v`](tb/tb_benchmark_runner.v), [`docs/Benchmark_Results.md`](docs/Benchmark_Results.md).
- **WP-09: Vivado Synthesis, Place & Route on AMD Xilinx Artix-7**
  - Implementation script: [`scripts/synth_rv32m_soc.tcl`](scripts/synth_rv32m_soc.tcl) targeting `xc7a100tcsg324-1`.

---

## 4. Hardware vs. Software Comparative Profiling (WP-08)

All five benchmarks were compiled using RISC-V GCC 13.4.0 under `-O2 -nostartfiles -T sw/common/link.ld` for both `-march=rv32i` (software emulation) and `-march=rv32im` (hardware accelerated):

| Workload ID | Benchmark Application | Primary Extension | RV32I Cycles (Soft) | RV32IM Cycles (Hard) | Core Speedup | Kernel Speedup | Retired Instr Reduction | Multi-Cycle Stalls |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`01_matmul`** | Dense Matrix Multiplication (4×4) | `MUL` | 2,602 | 806 | **3.23×** | **3.66×** | **2.62×** | 0 |
| **`02_fir_filter`** | 1D Digital FIR Filter (8-tap, 32 samples) | `MUL`, `MULH` | 87,021 | 4,243 | **20.51×** | **21.45×** | **18.93×** | 0 |
| **`03_taylor_series`** | Taylor Series Exp(2) & Factorials | `MUL`, `DIV` | 4,525 | 1,750 | **2.59×** | **2.66×** | **4.69×** | 1,056 |
| **`04_gcd_euclidean`** | Euclidean GCD (8 pairs) | `REM`, `REMU` | 2,064 | 1,359 | **1.52×** | **1.55×** | **5.00×** | 1,023 |
| **`05_newton_raphson`**| Newton-Raphson Sqrt (8 values) | `DIV`, `DIVU` | 10,470 | 4,026 | **2.60×** | **2.64×** | **10.07×** | 3,234 |

- **Peak Kernel Speedup:** **21.45×** on digital signal convolution (`02_fir_filter`).
- **Mean Core Speedup:** **6.09×** across entire execution runs (**6.39×** across computational kernels).
- **Cycle-Accurate Stalls:** In `04_gcd_euclidean`, 31 division/modulo operations generated exactly $31 \times 33 = 1,023$ hardware divider stalls.

---

## 5. FPGA Synthesis & Timing Closure (WP-09)

Synthesized using AMD Vivado 2025.2 targeting the AMD Xilinx Artix-7 `xc7a100tcsg324-1`:

```
------------------------------------------------------------------------------------------------
| Design Timing Summary: rv32m_soc_top (AMD Vivado 2025.2)
------------------------------------------------------------------------------------------------
    WNS(ns)      TNS(ns)  TNS Failing Endpoints  TNS Total Endpoints      WHS(ns)      THS(ns)
    -------      -------  ---------------------  -------------------      -------      -------
     +1.497        0.000                      0                40252       +0.121        0.000

All user specified timing constraints are met. Zero failing endpoints across 40,252 timing paths.
```

- **Target Clocks:**
  - 100 MHz Master Oscillator (`sys_clk_pin`, $T = 10.000\text{ ns}$)
  - 50 MHz Core Execution Clock (`clk_50m`, $T = 20.000\text{ ns}$)
- **Timing Slack (WNS):** **+1.497 ns** setup slack margin (Zero failing endpoints across all 40,252 paths).
- **Maximum System Frequency:** $F_{\max} \approx 54.0\text{ MHz}$ on complete SoC top level ($68.3\text{ MHz}$ on core datapath).
- **Resource Utilization:**
  - **DSP48E1 Slices:** 4 (1.67%)
  - **Slice LUTs:** 7,839 (12.36%) — 3,743 Logic LUTs (5.90%) + 4,096 Distributed RAM LUTs (21.56%)
  - **Slice Registers (FFs):** 1,916 (1.51%)
  - **Bonded IOBs:** 35 (16.67%)

---

## 6. How to Run & Verify

### 6.1 Multiplier & Divider Unit Verification
```bash
# Run standalone multiplier self-checking testbench (40,027 vectors)
iverilog -g2012 -I rtl/core -o sim_mult.vvp rtl/core/multiplier_rv32m.v tb/tb_multiplier.v
vvp sim_mult.vvp

# Run standalone divider corner-case testbench (4,048 vectors)
iverilog -g2012 -I rtl/core -o sim_div.vvp rtl/core/divider_rv32m.v tb/tb_divider.v
vvp sim_div.vvp
```

### 6.2 Pipeline & Full SoC Verification
```bash
# Run pipeline integration testbench (RV32M ALU & RAW hazards)
iverilog -g2012 -I rtl/core -o sim_pipe.vvp rtl/core/multiplier_rv32m.v rtl/core/divider_rv32m.v rtl/core/alu_rv32m.v rtl/core/control_decoder.v rtl/core/hazard_unit.v rtl/core/if_stage.v rtl/core/id_ex_stage.v rtl/core/wb_stage.v rtl/core/riscv_core.v rtl/core/rv32m_core.v tb/tb_rv32m_pipeline.v
vvp sim_pipe.vvp

# Run SoC top-level simulation (BRAM, MMIO telemetry, 7-segment display, UART TX)
iverilog -g2012 -I rtl/core -I rtl/soc -o sim_soc.vvp rtl/core/multiplier_rv32m.v rtl/core/divider_rv32m.v rtl/core/alu_rv32m.v rtl/core/control_decoder.v rtl/core/hazard_unit.v rtl/core/if_stage.v rtl/core/id_ex_stage.v rtl/core/wb_stage.v rtl/core/riscv_core.v rtl/core/rv32m_core.v rtl/soc/ram_2p.v rtl/soc/cycle_counter.v rtl/soc/seven_seg_driver.v rtl/soc/uart_tx.v rtl/soc/rv32m_soc_top.v tb/tb_rv32m_soc.v
vvp sim_soc.vvp
```

### 6.3 Automated Benchmark Compilation & Comparative Profiling
```bash
python scripts/run_benchmarks.py
```

### 6.4 AMD Vivado FPGA Top-Level Synthesis
```bash
vivado -mode batch -source scripts/synth_rv32m_soc.tcl -nolog -nojournal
```

---

## 7. Author Information

- **Sole Author & Lead:** Abhishek Kumar Deepak
- **Roll Number:** 250101002
- **GitHub:** [`abhiii927`](https://github.com/abhiii927)
- **Institution:** Department of Computer Science & Engineering, Indian Institute of Technology Guwahati (IIT Guwahati)
- **Course:** Advanced Computer Architecture & FPGA System Design (Group 22)
