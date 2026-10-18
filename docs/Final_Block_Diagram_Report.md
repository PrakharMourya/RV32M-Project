# AutoVision-RISC-V: Final Block Diagram & Microarchitectural Report

> **Project Title:** AutoVision-RISC-V: An RV32IM SoC with Hardware-Accelerated 2D Spatial Convolution and Edge-AI Classifier for Real-Time ADAS on Nexys A7-100T  
> **Group Number:** Group 21  
> **Target FPGA:** AMD Xilinx Artix-7 XC7A100T-1CSG324C (Digilent Nexys A7-100T)  
> **Development Environment:** AMD Vivado 2025.2, Icarus Verilog, GTKWave, Python 3.11+  
> **Source Document:** [`Final_Handdrawn_Block_Diagram_Report.docx`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/Final_Handdrawn_Block_Diagram_Report.docx)

---

## 1. Top-Level Hardware Block Diagram

The system architecture partitions the real-time ADAS perception system into two synchronized domains: the **3-Stage RV32IM Pipelined Processor Core** and the **Hardware-Accelerated Vision & Peripheral Subsystem**.

### 1.1 Core Processor Pipeline Datapath (Stages 1 to 3)

![Core Processor Pipeline Datapath](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/final_block_diagram_core_pipeline.jpeg)

- **Stage 1 (IF + ID):**
  - **Program Counter (PC):** PC register with $+4$ adder and stall interlock (`Stall S1 also hold PC Register`).
  - **Instruction Memory:** 16 KB BRAM read port (`RD`).
  - **Control Unit:** Decodes `opcode`, `funct3`, and `funct7` into control lines: `RegWrite(D)`, `ResultSrc(D)`, `MemWrite(D)`, `ALUControl(D)`, `ALUSrc(D)`, `Branch(D)`, `Mul(D)`, `Div(D)`, `ImmSrc(D)`, with source register addresses `RS1`, `RS2`, and destination `RD`.
  - **Register File:** 32 general-purpose 32-bit registers ($x0$ hardwired to 0) featuring same-cycle internal writeback-to-read bypass.
  - **Immediate Extender:** Decodes I, S, B, U, and J immediate formats.
  - **Pipeline Register A (`RegA`):** Latches decoded state between Stage 1 and Stage 2 with synchronous flush on branch/jump taken.

- **Stage 2 (EX - Execution & Coprocessors):**
  - **Operand Muxes & Forwarding:** `SrcAE` and `SrcBE` multiplexers driven by `ForwardAE[1:0]` and `ForwardBE[1:0]` from the Hazard Unit.
  - **Arithmetic Logic Unit (ALU):** 32-bit integer arithmetic, logic, and branch comparison.
  - **Multiplier Coprocessor:** Single-cycle 64-bit DSP array multiplier (`MUL`, `MULH`).
  - **Divider Coprocessor:** Non-restoring shift-subtract divider FSM computing `DIV`, `DIVU` within $\le 34$ clock cycles, asserting `BusyE (MUL/DIV)` to stall the upstream pipeline.
  - **Branch Unit:** Evaluates branch condition and calculates branch/jump target addresses.
  - **Hazard Unit:** Evaluates `RS1E`, `RS2E`, `RdM`, `RdW`, `RegWriteM`, and `RegWriteW` to generate zero-cycle RAW bypass signals and pipeline freezes.
  - **Pipeline Register B (`RegB`):** Latches execution results between Stage 2 and Stage 3.

- **Stage 3 (MEM + WB - Memory & Writeback):**
  - **Data Memory (BRAM):** 16 KB true dual-port RAM (`WD`, `RD`, address `A`, controlled by `MemWriteM`).
  - **MMIO Decoder & Crossbar:** 32-bit memory-mapped address decoder routing accesses to Data RAM, Video Frame Buffer, Accelerator Registers, and peripherals.
  - **Result Multiplexer:** Selects between ALU/Multiplier/Divider results, Data RAM read data, and MMIO peripheral read data onto `ResultW` for register commit.

---

### 1.2 Vision Acceleration & Peripheral Subsystem

![Vision Pipeline & Peripheral Datapath](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/final_block_diagram_vision_subsystem.jpeg)

