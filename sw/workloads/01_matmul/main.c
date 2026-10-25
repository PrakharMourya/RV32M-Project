// ==============================================================================
// RV32M Benchmark 01: Dense Matrix Multiplication (4x4 & 8x8)
// Work Package: [WP-07][SW] (Issue #07)
// Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
// ==============================================================================

#include "telemetry.h"

#define N 4

static const int32_t mat_a[N][N] = {
    {  1,  2,  3,  4 },
    {  5,  6,  7,  8 },
    {  9, 10, 11, 12 },
    { 13, 14, 15, 16 }
};

static const int32_t mat_b[N][N] = {
    { 16, 15, 14, 13 },
    { 12, 11, 10,  9 },
    {  8,  7,  6,  5 },
    {  4,  3,  2,  1 }
};

static int32_t mat_c[N][N];

int main(void) {
    uint64_t start_cycles = get_cycles();
    uint64_t start_instr  = get_instret();

    // Perform dense matrix multiplication: C_ij = sum_k (A_ik * B_kj)
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int32_t sum = 0;
            for (int k = 0; k < N; k++) {
                sum += mat_a[i][k] * mat_b[k][j];
            }
            mat_c[i][j] = sum;
        }
    }

    uint64_t end_cycles = get_cycles();
    uint64_t end_instr  = get_instret();

    uint32_t delta_cycles = (uint32_t)(end_cycles - start_cycles);
    uint32_t check_val = (uint32_t)mat_c[0][0]; // 1*16 + 2*12 + 3*8 + 4*4 = 80

    set_display(check_val);
    set_leds((uint32_t)mat_c[N-1][N-1]);

    return (int)delta_cycles;
}
