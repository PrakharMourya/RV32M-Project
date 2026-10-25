# RV32M-Core: Master System Architecture & LLM Context Brief
**Document Type:** Master Context Handover Document for LLM Sessions & Development Agents (Antigravity)  
**Project Title:** RV32I Processor Extension with RV32M Instruction Set Architecture  
**Group / Academic Standard:** Group 22 — IIT Guwahati Advanced Computer Architecture & FPGA System Design  
**Active Lead:** Abhishek Kumar Deepak (Roll: 250101002, GitHub: abhiii927)  
**Remote Repository:** https://github.com/abhiii927/RV32M-Project  
**Target FPGA Device:** AMD Xilinx Artix-7 (XC7A100T / XC7A35T, Digilent Nexys A7 / Basys 3)  
**Toolchain & Simulation:** AMD Vivado 2024.x/2025.x, Icarus Verilog 12+, GTKWave, RISC-V GNU Toolchain (riscv32-unknown-elf-gcc), Python 3.10+  

---

## 1. Quick-Start Instructions for LLMs & Antigravity
### How to Use This Document:
When initiating a session in Antigravity or any LLM code generation environment:
1. Supply this entire document as the system prompt or primary context brief.
2. Assign the specific Work Package (WP):
   - *"I am working on Issue #01 ([WP-01][CORE] RV32M Multiplier Unit Implementation). Refer to the interface contracts, signal widths, and sign-extension rules in the RV32M Context Brief, and generate the synthesizable Verilog for multiplier_rv32m.v and its self-checking testbench."*
3. **GitHub CLI Operations:** Use existing authenticated GitHub credentials (`gh`) to read issues, push commits, and update PRs across the repository `abhiii927/RV32M-Project` without prompting for manual access tokens.

---

## 2. Executive Project Summary
The objective of this project is to extend an existing baseline RV32I processor core with the complete, compliant hardware execution units defined in the RISC-V standard "M" Extension (RV32M).

Baseline RV32I systems emulate integer multiplication and division through software library calls (`__mulsi3`, `__divsi3`, `__modsi3`), incurring hundreds of clock cycles per operation. This design integrates hardware-accelerated integer multiplication and division coprocessors directly into the CPU execution stage, reducing multiplication latency to 1–2 cycles and division to $\le 34$ cycles, while providing corner-case compliance with the unprivileged RISC-V ISA specification.

```
+----------------------------------------------------------------------------------------------------+
|                                    RV32IM SoC Architecture Overview                                |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   |                              Pipelined RV32IM CPU Core                                     |   |
|   |                                                                                            |   |
|   |   +--------------------+     +-----------------------------------+     +---------------+   |   |
|   |   | Instruction Fetch  |     |     Instruction Decode / Execute  |     |   Writeback   |   |   |
|   |   |      (IF Stage)    |     |             (ID/EX Stage)         |     |  (WB Stage)   |   |   |
|   |   |                    |     |                                   |     |               |   |   |
|   |   |  - PC + 4 Adder    |===> |  - 32x32 General Regfile (x0-x31) |===> | - Result Mux  |   |   |
|   |   |  - Program Counter |     |  - Standard RV32I Integer ALU     |     | - Reg Write   |   |   |
|   |   |  - Fetch Arbiter   |     |  - Control & Sign Decoder         |     |   Commit      |   |   |
|   |   +--------------------+     +-----------------------------------+     +---------------+   |   |
|   |             |                                  |                              ^            |   |
|   |             |                 +----------------+----------------+             |            |   |
|   |             |                 |                                 |             |            |   |
|   |             |                 v                                 v             |            |   |
|   |             |     +-------------------------+     +-------------------------+ |            |   |
|   |             |     | Hardware Multiplier     |     | Hardware Divider        | |            |   |
|   |             |     | (Single-Cycle DSP /     |     | (Non-Restoring FSM /    | |            |   |
|   |             |     |  Pipelined Wallace)     |     |  Radix-2 Subtract)      | |            |   |
|   |             |     | MUL, MULH, MULHU, MULHSU|     | DIV, DIVU, REM, REMU    | |            |   |
|   |             |     +-------------------------+     +-------------------------+ |            |   |
|   |             |                 |                                 |             |            |   |
|   |             |                 +----------------+----------------+             |            |   |
|   |             |                                  |                              |            |   |
|   |             |                   +--------------v--------------+               |            |   |
|   |             +------------------>| Core Hazard & Stall Engine  |---------------+            |   |
|   |                                 | (Multi-cycle hold / bypass) |                            |   |
|   |                                 +-----------------------------+                            |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                  |                                                 |
|                                       32-Bit Interconnect / Memory Bus                             |
|                                                  |                                                 |
|   +----------------------------------------------+---------------------------------------------+   |
|   |                                  On-Chip Memory & Peripherals                              |   |
|   |                                                                                            |   |
|   |  - Dual-Port Instruction & Data BRAM (Dual-ported 16 KB / 32 KB unified or Harvard)        |   |
|   |  - Hardware Performance Counters (Cycle Count, Instruction Count, Stall Cycle Profiler)    |   |
|   |  - 115200-Baud Serial UART (Workload telemetry & benchmark reports to Host PC)             |   |
|   |  - FPGA Direct I/O Driver: 8-Digit 7-Segment Display & Active Status LEDs                  |   |
|   +--------------------------------------------------------------------------------------------+   |
+----------------------------------------------------------------------------------------------------+
```