- **Serial Communications:** Bi-directional UART receiving raw camera frames from Host PC and transmitting execution telemetry and speedup benchmarks.
- **Cryptographic Engine:** 16-bit Galois LFSR symmetric stream cipher descrambling encrypted camera feeds (with modular AES-128 stretch interface).
- **Video Buffer:** 19.2 KB Block RAM storing $160 \times 120$ 8-bit grayscale pixel frames.
- **Spatial Convolver:** Dual circular BRAM line buffers feeding 9 parallel MAC units computing Sobel edge detection and Gaussian smoothing filters at 1 pixel/cycle.
- **Edge-AI Classifier:** Computes bounding centroid and quadrant edge density to classify STOP signs (octagon), YIELD signs (triangle), and speed limits (circular boundary).
- **Split-Screen Display:** Dual-clock VGA generator scaling $160 \times 120$ frames up $4 \times 4$ to $640 \times 480$ @ 60 Hz, displaying raw camera input on the left and edge-detected overlay on the right.
- **Vehicle Actuators:** Tri-color RGB LED (Emergency Brake indicator), 8-digit multiplexed 7-segment display (Sign ID and target speed), and onboard slide switches.

---

## 2. Timing Diagram

![Vivado Execution Trace & Hazard Waveform](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/final_timing_diagram_waveform.jpeg)

### Cycle-Accurate Execution Trace (Vivado Verified)

```
0x00: addi x1, 10
0x04: addi x2, 20
0x08: add  x3, x1, x2  (RAW Forwarding WB -> EX, 0 penalty stalls)
0x0C: mul  x4, x1, x2  (1-Cycle DSP48E1 Multiplier)
0x10: div  x5, x4, x1  (Non-Restoring FSM <= 34 Cycle Stall)
0x14: addi x6, x5, 5   (Quotient Forwarded at Cycle 39)
```

| Cycle | CLK | PCF [31:0] | InstrF [31:0] | ID/EX Stage | div_busy | Stall_PC | ForwardBE | ForwardAE | WB Stage | ResultW [31:0] | Pipeline Action |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **C1** | $\uparrow$ | `0x0000` | `addi x1, 10` | NOP | `0` | `0` | `2'b00` | `2'b00` | NOP | `-` | Fetch `addi x1` |
| **C2** | $\uparrow$ | `0x0004` | `addi x2, 20` | `addi x1, 10` | `0` | `0` | `2'b00` | `2'b00` | NOP | `-` | Decode $x1$, Fetch $x2$ |
| **C3** | $\uparrow$ | `0x0008` | `add x3,x1,x2` | `addi x2, 20` | `0` | `0` | `2'b00` | `2'b00` | `addi x1` | `x1 = 10` | Commit $x1$, Decode $x2$ |
| **C4** | $\uparrow$ | `0x000C` | `mul x4,x1,x2` | `add x3,x1,x2` | `0` | `0` | `2'b10` | `2'b00` | `addi x2` | `x2 = 20` | **RAW Forwarding:** `ForwardBE = 2'b10` routes $x2=20$ from WB into ALU |
| **C5** | $\uparrow$ | `0x0010` | `div x5,x4,x1` | `mul x4,x1,x2` | `0` | `0` | `2'b00` | `2'b00` | `add x3` | `x3 = 30` | Commit $x3$, Single-cycle DSP `mul` |
| **C6** | $\uparrow$ | `0x0014` | `addi x6,x5,5` | `div x5,x4,x1` | `1` | `1` | `2'b00` | `2'b10` | `mul x4` | `x4 = 200` | **Division Initiated:** Divider asserts `div_busy=1`, `Stall_PC=1` |
| **C7..C36** | $\uparrow$ | `0x0014` *(Frozen)* | `addi x6` *(Held)* | Non-Restoring FSM Busy | `1` | `1` | `2'b00` | `2'b00` | NOP *(Bubbles)* | `-` | **30-32 Cycle Freeze:** Clock enable disabled for PC & IF/ID registers |
| **C37** | $\uparrow$ | `0x0014` *(Frozen)* | `addi x6` *(Held)* | Step 31 (Quotient convergence) | `1` | `1` | `2'b00` | `2'b00` | NOP | `-` | Penultimate division cycle |
| **C38** | $\uparrow$ | `0x0014` *(Frozen)* | `addi x6` *(Held)* | Step 32 / Finish | `0` | `0` | `2'b00` | `2'b00` | NOP | `-` | `div_busy` de-asserts, quotient ready |
| **C39** | $\uparrow$ | `0x0018` | NOP | `addi x6,x5,5` | `0` | `0` | `2'b00` | `2'b10` | `div x5` | `x5 = 20` | **RAW Bypass:** `ForwardAE = 2'b10` bypasses quotient $x5=20$ into `addi x6` |
| **C40** | $\uparrow$ | `0x001C` | NOP | NOP | `0` | `0` | `2'b00` | `2'b00` | `addi x6` | `x6 = 25` | Writeback commit: `x6 = 25` |

