# ==============================================================================
# RV32M-Core: Master System Architecture & C Runtime Startup Code
# File: sw/common/crt0.s
# Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
# ==============================================================================

.section .text.init
.global _start
.type _start, @function

_start:
    # 1. Initialize all architectural registers to zero
    li x1,  0
    li x2,  0
    li x3,  0
    li x4,  0
    li x5,  0
    li x6,  0
    li x7,  0
    li x8,  0
    li x9,  0
    li x10, 0
    li x11, 0
    li x12, 0
    li x13, 0
    li x14, 0
    li x15, 0
    li x16, 0
    li x17, 0
    li x18, 0
    li x19, 0
    li x20, 0
    li x21, 0
    li x22, 0
    li x23, 0
    li x24, 0
    li x25, 0
    li x26, 0
    li x27, 0
    li x28, 0
    li x29, 0
    li x30, 0
    li x31, 0

    # 2. Set up stack pointer (top of 16 KB BRAM: 0x00003FFC)
    la sp, _stack_top

    # 3. Clear .bss section
    la a0, _sbss
    la a1, _ebss
    bge a0, a1, bss_cleared
bss_loop:
    sw zero, 0(a0)
    addi a0, a0, 4
    blt a0, a1, bss_loop
bss_cleared:

    # 4. Jump to main()
    call main

    # 5. Program complete: output return code to 7-segment display & LEDs
    # MMIO 0x8000_0020 (7-Seg), 0x8000_0024 (LEDs)
    li t0, 0x80000020
    sw a0, 0(t0)        # Write result to 7-Segment
    sw a0, 4(t0)        # Write result to LEDs

    # Halt / idle loop
_halt:
    j _halt

.size _start, . - _start