### Key Target Specifications:
- **Target Frequency:** 50 MHz – 100 MHz on Xilinx Artix-7.
- **ISA Extension:** Unprivileged RV32M standard (`funct7 = 7'b0000001`, `opcode = 7'b0110011`).
- **Multiplier Throughput/Latency:** 1-cycle combinational/DSP-assisted, or 2-cycle pipelined register slice.
- **Divider Latency:** $\le 34$ cycles for 32-bit division; 1-cycle immediate exit for divide-by-zero and signed overflow corner cases.
- **Verification Target:** Zero mismatch across random self-checking vectors and direct speedup benchmarking against software emulation on 5 C workloads.

---

## 3. Work Packages & Milestone Tracking
| Issue / WP | Title | Focus Area | Deliverables |
| :--- | :--- | :--- | :--- |
| **WP-01** | [CORE] RV32M Hardware Multiplier Engine | Multiplier RTL | `multiplier_rv32m.v`: Full 64-bit internal product, sign control for MUL, MULH, MULHSU, MULHU. |
| **WP-02** | [VERIF] Multiplier Standalone Self-Checking TB | Multiplier TB | `tb_multiplier.v`: Automated testbench with edge cases (all zeroes, sign limits, random vectors). |
| **WP-03** | [CORE] Non-Restoring 32-Bit Hardware Divider FSM | Divider RTL | `divider_rv32m.v`: FSM computing DIV, DIVU, REM, REMU, early termination, stall signal. |
| **WP-04** | [VERIF] Divider Corner-Case & Exhaustive TB | Divider TB | `tb_divider.v`: Verification of divide-by-zero, negative dividend/divisor, overflow bounds. |
| **WP-05** | [CORE] Control Unit & ALU Pipeline Integration | Pipeline / Decode | `alu_rv32m.v`, `decode_unit.v`, `hazard_stall_unit.v`: Opcode integration and multi-cycle stall freeze. |
| **WP-06** | [SOC] Performance Telemetry & Hardware Display | Peripherals | `seven_seg_driver.v`, `cycle_counter.v`, `uart_tx.v`: Real-time display of cycle counts and outputs. |
| **WP-07** | [SW] 5 Calculation-Heavy C Benchmarks | Workloads | Matrix multiplication, FIR filter, Factorial/Taylor series, Integer GCD, Polynomial evaluation. |
| **WP-08** | [BENCH] Hardware vs. Software Comparative Profiling | Verification | Comparative execution trace showing hardware speedup over GCC software emulation libraries. |
| **WP-09** | [SYNTH] Vivado Synthesis, Place & Route on FPGA | Implementation | Resource utilization table (LUTs, FFs, DSPs, BRAM) and timing closure report. |

---

## 4. RV32M Microarchitecture & Hardware Interface Contracts

