// ==============================================================================
// RV32M Benchmark 04: Euclidean Integer GCD & Division
// Work Package: [WP-07][SW] (Issue #07)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// ==============================================================================

#include "telemetry.h"

#define NUM_PAIRS 8

static const uint32_t a_vals[NUM_PAIRS] = { 48, 1071, 123456, 98765432, 54321, 1000000, 270, 841 };
static const uint32_t b_vals[NUM_PAIRS] = { 18,  462,     789,   123456,   9876,   350000, 192,  29 };
static uint32_t gcd_results[NUM_PAIRS];

static uint32_t gcd(uint32_t a, uint32_t b) {
    while (b != 0) {
        uint32_t rem = a % b;
        a = b;
        b = rem;
    }
    return a;
}

int main(void) {
    uint64_t start_cycles = get_cycles();

    uint32_t checksum = 0;
    for (int i = 0; i < NUM_PAIRS; i++) {
        gcd_results[i] = gcd(a_vals[i], b_vals[i]);
        checksum += gcd_results[i];
    }

    uint64_t end_cycles = get_cycles();
    uint32_t delta_cycles = (uint32_t)(end_cycles - start_cycles);

    set_display(checksum);
    set_leds(gcd_results[0]);

    return (int)delta_cycles;
}
