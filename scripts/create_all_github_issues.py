#!/usr/bin/env python3
"""
AutoVision-RISC-V: Production-Grade GitHub Issue Creation Script
Repository: RsbhThakur/AutoVision
Architectural Standards: IIT Guwahati CS/EE Advanced Computer Architecture & FPGA Design
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.error
import urllib.parse

# STRICT SAFETY CHECK: Ensure forbidden names never occur anywhere
FORBIDDEN_WORDS = ["rupavath", "rajesh"]

def get_github_token():
    try:
        res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        print(f"Error obtaining token via gh CLI: {e}")
        sys.exit(1)

def github_api_request(method, endpoint, token, data=None):
    url = f"https://api.github.com/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AutoVision-Issue-Architect"
    }
    
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return {}
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"HTTP Error {e.code} for {url}: {err_msg}")
        raise e

def create_or_update_label(token, name, color, description):
    endpoint = "repos/RsbhThakur/AutoVision/labels"
    data = {
        "name": name,
        "color": color,
        "description": description
    }
    try:
        github_api_request("POST", endpoint, token, data)
        print(f"[LABEL] Created: {name}")
    except urllib.error.HTTPError as e:
        if e.code == 422: # Already exists, update it
            update_endpoint = f"repos/RsbhThakur/AutoVision/labels/{urllib.parse.quote(name)}"
            github_api_request("PATCH", update_endpoint, token, {"color": color, "description": description})
            print(f"[LABEL] Updated: {name}")
        else:
            raise e

def create_issue(token, title, body, assignees, labels):
    # Strict validation against forbidden words
    full_text = f"{title}\n{body}\n{' '.join(assignees)}\n{' '.join(labels)}".lower()
    for word in FORBIDDEN_WORDS:
        if word in full_text:
            raise ValueError(f"CRITICAL VIOLATION: Forbidden word '{word}' found in issue!")

    endpoint = "repos/RsbhThakur/AutoVision/issues"
    data = {
        "title": title,
        "body": body,
        "assignees": assignees,
        "labels": labels
    }
    resp = github_api_request("POST", endpoint, token, data)
    num = resp.get("number")
    html_url = resp.get("html_url")
    print(f"[SUCCESS] Created Issue #{num}: {title} -> {html_url}")
    return resp

# ==============================================================================
# LABELS DEFINITION
# ==============================================================================
LABELS = [
    {"name": "core", "color": "0E8A16", "description": "RV32I Core & Pipeline Datapath"},
    {"name": "accelerator", "color": "B60205", "description": "Hardware Vision & Crypto Accelerators"},
    {"name": "video-subsystem", "color": "1D76DB", "description": "VGA Controller & Frame Buffer"},
    {"name": "soc-integration", "color": "5319E7", "description": "Interconnect, Top-Level & Peripherals"},
    {"name": "verification", "color": "FBCA04", "description": "Testbenches, Waveforms & Assertions"},
    {"name": "firmware", "color": "006B75", "description": "Embedded C & Assembly Software"},
    {"name": "synthesis", "color": "D93F0B", "description": "Vivado Timing Closure, P&R & Bitstream"},
    {"name": "stretch-goal", "color": "E99695", "description": "Advanced Research & Stretch Objectives"},
    {"name": "milestone-1", "color": "C5DEF5", "description": "Milestone 1: Core & Vision Accelerators"},
    {"name": "milestone-2", "color": "BFD4F2", "description": "Milestone 2: SoC Integration & Waveforms"},
    {"name": "milestone-3", "color": "D4C5F9", "description": "Milestone 3: Physical Board Demo & Timing Closure"}
]

# ==============================================================================
# 18 DETAILED WORK PACKAGES / GITHUB ISSUES
# ==============================================================================
ISSUES_DATA = [
    # --------------------------------------------------------------------------
    # ISSUE 1: Rohit-Yadav19
    # --------------------------------------------------------------------------
    {
        "title": "[WP-01][CORE] ISA & 3-Stage RV32I Processor Core RTL Implementation",
        "assignees": ["Rohit-Yadav19"],
        "labels": ["core", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Implement the baseline 3-stage pipelined RV32I processor core datapath for the Nexys A7-100T FPGA (Artix-7 XC7A100T). The core partitions execution into:
- **Stage 1 (IF):** Instruction Fetch with PC incrementer and branch redirect multiplexer.
- **Stage 2 (ID/EX):** Instruction Decode, operand fetch, immediate extension, and ALU execution.
- **Stage 3 (WB):** Memory access routing and Register File writeback commit.

This module forms the computational backbone of the AutoVision ADAS platform.

---

## 2. Microarchitecture & Module Breakdown
- **Source Files:**
  - `rtl/core/riscv_core.v` (Top-level core container)
  - `rtl/core/if_stage.v` (Program counter, +4 adder, fetch registers)
  - `rtl/core/id_ex_stage.v` (Decoder, regfile, imm-gen, operand muxes, ALU)
  - `rtl/core/wb_stage.v` (Result selector, memory read alignment, commit logic)
  - `rtl/core/alu.v` (32-bit arithmetic, logic, and branch comparator)
  - `rtl/core/opcodes.vh` (Standard RV32I opcodes, funct3, and funct7 constants)
- **Supported Instructions (37 Base Instructions):**
  - ALU Reg-Reg: `ADD`, `SUB`, `SLL`, `SLT`, `SLTU`, `XOR`, `SRL`, `SRA`, `OR`, `AND`
  - ALU Imm: `ADDI`, `SLTI`, `SLTIU`, `XORI`, `ORI`, `ANDI`, `SLLI`, `SRLI`, `SRAI`
  - Loads/Stores: `LW`, `LH`, `LHU`, `LB`, `LBU`, `SW`, `SH`, `SB`
  - Branches: `BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`
  - Jumps & Upper Imm: `JAL`, `JALR`, `LUI`, `AUIPC`

---

## 3. Hardware Interface Contracts (`riscv_core.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 50 MHz | Master system clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low system reset |
| `imem_addr` | Output | 32 | 50 MHz | Instruction byte address sent to Instruction BRAM |
| `imem_data` | Input | 32 | 50 MHz | 32-bit fetched instruction word |
| `dmem_read_req` | Output | 1 | 50 MHz | Data memory read strobe |
| `dmem_write_req`| Output | 1 | 50 MHz | Data memory write strobe |
| `dmem_byte_enable` | Output | 4 | 50 MHz | Byte write enables (`4'b0001` byte, `4'b0011` half, `4'b1111` word) |
| `dmem_addr` | Output | 32 | 50 MHz | Data memory / MMIO target byte address |
| `dmem_wdata` | Output | 32 | 50 MHz | Data to write into Data RAM / MMIO registers |
| `dmem_rdata` | Input | 32 | 50 MHz | Data read response from Data RAM / MMIO |
| `coproc_busy` | Input | 1 | 50 MHz | External coprocessor stall freeze input |
| `debug_pc` | Output | 32 | 50 MHz | Architectural retire PC for telemetry and verification |
| `debug_instruction` | Output | 32 | 50 MHz | Architectural retire instruction word |
| `debug_reg_write` | Output | 1 | 50 MHz | High when destination register is written |
| `debug_rd` | Output | 5 | 50 MHz | Destination register index ($x0..x31$) |
| `debug_wdata` | Output | 32 | 50 MHz | 32-bit value committed into register file |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** None (Foundational Work Package).
- **Parallel Work Packages:** WP-03 (DSP Multiplier), WP-05 (Divider FSM), WP-07 (Line Buffer), WP-10 (Frame Buffer).
- **Schedule Alignment:** Gantt Chart Oct 1 – Oct 10 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** 50 MHz clean clock and asynchronous active-low reset from top-level Nexys wrapper.
- **Downstream Handoffs:**
  - Delivers decoded instruction fields (`rs1`, `rs2`, `rd`, `opcode`) to Hazard Unit (WP-02).
  - Delivers execution operand buses to DSP Multiplier (WP-03) and Divider (WP-05).
  - Delivers memory transaction requests to MMIO Crossbar (WP-15).

---

## 6. Manual Verification Procedure
```bash
# 1. Compile core datapath with Icarus Verilog
iverilog -g2012 -o sim_core.vvp rtl/core/*.v tb/tb_pipeline_25cycles.v

# 2. Run execution trace simulation
vvp sim_core.vvp

# 3. Inspect pipeline waveforms in GTKWave
gtkwave waveform.vcd
# Verify that debug_pc increments sequentially by 4 and registers commit correctly
```

---

## 7. Automated Verification Suite
- Assemble baseline diagnostic workloads:
  `python sw/tools/riscv_assembler.py sw/workloads/test_boot.s -o sim_build/imem.hex`
- Run simulation and verify return code register $x3 = 32'h00000001$ (Pass) with 0 error codes.

---

## 8. Acceptance Criteria
- [ ] Synthesizes cleanly with zero multi-source driver warnings in Vivado 2025.2.
- [ ] Register file contains 32 general-purpose 32-bit registers with $x0$ hardwired to 0.
- [ ] Immediate generator properly sign-extends I, S, B, U, and J types according to RISC-V specification.
- [ ] All 37 base RV32I instructions pass functional verification without illegal opcode traps.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 2: Rohit-Yadav19
    # --------------------------------------------------------------------------
    {
        "title": "[WP-02][CORE] Hazard Forwarding, Stall Interlock & Flush Control Unit",
        "assignees": ["Rohit-Yadav19"],
        "labels": ["core", "verification", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Design and verify the centralized hazard detection and data forwarding unit (`hazard_unit.v`). The unit resolves data (RAW) and control hazards across the 3-stage pipeline without sacrificing performance, achieving zero penalty stalls for computational dependencies.

---

## 2. Microarchitecture & Theory of Operation
- **Zero-Cycle RAW Data Forwarding:**
  - Evaluates writeback stage commit state (`wb_reg_write`, `wb_rd`).
  - When `wb_rd != 5'd0` and `wb_rd == id_rs1`, asserts `forward_a = 2'b10` to route `wb_forward_data` directly into ALU operand input A.
  - When `wb_rd != 5'd0` and `wb_rd == id_rs2`, asserts `forward_b = 2'b10` to route `wb_forward_data` directly into ALU operand input B.
- **Multi-Cycle Stall Handling:**
  - If Divider coprocessor asserts `div_busy` or external vision coprocessor asserts `coproc_busy`:
    - Asserts `stall_pipeline = 1`.
    - Freezes the Program Counter (`imem_addr`) and Stage 1 pipeline registers (`if_stage`), preserving instruction state.
- **Control Hazard Flushing:**
  - When branch condition evaluates true (`branch_taken = 1`) or jump executed (`is_jal || is_jalr`):
    - Asserts `flush_if = 1` for 1 clock cycle.
    - Synchronously flushes fetched instruction in Stage 1 register into a bubble (`NOP` = `32'h00000013`).

---

## 3. Hardware Interface Contracts (`hazard_unit.v`)

| Port Name | Direction | Width | Description |
| :--- | :---: | :---: | :--- |
| `id_rs1` | Input | 5 | Source register 1 address from decode stage |
| `id_rs2` | Input | 5 | Source register 2 address from decode stage |
| `wb_reg_write` | Input | 1 | Register write enable signal from writeback stage |
| `wb_rd` | Input | 5 | Destination register address from writeback stage |
| `div_busy` | Input | 1 | Stall signal from non-restoring divider FSM |
| `coproc_busy` | Input | 1 | Stall signal from 2D convolution accelerator |
| `branch_taken` | Input | 1 | Asserted when branch condition is satisfied |
| `is_jal` | Input | 1 | Asserted when JAL instruction is decoded |
| `is_jalr` | Input | 1 | Asserted when JALR instruction is decoded |
| `forward_a` | Output | 2 | Forwarding mux select for operand A (`2'b00`: RegFile, `2'b10`: Forwarded WB) |
| `forward_b` | Output | 2 | Forwarding mux select for operand B (`2'b00`: RegFile, `2'b10`: Forwarded WB) |
| `stall_pipeline`| Output | 1 | Synchronous freeze enable for PC and Stage 1 registers |
| `flush_if` | Output | 1 | Synchronous clear for Stage 1 instruction register |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-01 (RV32I Core RTL).
- **Parallel Work Packages:** WP-03 (DSP Multiplier), WP-04 (Multiplier Testbench), WP-05 (Divider FSM), WP-06 (Divider Testbench).
- **Schedule Alignment:** Gantt Chart Oct 16 – Oct 25 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Register addresses and control strobes from `if_stage.v`, `id_ex_stage.v`, `wb_stage.v`, and coprocessors.
- **Downstream Handoffs:** Delivers forwarding controls and clock enable masks to pipeline registers in `riscv_core.v`.

---

## 6. Manual Verification Procedure
```bash
# Compile and run 25-cycle pipeline hazard simulation
iverilog -g2012 -o sim_hazard.vvp rtl/core/*.v tb/tb_pipeline_25cycles.v
vvp sim_hazard.vvp

# Open GTKWave and inspect signals:
# Cycle 4: Check ForwardBE == 2'b10 (bypassing x2=20 from WB stage into ALU)
# Cycle 6: Check stall_pipeline == 1 when div_busy == 1
# Cycle 39: Check ForwardAE == 2'b10 (bypassing divider quotient x5=20 into addi x6)
```

---

## 7. Automated Verification Suite
- Run automated simulation: `tb_pipeline_25cycles.v` verifies exact cycle counts, forwarding activation, and stall duration matching Table 2 of Section 2 in the design report.

---

## 8. Acceptance Criteria
- [ ] 0 penalty cycles for back-to-back RAW data dependencies (`WB -> EX` forwarding).
- [ ] PC and Stage 1 registers remain completely frozen without state loss during `div_busy` stalls.
- [ ] Exactly 1 cycle bubble (`NOP`) inserted upon branch misprediction/taken.
- [ ] Combinational forwarding paths achieve timing closure at 50 MHz.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 3: PrakharMourya
    # --------------------------------------------------------------------------
    {
        "title": "[WP-03][CORE] Single-Cycle 64-Bit DSP Array Multiplier Coprocessor (RV32M)",
        "assignees": ["PrakharMourya"],
        "labels": ["core", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Implement the high-throughput, single-cycle integer multiplier coprocessor (`multiplier.v`) compliant with the RISC-V M-Extension specification. The multiplier infers dedicated AMD Xilinx Artix-7 `DSP48E1` hard slices to compute 64-bit products in a single clock cycle at 50 MHz.

---

## 2. Supported Instructions & Arithmetic Semantics
- `MUL` (`funct3 = 3'b000`): Lower 32 bits of signed $\\times$ signed: `result = (signed(A) * signed(B))[31:0]`.
- `MULH` (`funct3 = 3'b001`): Upper 32 bits of signed $\\times$ signed: `result = (signed(A) * signed(B))[63:32]`.
- `MULHSU` (`funct3 = 3'b010`): Upper 32 bits of signed $\\times$ unsigned: `result = (signed(A) * unsigned(B))[63:32]`.
- `MULHU` (`funct3 = 3'b011`): Upper 32 bits of unsigned $\\times$ unsigned: `result = (unsigned(A) * unsigned(B))[63:32]`.

---

## 3. Hardware Interface Contracts (`multiplier.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 50 MHz | System clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `enable` | Input | 1 | 50 MHz | Active-high multiplier unit enable strobe |
| `funct3` | Input | 3 | 50 MHz | Instruction funct3 field defining signed/unsigned mode |
| `operand_a` | Input | 32 | 50 MHz | 32-bit multiplicand operand |
| `operand_b` | Input | 32 | 50 MHz | 32-bit multiplier operand |
| `result` | Output | 32 | 50 MHz | Selected 32-bit slice of the 64-bit product |
| `ready` | Output | 1 | 50 MHz | Combinational ready indicator (always 1'b1) |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** WP-01 (Architecture interface definition).
- **Parallel Work Packages:** WP-01 (RV32I Core), WP-05 (Divider FSM), WP-07 (Line Buffer), WP-10 (Frame Buffer).
- **Schedule Alignment:** Gantt Chart Oct 6 – Oct 15 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Consumes `funct3`, `operand_a`, and `operand_b` from `id_ex_stage.v`.
- **Downstream Handoffs:** Feeds 32-bit result into `id_ex_stage` result multiplexer for writeback commit; passes unit validation to WP-04.

---

## 6. Manual Verification Procedure
```bash
# Compile and run standalone multiplier unit testbench
iverilog -g2012 -o sim_multiplier.vvp rtl/core/multiplier.v tb/tb_multiplier.v
vvp sim_multiplier.vvp
```

---

## 7. Automated Verification Suite
- Test suite executes `tb_multiplier.v`, testing boundary values ($0, 1, -1, 2^{31}-1, -2^{31}$) and 10,000 randomized 32-bit operand pairs against 64-bit reference models.
- Verification command must terminate with: `[MULTIPLIER TEST] ALL TESTS PASSED (0 ERRORS)`.

---

## 8. Acceptance Criteria
- [ ] Fully supports `MUL`, `MULH`, `MULHSU`, and `MULHU` with bit-exact compliance.
- [ ] Single-cycle throughput (1 multiplication per clock cycle).
- [ ] Vivado implementation synthesizes exactly 4 `DSP48E1` slices on Artix-7 (1.67% DSP utilization budget).
- [ ] Setup timing slack positive ($> +2.0$ ns) at 50 MHz.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 4: PrakharMourya
    # --------------------------------------------------------------------------
    {
        "title": "[WP-04][VERIF] Multiplier Unit Testbench & 10,000 Randomized Test Vectors",
        "assignees": ["PrakharMourya"],
        "labels": ["verification", "core", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Construct an automated, self-checking testbench (`tb_multiplier.v`) providing 100% functional and branch coverage of the `multiplier.v` coprocessor across all 4 RV32M multiplication instructions.

---

## 2. Test Plan & Vector Specifications
1. **Deterministic Corner Cases:**
   - Multiplication by zero: $0 \\times X = 0$ for all sign modes.
   - Identity: $1 \\times X = X$.
   - Negative identity: $-1 \\times X = -X$.
   - Max Positive Signed: `32'h7FFF_FFFF` ($2^{31}-1$).
   - Min Negative Signed: `32'h8000_0000` ($-2^{31}$).
   - Max Unsigned: `32'hFFFF_FFFF` ($2^{32}-1$).
   - Asymmetric Signs (`MULHSU`): Test negative multiplicand with large unsigned multiplier ($(-10) \\times 2^{31}$).
2. **Exhaustive Pseudo-Random Stress Suite:**
   - 10,000 pseudo-random 32-bit operand pairs generated using uniform PRNG.
   - For every vector, evaluate `MUL`, `MULH`, `MULHSU`, and `MULHU` in parallel against a 64-bit software golden model.

---

## 3. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-03 (DSP Multiplier).
- **Parallel Work Packages:** WP-02 (Hazard Unit), WP-05 (Divider FSM), WP-06 (Divider Testbench).
- **Schedule Alignment:** Gantt Chart Oct 11 – Oct 20 (Milestone 1).

---

## 4. Handoff Contracts
- **Upstream Requirements:** `rtl/core/multiplier.v` implementation.
- **Downstream Handoffs:** Delivers signed-off multiplier verification logs enabling safe core integration in `riscv_core.v`.

---

## 5. Manual Verification Procedure
```bash
# Run self-checking testbench
iverilog -g2012 -o sim_mult.vvp rtl/core/multiplier.v tb/tb_multiplier.v
vvp sim_mult.vvp

# Check stdout:
# Multiplier Self-Checking Testbench
# Running 10,000 random vectors...
# Errors: 0
```

---

## 6. Automated Verification Suite
- Scripted execution:
  `python -c "import subprocess; res = subprocess.run(['vvp', 'sim_mult.vvp'], capture_output=True, text=True); assert 'Errors: 0' in res.stdout and res.returncode == 0, 'Multiplier verification failed'"`

---

## 7. Acceptance Criteria
- [ ] 10,000 randomized vectors simulated with zero error reports.
- [ ] Zero false-positives or sign-extension mismatches across `MULHSU` and `MULH`.
- [ ] Self-terminating with `$finish` and non-zero exit code on failure.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 5: Sajan-kumar1133
    # --------------------------------------------------------------------------
    {
        "title": "[WP-05][CORE] Non-Restoring Shift-Subtract Divider FSM Coprocessor (RV32M)",
        "assignees": ["Sajan-kumar1133"],
        "labels": ["core", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Design and implement the multi-cycle non-restoring shift-subtract integer divider and modulo remainder unit (`divider.v`). The module provides full hardware compliance with the RISC-V M-Extension specification while bounding latency to $\\le 34$ clock cycles and featuring instant 1-cycle bypass for arithmetic corner cases.

---

## 2. Microarchitecture & State Machine
- **Supported Instructions:**
  - `DIV` (`funct3 = 3'b100`): Signed quotient.
  - `DIVU` (`funct3 = 3'b101`): Unsigned quotient.
  - `REM` (`funct3 = 3'b110`): Signed remainder (sign matching dividend).
  - `REMU` (`funct3 = 3'b111`): Unsigned remainder.
- **Finite State Machine (FSM):**
  - `IDLE`: Waits for `start = 1`. Evaluates corner cases combinationally.
  - `INIT_DIV`: Samples absolute values and sign flags; initializes 64-bit shift register.
  - `DIV_STEP`: Iterates 32 clock cycles of non-restoring add/subtract shifts.
  - `COMPUTE_SIGN`: Adjusts two's complement sign of quotient and remainder.
  - `DONE`: Asserts `done = 1`, presents `result[31:0]`, and de-asserts `busy = 0`.
- **Zero-Cycle Corner-Case Bypass:**
  - **Divide-by-zero ($B = 0$):** `DIV`/`DIVU` returns `32'hFFFF_FFFF` ($-1$); `REM`/`REMU` returns dividend $A$. De-asserts `busy` in 1 cycle!
  - **Signed Overflow ($A = -2^{31}, B = -1$):** `DIV` returns $-2^{31}$ (`32'h8000_0000`); `REM` returns 0. De-asserts `busy` in 1 cycle!

---

## 3. Hardware Interface Contracts (`divider.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 50 MHz | Master clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `start` | Input | 1 | 50 MHz | 1-cycle pulse initiating division operation |
| `funct3` | Input | 3 | 50 MHz | Selects `DIV`, `DIVU`, `REM`, or `REMU` |
| `dividend_in` | Input | 32 | 50 MHz | Numerator operand ($A$) |
| `divisor_in` | Input | 32 | 50 MHz | Denominator operand ($B$) |
| `result` | Output | 32 | 50 MHz | 32-bit quotient or remainder |
| `busy` | Output | 1 | 50 MHz | High during iterative calculation (stalls processor core) |
| `done` | Output | 1 | 50 MHz | 1-cycle strobe indicating calculation complete |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** WP-01 (Architecture interface definition).
- **Parallel Work Packages:** WP-01 (RV32I Core), WP-03 (DSP Multiplier), WP-07 (Line Buffer), WP-10 (Frame Buffer).
- **Schedule Alignment:** Gantt Chart Oct 6 – Oct 20 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Operands and trigger from `id_ex_stage.v`.
- **Downstream Handoffs:** Asserts `div_busy` into `hazard_unit.v` to freeze pipeline; forwards quotient/remainder to writeback mux.

---

## 6. Manual Verification Procedure
```bash
# Compile and simulate divider unit
iverilog -g2012 -o sim_div.vvp rtl/core/divider.v tb/tb_divider.v
vvp sim_div.vvp
```

---

## 7. Automated Verification Suite
- Execute `tb_divider.v` testing signed/unsigned division, boundary conditions, and latency checks. Output must confirm 0 errors.

---

## 8. Acceptance Criteria
- [ ] Strict compliance with RISC-V specification for divide-by-zero and signed overflow.
- [ ] Remainder sign strictly matches dividend sign.
- [ ] Non-restoring execution latency bounded to $\\le 34$ clock cycles.
- [ ] Infers pure slice logic without consuming DSP blocks.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 6: Sajan-kumar1133
    # --------------------------------------------------------------------------
    {
        "title": "[WP-06][VERIF] Divider Standalone Self-Checking Testbench & Corner-Case Suite",
        "assignees": ["Sajan-kumar1133"],
        "labels": ["verification", "core", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Develop an automated, self-checking testbench (`tb_divider.v`) validating `divider.v` across every instruction type (`DIV`, `DIVU`, `REM`, `REMU`) and corner case.

---

## 2. Test Plan & Boundary Specifications
1. **RISC-V Compliance Edge Cases:**
   - Division by zero: `DIV(x, 0) == -1`, `DIVU(x, 0) == 32'hFFFF_FFFF`, `REM(x, 0) == x`, `REMU(x, 0) == x`.
   - Overflow: `DIV(-2147483648, -1) == -2147483648`, `REM(-2147483648, -1) == 0`.
   - Division of zero: `DIV(0, x) == 0`, `REM(0, x) == 0`.
2. **Sign Variations:**
   - $(+A) / (+B)$, $(-A) / (+B)$, $(+A) / (-B)$, $(-A) / (-B)$.
   - Verify that $(-14) \\% 3 = -2$ and $14 \\% (-3) = 2$.
3. **Latency Verification:**
   - Measure cycle count from `start` to `done`.
   - Assert standard divisions complete in $\\le 34$ cycles.
   - Assert divide-by-zero corner bypass completes in $\\le 1$ cycle.
4. **Randomized Stress Suite:**
   - 2,000 pseudo-random operand pairs verified against behavioral integer division reference.

---

## 3. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-05 (Divider FSM).
- **Parallel Work Packages:** WP-02 (Hazard Unit), WP-04 (Multiplier Testbench), WP-08 (Conv2D Engine), WP-09 (Conv2D Testbench).
- **Schedule Alignment:** Gantt Chart Oct 11 – Oct 20 (Milestone 1).

---

## 4. Handoff Contracts
- **Upstream Requirements:** `rtl/core/divider.v`.
- **Downstream Handoffs:** Verified divider IP signed off for SoC integration.

---

## 5. Manual Verification Procedure
```bash
iverilog -g2012 -o sim_div.vvp rtl/core/divider.v tb/tb_divider.v
vvp sim_div.vvp
# Terminal must display:
# [DIVIDER TEST] PASSED: All corner cases and random tests completed with 0 errors
```

---

## 6. Automated Verification Suite
- Scripted test runner:
  `python -c "import subprocess; res = subprocess.run(['vvp', 'sim_div.vvp'], capture_output=True, text=True); assert '0 errors' in res.stdout.lower() and res.returncode == 0"`

---

## 7. Acceptance Criteria
- [ ] 100% pass on all RISC-V specification corner cases.
- [ ] Cycle counter asserts latency $\\le 34$ cycles for all standard tests.
- [ ] Zero simulation errors or race conditions during FSM state transitions.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 7: RsbhThakur
    # --------------------------------------------------------------------------
    {
        "title": "[WP-07][ACCEL] Dual Circular BRAM Line Buffer Streaming FIFO (320 Bytes)",
        "assignees": ["RsbhThakur"],
        "labels": ["accelerator", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Design and implement the dual circular line buffer streaming FIFO (`conv2d_line_buffer.v`). In real-time 2D spatial convolution on a $160 \\times 120$ video frame, computing a $3 \\times 3$ kernel requires simultaneous access to pixels from row $N$, row $N-1$, and row $N-2$. The line buffer stores two horizontal scanlines ($2 \\times 160 = 320$ bytes) and delivers a 3-pixel vertical column every clock cycle.

---

## 2. Microarchitecture & Memory Organization
- **Buffer Structure:**
  - Line Buffer 0: Depth 160 bytes (stores Row $N-2$).
  - Line Buffer 1: Depth 160 bytes (stores Row $N-1$).
- **Circular Pointer Operation:**
  - Write and read pointers increment on every active `pixel_valid_in` pulse and wrap to 0 after reaching 159.
  - Incoming pixel (Row $N$) is written into Line Buffer 1, while Line Buffer 1's previous content is shifted into Line Buffer 0.
- **Concurrent Output Bus:**
  - `row0_pixel[7:0]`: Scanline $N-2$ pixel.
  - `row1_pixel[7:0]`: Scanline $N-1$ pixel.
  - `row2_pixel[7:0]`: Current incoming pixel (Scanline $N$).

---

## 3. Hardware Interface Contracts (`conv2d_line_buffer.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 25 MHz | Video processing clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `pixel_valid_in` | Input | 1 | 25 MHz | Strobe indicating valid incoming pixel |
| `pixel_in` | Input | 8 | 25 MHz | Incoming 8-bit grayscale pixel |
| `row0_pixel` | Output | 8 | 25 MHz | Output pixel from row $N-2$ (lag: 320 cycles) |
| `row1_pixel` | Output | 8 | 25 MHz | Output pixel from row $N-1$ (lag: 160 cycles) |
| `row2_pixel` | Output | 8 | 25 MHz | Current row $N$ pixel (unregistered bypass) |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** None (Independent accelerator module).
- **Parallel Work Packages:** WP-01 (RV32I Core), WP-03 (DSP Multiplier), WP-05 (Divider FSM), WP-10 (Frame Buffer).
- **Schedule Alignment:** Gantt Chart Oct 6 – Oct 15 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Single-pixel stream from Video Frame Buffer or camera interface.
- **Downstream Handoffs:** Synchronous 3-row vertical bus (`row0_pixel`, `row1_pixel`, `row2_pixel`) fed directly to `conv2d_engine.v` (WP-08).

---

## 6. Manual Verification Procedure
```bash
# Compile and simulate line buffer
iverilog -g2012 -o sim_lb.vvp rtl/accelerators/conv2d_line_buffer.v tb/tb_conv2d.v
vvp sim_lb.vvp
# Inspect waveforms in GTKWave:
# Verify row1_pixel lags row2_pixel by exactly 160 cycles
# Verify row0_pixel lags row1_pixel by exactly 160 cycles
```

---

## 7. Automated Verification Suite
- Self-checking testbench asserting that pixel value written at cycle $T$ emerges on `row1_pixel` at cycle $T+160$ and `row0_pixel` at cycle $T+320$.

---

## 8. Acceptance Criteria
- [ ] Circular pointers wrap cleanly at 160 without pointer drift or phase skew.
- [ ] Storage footprint bounded to 320 bytes (0.08 BRAMs or distributed LUTRAM).
- [ ] Sustained throughput: produces valid 3-row output every clock cycle under continuous input.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 8: RsbhThakur
    # --------------------------------------------------------------------------
    {
        "title": "[WP-08][ACCEL] Parallel 9-MAC Conv2D Spatial Filtering Engine RTL",
        "assignees": ["RsbhThakur"],
        "labels": ["accelerator", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Design and implement the high-throughput 2D spatial convolution hardware accelerator (`conv2d_engine.v`). Operating on a $3 \\times 3$ sliding spatial window, the engine computes edge gradients, noise filtering, or image transformations at a sustained throughput of 1 output pixel per clock cycle (60 FPS @ 25 MHz).

---

## 2. Microarchitecture & Operating Modes
- **$3 \\times 3$ Sliding Window Matrix Registers:**
  ```
  [p00  p01  p02]   (Row 0 from Line Buffer 0)
  [p10  p11  p12]   (Row 1 from Line Buffer 1)
  [p20  p21  p22]   (Row 2 current pixel)
  ```
- **Supported Filter Modes (`filter_mode[1:0]`):**
  - `2'b00` - **Sobel Spatial Edge Detection:**
    $$G_x = (p_{02} + 2p_{12} + p_{22}) - (p_{00} + 2p_{10} + p_{20})$$
    $$G_y = (p_{20} + 2p_{21} + p_{22}) - (p_{00} + 2p_{01} + p_{02})$$
    $$|G| = |G_x| + |G_y|$$
    `pixel_out = (|G| >= edge_threshold) ? 8'hFF : 8'h00`
  - `2'b01` - **Gaussian Noise Smoothing (Low-Pass Filter):**
    $$p_{out} = \\frac{1}{16} [p_{00} + 2p_{01} + p_{02} + 2p_{10} + 4p_{11} + 2p_{12} + p_{20} + 2p_{21} + p_{22}]$$
  - `2'b10` - **Dynamic Image Inversion:** `pixel_out = 255 - p11`.
  - `2'b11` - **Pass-Through Mode:** `pixel_out = p11`.

---

## 3. Hardware Interface Contracts (`conv2d_engine.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 25 MHz | Video processing clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `enable` | Input | 1 | 25 MHz | Accelerator enable strobe |
| `filter_mode` | Input | 2 | 25 MHz | 00: Sobel, 01: Gaussian, 10: Invert, 11: Pass |
| `edge_threshold` | Input | 8 | 25 MHz | Edge binarization threshold (e.g., 8'd60) |
| `pixel_valid_in` | Input | 1 | 25 MHz | Valid input pixel indicator |
| `pixel_in` | Input | 8 | 25 MHz | 8-bit incoming grayscale pixel |
| `pixel_valid_out`| Output | 1 | 25 MHz | Valid output pixel strobe |
| `pixel_out` | Output | 8 | 25 MHz | Filtered output pixel |
| `raw_center_pixel` | Output | 8 | 25 MHz | Raw center pixel ($p_{11}$) for split-screen mux |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-07 (Line Buffer).
- **Parallel Work Packages:** WP-02 (Hazard Unit), WP-04 (Multiplier Testbench), WP-06 (Divider Testbench), WP-11 (VGA Controller), WP-12 (Edge-AI Classifier).
- **Schedule Alignment:** Gantt Chart Oct 6 – Oct 25 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Synchronous 3-row vertical bus from `conv2d_line_buffer.v`.
- **Downstream Handoffs:** Delivers `pixel_out`, `pixel_valid_out`, and `raw_center_pixel` to VGA Split-Screen Compositor (WP-11) and Edge-AI Classifier (WP-12).

---

## 6. Manual Verification Procedure
```bash
# Compile and simulate Conv2D engine
iverilog -g2012 -o sim_conv2d.vvp rtl/accelerators/*.v tb/tb_conv2d.v
vvp sim_conv2d.vvp
# Open GTKWave: check that pixel_valid_out asserts after window pipeline fill
```

---

## 7. Automated Verification Suite
- Self-checking testbench streams edge step patterns; asserts Sobel gradient calculation matches exact theoretical value.

---

## 8. Acceptance Criteria
- [ ] Pipelined 9-MAC arithmetic tree runs at 1 output pixel per cycle (25 MHz).
- [ ] Bit-exact mathematical execution across all 4 filter modes.
- [ ] Correct boundary padding without memory underflow/overflow.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 9: RsbhThakur
    # --------------------------------------------------------------------------
    {
        "title": "[WP-09][VERIF] Conv2D Streaming Testbench & Golden Model Image Verification",
        "assignees": ["RsbhThakur"],
        "labels": ["verification", "accelerator", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Build an end-to-end automated verification framework (`tb_conv2d.v`) and Python validation suite comparing the hardware `conv2d_engine.v` output against an OpenCV/NumPy golden software reference model.

---

## 2. Verification Methodology
1. **Synthetic Test Patterns:**
   - Sharp vertical edge transition ($0 \\rightarrow 255$).
   - Sharp horizontal edge transition.
   - Diagonal edge transition.
   - Uniform solid color (all 0, all 255) yielding zero edge gradient.
2. **Real-World Image Verification:**
   - Input traffic sign image ($160 \\times 120$ pixels) converted to hex memory format via `sw/tools/image_to_hex.py`.
   - `tb_conv2d.v` streams 19,200 bytes into Verilog simulation and captures output stream to `conv2d_out.hex`.
   - Python script compares Verilog simulation output with OpenCV `cv2.Sobel()` and `cv2.GaussianBlur()`.
   - Pass Criterion: Bit-exact match (MSE = 0.00).

---

## 3. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-08 (Conv2D Engine RTL).
- **Parallel Work Packages:** WP-04 (Multiplier Testbench), WP-06 (Divider Testbench), WP-12 (Edge-AI Classifier), WP-13 (7-Segment & Actuators).
- **Schedule Alignment:** Gantt Chart Oct 16 – Oct 25 (Milestone 1).

---

## 4. Handoff Contracts
- **Upstream Requirements:** `conv2d_engine.v` and `conv2d_line_buffer.v`.
- **Downstream Handoffs:** Verified hardware accelerator signed off for top-level SoC integration.

---

## 5. Manual Verification Procedure
```bash
# Run streaming testbench
iverilog -g2012 -o sim_conv2d.vvp rtl/accelerators/*.v tb/tb_conv2d.v
vvp sim_conv2d.vvp

# Run automated Python golden model verification
python scripts/verify_all_deliverables.py
```

---

## 6. Automated Verification Suite
- Scripted execution:
  `python -c "import subprocess; res = subprocess.run(['vvp', 'sim_conv2d.vvp'], capture_output=True, text=True); assert 'CONV2D TEST PASSED' in res.stdout"`

---

## 7. Acceptance Criteria
- [ ] Zero pixel mismatches between Verilog output and OpenCV reference model.
- [ ] No image shift or coordinate displacement in output frame.
- [ ] Verification script reports 100% pass across Sobel, Gaussian, and Invert modes.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 10: SarthakKhot
    # --------------------------------------------------------------------------
    {
        "title": "[WP-10][VIDEO] Dual-Port Video Frame Buffer Block RAM (19.2 KB)",
        "assignees": ["SarthakKhot"],
        "labels": ["video-subsystem", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Design and instantiate the true dual-port asynchronous video frame buffer (`frame_buffer.v`) storing $160 \\times 120$ 8-bit grayscale pixels (19,200 bytes = 19.2 KB). The frame buffer decouples the 50 MHz processor/UART write clock domain from the 25 MHz VGA raster scan read clock domain.

---

## 2. Microarchitecture & Memory Budget
- **Dual-Clock Architecture:**
  - **Port A (Write Domain - 50 MHz):**
    - Driven by MMIO crossbar or UART frame receiver.
    - Write address `waddr[14:0]` ($0 \\dots 19,199$), write data `wdata[7:0]`, write enable `we`.
  - **Port B (Read Domain - 25 MHz):**
    - Driven by VGA raster timing generator.
    - Read address `raddr[14:0]` ($0 \\dots 19,199$), read data `rdata[7:0]`.
- **FPGA Resource Budget:**
  - Infers dedicated Xilinx Artix-7 36 Kb Block RAM primitives (`RAMB36E1`).
  - Total BRAM consumption: 5-6 36 Kb BRAM blocks ($\\approx 4.5\\%$ of Artix-7 XC7A100T budget).

---

## 3. Hardware Interface Contracts (`frame_buffer.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk_write` | Input | 1 | 50 MHz | Processor / UART write domain clock |
| `clk_read` | Input | 1 | 25 MHz | VGA raster display read domain clock |
| `we` | Input | 1 | 50 MHz | Frame buffer write enable |
| `waddr` | Input | 15 | 50 MHz | Write byte address ($0 \\dots 19,199$) |
| `wdata` | Input | 8 | 50 MHz | Pixel data byte to write |
| `raddr` | Input | 15 | 25 MHz | Read byte address ($0 \\dots 19,199$) |
| `rdata` | Output | 8 | 25 MHz | Continuous pixel data readout |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** None (Foundational video subsystem module).
- **Parallel Work Packages:** WP-01 (RV32I Core), WP-03 (DSP Multiplier), WP-05 (Divider FSM), WP-07 (Line Buffer).
- **Schedule Alignment:** Gantt Chart Oct 6 – Oct 15 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Connected to MMIO Crossbar (WP-15) / UART for frame writes.
- **Downstream Handoffs:** Streams raw pixel data to VGA Controller & Compositor (WP-11) and Conv2D Engine (WP-08).

---

## 6. Manual Verification Procedure
```bash
# Verify dual-port RAM instantiation and clock-domain crossing
iverilog -g2012 -o sim_fb.vvp rtl/video/frame_buffer.v tb/tb_autovision_soc.v
vvp sim_fb.vvp
```

---

## 7. Automated Verification Suite
- Self-checking BRAM pattern test: writes unique hash pattern across all 19,200 memory cells via Port A; reads back and verifies via Port B at 25 MHz.

---

## 8. Acceptance Criteria
- [ ] 19,200 bytes mapped with clean address wrap at `0x4AFF`.
- [ ] Infers true dual-port `RAMB36E1` primitives without falling back to distributed LUTs.
- [ ] Glitch-free clock-domain crossing between 50 MHz write domain and 25 MHz read domain.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 11: SarthakKhot
    # --------------------------------------------------------------------------
    {
        "title": "[WP-11][VIDEO] VGA 640x480 @ 60Hz Timing Controller & Split-Screen Compositor",
        "assignees": ["SarthakKhot"],
        "labels": ["video-subsystem", "milestone-1"],
        "body": """## 1. Architectural Objective & Context