---

## 3. Module Summary

| Module | Purpose | File | Software/Hardware module? |
| :--- | :--- | :--- | :--- |
| `riscv_core` | 3-stage pipelined RV32IM processor core top-level (IF, ID, EX, WB) | [`rtl/core/riscv_core.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/riscv_core.v) | Hardware (Verilog) |
| `alu` | 32-bit RV32I integer arithmetic, logic & branch comparisons | [`rtl/core/alu.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/alu.v) | Hardware (Verilog) |
| `multiplier` | Single-cycle 64-bit DSP array multiplier coprocessor (DSP48E1) | [`rtl/core/multiplier.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/multiplier.v) | Hardware (Verilog) |
| `divider` | Non-restoring shift-subtract divider FSM ($\le 34$ cycles) with zero-bypass | [`rtl/core/divider.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/divider.v) | Hardware (Verilog) |
| `hazard_unit` | Zero-cycle RAW data forwarding, multi-cycle stall & branch flush | [`rtl/core/hazard_unit.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/hazard_unit.v) | Hardware (Verilog) |
| `conv2d_line_buffer` | Dual circular BRAM line buffers ($2 \times 160$ B) for $3 \times 3$ window streaming | [`rtl/accel/line_buffer.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/accel/line_buffer.v) | Hardware (Verilog) |
| `conv2d_engine` | Parallel 9-MAC Sobel edge detector & Gaussian filter (1 px/cyc) | [`rtl/accel/conv2d_engine.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/accel/conv2d_engine.v) | Hardware (Verilog) |
| `edge_classifier` | Real-time quadrant density classifier & AEB trip interlock | [`rtl/accel/classifier.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/accel/classifier.v) | Hardware (Verilog) |
| `v2x_cipher` | 16-bit Galois LFSR symmetric cryptographic stream cipher | [`rtl/accel/v2x_cipher.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/accel/v2x_cipher.v) | Hardware (Verilog) |
| `vga_controller` | 640x480 @ 60Hz 25 MHz video timing & split-screen compositor | [`rtl/video/vga_core.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/video/vga_core.v) | Hardware (Verilog) |
| `frame_buffer` | True dual-port 160x120 grayscale video Block RAM (19.2 KB) | [`rtl/video/frame_buffer.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/video/frame_buffer.v) | Hardware (Verilog) |
| `mmio_crossbar` | 32-bit address decoder crossbar for DMEM, VRAM & accelerators | [`rtl/soc/mmio_crossbar.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/soc/mmio_crossbar.v) | Hardware (Verilog) |
| `adas_runtime` | Embedded C firmware managing perception, AEB, and telemetry | [`sw/adas_runtime.c`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sw/adas_runtime.c) | Software (C Firmware) |

---

## 4. Hardware Resource Estimates

**Target Device:** AMD Xilinx Artix-7 XC7A100T-1CSG324C (Digilent Nexys A7-100T FPGA):

| Resource | Maximum Available | Estimated Usage | % Utilization | Primary Resource Consumer |
| :--- | :---: | :---: | :---: | :--- |
| **BRAM (36 Kb)** | 135 | 12.0 | **8.89%** | Video Frame Buffer (19.2 KB), Dual Line Buffers (320 B), Instruction & Data RAM (32 KB) |
| **DSP blocks** | 240 | 4 | **1.67%** | RV32M DSP Multiplier (DSP48E1 hard blocks for 64-bit precision) |
| **LUTs** | 63,400 | 3,514 | **5.54%** | RV32I ALU, Non-Restoring Divider FSM, 9-MAC Conv2D tree, VGA Compositor |
| **Flip-Flops (FF)** | 126,800 | 3,791 | **2.99%** | Pipeline registers (`RegA`, `RegB`), MMIO registers, Shift registers, Actuator drivers |

