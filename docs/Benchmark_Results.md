# RV32M-Core: Hardware vs. Software Comparative Profiling Report

**Work Package:** [WP-08][BENCH] Comparative Profiling Engine  
**Academic Standard:** Group 22 — IIT Guwahati Advanced Computer Architecture & FPGA System Design  
**Target FPGA:** AMD Xilinx Artix-7 (XC7A100T-1CSG324C / Basys 3 & Nexys A7)  
**Toolchain:** GCC 13.4.0 (riscv64-unknown-elf-gcc), Icarus Verilog 12+, AMD Vivado 2025.2  

---

## 1. Executive Summary & Hardware Acceleration Highlights

The RV32M hardware execution unit extends the baseline RV32I pipeline with single-cycle DSP-assisted multiplication and a 32-step non-restoring divider FSM. In standard RV32I architectures, integer multiplication and division rely entirely on GCC software emulation subroutines (`__mulsi3`, `__divsi3`, `__udivsi3`, `__modsi3`, `__umodsi3`), which incur severe branch overheads, loop counters, and hundreds of execution cycles.

Across five industry-standard computational workloads, the integrated RV32M hardware execution coprocessor achieves dramatic throughput improvements:

| Workload ID | Benchmark Application | Target Operations | RV32I Cycles (Soft) | RV32IM Cycles (Hard) | Core Speedup | Kernel Speedup | Instr Reduction |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **01_matmul** | Dense Matrix Multiplication (4x4) | `MUL` | 2,602 | 806 | **3.23×** | **3.66×** | **2.62×** |
| **02_fir_filter** | 1D Digital FIR Filter (8-tap, 32 samples) | `MUL, MULH` | 87,021 | 4,243 | **20.51×** | **21.45×** | **18.93×** |
| **03_taylor_series** | Taylor Series Exp(2) & Factorials | `MUL, DIV` | 4,525 | 1,750 | **2.59×** | **2.66×** | **4.69×** |
| **04_gcd_euclidean** | Euclidean Greatest Common Divisor (8 pairs) | `REM / REMU` | 2,064 | 1,359 | **1.52×** | **1.55×** | **5.00×** |
| **05_newton_raphson** | Newton-Raphson Integer Square Root (8 values) | `DIV / DIVU` | 10,470 | 4,026 | **2.60×** | **2.64×** | **10.07×** |

> [!NOTE]
> **Mean Core Speedup:** 6.09× across entire execution runs; **Mean Kernel Speedup:** 6.39× for computation loops.

---

## 2. Granular Microarchitectural Profiling Breakdown

### 2.1 Dense Matrix Multiplication (4x4) (`01_matmul`)

- **Description:** Heavy integer multiplication and accumulation
- **Primary ISA Extension:** `MUL`

| Microarchitectural Metric | Baseline RV32I (Soft Emulation) | RV32IM (Hardware Accelerated) | Improvement Factor |
|:---|:---:|:---:|:---:|
| Total Program Cycles | 2,602 | 806 | **3.23× faster** |
| Retired Instructions | 1,494 | 571 | **2.62× fewer instructions** |
| Divider Pipeline Stalls | 0 | 0 | 0 stall cycles |
| Average CPI (Cycles / Instr) | 1.74 | 1.41 | — |
| Kernel Execution Cycles | 2,448 | 668 | **3.66× kernel speedup** |

### 2.2 1D Digital FIR Filter (8-tap, 32 samples) (`02_fir_filter`)

- **Description:** Q15 fixed-point convolution and 64-bit accumulation
- **Primary ISA Extension:** `MUL, MULH`

| Microarchitectural Metric | Baseline RV32I (Soft Emulation) | RV32IM (Hardware Accelerated) | Improvement Factor |
|:---|:---:|:---:|:---:|
| Total Program Cycles | 87,021 | 4,243 | **20.51× faster** |
| Retired Instructions | 61,860 | 3,267 | **18.93× fewer instructions** |
| Divider Pipeline Stalls | 0 | 0 | 0 stall cycles |
| Average CPI (Cycles / Instr) | 1.41 | 1.30 | — |
| Kernel Execution Cycles | 86,812 | 4,047 | **21.45× kernel speedup** |

### 2.3 Taylor Series Exp(2) & Factorials (`03_taylor_series`)

- **Description:** Alternating multiplication and division progression
- **Primary ISA Extension:** `MUL, DIV`

| Microarchitectural Metric | Baseline RV32I (Soft Emulation) | RV32IM (Hardware Accelerated) | Improvement Factor |
|:---|:---:|:---:|:---:|
| Total Program Cycles | 4,525 | 1,750 | **2.59× faster** |
| Retired Instructions | 2,337 | 498 | **4.69× fewer instructions** |
| Divider Pipeline Stalls | 0 | 1056 | 1056 stall cycles |
| Average CPI (Cycles / Instr) | 1.94 | 3.51 | — |
| Kernel Execution Cycles | 4,448 | 1,675 | **2.66× kernel speedup** |

### 2.4 Euclidean Greatest Common Divisor (8 pairs) (`04_gcd_euclidean`)

- **Description:** Iterative modulo remainder calculation
- **Primary ISA Extension:** `REM / REMU`

| Microarchitectural Metric | Baseline RV32I (Soft Emulation) | RV32IM (Hardware Accelerated) | Improvement Factor |
|:---|:---:|:---:|:---:|
| Total Program Cycles | 2,064 | 1,359 | **1.52× faster** |
| Retired Instructions | 1,035 | 207 | **5.00× fewer instructions** |
| Divider Pipeline Stalls | 0 | 1023 | 1023 stall cycles |
| Average CPI (Cycles / Instr) | 1.99 | 6.57 | — |
| Kernel Execution Cycles | 1,955 | 1,262 | **1.55× kernel speedup** |

### 2.5 Newton-Raphson Integer Square Root (8 values) (`05_newton_raphson`)

- **Description:** Iterative quotient approximation and division
- **Primary ISA Extension:** `DIV / DIVU`

| Microarchitectural Metric | Baseline RV32I (Soft Emulation) | RV32IM (Hardware Accelerated) | Improvement Factor |
|:---|:---:|:---:|:---:|
| Total Program Cycles | 10,470 | 4,026 | **2.60× faster** |
| Retired Instructions | 5,166 | 513 | **10.07× fewer instructions** |
| Divider Pipeline Stalls | 0 | 3234 | 3234 stall cycles |
| Average CPI (Cycles / Instr) | 2.03 | 7.85 | — |
| Kernel Execution Cycles | 10,361 | 3,929 | **2.64× kernel speedup** |