Implement the industry-standard 640x480 @ 60Hz VGA timing generator and real-time split-screen compositor (`vga_controller.v`, `split_screen_mux.v`). The subsystem upscales $160 \\times 120$ camera frames $4 \\times 4$ and renders a dual-view ADAS HUD on an external monitor.

---

## 2. Microarchitecture & Display Pipeline
- **VGA Timing Standard (25.175 MHz Pixel Clock):**
  - Horizontal: Visible 640, Front Porch 16, Sync Pulse 96, Back Porch 48 (Total = 800 pixels).
  - Vertical: Visible 480, Front Porch 10, Sync Pulse 2, Back Porch 33 (Total = 525 lines).
- **$4 \\times 4$ Coordinate Upscaler:**
  - Translates VGA screen coordinates $(X, Y)$ into frame buffer coordinates via bit shifts: `fb_x = x >> 2`, `fb_y = y >> 2`.
- **Split-Screen HUD Compositor (`split_screen_mux.v`):**
  - Left Half ($X < 320$): Renders raw incoming grayscale video.
  - Right Half ($X \\ge 320$): Renders real-time Sobel edge-detected overlay.
  - Center Dividing Line ($X = 320$): Bright green vertical boundary.
  - Bounding Box HUD: Draws rectangular colored overlay around classified traffic signs.

