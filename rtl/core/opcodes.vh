// ==============================================================================
// AutoVision-RISC-V: RV32IM Standard Opcode and Funct Definitions
// Standard: RISC-V Unprivileged ISA V20191213 (RV32IM)
// Target FPGA: AMD Xilinx Artix-7 XC7A100T-1CSG324C
// Academic Standard: IIT Guwahati Advanced Computer Architecture (10/10 Target)
// ==============================================================================

`ifndef OPCODES_VH
`define OPCODES_VH

// -----------------------------------------------------------------------------
// Base RV32I Major Opcodes (7-bit)
// -----------------------------------------------------------------------------
`define OPCODE_R_TYPE      7'b0110011  // Reg-Reg ALU & RV32M instructions
`define OPCODE_I_TYPE      7'b0010011  // Immediate ALU (ADDI, SLTI, etc.)
`define OPCODE_LOAD        7'b0000011  // Load instructions (LB, LH, LW, LBU, LHU)
`define OPCODE_STORE       7'b0100011  // Store instructions (SB, SH, SW)
`define OPCODE_BRANCH      7'b1100011  // Conditional Branch (BEQ, BNE, BLT, BGE, BLTU, BGEU)
`define OPCODE_JAL         7'b1101111  // Jump and Link (Unconditional Jump)
`define OPCODE_JALR        7'b1100111  // Jump and Link Register (Indirect Jump)
`define OPCODE_LUI         7'b0110111  // Load Upper Immediate
`define OPCODE_AUIPC       7'b0010111  // Add Upper Immediate to PC
`define OPCODE_SYSTEM      7'b1110011  // System instructions (ECALL, EBREAK, CSR)
`define OPCODE_FENCE       7'b0001111  // Memory ordering fence

`endif // OPCODES_VH