### 4.1 Instruction Encoding Specifications
All RV32M instructions share the standard R-type format (`opcode = 7'b0110011` / `0x33`) and are distinguished from RV32I operations by `funct7 = 7'b0000001`.

| Instruction | funct7 | rs2 | rs1 | funct3 | rd | opcode | Operation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MUL** | `7'b0000001` | src2 | src1 | `3'b000` | dest | `7'b0110011` | $R_d = (R_{s1} \times R_{s2})[31:0]$ (Signed $\times$ Signed) |
| **MULH** | `7'b0000001` | src2 | src1 | `3'b001` | dest | `7'b0110011` | $R_d = (R_{s1} \times R_{s2})[63:32]$ (Signed $\times$ Signed) |
| **MULHSU** | `7'b0000001` | src2 | src1 | `3'b010` | dest | `7'b0110011` | $R_d = (R_{s1} \times R_{s2})[63:32]$ (Signed $\times$ Unsigned) |
| **MULHU** | `7'b0000001` | src2 | src1 | `3'b011` | dest | `7'b0110011` | $R_d = (R_{s1} \times R_{s2})[63:32]$ (Unsigned $\times$ Unsigned) |
| **DIV** | `7'b0000001` | src2 | src1 | `3'b100` | dest | `7'b0110011` | $R_d = R_{s1} / R_{s2}$ (Signed Division) |
| **DIVU** | `7'b0000001` | src2 | src1 | `3'b101` | dest | `7'b0110011` | $R_d = R_{s1} / R_{s2}$ (Unsigned Division) |
| **REM** | `7'b0000001` | src2 | src1 | `3'b110` | dest | `7'b0110011` | $R_d = R_{s1} \pmod{R_{s2}}$ (Signed Remainder) |
| **REMU** | `7'b0000001` | src2 | src1 | `3'b111` | dest | `7'b0110011` | $R_d = R_{s1} \pmod{R_{s2}}$ (Unsigned Remainder) |

### 4.2 Multiplier Engine Interface (`multiplier_rv32m.v`)
The multiplier performs a 33-bit $\times$ 33-bit signed/unsigned multiplication to handle all signedness combinations uniformly:
- If operand $A$ is signed and bit 31 is 1, sign-extend to bit 32: `{op_a[31], op_a}`.
- If operand $A$ is unsigned, zero-extend: `{1'b0, op_a}`.

```verilog
module multiplier_rv32m (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,          // Trigger signal from decode stage
    input  wire [2:0]  funct3,         // 3'b000: MUL, 3'b001: MULH, 3'b010: MULHSU, 3'b011: MULHU
    input  wire [31:0] operand_a,      // rs1 data
    input  wire [31:0] operand_b,      // rs2 data
    output reg  [31:0] result,         // Selected lower or upper 32-bit slice
    output reg         ready           // High when computation is valid
);
```

### 4.3 Divider Engine Interface (`divider_rv32m.v`)
The divider implements a 32-cycle non-restoring or restoring shift-subtract algorithm. It must enforce all boundary edge cases specified in the RISC-V ISA manual:

#### Corner-Case Arithmetic Specifications:
1. **Division by Zero ($R_{s2} = 0$):**
   - $\text{DIV}(x, 0) \to -1$ (`32'hFFFF_FFFF`)
   - $\text{DIVU}(x, 0) \to 2^{32} - 1$ (`32'hFFFF_FFFF`)
   - $\text{REM}(x, 0) \to x$ (Original Dividend)
   - $\text{REMU}(x, 0) \to x$ (Original Dividend)
   - *Optimization:* Early exit asserted in cycle 1 without running the 32-step FSM.

2. **Signed Overflow ($R_{s1} = -2^{31} = \text{0x8000_0000}$ and $R_{s2} = -1$):**
   - $\text{DIV}(-2^{31}, -1) \to -2^{31}$ (`32'h8000_0000`)
   - $\text{REM}(-2^{31}, -1) \to 0$ (`32'h0000_0000`)
   - *Optimization:* Early exit asserted in cycle 1.

