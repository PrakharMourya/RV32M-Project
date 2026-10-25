// ==============================================================================
// RV32M-Core: Master System Architecture & Telemetry Driver Header
// File: sw/common/telemetry.h
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// ==============================================================================

#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <stdint.h>

#define MMIO_CYCLE_LOW   (*(volatile uint32_t*)0x80000000)
#define MMIO_CYCLE_HIGH  (*(volatile uint32_t*)0x80000004)
#define MMIO_INSTRET_LOW (*(volatile uint32_t*)0x80000008)
#define MMIO_INSTRET_HI  (*(volatile uint32_t*)0x8000000C)
#define MMIO_STALL_LOW   (*(volatile uint32_t*)0x80000010)
#define MMIO_STALL_HIGH  (*(volatile uint32_t*)0x80000014)

#define MMIO_7SEG        (*(volatile uint32_t*)0x80000020)
#define MMIO_LEDS        (*(volatile uint32_t*)0x80000024)

#define MMIO_UART_DATA   (*(volatile uint32_t*)0x80000030)
#define MMIO_UART_STATUS (*(volatile uint32_t*)0x80000034)

static inline uint64_t get_cycles(void) {
    uint32_t hi1 = MMIO_CYCLE_HIGH;
    uint32_t lo  = MMIO_CYCLE_LOW;
    uint32_t hi2 = MMIO_CYCLE_HIGH;
    if (hi1 != hi2) {
        lo = MMIO_CYCLE_LOW;
        hi1 = hi2;
    }
    return (((uint64_t)hi1) << 32) | lo;
}

static inline uint64_t get_instret(void) {
    uint32_t hi1 = MMIO_INSTRET_HI;
    uint32_t lo  = MMIO_INSTRET_LOW;
    uint32_t hi2 = MMIO_INSTRET_HI;
    if (hi1 != hi2) {
        lo = MMIO_INSTRET_LOW;
        hi1 = hi2;
    }
    return (((uint64_t)hi1) << 32) | lo;
}

static inline uint64_t get_stalls(void) {
    uint32_t hi1 = MMIO_STALL_HIGH;
    uint32_t lo  = MMIO_STALL_LOW;
    uint32_t hi2 = MMIO_STALL_HIGH;
    if (hi1 != hi2) {
        lo = MMIO_STALL_LOW;
        hi1 = hi2;
    }
    return (((uint64_t)hi1) << 32) | lo;
}

static inline void set_display(uint32_t val) {
    MMIO_7SEG = val;
}

static inline void set_leds(uint32_t val) {
    MMIO_LEDS = val;
}

static inline void uart_putc(char c) {
    // Wait for tx_ready (bit 0)
    while ((MMIO_UART_STATUS & 0x1) == 0);
    MMIO_UART_DATA = (uint32_t)c;
}

static inline void uart_puts(const char* s) {
    while (*s) {
        uart_putc(*s++);
    }
}

#endif // TELEMETRY_H
