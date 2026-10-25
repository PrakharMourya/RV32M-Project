#!/usr/bin/env bash
# ==============================================================================
# RV32M-Core: Master Benchmark Compilation Script
# Work Package: [WP-08][BENCH]
# Group 22 — IIT Guwahati Advanced Computer Architecture
# Target: Compiles 5 workloads for both RV32I (software) and RV32IM (hardware)
# ==============================================================================

set -e

# Toolchain detection (riscv32-unknown-elf-gcc, riscv64-unknown-elf-gcc, or Vivado bundled)
if command -v riscv32-unknown-elf-gcc &> /dev/null; then
    CC=riscv32-unknown-elf-gcc
    OBJDUMP=riscv32-unknown-elf-objdump
    OBJCOPY=riscv32-unknown-elf-objcopy
elif command -v riscv64-unknown-elf-gcc &> /dev/null; then
    CC=riscv64-unknown-elf-gcc
    OBJDUMP=riscv64-unknown-elf-objdump
    OBJCOPY=riscv64-unknown-elf-objcopy
elif [ -f "D:/VIVADO/2025.2/gnu/riscv/nt/bin/riscv64-unknown-elf-gcc.exe" ]; then
    CC="D:/VIVADO/2025.2/gnu/riscv/nt/bin/riscv64-unknown-elf-gcc.exe"
    OBJDUMP="D:/VIVADO/2025.2/gnu/riscv/nt/bin/riscv64-unknown-elf-objdump.exe"
    OBJCOPY="D:/VIVADO/2025.2/gnu/riscv/nt/bin/riscv64-unknown-elf-objcopy.exe"
else
    echo "ERROR: RISC-V GCC toolchain not found!"
    exit 1
fi

CFLAGS="-O2 -nostartfiles -T sw/common/link.ld -I sw/common -Wall"
COMMON_SRC="sw/common/crt0.s"

WORKLOADS=(
    "01_matmul"
    "02_fir_filter"
    "03_taylor_series"
    "04_gcd_euclidean"
    "05_newton_raphson"
)

echo "=============================================================================="
echo "Compiling 5 Benchmarks with RV32I (Software) & RV32IM (Hardware Accelerated)"
echo "Toolchain: $CC"
echo "=============================================================================="

for WL in "${WORKLOADS[@]}"; do
    DIR="sw/workloads/$WL"
    SRC="$DIR/main.c"
    
    echo ">>> Building Benchmark: $WL"

    # 1. Software Emulation Mode (-march=rv32i -mabi=ilp32)
    $CC -march=rv32i -mabi=ilp32 $CFLAGS $COMMON_SRC $SRC -o "$DIR/${WL}_rv32i.elf"
    $OBJDUMP -d "$DIR/${WL}_rv32i.elf" > "$DIR/${WL}_rv32i.dump"
    $OBJCOPY -O verilog --verilog-data-width=4 "$DIR/${WL}_rv32i.elf" "$DIR/${WL}_rv32i.hex" 2>/dev/null || true

    # 2. Hardware Accelerated Mode (-march=rv32im -mabi=ilp32)
    $CC -march=rv32im -mabi=ilp32 $CFLAGS $COMMON_SRC $SRC -o "$DIR/${WL}_rv32im.elf"
    $OBJDUMP -d "$DIR/${WL}_rv32im.elf" > "$DIR/${WL}_rv32im.dump"
    $OBJCOPY -O verilog --verilog-data-width=4 "$DIR/${WL}_rv32im.elf" "$DIR/${WL}_rv32im.hex" 2>/dev/null || true

    echo "    -> Generated: ${WL}_rv32i.elf, ${WL}_rv32i.dump"
    echo "    -> Generated: ${WL}_rv32im.elf, ${WL}_rv32im.dump"
done

echo "=============================================================================="
echo "Benchmark Compilation Complete!"
echo "=============================================================================="