3. **Sign Rule for Remainder:**
   - The sign of a non-zero remainder equals the sign of the dividend ($R_{s1}$).

```verilog
module divider_rv32m (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,          // Asserted when a DIV/REM opcode is in EX stage
    input  wire [2:0]  funct3,         // 3'b100: DIV, 3'b101: DIVU, 3'b110: REM, 3'b111: REMU
    input  wire [31:0] dividend,       // rs1
    input  wire [31:0] divisor,        // rs2
    output reg  [31:0] quotient,
    output reg  [31:0] remainder,
    output reg  [31:0] result,         // Selected output routed to rd
    output reg         busy,           // High during multi-cycle operation -> stalls pipeline
    output reg         done            // 1-cycle active pulse when execution finishes
);
```

### 4.4 Hazard & Pipeline Interlock Contract
When a divide instruction enters the Execute stage:
1. `divider_rv32m` asserts `busy = 1`.
2. The core hazard unit asserts `stall_pipeline = 1`.
3. The Program Counter register and the IF/ID pipeline register are frozen (clock enable de-asserted).
4. When `done = 1`, the result is routed into the writeback register, `stall_pipeline` de-asserts, and instruction flow resumes without unintended duplicate executions.

---

## 5. Memory Map & Telemetry Control
| Address Range | Size | Access | Description |
| :--- | :--- | :--- | :--- |
| `0x0000_0000 - 0x0000_3FFF` | 16 KB | R/W | Unified Instruction/Data BRAM (Firmware code, stack, heap) |
| `0x8000_0000 - 0x8000_0007` | 8 B | R/W | Cycle Counter: 64-bit performance cycle counter (mcycle mirror) |
| `0x8000_0008 - 0x8000_000F` | 8 B | R/W | Instruction Counter: 64-bit retired instruction counter (minstret) |
| `0x8000_0010 - 0x8000_0017` | 8 B | R/W | Stall Counter: 64-bit stall cycles consumed by M-extension operations |
| `0x8000_0020 - 0x8000_0023` | 4 B | W | 7-Segment Display Register: Output computed numerical values |
| `0x8000_0024 - 0x8000_0027` | 4 B | W | LED Actuator Register: Benchmark status / Pass-Fail flags |
| `0x8000_0030 - 0x8000_0037` | 8 B | R/W | UART Transceiver: 115200-baud TX/RX data and status registers |

---

## 6. Execution Waveform Specification
```
Cycle:       C1      C2      C3      C4           C35     C36     C37
CLK:       __/---  __/---  __/---  __/---  ...  __/---  __/---  __/---
Instr:     [MUL]   [DIV]   [DIV (stalled)]      [DIV]   [ADD]   [SUB]
div_start: ______  /-----  ______  ______  ...  ______  ______  ______
div_busy:  ______  /---------------------  ...  /-----  ______  ______
stall:     ______  /---------------------  ...  /-----  ______  ______
PC:        0x04    0x08    0x08    0x08    ...  0x08    0x0C    0x10
div_done:  ______  ______  ______  ______  ...  ______  /-----  ______
rd_data:   [Prod]  ------  ------  ------  ...  ------  [Quot]  [Sum]
```

---

## 7. The 5 Evaluation C Workloads (Calculation-Heavy)
To validate the efficiency gains of the hardware M-extension over software routines, the following 5 workloads must be compiled in two modes:
- **Software Emulation Mode:** `-march=rv32i -mabi=ilp32` (uses GCC software division/multiplication runtime routines).
- **Hardware Accelerated Mode:** `-march=rv32im -mabi=ilp32` (emits hardware mul, div, rem opcodes).

| # | Benchmark Workload | Mathematical Function | Dominant Operation |
| :--- | :--- | :--- | :--- |
| 1 | Matrix Multiplication (4×4 / 8×8) | Dense dot-product: $C_{ij} = \sum A_{ik} \cdot B_{kj}$ | Heavy MUL concentration |
| 2 | 1D Digital FIR Filter | Convolution: $y[n] = \sum_{k=0}^M b_k \cdot x[n-k]$ | MUL, MAC accumulation |
| 3 | Integer Factorial & Taylor Series | $e^x \approx \sum \frac{x^n}{n!}$ or sine series | Interleaved MUL and DIV |
| 4 | Euclidean Integer GCD & Division | Repeated modulo: $\gcd(a, b) = \gcd(b, a \pmod b)$ | Heavy REM, DIV |
| 5 | Fixed-Point Polynomial Root / Newton-Raphson | $x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$ | Repeated division & scaling |

