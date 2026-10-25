/* ==============================================================================
 * RV32M-Core: Master System Architecture & Linker Script
 * File: sw/common/link.ld
 * Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
 * Target: 16 KB Unified Instruction/Data BRAM (0x0000_0000 - 0x0000_3FFF)
 * ============================================================================== */

OUTPUT_ARCH( "riscv" )
ENTRY(_start)

MEMORY
{
    RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 16K
}

SECTIONS
{
    .text : {
        . = ALIGN(4);
        *(.text.init)
        *(.text)
        *(.text.*)
        . = ALIGN(4);
        _etext = .;
    } > RAM

    .rodata : {
        . = ALIGN(4);
        *(.rodata)
        *(.rodata.*)
        *(.srodata)
        *(.srodata.*)
        . = ALIGN(4);
    } > RAM

    .data : {
        . = ALIGN(4);
        _sdata = .;
        *(.data)
        *(.data.*)
        *(.sdata)
        *(.sdata.*)
        . = ALIGN(4);
        _edata = .;
    } > RAM

    .bss : {
        . = ALIGN(4);
        _sbss = .;
        *(.sbss)
        *(.sbss.*)
        *(.bss)
        *(.bss.*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > RAM

    /* Stack allocated at top of 16 KB BRAM */
    . = ALIGN(16);
    _stack_top = ORIGIN(RAM) + LENGTH(RAM) - 4;
}
