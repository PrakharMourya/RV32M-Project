// ==============================================================================
// RV32M Benchmark 02: 1D Digital Finite Impulse Response (FIR) Filter
// Work Package: [WP-07][SW] (Issue #07)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// ==============================================================================

#include "telemetry.h"

#define NUM_SAMPLES 32
#define NUM_TAPS    8

// Q15 fixed-point FIR filter coefficients
static const int32_t coeffs[NUM_TAPS] = {
    327, 1638, 4915, 9502, 9502, 4915, 1638, 327
};

// Input sample signal
static const int32_t input_signal[NUM_SAMPLES] = {
    1000, 1500, 2000, 2500, 3000, 2500, 2000, 1500,
    1000,  500,    0, -500,-1000,-1500,-2000,-2500,
   -3000,-2500,-2000,-1500,-1000, -500,    0,  500,
    1000, 1500, 2000, 2500, 3000, 2500, 2000, 1500
};

static int32_t output_signal[NUM_SAMPLES];

int main(void) {
    uint64_t start_cycles = get_cycles();

    // 1D Digital Convolution: y[n] = sum_k (b_k * x[n-k]) >> 15
    for (int n = 0; n < NUM_SAMPLES; n++) {
        int64_t acc = 0;
        for (int k = 0; k < NUM_TAPS; k++) {
            if (n >= k) {
                acc += (int64_t)coeffs[k] * input_signal[n - k];
            }
        }
        output_signal[n] = (int32_t)(acc >> 15);
    }

    uint64_t end_cycles = get_cycles();
    uint32_t delta_cycles = (uint32_t)(end_cycles - start_cycles);

    set_display((uint32_t)output_signal[NUM_SAMPLES - 1]);
    set_leds((uint32_t)output_signal[NUM_TAPS]);

    return (int)delta_cycles;
}