---

## 3. Hardware Interface Contracts (`vga_controller.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk_25mhz` | Input | 1 | 25 MHz | Video pixel clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `raw_pixel` | Input | 8 | 25 MHz | Raw pixel byte from Frame Buffer |
| `edge_pixel` | Input | 8 | 25 MHz | Filtered edge pixel from Conv2D Engine |
| `sign_detected` | Input | 1 | 25 MHz | High when sign classifier detects object |
| `bbox_coords` | Input | 32 | 25 MHz | Packed bounding box $[X_{min}, Y_{min}, X_{max}, Y_{max}]$ |
| `vga_hsync` | Output | 1 | 25 MHz | Horizontal sync pulse to VGA DAC |
| `vga_vsync` | Output | 1 | 25 MHz | Vertical sync pulse to VGA DAC |
| `vga_r` | Output | 4 | 25 MHz | 4-bit Red color channel to Nexys A7 resistor ladder |
| `vga_g` | Output | 4 | 25 MHz | 4-bit Green color channel to Nexys A7 resistor ladder |
| `vga_b` | Output | 4 | 25 MHz | 4-bit Blue color channel to Nexys A7 resistor ladder |
| `pixel_x` | Output | 10 | 25 MHz | Current screen X raster coordinate ($0 \\dots 639$) |
| `pixel_y` | Output | 10 | 25 MHz | Current screen Y raster coordinate ($0 \\dots 479$) |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-10 (Frame Buffer).
- **Parallel Work Packages:** WP-07 (Line Buffer), WP-08 (Conv2D Engine), WP-12 (Edge-AI Classifier), WP-13 (7-Segment).
- **Schedule Alignment:** Gantt Chart Oct 11 – Oct 30 (Milestone 1).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Raw pixels from `frame_buffer.v` and edge pixels from `conv2d_engine.v`.
- **Downstream Handoffs:** Drives physical Nexys A7 VGA output connector pins defined in `constr/nexys_a7_100t.xdc`.

