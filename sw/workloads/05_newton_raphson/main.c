// ==============================================================================
// RV32M Benchmark 05: Fixed-Point Polynomial Root / Newton-Raphson Division
// Work Package: [WP-07][SW] (Issue #07)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// ==============================================================================

#include "telemetry.h"

// Computes square root using Newton-Raphson integer method:
// x_{n+1} = (x_n + S / x_n) / 2
// Runs repeated integer division and scaling over a batch of inputs

#define NUM_TESTS 8
static const uint32_t radicands[NUM_TESTS] = {
    144, 10000, 65536, 1234567, 100000000, 500000, 9999999, 2147483647
};

static uint32_t isqrt_newton(uint32_t val) {
    if (val == 0) return 0;
    uint32_t x = val;
    uint32_t y = (x + 1) / 2;
    while (y < x) {
        x = y;
        y = (x + val / x) / 2;
    }
    return x;
}

static uint32_t root_results[NUM_TESTS];

int main(void) {
    uint64_t start_cycles = get_cycles();

    uint32_t checksum = 0;
    for (int i = 0; i < NUM_TESTS; i++) {
        root_results[i] = isqrt_newton(radicands[i]);
        checksum += root_results[i];
    }

    uint64_t end_cycles = get_cycles();
    uint32_t delta_cycles = (uint32_t)(end_cycles - start_cycles);

    set_display(checksum);
    set_leds(root_results[0]); // isqrt(144) = 12

    return (int)delta_cycles;
}