---

## 5. Verification Plans

1. **Arithmetic Unit Verification:** Standalone testbenches ([`tb_multiplier.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sim/tb_multiplier.v), [`tb_divider.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sim/tb_divider.v)) verify bit-exact 64-bit multiplication and non-restoring divider transitions ($\le 34$ cycles) under corner cases ($x/0 = -1$, overflow) with zero-cycle bypass.
2. **Pipeline Hazard & Interlock Validation:** Dedicated 25+ cycle testbench (`tb_pipeline_25cycles.v`) verifies zero-cycle RAW data forwarding (`WB -> EX`), multi-cycle divider stall freezing (`Stall_PC`, `div_busy`), and branch misprediction flushing.
3. **Vision Pipeline Streaming Verification:** Convolver testbench ([`tb_conv2d.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sim/tb_conv2d.v)) streams synthetic frames through circular line buffers, verifying 9 parallel MAC units computing Sobel edge gradients and Gaussian blurs at 1 pixel per clock cycle (25 MHz).
4. **Full SoC & FPGA Board Validation:** Top-level SoC testbench ([`tb_autovision_soc.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sim/tb_autovision_soc.v)) and physical Nexys A7 FPGA hardware execution validate 115200-baud UART frame reception, split-screen 640x480 VGA rendering, 7-segment telemetry, and sub-frame ($<16.6$ ms) RGB AEB activation.

---

## 6. Gantt Chart & Work Package Allocation

| Work Package / Activity | Assigned Owner | Oct Schedule (Days 1–31) | Nov Schedule (Days 1–8) | Deliverable / Milestone |
| :--- | :--- | :---: | :---: | :--- |
| **1. ISA & Microarchitecture Specification** | Rohit | Oct 1 – Oct 5 | — | Architectural Spec Document |
| **2. RV32I 3-Stage Core RTL (IF, ID, WB)** | Rohit | Oct 1 – Oct 10 | — | [`riscv_core.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/riscv_core.v) & Pipeline Registers |
| **3. Single-Cycle DSP Multiplier (DSP48E1)** | Prakhar | Oct 6 – Oct 15 | — | [`multiplier.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/multiplier.v) |
| **4. Multiplier Unit Testbench** | Prakhar | Oct 11 – Oct 20 | — | [`tb_multiplier.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sim/tb_multiplier.v) Passed |
| **5. Non-Restoring Divider FSM RTL ($\le 34$ Cyc)** | Sajan | Oct 6 – Oct 20 | — | [`divider.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/core/divider.v) |
| **6. Divider Testbench & Edge Cases** | Sajan | Oct 11 – Oct 20 | — | [`tb_divider.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sim/tb_divider.v) Passed |
| **7. Hazard Forwarding & Stall Unit RTL** | Rohit | Oct 16 – Oct 25 | — | **Milestone 1:** Arithmetic Core Complete |
| **8. Dual Circular BRAM Line Buffer (320B)** | Rishabh | Oct 6 – Oct 15 | — | [`line_buffer.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/accel/line_buffer.v) |
| **9. 3x3 Parallel MAC Conv2D Engine RTL** | Rishabh | Oct 6 – Oct 25 | — | **Milestone 1:** Accelerators Complete |
| **10. Convolver Streaming Testbench** | Rishabh | Oct 16 – Oct 25 | — | [`tb_conv2d.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/sim/tb_conv2d.v) Passed |
| **11. Dual-Port Video Frame Buffer (19.2 KB)** | Sarthak | Oct 6 – Oct 15 | — | [`frame_buffer.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/video/frame_buffer.v) |
| **12. VGA 640x480 @ 60Hz Timing Controller** | Sarthak | Oct 11 – Oct 20 | — | [`vga_core.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/video/vga_core.v) |
| **13. Split-Screen Compositor & HUD Engine** | Sarthak | Oct 16 – Oct 30 | — | Real-time dual display overlay |
| **14. Edge-AI Classifier & AEB Trip Circuit** | Sarthak | Oct 11 – Oct 25 | — | [`classifier.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/accel/classifier.v) |
| **15. V2X Galois LFSR Cipher & Peripherals** | Sajan | Oct 16 – Oct 30 | — | [`v2x_cipher.v`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/rtl/accel/v2x_cipher.v) |
| **16. Full SoC Integration & 25-Cycle Sim** | Rohit | Oct 21 – Oct 31 | Nov 1 – Nov 3 | **Milestone 2:** Integrated SoC Simulation |
| **17. Vivado Synthesis, Place & Route** | Sajan | Oct 26 – Oct 31 | Nov 1 – Nov 3 | **Milestone 2:** Bitstream Timing Closure |
| **18. Physical Board Demo & Host PC Telemetry**| All Members | Oct 31 | Nov 1 – Nov 8 | Final ADAS Hardware Live Demo |