---

## 6. Manual Verification Procedure
```bash
# Simulate 1 full VGA frame (525 lines x 800 pixels)
iverilog -g2012 -o sim_vga.vvp rtl/video/*.v tb/tb_autovision_soc.v
vvp sim_vga.vvp
# Verify in GTKWave that HSYNC and VSYNC pulses occur with exact specified durations
```

---

## 7. Automated Verification Suite
- Self-checking testbench asserting that RGB outputs are strictly 0 during horizontal and vertical blanking periods.

---

## 8. Acceptance Criteria
- [ ] Pixel clock and sync timing strictly adhere to standard 640x480 @ 60Hz VGA timings.
- [ ] Split-screen compositor renders left raw and right edge frames without tearing.
- [ ] Connects cleanly to Nexys A7 12-bit VGA resistor ladder DAC.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 12: SarthakKhot
    # --------------------------------------------------------------------------
    {
        "title": "[WP-12][ACCEL] Edge-AI Geometric Obstacle Classifier & AEB Trip Circuit",
        "assignees": ["SarthakKhot"],
        "labels": ["accelerator", "soc-integration", "milestone-2"],
        "body": """## 1. Architectural Objective & Context
Implement the hardware Edge-AI classifier and Autonomous Emergency Braking (AEB) trip interlock (`edge_classifier.v`). Analyzing edge spatial distribution in real-time, the module identifies road obstacles and traffic signs (STOP octagon, YIELD triangle, Speed Limit circle), asserting an emergency brake signal in sub-frame latency ($<16.6$ ms).

---

## 2. Microarchitecture & Algorithmic Classification
- **Centroid & Bounding Box Tracker:**
  - Accumulates active edge pixel coordinates $(X, Y)$ across the $160 \\times 120$ frame.
  - Dynamically updates $[X_{min}, Y_{min}, X_{max}, Y_{max}]$ to isolate region-of-interest (ROI).
- **Quadrant Edge Density Analysis:**
  - Partitions ROI into 4 quadrants ($Q_1, Q_2, Q_3, Q_4$).
  - **Octagon (STOP Sign):** Balanced density across all 4 quadrants with symmetric corner chamfers $\\implies$ `SIGN_STOP` (`3'b001`).
  - **Triangle (YIELD Sign):** Heavy bottom quadrant density with apex at top $\\implies$ `SIGN_YIELD` (`3'b010`).
  - **Circle (Speed Limit):** Uniform radial distribution with aspect ratio $\\approx 1.0 \\implies$ `SIGN_SPEED_LIMIT` (`3'b011`).
- **Hardware Autonomous Emergency Braking (AEB) Interlock:**
  - When `SIGN_STOP` or forward collision obstacle is detected in lower ROI ($Y > 60$):
    - Asserts `aeb_trigger = 1` immediately without waiting for software polling.
    - Activates emergency brake indicator with sub-frame response ($<16.6$ ms).

---

## 3. Hardware Interface Contracts (`edge_classifier.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 25 MHz | Video processing clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `pixel_valid` | Input | 1 | 25 MHz | Valid pixel strobe |
| `pixel_is_edge`| Input | 1 | 25 MHz | Binary edge pixel flag from Conv2D engine |
| `pixel_x` | Input | 8 | 25 MHz | Current X coordinate ($0 \\dots 159$) |
| `pixel_y` | Input | 8 | 25 MHz | Current Y coordinate ($0 \\dots 119$) |
| `frame_start` | Input | 1 | 25 MHz | Pulse indicating start of new video frame |
| `sign_id` | Output | 3 | 25 MHz | Classified sign ID (`000`: None, `001`: STOP, `010`: YIELD, `011`: SPEED) |
| `confidence` | Output | 8 | 25 MHz | Detection confidence score ($0 \\dots 255$) |
| `bbox_valid` | Output | 1 | 25 MHz | High when valid bounding box is calculated |
| `bbox_coords` | Output | 32 | 25 MHz | Packed bounding box $[X_{min}, Y_{min}, X_{max}, Y_{max}]$ |
| `aeb_trigger` | Output | 1 | 25 MHz | Direct hardware autonomous emergency brake interlock |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-08 (Conv2D Engine RTL).
- **Parallel Work Packages:** WP-09 (Conv2D Testbench), WP-13 (7-Segment & Actuators), WP-14 (V2X Cipher).
- **Schedule Alignment:** Gantt Chart Oct 11 – Oct 25 (Milestone 2).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Edge pixel stream from `conv2d_engine.v`.
- **Downstream Handoffs:** Feeds bounding box to `vga_controller.v` (WP-11), `aeb_trigger` to Actuator Controller (WP-13), and telemetry to MMIO Crossbar (WP-15).

---

## 6. Manual Verification Procedure
```bash
# Compile and simulate classifier with synthetic test patterns
iverilog -g2012 -o sim_class.vvp rtl/accelerators/edge_classifier.v tb/tb_conv2d.v
vvp sim_class.vvp
# Check terminal: verify sign_id == 3'b001 when STOP pattern is presented
```

---

## 7. Automated Verification Suite
- Automated testbench asserting that presenting a synthetic octagon activates `aeb_trigger` within 100 clock cycles of frame completion.

---

## 8. Acceptance Criteria
- [ ] Real-time classification throughput matching incoming pixel stream (25 MHz).
- [ ] Accurately distinguishes STOP, YIELD, and Speed Limit sign geometric profiles.
- [ ] Sub-frame ($<16.6$ ms) deterministic AEB activation.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 13: SarthakKhot
    # --------------------------------------------------------------------------
    {
        "title": "[WP-13][SOC] 7-Segment Multi-Digit Telemetry & Actuator Controllers",
        "assignees": ["SarthakKhot"],
        "labels": ["soc-integration", "milestone-2"],
        "body": """## 1. Architectural Objective & Context
Design and integrate the multiplexed 8-digit 7-segment display driver (`seven_seg_driver.v`) and vehicle actuator controller (`actuator_controller.v`) for the Nexys A7 FPGA board.

---

## 2. Microarchitecture & Peripheral Controls
- **Multiplexed 8-Digit 7-Segment Display Driver:**
  - 1 kHz refresh rate generator derived from 50 MHz system clock (1 ms active window per digit).
  - Displays real-time ADAS telemetry:
    - Digits [7:4]: Vehicle speed / target speed limit (e.g. `SP-50`).
    - Digits [3:0]: Detected sign code / AEB status (e.g. `StOP`, `CLr`, `brAK`).
- **Vehicle Actuator Controller (`actuator_controller.v`):**
  - Tri-color RGB LED (`LED16_R`, `LED16_G`, `LED16_B`):
    - **Red:** Autonomous Emergency Brake Tripped (`aeb_trigger = 1`).
    - **Yellow/Amber:** Warning / Yield sign ahead.
    - **Green:** Normal cruise / path clear.
  - Slide Switch Interface (`SW[15:0]`): Debounced user controls for filter mode selection and manual edge threshold tuning.

---

## 3. Hardware Interface Contracts (`seven_seg_driver.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 50 MHz | Master system clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `speed_data` | Input | 16 | 50 MHz | Packed BCD/Hex speed value for digits [7:4] |
| `status_code` | Input | 16 | 50 MHz | Status characters for digits [3:0] |
| `aeb_trigger` | Input | 1 | 50 MHz | Hardware AEB trip flag |
| `anode` | Output | 8 | 50 MHz | Active-low digit enable anodes (`AN[7:0]`) |
| `cathode` | Output | 7 | 50 MHz | Active-low segment cathodes (`CA..CG`) |
| `dp` | Output | 1 | 50 MHz | Active-low decimal point cathode |
| `rgb_led` | Output | 3 | 50 MHz | Tri-color RGB LED drive (`{R, G, B}`) |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-12 (Edge-AI Classifier).
- **Parallel Work Packages:** WP-14 (V2X Cipher), WP-15 (MMIO Crossbar).
- **Schedule Alignment:** Gantt Chart Oct 16 – Oct 30 (Milestone 2).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Telemetry data from MMIO crossbar and `aeb_trigger` from classifier.
- **Downstream Handoffs:** Drives physical Nexys A7 FPGA pins mapped in `constr/nexys_a7_100t.xdc`.

---

## 6. Manual Verification Procedure
```bash
# Test 7-segment multiplexer
iverilog -g2012 -o sim_7seg.vvp rtl/soc/seven_seg_driver.v tb/tb_autovision_soc.v
vvp sim_7seg.vvp
# Check GTKWave: verify anodes rotate sequentially 8'b11111110 -> 8'b11111101 -> ...
```

---

## 7. Automated Verification Suite
- Testbench asserting that asserting `aeb_trigger = 1` immediately switches RGB LED from Green (`3'b010`) to Red (`3'b100`) in 0 clock cycles.

---

## 8. Acceptance Criteria
- [ ] Flicker-free 1 kHz multiplexing on physical 8-digit 7-segment displays.
- [ ] Instantaneous hardware transition of RGB LED to Red upon emergency brake activation.
- [ ] Clean pin assignment matching Digilent Nexys A7-100T schematic.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 14: Sajan-kumar1133
    # --------------------------------------------------------------------------
    {
        "title": "[WP-14][ACCEL][STRETCH] 16-Bit Galois LFSR Cryptographic Stream Cipher Descrambler",
        "assignees": ["Sajan-kumar1133"],
        "labels": ["accelerator", "stretch-goal", "milestone-2"],
        "body": """## 1. Architectural Objective & Context
[Stretch Goal / Advanced Feature] Implement the V2X cryptographic stream cipher hardware descrambler (`v2x_cipher.v`). The cipher secures incoming camera pixel feeds over UART against tampering, decrypting video frames in real-time with modular architecture preparing for AES-128 coprocessor expansion.

---

## 2. Microarchitecture & Cryptographic Algorithm
- **16-Bit Galois LFSR Keystream Generator:**
  - Primitive feedback polynomial:
    $$P(x) = x^{16} + x^{14} + x^{13} + x^{11} + 1$$
  - Feedback tap mask: `16'hD400`.
  - Generates maximal pseudo-random cycle period of $2^{16}-1 = 65,535$ non-repeating states.
- **Dynamic Key Seed Management:**
  - Initial 16-bit cryptographic seed loaded securely via MMIO register (`0x8000_0060`).
- **Stream Decryption:**
  - `plain_pixel_out[7:0] = cipher_pixel_in[7:0] ^ keystream[7:0]`.
  - Zero latency impact: decrypts 1 pixel per clock cycle without FIFO delay.

---

## 3. Hardware Interface Contracts (`v2x_cipher.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 50 MHz | Master system clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `enable` | Input | 1 | 50 MHz | Active-high cipher enable |
| `load_seed` | Input | 1 | 50 MHz | Strobe loading initial crypto key seed |
| `seed_in` | Input | 16 | 50 MHz | 16-bit secret encryption key seed |
| `pixel_valid_in`| Input | 1 | 50 MHz | Strobe for incoming scrambled pixel |
| `cipher_pixel_in`| Input| 8 | 50 MHz | Encrypted 8-bit pixel byte from UART |
| `pixel_valid_out`| Output| 1 | 50 MHz | Strobe for descrambled pixel |
| `plain_pixel_out`| Output| 8 | 50 MHz | Decrypted plaintext pixel sent to frame buffer |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** WP-10 (Video Frame Buffer).
- **Parallel Work Packages:** WP-12 (Edge-AI Classifier), WP-13 (7-Segment & Actuators), WP-15 (MMIO Crossbar).
- **Schedule Alignment:** Gantt Chart Oct 16 – Oct 30 (Milestone 2).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Encrypted byte stream from UART receiver and crypto seed from MMIO crossbar.
- **Downstream Handoffs:** Writes decrypted pixel stream directly into Video Frame Buffer (WP-10).

---

## 6. Manual Verification Procedure
```bash
# Verify LFSR reversibility
iverilog -g2012 -o sim_cipher.vvp rtl/accelerators/v2x_cipher.v tb/tb_autovision_soc.v
vvp sim_cipher.vvp
# Encrypt image in Python using matching polynomial; verify plain image emerges from RTL
```

---

## 7. Automated Verification Suite
- Automated Python & Verilog co-simulation test verifying that applying identical key seed produces bit-exact decrypted image matching original unencrypted frame.

---

## 8. Acceptance Criteria
- [ ] Bit-exact reversible encryption/decryption verified against software model.
- [ ] Zero throughput penalty: processes 1 pixel per clock cycle.
- [ ] Minimal FPGA area: consumes $<50$ LUTs on Artix-7.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 15: Rohit-Yadav19
    # --------------------------------------------------------------------------
    {
        "title": "[WP-15][SOC] 32-Bit Memory-Mapped Crossbar Interconnect & Peripheral Bridge",
        "assignees": ["Rohit-Yadav19"],
        "labels": ["soc-integration", "core", "milestone-2"],
        "body": """## 1. Architectural Objective & Context
Implement the centralized 32-bit Memory-Mapped I/O (MMIO) address decoder and routing crossbar (`mmio_crossbar.v`). The crossbar glues the RV32IM processor core to Data RAM, Video Frame Buffer, Hardware Accelerators, and all board peripherals with single-cycle response.

---

## 2. Complete AutoVision SoC Memory Map

| Address Range | Size | Target Peripheral | Subsystem Function |
| :--- | :---: | :--- | :--- |
| `0x0000_0000 - 0x0000_3FFF` | 16 KB | Instruction BRAM | Core firmware & boot vector |
| `0x0001_0000 - 0x0001_3FFF` | 16 KB | Data BRAM | Stack, heap, and runtime variables |
| `0x8000_0000 - 0x8000_4AFF` | 19.2 KB | Video Frame Buffer | $160 \\times 120$ 8-bit grayscale frame store |
| `0x8000_0010 - 0x8000_001F` | 16 B | Conv2D Control Regs | Filter mode, edge threshold, start/status |
| `0x8000_0020 - 0x8000_002F` | 16 B | Classifier Telemetry | Detected sign ID, confidence, bounding box |
| `0x8000_0030 - 0x8000_003F` | 16 B | Actuators & RGB LEDs | Brake force, RGB override, status LEDs |
| `0x8000_0040 - 0x8000_004F` | 16 B | 7-Segment Display | Digits [7:0] hex values, decimal points |
| `0x8000_0050 - 0x8000_005F` | 16 B | UART Transceiver | TX/RX data, baud rate divisor, status |
| `0x8000_0060 - 0x8000_006F` | 16 B | V2X Cipher Seed | Initial cryptographic seed, cipher enable |

---

## 3. Hardware Interface Contracts (`mmio_crossbar.v`)

| Port Name | Direction | Width | Clock Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | 50 MHz | Master clock |
| `reset_n` | Input | 1 | Asynchronous | Active-low reset |
| `cpu_addr` | Input | 32 | 50 MHz | Byte address from processor core datapath |
| `cpu_wdata` | Input | 32 | 50 MHz | Store data from processor core |
| `cpu_write_req` | Input | 1 | 50 MHz | Write strobe from core |
| `cpu_read_req` | Input | 1 | 50 MHz | Read strobe from core |
| `cpu_byte_enable`| Input| 4 | 50 MHz | Byte write mask (`SB`, `SH`, `SW`) |
| `cpu_rdata` | Output | 32 | 50 MHz | Multiplexed read data returned to core |
| Slave Selects | Outputs| 1 each| 50 MHz | Individual chip select strobes (`cs_dmem`, `cs_vram`, `cs_conv`, etc.) |

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-01 (RV32I Core), WP-08 (Conv2D Engine), WP-10 (Frame Buffer), WP-12 (Edge-AI Classifier), WP-13 (7-Segment).
- **Parallel Work Packages:** WP-14 (V2X Cipher).
- **Schedule Alignment:** Gantt Chart Oct 21 – Oct 31 (Milestone 2).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Memory bus from `riscv_core.v`.
- **Downstream Handoffs:** Routes transactions to all memory and peripheral slaves with deterministic 1-cycle latency.

---

## 6. Manual Verification Procedure
```bash
# Verify MMIO address decoding
iverilog -g2012 -o sim_bus.vvp rtl/soc/mmio_crossbar.v tb/tb_autovision_soc.v
vvp sim_bus.vvp
# Check GTKWave: verify writes to 0x8000_0040 only assert cs_seven_seg
```

---

## 7. Automated Verification Suite
- Self-checking bus test accessing each slave address range, verifying correct chip select activation and data integrity.

---

## 8. Acceptance Criteria
- [ ] Complete address decode without aliasing across memory regions.
- [ ] Single-cycle read response multiplexing with 0 wait states.
- [ ] Full compliance with RV32I load/store semantics (`LB`, `LH`, `LW`, `SB`, `SH`, `SW`).
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 16: Rohit-Yadav19
    # --------------------------------------------------------------------------
    {
        "title": "[WP-16][VERIF] Integrated SoC Testbench & 25-Cycle Hazard Waveform Simulation",
        "assignees": ["Rohit-Yadav19"],
        "labels": ["verification", "soc-integration", "milestone-2"],
        "body": """## 1. Architectural Objective & Context
Construct the integrated top-level SoC testbench (`tb_autovision_soc.v`) and dedicated 25-cycle pipeline execution testbench (`tb_pipeline_25cycles.v`). This testbench reproduces and verifies the exact cycle-by-cycle microarchitectural timing diagram from Section 2 of the design report.

---

## 2. Cycle-Accurate Execution Trace (Vivado Verified)
```
0x00: addi x1, 10
0x04: addi x2, 20
0x08: add  x3, x1, x2  (RAW Forwarding WB -> EX, 0 penalty stalls)
0x0C: mul  x4, x1, x2  (1-Cycle DSP48E1 Multiplier)
0x10: div  x5, x4, x1  (Non-Restoring FSM <= 34 Cycle Stall)
0x14: addi x6, x5, 5   (Quotient Forwarded at Cycle 39)
```

### Detailed Pipeline Timing Expectations:
- **Cycle 4:** RAW data forwarding: `ForwardBE = 2'b10` routes $x2=20$ from WB into ALU execution stage.
- **Cycle 5:** Multiplier executes $x4 = x1 \\times x2 = 10 \\times 20 = 200$ in 1 cycle.
- **Cycle 6:** Divider initiates FSM, asserts `div_busy = 1` and `Stall_PC = 1`.
- **Cycles 7..36:** Clock enable gated for PC and Stage 1 registers; pipeline freezes while divider iterates.
- **Cycle 38:** Divider finishes, de-asserts `div_busy = 0`.
- **Cycle 39:** `ForwardAE = 2'b10` bypasses quotient $x5=20$ into `addi x6, x5, 5`.
- **Cycle 40:** Writeback stage commits $x6 = 25$.

---

## 3. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-02 (Hazard Unit), WP-04 (Multiplier Testbench), WP-06 (Divider Testbench), WP-09 (Conv2D Testbench), WP-15 (MMIO Crossbar).
- **Parallel Work Packages:** WP-17 (Vivado Synthesis).
- **Schedule Alignment:** Gantt Chart Oct 21 – Oct 31 / Nov 1 – Nov 3 (Milestone 2).

---

## 4. Handoff Contracts
- **Upstream Requirements:** All RTL modules across `rtl/core/`, `rtl/accelerators/`, `rtl/video/`, and `rtl/soc/`.
- **Downstream Handoffs:** Delivers verified waveform `.vcd` artifact and simulation logs for course grading.

---

## 5. Manual Verification Procedure
```bash
# Run 25-cycle hazard simulation
iverilog -g2012 -o sim_25c.vvp rtl/core/*.v rtl/accelerators/*.v rtl/soc/*.v rtl/video/*.v tb/tb_pipeline_25cycles.v
vvp sim_25c.vvp

# Open GTKWave and verify signals match Table 2 of Section 2 in the design report:
gtkwave waveform.vcd
```

---

## 6. Automated Verification Suite
- Scripted assertions:
  `python -c "import subprocess; res = subprocess.run(['vvp', 'sim_25c.vvp'], capture_output=True, text=True); assert 'PIPELINE 25-CYCLE TEST PASSED' in res.stdout"`

---

## 7. Acceptance Criteria
- [ ] Waveform trace perfectly reproduces Vivado-verified timing diagram in design report.
- [ ] Zero simulation errors or undefined (`'x'`) signal propagations.
- [ ] VCD dump successfully generated for documentation and submission presentation.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 17: Sajan-kumar1133
    # --------------------------------------------------------------------------
    {
        "title": "[WP-17][SYNTH] Vivado Synthesis, Place & Route, and 50 MHz Timing Closure",
        "assignees": ["Sajan-kumar1133"],
        "labels": ["synthesis", "milestone-3"],
        "body": """## 1. Architectural Objective & Context
Execute complete physical implementation in AMD Vivado 2025.2 targeting the Digilent Nexys A7-100T FPGA (`xc7a100tcsg324-1`). The work package closes setup and hold timing at 50 MHz system clock and generates the production programming bitstream.

---

## 2. Implementation Specifications & Targets
- **Target Device:** AMD Xilinx Artix-7 XC7A100T-1CSG324C.
- **Clock Domains:**
  - `clk_50mhz`: System clock for RV32IM core, MMIO crossbar, line buffers, and peripherals ($T_{clk} = 20.000$ ns).
  - `clk_25mhz`: VGA pixel clock ($T_{clk} = 39.722$ ns) generated via MMCME2 / clock divider.
- **Physical Constraints:** Pin mapping defined in `constr/nexys_a7_100t.xdc`.
- **Timing Closure Goals:**
  - Setup Slack ($WNS$): $\\ge +2.0$ ns (Target: $+2.410$ ns).
  - Hold Slack ($WHS$): $\\ge +0.05$ ns.
  - Zero unconstrained paths and zero timing violations.
- **Resource Budget Caps:**
  - Block RAM: $\\le 12$ 36 Kb BRAMs ($\\\\le 8.89\\\\%$ of 135 available).
  - DSP48E1 Slices: $\\le 4$ DSPs ($\\\\le 1.67\\\\%$ of 240 available).
  - Slice LUTs: $\\le 4,000$ LUTs ($\\\\le 6.3\\\\%$ of 63,400 available).
  - Flip-Flops: $\\le 4,500$ FFs ($\\\\le 3.5\\\\%$ of 126,800 available).

---

## 3. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-15 (MMIO Crossbar), WP-16 (Integrated SoC Testbench).
- **Parallel Work Packages:** WP-18 (Embedded Firmware & Live Demo).
- **Schedule Alignment:** Gantt Chart Oct 26 – Oct 31 / Nov 1 – Nov 3 (Milestone 2/3).

---

## 4. Handoff Contracts
- **Upstream Requirements:** Clean RTL codebase and XDC constraints.
- **Downstream Handoffs:** Delivers implementation run reports (`utilization.rpt`, `timing_summary.rpt`) and bitstream (`autovision_top_nexys.bit`).

---

## 5. Manual Verification Procedure
```bash
# Execute Vivado batch build
vivado -mode batch -source scripts/build_bitstream.tcl

# Inspect timing report
grep -i "slack" timing_summary.rpt
# Verify: Slack (MET) : +2.410ns
```

---

## 6. Automated Verification Suite
- Script `scripts/verify_all_deliverables.py` checks that bitstream exists, size $> 3.5$ MB, and no negative slacks reported in Vivado logs.

---

## 7. Acceptance Criteria
- [ ] Timing closed with positive setup ($WNS > 0$) and hold slack ($WHS > 0$).
- [ ] Resource usage strictly within Section 4 estimates of design report.
- [ ] Production bitstream `autovision_top_nexys.bit` generated with zero DRC errors.
"""
    },

    # --------------------------------------------------------------------------
    # ISSUE 18: RsbhThakur
    # --------------------------------------------------------------------------
    {
        "title": "[WP-18][FW] Embedded C ADAS Firmware, Host PC Streaming Bridge & Live FPGA Board Demo",
        "assignees": ["RsbhThakur"],
        "labels": ["firmware", "soc-integration", "milestone-3"],
        "body": """## 1. Architectural Objective & Context
Develop the embedded C ADAS perception runtime firmware (`sw/workloads/05_adas_runtime/adas_runtime.c`) and Host PC streaming bridge (`scripts/host_pc_demo.py`). This delivers the final end-to-end working demonstration on the physical Nexys A7-100T FPGA board.

---

## 2. Software Architecture & Flow
1. **Embedded C ADAS Firmware (`adas_runtime.c`):**
   - Configures UART transceiver for 115200 baud streaming.
   - Programmed via custom RISC-V toolchain (`sw/tools/riscv_assembler.py`).
   - Initializes Conv2D accelerator (`filter_mode = 2'b00`, `edge_threshold = 8'd60`).
   - Polls frame buffer status, reads detected sign ID and confidence from `0x8000_0020`.
   - Drives 7-segment display with vehicle speed / speed limits.
   - Controls RGB LED for AEB warning state.
   - Returns cycle execution counts and throughput metrics to Host PC.
2. **Host PC Streaming Bridge (`scripts/host_pc_demo.py`):**
   - Captures frames from webcam or pre-recorded road video dataset.
   - Resizes frames to $160 \\times 120$ grayscale, applies Galois LFSR stream encryption, and transmits over USB-UART.
   - Receives telemetry packets from FPGA, displaying real-time FPS, detected signs, and AEB status in OpenCV dashboard.

---

## 3. Physical Hardware Demonstration Setup
- **Nexys A7-100T Board Connections:**
  - Micro-USB: Power, JTAG bitstream programming, and 115200-baud UART telemetry.
  - VGA Port: External monitor displaying 640x480 @ 60Hz split-screen video (Left: Raw, Right: Sobel Edges).
  - Tri-color RGB LED (`LD16`): Red on Emergency Brake, Green on Clear Cruise.
  - 8-Digit 7-Segment Display: Real-time speed and status readouts.
  - Slide Switches (`SW[1:0]`): Dynamic filter mode switching (Sobel / Gaussian / Invert / Pass).

---

## 4. Dependencies & Scheduling
- **Predecessor Dependencies:** Blocked by WP-16 (SoC Verification), WP-17 (Vivado Synthesis).
- **Schedule Alignment:** Gantt Chart Oct 31 – Nov 8 (Final Evaluation Milestone).

---

## 5. Handoff Contracts
- **Upstream Requirements:** Operational FPGA bitstream and UART interface.
- **Downstream Handoffs:** Complete live hardware demonstration for course evaluation committee.

---

## 6. Manual Verification Procedure
```bash
# 1. Program bitstream onto Nexys A7
vivado -mode batch -source scripts/program_fpga.tcl

# 2. Launch Host PC streaming bridge
python scripts/host_pc_demo.py --port COM3 --video assets/traffic_test.mp4

# 3. Observe VGA monitor for 60 FPS split-screen video
# 4. Present STOP sign and observe immediate Red RGB LED AEB activation
```

---

## 7. Automated Verification Suite
- Python UART loopback test validating frame checksums, packet framing, and telemetry logging with zero packet drops.

---

## 8. Acceptance Criteria
- [ ] Sustained video frame streaming over UART at 115200 baud with zero corruptions.
- [ ] Split-screen video (raw vs. Sobel edges) rendered cleanly on VGA monitor at 60 Hz.
- [ ] Autonomous emergency brake trips reliably with sub-frame ($<16.6$ ms) latency when STOP sign appears.
- [ ] Complete project signed off for 10/10 evaluation score.
"""
    }
]

def main():
    token = get_github_token()
    print("[INIT] Verifying GitHub authentication and safety rules...")
    
    # 1. Create/update labels
    print("[PHASE 1] Creating repository labels...")
    for lbl in LABELS:
        create_or_update_label(token, lbl["name"], lbl["color"], lbl["description"])

    # 2. Create issues
    print("\n[PHASE 2] Creating 18 architectural issues...")
    created_issues = []
    for issue in ISSUES_DATA:
        resp = create_issue(
            token=token,
            title=issue["title"],
            body=issue["body"],
            assignees=issue["assignees"],
            labels=issue["labels"]
        )
        created_issues.append({
            "number": resp.get("number"),
            "title": resp.get("title"),
            "url": resp.get("html_url"),
            "assignee": issue["assignees"][0],
            "labels": ", ".join(issue["labels"])
        })
        time.sleep(1.0) # Avoid GitHub secondary rate limits

    # 3. Generate summary report
    print("\n[PHASE 3] Generating issue summary report...")
    report_file = os.path.join("docs", "github_issues_summary.md")
    os.makedirs("docs", exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# AutoVision-RISC-V: GitHub Issues Master Directory\n\n")
        f.write("| Issue | Title | Assignee | Labels | URL |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- |\n")
        for it in created_issues:
            f.write(f"| #{it['number']} | {it['title']} | `{it['assignee']}` | `{it['labels']}` | [{it['title']}]({it['url']}) |\n")
    
    print(f"[COMPLETE] Created all {len(created_issues)} issues successfully!")
    print(f"Summary saved to {report_file}")

if __name__ == "__main__":
    main()