---

## 8. Repository Layout & Target Directory Tree
```
RV32M-Project/
├── constr/
│   └── basys3_nexys.xdc        # Board constraints (Clocks, 7-Segment, Switches, LEDs)
├── docs/
│   ├── Architecture_Brief.md   # This master context document
│   └── Benchmark_Results.md    # Cycle comparison: RV32I (soft) vs. RV32IM (hard)
├── rtl/
│   ├── core/
│   │   ├── alu_rv32m.v         # Combined ALU handling I-type and M-type results
│   │   ├── control_decoder.v   # Instruction decoder for funct7/funct3 M opcodes
│   │   ├── divider_rv32m.v     # Non-restoring division & modulo engine
│   │   ├── hazard_unit.v       # Pipeline freeze and multicycle stall logic
│   │   ├── multiplier_rv32m.v  # Hardware multiplier engine (DSP or array)
│   │   └── rv32m_core.v        # Top-level pipelined CPU core
│   └── soc/
│       ├── cycle_counter.v     # Performance benchmark cycle timer
│       ├── ram_2p.v            # Dual-port on-chip memory block
│       ├── rv32m_soc_top.v     # Top SoC integration wrapper
│       ├── seven_seg_driver.v  # Dynamic multiplexer for 7-segment display
│       └── uart_tx.v           # Diagnostic serial transmitter
├── sw/
│   ├── common/
│   │   ├── crt0.s              # RISC-V C runtime start-up code
│   │   └── link.ld             # Linker script matching BRAM address map
│   └── workloads/
│       ├── 01_matmul/          # Matrix multiplication workload
│       ├── 02_fir_filter/      # Finite Impulse Response filter workload
│       ├── 03_taylor_series/   # Factorial and Taylor series workload
│       ├── 04_gcd_euclidean/   # Greatest Common Divisor workload
│       └── 05_newton_raphson/  # Fixed-point division workload
├── tb/
│   ├── tb_divider.v            # Unit testbench for divider corner cases
│   ├── tb_multiplier.v         # Unit testbench for multiplier operations
│   └── tb_rv32m_soc.v          # System-level testbench executing firmware
└── scripts/
    ├── compile_benchmarks.sh   # Compiles workloads for both rv32i and rv32im
    ├── run_simulation.sh       # Runs Icarus Verilog + GTKWave batch tests
    └── run_synth.tcl           # Vivado non-project batch synthesis script
```

---

## 9. Antigravity Prompting Templates
- **For Multiplier RTL (WP-01):**
  *"Using the RV32M Master Architecture Context, implement rtl/core/multiplier_rv32m.v in synthesizable Verilog-2001. Ensure clean parameterization for handling MUL, MULH, MULHSU, and MULHU using 33-bit operand sign-extension. The output must be registered and generate a 1-cycle ready flag."*
- **For Divider RTL (WP-03):**
  *"Using the RV32M Master Architecture Context, generate rtl/core/divider_rv32m.v. Implement a non-restoring radix-2 division state machine with: (1) immediate single-cycle bypass for divide-by-zero ($R_{s2} = 0$) and overflow ($-2^{31} / -1$); (2) 32-cycle sequential shift-subtract for all valid inputs; (3) correct sign restoration for signed DIV and REM. Provide full synchronous active-low rst_n reset."*
- **For Comparative Benchmarking Scripts (WP-08):**
  *"Generate scripts/compile_benchmarks.sh and the benchmark framework for the 5 workloads listed in Section 7 of the RV32M Context Brief. Include Makefile rules to build each test with both riscv32-unknown-elf-gcc -march=rv32i and -march=rv32im, outputting disassembly files to inspect whether software library calls (__divsi3, __mulsi3) are successfully replaced by native hardware instructions."*