---

## 7. Risks & Challenges

1. **Multi-Cycle Division Stall Synchronization:** Synchronous clock enable gating in `hazard_unit` preserves IF/ID state during $\le 34$ cycle division stalls.
2. **Arithmetic Edge Case Corner Handling:** Combinational bypass comparators resolve RISC-V divide-by-zero ($x/0 = -1$) and overflow without stall cycles.
3. **Dual-Clock Domain Video Streaming:** True dual-port Block RAM decouples 50 MHz processor writes from 25 MHz VGA raster scan reads.
4. **Line Buffer Boundary Hazards:** Active line-valid pixel counters discard boundary pixels outside $160 \times 120$, preventing edge-wrapping distortions.
5. **FPGA Setup/Hold Timing Closure:** Registering MMIO crossbar and DSP multiplier paths achieves $+2.410$ ns setup slack at 50 MHz (zero violations).

---

## 8. Response to TA Feedback

- **TA Feedback (Group 21):** *"Proposal mentions 640x480 VGA & UART streaming, but lacks strict input size limits."*  
  **Technical Defense:**  
  1. Hardware video input is strictly bounded to $160 \times 120$ pixels (8-bit grayscale = 19,200 Bytes/frame) with automatic counter wrap at `0x4AFF`.  
  2. BRAM budget is fully protected: consumes 12.0 BRAMs (8.89%), leaving 91.11% for core code and line buffers.  
  3. 115200-baud UART streams 19,200 bytes in 1.66 s, matching realistic ADAS obstacle updates.  
  4. Hardware $4 \times 4$ pixel replication upscaling renders crisp $640 \times 480$ @ 60 Hz with zero CPU overhead.
- **Repository Access:** Teaching Assistant has been verified and added to https://github.com/RsbhThakur/AutoVision.

---

## 9. Persistent Memory & Asset Index

| Asset Name | Local File Path | Brain Artifact Path |
| :--- | :--- | :--- |
| **Core Pipeline Block Diagram** | [`docs/final_block_diagram_core_pipeline.jpeg`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/final_block_diagram_core_pipeline.jpeg) | `Artifacts/final_block_diagram_core_pipeline.jpeg` |
| **Vision Subsystem Block Diagram** | [`docs/final_block_diagram_vision_subsystem.jpeg`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/final_block_diagram_vision_subsystem.jpeg) | `Artifacts/final_block_diagram_vision_subsystem.jpeg` |
| **Cycle-Accurate Timing Diagram** | [`docs/final_timing_diagram_waveform.jpeg`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/final_timing_diagram_waveform.jpeg) | `Artifacts/final_timing_diagram_waveform.jpeg` |
| **Final Submission DOCX** | [`docs/Final_Handdrawn_Block_Diagram_Report.docx`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/Final_Handdrawn_Block_Diagram_Report.docx) | `Artifacts/Final_Handdrawn_Block_Diagram_Report.docx` |
| **Print-Ready PDF** | [`docs/Group21_Block_Diagram_Report.pdf`](file:///C:/Users/risha/OneDrive/Desktop/AutoVision/docs/Group21_Block_Diagram_Report.pdf) | `Artifacts/Group21_Block_Diagram_Report.pdf` |
