// ==============================================================================
// RV32M Benchmark 03: Integer Factorial & Taylor Series Expansion
// Work Package: [WP-07][SW] (Issue #07)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// ==============================================================================

#include "telemetry.h"

// Computes exp(x) scaled by SCALE=10000 using Taylor Series:
// e^x ~ 1 + x + x^2/2! + x^3/3! + x^4/4! + ... + x^N/N!
#define SCALE 10000
#define TERMS 8

int main(void) {
    uint64_t start_cycles = get_cycles();

    int32_t x = 2; // Compute e^2 * 10000 ~ 73890
    int64_t sum = SCALE;
    int64_t term = SCALE;

    for (int n = 1; n <= TERMS; n++) {
        // term_n = term_{n-1} * x / n
        term = (term * x) / n;
        sum += term;
    }

    uint64_t end_cycles = get_cycles();
    uint32_t delta_cycles = (uint32_t)(end_cycles - start_cycles);

    set_display((uint32_t)sum);
    set_leds((uint32_t)term);

    return (int)delta_cycles;
}
