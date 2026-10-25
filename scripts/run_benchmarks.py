#!/usr/bin/env python3
"""
==============================================================================
RV32M-Core: Master Benchmark Compilation & Profiling Suite
Work Package: [WP-08][BENCH] (Hardware vs. Software Comparative Profiling)
Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
==============================================================================
"""

import os
import sys
import subprocess
import re

GCC = r"D:/VIVADO/2025.2/gnu/riscv/nt/bin/riscv64-unknown-elf-gcc.exe"
OBJDUMP = r"D:/VIVADO/2025.2/gnu/riscv/nt/bin/riscv64-unknown-elf-objdump.exe"
OBJCOPY = r"D:/VIVADO/2025.2/gnu/riscv/nt/bin/riscv64-unknown-elf-objcopy.exe"
IVERILOG = r"C:/iverilog/bin/iverilog.exe"
VVP = r"C:/iverilog/bin/vvp.exe"

WORKLOADS = [
    {
        "id": "01_matmul",
        "name": "Dense Matrix Multiplication (4x4)",
        "desc": "Heavy integer multiplication and accumulation",
        "primary_m": "MUL"
    },
    {
        "id": "02_fir_filter",
        "name": "1D Digital FIR Filter (8-tap, 32 samples)",
        "desc": "Q15 fixed-point convolution and 64-bit accumulation",
        "primary_m": "MUL, MULH"
    },
    {
        "id": "03_taylor_series",
        "name": "Taylor Series Exp(2) & Factorials",
        "desc": "Alternating multiplication and division progression",
        "primary_m": "MUL, DIV"
    },
    {
        "id": "04_gcd_euclidean",
        "name": "Euclidean Greatest Common Divisor (8 pairs)",
        "desc": "Iterative modulo remainder calculation",
        "primary_m": "REM / REMU"
    },
    {
        "id": "05_newton_raphson",
        "name": "Newton-Raphson Integer Square Root (8 values)",
        "desc": "Iterative quotient approximation and division",
        "primary_m": "DIV / DIVU"
    }
]

def compile_benchmark(wl_id, march, output_elf, output_dump, output_hex):
    src = f"sw/workloads/{wl_id}/main.c"
    crt0 = "sw/common/crt0.s"
    ld = "sw/common/link.ld"
    inc = "sw/common"
    
    cmd_compile = [
        GCC,
        f"-march={march}",
        "-mabi=ilp32",
        "-O2",
        "-nostartfiles",
        f"-T{ld}",
        f"-I{inc}",
        "-Wall",
        crt0,
        src,
        "-o", output_elf
    ]
    subprocess.check_call(cmd_compile)
    
    # Generate objdump
    with open(output_dump, "w") as f_dump:
        subprocess.check_call([OBJDUMP, "-d", output_elf], stdout=f_dump)
        
    # Generate hex
    cmd_elf2hex = [
        sys.executable,
        "scripts/elf2hex.py",
        output_elf,
        output_hex,
        OBJCOPY
    ]
    subprocess.check_call(cmd_elf2hex)

def run_simulation(sim_vvp, hex_file):
    cmd_vvp = [VVP, sim_vvp, f"+HEXFILE={hex_file}"]
    result = subprocess.run(cmd_vvp, capture_output=True, text=True)
    out = result.stdout
    
    cycles = 0
    instructions = 0
    stalls = 0
    ret_val = 0
    
    for line in out.splitlines():
        if "CYCLES:" in line:
            m = re.search(r"CYCLES:\s+(\d+)", line)
            if m: cycles = int(m.group(1))
        elif "INSTRUCTIONS:" in line:
            m = re.search(r"INSTRUCTIONS:\s+(\d+)", line)
            if m: instructions = int(m.group(1))
        elif "DIV_STALLS:" in line:
            m = re.search(r"DIV_STALLS:\s+(\d+)", line)
            if m: stalls = int(m.group(1))
        elif "RETURN_A0:" in line:
            m = re.search(r"RETURN_A0:\s+0x[0-9a-fA-F]+\s+\((\d+)\)", line)
            if m: ret_val = int(m.group(1))
            
    return {
        "cycles": cycles,
        "instructions": instructions,
        "stalls": stalls,
        "kernel_cycles": ret_val,
        "cpi": cycles / instructions if instructions > 0 else 0.0,
        "output": out
    }

