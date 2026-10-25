#!/usr/bin/env python3
"""
RV32M-Core: ELF to Verilog Hex Memory Image Converter
Converts RISC-V ELF/Binary executable into a 32-bit word format for $readmemh.
Academic Standard: Group 22 — IIT Guwahati Advanced Computer Architecture
"""

import sys
import subprocess
import struct
import os

def elf_to_hex(elf_path, hex_path, objcopy_path="riscv64-unknown-elf-objcopy"):
    bin_path = elf_path.replace(".elf", ".bin")
    
    # 1. Convert ELF to raw binary
    cmd = [objcopy_path, "-O", "binary", elf_path, bin_path]
    subprocess.check_call(cmd)
    
    # 2. Read binary and write 32-bit words in hex
    with open(bin_path, "rb") as f_in, open(hex_path, "w") as f_out:
        data = f_in.read()
        
        # Pad to 4-byte boundary
        if len(data) % 4 != 0:
            data += b"\x00" * (4 - (len(data) % 4))
            
        words = struct.unpack(f"<{len(data) // 4}I", data)
        for w in words:
            f_out.write(f"{w:08x}\n")
            
    # Cleanup intermediate binary
    if os.path.exists(bin_path):
        os.remove(bin_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python elf2hex.py <input.elf> <output.hex> [objcopy_path]")
        sys.exit(1)
        
    elf_p = sys.argv[1]
    hex_p = sys.argv[2]
    objcopy_p = sys.argv[3] if len(sys.argv) > 3 else "riscv64-unknown-elf-objcopy"
    elf_to_hex(elf_p, hex_p, objcopy_p)
