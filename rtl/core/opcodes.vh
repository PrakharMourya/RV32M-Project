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

// -----------------------------------------------------------------------------
// RV32M Standard Extension Definitions
// -----------------------------------------------------------------------------
`define FUNCT7_M_EXTENSION 7'b0000001  // funct7 distinguishing M-extension from base ALU

// Multiplier funct3 Field Codes (RV32M)
`define FUNCT3_MUL         3'b000  // MUL:    Signed x Signed, lower 32 bits
`define FUNCT3_MULH        3'b001  // MULH:   Signed x Signed, upper 32 bits
`define FUNCT3_MULHSU      3'b010  // MULHSU: Signed x Unsigned, upper 32 bits
`define FUNCT3_MULHU       3'b011  // MULHU:  Unsigned x Unsigned, upper 32 bits

// Divider funct3 Field Codes (RV32M)
`define FUNCT3_DIV         3'b100  // DIV:    Signed divide quotient
`define FUNCT3_DIVU        3'b101  // DIVU:   Unsigned divide quotient
`define FUNCT3_REM         3'b110  // REM:    Signed divide remainder
`define FUNCT3_REMU        3'b111  // REMU:   Unsigned divide remainder

// -----------------------------------------------------------------------------
// Base RV32I ALU funct3 Field Codes
// -----------------------------------------------------------------------------
`define FUNCT3_ADD_SUB     3'b000  // ADD (funct7=0) / SUB (funct7=0x20)
`define FUNCT3_SLL         3'b001  // Shift Left Logical
`define FUNCT3_SLT         3'b010  // Set Less Than (Signed)
`define FUNCT3_SLTU        3'b011  // Set Less Than Unsigned
`define FUNCT3_XOR         3'b100  // Bitwise Exclusive OR
`define FUNCT3_SRL_SRA     3'b101  // Shift Right Logical (funct7=0) / Arithmetic (funct7=0x20)
`define FUNCT3_OR          3'b110  // Bitwise OR
`define FUNCT3_AND         3'b111  // Bitwise AND

// -----------------------------------------------------------------------------
// Branch Condition funct3 Field Codes
// -----------------------------------------------------------------------------
`define FUNCT3_BEQ         3'b000  // Branch if Equal
`define FUNCT3_BNE         3'b001  // Branch if Not Equal
`define FUNCT3_BLT         3'b100  // Branch if Less Than (Signed)
`define FUNCT3_BGE         3'b101  // Branch if Greater Than or Equal (Signed)
`define FUNCT3_BLTU        3'b110  // Branch if Less Than Unsigned
`define FUNCT3_BGEU        3'b111  // Branch if Greater Than or Equal Unsigned

// -----------------------------------------------------------------------------
// Load Instruction funct3 Field Codes
// -----------------------------------------------------------------------------
`define FUNCT3_LB          3'b000  // Load Byte (Signed)
`define FUNCT3_LH          3'b001  // Load Halfword (Signed)
`define FUNCT3_LW          3'b010  // Load Word
`define FUNCT3_LBU         3'b100  // Load Byte Unsigned
`define FUNCT3_LHU         3'b101  // Load Halfword Unsigned

// -----------------------------------------------------------------------------
// Store Instruction funct3 Field Codes
// -----------------------------------------------------------------------------
`define FUNCT3_SB          3'b000  // Store Byte
`define FUNCT3_SH          3'b001  // Store Halfword
`define FUNCT3_SW          3'b010  // Store Word

// -----------------------------------------------------------------------------
// Internal ALU Operation Control Codes (4-bit)
// -----------------------------------------------------------------------------
`define ALU_CTRL_ADD       4'b0000 // Addition: A + B
`define ALU_CTRL_SUB       4'b0001 // Subtraction: A - B
`define ALU_CTRL_SLL       4'b0010 // Shift Left Logical: A << B[4:0]
`define ALU_CTRL_SLT       4'b0011 // Set Less Than Signed: (signed(A) < signed(B)) ? 1 : 0
`define ALU_CTRL_SLTU      4'b0100 // Set Less Than Unsigned: (A < B) ? 1 : 0
`define ALU_CTRL_XOR       4'b0101 // Bitwise XOR: A ^ B
`define ALU_CTRL_SRL       4'b0110 // Shift Right Logical: A >> B[4:0]
`define ALU_CTRL_SRA       4'b0111 // Shift Right Arithmetic: signed(A) >>> B[4:0]
`define ALU_CTRL_OR        4'b1000 // Bitwise OR: A | B
`define ALU_CTRL_AND       4'b1001 // Bitwise AND: A & B
`define ALU_CTRL_PASS_B    4'b1010 // Pass Operand B (used for LUI: imm)

`endif // OPCODES_VH