def main():
    print("==============================================================================")
    print("RV32M-Core: Compiling Benchmark Testbench Simulator")
    print("==============================================================================")
    
    sim_vvp = "sim_bench_runner.vvp"
    cmd_iverilog = [
        IVERILOG,
        "-g2012",
        "-Irtl/include",
        "-Irtl/core",
        "-Irtl/soc",
        "-o", sim_vvp,
        "rtl/core/multiplier_rv32m.v",
        "rtl/core/divider_rv32m.v",
        "rtl/core/alu_rv32m.v",
        "rtl/core/control_decoder.v",
        "rtl/core/id_ex_stage.v",
        "rtl/core/if_stage.v",
        "rtl/core/hazard_unit.v",
        "rtl/core/wb_stage.v",
        "rtl/core/riscv_core.v",
        "rtl/core/rv32m_core.v",
        "rtl/soc/ram_2p.v",
        "rtl/soc/cycle_counter.v",
        "rtl/soc/seven_seg_driver.v",
        "rtl/soc/uart_tx.v",
        "rtl/soc/rv32m_soc_top.v",
        "tb/tb_benchmark_runner.v"
    ]
    subprocess.check_call(cmd_iverilog)
    print("-> Testbench simulator compiled successfully!")
    
    results = []
    
    for wl in WORKLOADS:
        w_id = wl["id"]
        dir_path = f"sw/workloads/{w_id}"
        
        print(f"\n==============================================================================")
        print(f"Profiling Workload: {wl['name']} [{w_id}]")
        print(f"==============================================================================")
        
        # 1. RV32I Software Emulation
        elf_i = f"{dir_path}/{w_id}_rv32i.elf"
        dump_i = f"{dir_path}/{w_id}_rv32i.dump"
        hex_i = f"{dir_path}/{w_id}_rv32i.hex"
        compile_benchmark(w_id, "rv32i", elf_i, dump_i, hex_i)
        res_i = run_simulation(sim_vvp, hex_i)
        print(f"  [RV32I  Soft] Cycles: {res_i['cycles']}, Instr: {res_i['instructions']}, Kernel: {res_i['kernel_cycles']}")
        
        # 2. RV32IM Hardware Acceleration
        elf_im = f"{dir_path}/{w_id}_rv32im.elf"
        dump_im = f"{dir_path}/{w_id}_rv32im.dump"
        hex_im = f"{dir_path}/{w_id}_rv32im.hex"
        compile_benchmark(w_id, "rv32im", elf_im, dump_im, hex_im)
        res_im = run_simulation(sim_vvp, hex_im)
        print(f"  [RV32IM Hard] Cycles: {res_im['cycles']}, Instr: {res_im['instructions']}, Stalls: {res_im['stalls']}, Kernel: {res_im['kernel_cycles']}")
        
        # Calculate speedups
        speedup_total = res_i["cycles"] / res_im["cycles"] if res_im["cycles"] > 0 else 1.0
        speedup_kernel = res_i["kernel_cycles"] / res_im["kernel_cycles"] if res_im["kernel_cycles"] > 0 else 1.0
        instr_reduc = res_i["instructions"] / res_im["instructions"] if res_im["instructions"] > 0 else 1.0
        
        print(f"  -> Total Core Speedup:   {speedup_total:.2f}x")
        print(f"  -> Kernel Workload Speedup: {speedup_kernel:.2f}x")
        print(f"  -> Instruction Reduction:   {instr_reduc:.2f}x")
        
        results.append({
            "meta": wl,
            "res_i": res_i,
            "res_im": res_im,
            "speedup_total": speedup_total,
            "speedup_kernel": speedup_kernel,
            "instr_reduc": instr_reduc
        })
        
    # Generate Markdown Table Report
    report_path = "docs/Benchmark_Results.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# RV32M-Core: Hardware vs. Software Comparative Profiling Report\n\n")
        f.write("**Work Package:** [WP-08][BENCH] Comparative Profiling Engine  \n")
        f.write("**Academic Standard:** Group 22 — IIT Guwahati Advanced Computer Architecture & FPGA System Design  \n")
        f.write("**Target FPGA:** AMD Xilinx Artix-7 (XC7A100T-1CSG324C / Basys 3 & Nexys A7)  \n")
        f.write("**Toolchain:** GCC 13.4.0 (riscv64-unknown-elf-gcc), Icarus Verilog 12+, AMD Vivado 2025.2  \n\n")
        f.write("---\n\n")
        f.write("## 1. Executive Summary & Hardware Acceleration Highlights\n\n")
        f.write("The RV32M hardware execution unit extends the baseline RV32I pipeline with single-cycle DSP-assisted multiplication and a 32-step non-restoring divider FSM. ")
        f.write("In standard RV32I architectures, integer multiplication and division rely entirely on GCC software emulation subroutines (`__mulsi3`, `__divsi3`, `__udivsi3`, `__modsi3`, `__umodsi3`), which incur severe branch overheads, loop counters, and hundreds of execution cycles.\n\n")
        f.write("Across five industry-standard computational workloads, the integrated RV32M hardware execution coprocessor achieves dramatic throughput improvements:\n\n")
        
        # Summary table
        f.write("| Workload ID | Benchmark Application | Target Operations | RV32I Cycles (Soft) | RV32IM Cycles (Hard) | Core Speedup | Kernel Speedup | Instr Reduction |\n")
        f.write("|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|\n")
        for r in results:
            m = r["meta"]
            ri = r["res_i"]
            rim = r["res_im"]
            f.write(f"| **{m['id']}** | {m['name']} | `{m['primary_m']}` | {ri['cycles']:,} | {rim['cycles']:,} | **{r['speedup_total']:.2f}×** | **{r['speedup_kernel']:.2f}×** | **{r['instr_reduc']:.2f}×** |\n")
            
        # Geometric mean / average
        avg_core_speedup = sum(r["speedup_total"] for r in results) / len(results)
        avg_kernel_speedup = sum(r["speedup_kernel"] for r in results) / len(results)
        f.write(f"\n> [!NOTE]\n> **Mean Core Speedup:** {avg_core_speedup:.2f}× across entire execution runs; **Mean Kernel Speedup:** {avg_kernel_speedup:.2f}× for computation loops.\n\n")
        
        f.write("---\n\n")
        f.write("## 2. Granular Microarchitectural Profiling Breakdown\n\n")
        for r in results:
            m = r["meta"]
            ri = r["res_i"]
            rim = r["res_im"]
            f.write(f"### 2.{results.index(r)+1} {m['name']} (`{m['id']}`)\n\n")
            f.write(f"- **Description:** {m['desc']}\n")
            f.write(f"- **Primary ISA Extension:** `{m['primary_m']}`\n\n")
            f.write("| Microarchitectural Metric | Baseline RV32I (Soft Emulation) | RV32IM (Hardware Accelerated) | Improvement Factor |\n")
            f.write("|:---|:---:|:---:|:---:|\n")
            f.write(f"| Total Program Cycles | {ri['cycles']:,} | {rim['cycles']:,} | **{r['speedup_total']:.2f}× faster** |\n")
            f.write(f"| Retired Instructions | {ri['instructions']:,} | {rim['instructions']:,} | **{r['instr_reduc']:.2f}× fewer instructions** |\n")
            f.write(f"| Divider Pipeline Stalls | {ri['stalls']} | {rim['stalls']} | {rim['stalls']} stall cycles |\n")
            f.write(f"| Average CPI (Cycles / Instr) | {ri['cpi']:.2f} | {rim['cpi']:.2f} | — |\n")
            f.write(f"| Kernel Execution Cycles | {ri['kernel_cycles']:,} | {rim['kernel_cycles']:,} | **{r['speedup_kernel']:.2f}× kernel speedup** |\n\n")

    print(f"\n==============================================================================")
    print(f"Profiling Complete! Report written to {report_path}")
    print(f"==============================================================================")

if __name__ == "__main__":
    main()
