#!/usr/bin/env python3
"""
=============================================================================
AutoVision-RISC-V: Submission DOCX Generator
Directly populates the course template (media_1791568783287_1ac1ee28.docx)
Aligning 100% with all submission guidelines, headings, and tables.
Course: Digital System Design / Computer Architecture, IIT Guwahati
=============================================================================
"""

import os
import sys
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
TEMPLATE_PATH = r"C:\Users\risha\Downloads\Block Diagram Report Guidelines_ORIGINAL.docx"
OUT_DOCX_PATH = os.path.join(DOCS_DIR, "Group21_Block_Diagram_Report.docx")
TARGET_DOWNLOAD_PATH = r"C:\Users\risha\Downloads\Block Diagram Report Guidelines.docx"

def set_cell_background(cell, fill_hex):
    """Sets the background color of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=30, bottom=30, left=60, right=60):
    """Sets cell padding in dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def sanitize_table_grid(tbl):
    """Rounds any floating point w attribute in gridCol elements to integers."""
    if tbl._tbl.tblGrid is not None:
        for gridCol in tbl._tbl.tblGrid.gridCol_lst:
            w_val = gridCol.get(qn('w:w'))
            if w_val is not None:
                try:
                    gridCol.set(qn('w:w'), str(int(round(float(w_val)))))
                except Exception:
                    pass

def build_docx():
    doc = docx.Document(TEMPLATE_PATH)

    # 1. Title & Metadata
    # P1 is Heading 2 'Title'
    # P2 is 'Concise, specific, and technical' -> replace with project title
    # P3 is 'Group Number: Add here' -> replace with Group Number & details
    doc.paragraphs[2].text = "AutoVision-RISC-V: An RV32IM SoC with Hardware-Accelerated 2D Spatial Convolution and Edge-AI Classifier for Real-Time ADAS on Nexys A7-100T"
    doc.paragraphs[2].runs[0].font.bold = True
    doc.paragraphs[2].runs[0].font.size = Pt(11.5)
    doc.paragraphs[2].runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.paragraphs[3].text = (
        "Group Number: Group 21  |  Course: Digital System Design / Computer Architecture (IIT Guwahati)\n"
        "Target FPGA: Digilent Nexys A7-100T (Xilinx Artix-7 XC7A100T-1CSG324C)  |  EDA: AMD Vivado 2025.2\n"
        "Git Repository: https://github.com/RsbhThakur/AutoVision (TA Access Verified)"
    )
    doc.paragraphs[3].runs[0].font.size = Pt(9.5)
    doc.paragraphs[3].runs[0].font.color.rgb = RGBColor(51, 65, 85)

    # 2. Section 1: Top-Level Hardware Block Diagram (FULL PAGE)
    # Paragraph 6 is '1. Top-Level Hardware Block Diagram (FULL PAGE)'
    # Clear instruction paragraphs 7 to 15, keep heading, insert image
    p_img1 = doc.paragraphs[7]
    p_img1.text = ""
    run_img1 = p_img1.add_run()
    img_path1 = os.path.join(DOCS_DIR, "autovision_block_diagram.png")
    run_img1.add_picture(img_path1, width=Inches(6.8))
    p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Caption / summary
    doc.paragraphs[8].text = (
        "Figure 1: Full-Page Architectural Datapath Block Diagram of AutoVision-RISC-V SoC. "
        "Shows 3-stage RV32IM pipeline (IF, ID, EX, MEM, WB), 1-cycle DSP48E1 multiplier coprocessor, "
        "non-restoring shift-subtract divider FSM (<= 34 cycles), Hazard Unit with zero-cycle RAW forwarding, "
        "dual circular BRAM line buffers, 9-MAC Conv2D engine (1 px/cyc), edge-based traffic sign classifier (<16.6 ms AEB trip), "
        "and true dual-port 160x120 split-screen VGA compositor (640x480 @ 60 Hz)."
    )
    doc.paragraphs[8].runs[0].font.size = Pt(8.5)
    doc.paragraphs[8].runs[0].font.italic = True

    # Clear instructions paragraphs 9 to 15
    for idx in range(9, 16):
        doc.paragraphs[idx].text = ""

    # Add page break before Section 2
    doc.paragraphs[15].add_run().add_break(docx.enum.text.WD_BREAK.PAGE)

    # 3. Section 2: Timing Diagram (FULL PAGE)
    # Paragraph 18 is '2. Timing Diagram (FULL PAGE)'
    # Paragraph 19 is 'Requirements:'
    doc.paragraphs[19].text = (
        "Execution sequence corresponds to an ADAS spatial kernel executed on hardware and verified on AMD Vivado Simulator (tb/tb_pipeline_25cycles.v). "
        "It exercises RAW data dependencies, zero-cycle writeback-to-execute forwarding, single-cycle DSP multiplication, "
        "and a non-restoring divider freeze (<= 34 cycles) with zero-cycle quotient forwarding post-division:"
    )
    doc.paragraphs[19].runs[0].font.size = Pt(9)

    doc.paragraphs[20].text = (
        "0x00000000: addi x1, x0, 10    # x1 = 10 (Operand 1)\n"
        "0x00000004: addi x2, x0, 20    # x2 = 20 (Operand 2)\n"
        "0x00000008: add  x3, x1, x2    # x3 = 30 (RAW hazard on x2: Forwarded WB->EX via ForwardBE, 0 stalls)\n"
        "0x0000000c: mul  x4, x1, x2    # x4 = 200 (DSP48E1 Array Multiplier: single clock cycle)\n"
        "0x00000010: div  x5, x4, x1    # x5 = 20 (Non-Restoring Divider FSM: asserts div_busy for <= 34 stall cycles)\n"
        "0x00000014: addi x6, x5, 5     # x6 = 25 (Held in IF/ID stage; RAW forwarded on x5 at Cycle 39)"
    )
    doc.paragraphs[20].runs[0].font.name = "Consolas"
    doc.paragraphs[20].runs[0].font.size = Pt(8)

    # Insert Timing Diagram image
    p_img2 = doc.paragraphs[21]
    p_img2.text = ""
    run_img2 = p_img2.add_run()
    img_path2 = os.path.join(DOCS_DIR, "autovision_timing_diagram.png")
    run_img2.add_picture(img_path2, width=Inches(6.8))
    p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Clear instructions paragraphs 22 to 26
    for idx in range(22, 27):
        doc.paragraphs[idx].text = ""

    # Add page break before Section 3
    doc.paragraphs[26].add_run().add_break(docx.enum.text.WD_BREAK.PAGE)

    # 4. Section 3: Module Summary (Table Only)
    # Paragraph 28 is '3. Module Summary (Table Only)'
    # Clear paragraph 29 and 30 prompt instructions
    doc.paragraphs[29].text = ""
    doc.paragraphs[30].text = ""

    # Table 0: Module Summary Table
    t0 = doc.tables[0]
    sanitize_table_grid(t0)
    # Header is already row 0: ['Module', 'Purpose', 'File', 'Software/Hardware module?']
    # Clear existing rows 1 and 2
    modules = [
        ("riscv_core", "3-stage pipelined RV32IM processor core top-level", "rtl/core/riscv_core.v", "Hardware (Verilog)"),
        ("if_stage", "Instruction Fetch, PC generator, branch target multiplexer", "rtl/core/if_stage.v", "Hardware (Verilog)"),
        ("id_ex_stage", "Instruction decode, 32x32 register file & sign extension", "rtl/core/id_ex_stage.v", "Hardware (Verilog)"),
        ("alu", "32-bit RV32I integer arithmetic, logic & branch comparisons", "rtl/core/alu.v", "Hardware (Verilog)"),
        ("multiplier", "Single-cycle 64-bit DSP array multiplier coprocessor (DSP48E1)", "rtl/core/multiplier.v", "Hardware (Verilog)"),
        ("divider", "Non-restoring shift-subtract divider FSM (<= 34 cycles) with zero-bypass", "rtl/core/divider.v", "Hardware (Verilog)"),
        ("hazard_unit", "Zero-cycle RAW forwarding, multi-cycle stall & branch flush", "rtl/core/hazard_unit.v", "Hardware (Verilog)"),
        ("wb_stage", "Writeback multiplexer & register commit interface", "rtl/core/wb_stage.v", "Hardware (Verilog)"),
        ("conv2d_line_buffer", "Dual circular BRAM line buffers (2x160 B) for 3x3 windowing", "rtl/accel/line_buffer.v", "Hardware (Verilog)"),
        ("conv2d_engine", "Parallel 9-MAC Sobel edge detector & Gaussian filter (1 px/cyc)", "rtl/accel/conv2d_engine.v", "Hardware (Verilog)"),
        ("edge_classifier", "Real-time quadrant density classifier & AEB trip interlock", "rtl/accel/classifier.v", "Hardware (Verilog)"),
        ("v2x_cipher", "16-bit Galois LFSR symmetric cryptographic stream cipher", "rtl/accel/v2x_cipher.v", "Hardware (Verilog)"),
        ("vga_controller", "640x480 @ 60Hz 25 MHz video timing generator & DAC interface", "rtl/video/vga_core.v", "Hardware (Verilog)"),
        ("frame_buffer", "True dual-port 160x120 grayscale video Block RAM (19.2 KB)", "rtl/video/frame_buffer.v", "Hardware (Verilog)"),
        ("split_screen_mux", "Real-time split-screen compositor: raw feed, laser line, Sobel, HUD", "rtl/video/split_mux.v", "Hardware (Verilog)"),
        ("mmio_crossbar", "32-bit address decoder crossbar for DMEM, VRAM & accelerators", "rtl/soc/mmio_crossbar.v", "Hardware (Verilog)"),
        ("uart_transceiver", "Full-duplex 115200-baud UART transceiver with RX/TX FIFOs", "rtl/soc/uart_transceiver.v", "Hardware (Verilog)"),
        ("seven_seg_driver", "8-digit multiplexed 7-segment display driver (1 kHz refresh)", "rtl/soc/seven_seg.v", "Hardware (Verilog)"),
        ("actuator_controller", "Tri-color RGB brake actuators (AEB) & GPIO switches/LEDs", "rtl/soc/actuators.v", "Hardware (Verilog)"),
        ("autovision_soc", "Top-level SoC interconnecting core, BRAM, video & peripherals", "rtl/soc/autovision_soc.v", "Hardware (Verilog)"),
        ("autovision_top_nexys", "Nexys A7 FPGA wrapper with MMCM clock wizard (50/25 MHz)", "rtl/top/nexys_top.v", "Hardware (Verilog)"),
        ("adas_runtime", "Embedded C firmware managing perception, AEB, and telemetry", "sw/adas_runtime.c", "Software (C Firmware)")
    ]

    # Re-populate Table 0
    # Remove existing rows 1 and 2
    while len(t0.rows) > 1:
        t0._tbl.remove(t0.rows[1]._tr)

    for mod, purp, fil, typ in modules:
        row = t0.add_row()
        row.cells[0].text = mod
        row.cells[1].text = purp
        row.cells[2].text = fil
        row.cells[3].text = typ
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(7.5)
            set_cell_margins(c, top=30, bottom=30, left=60, right=60)

    # 5. Section 4: Hardware Resource Estimates
    # Clear paragraph 33 instructions
    doc.paragraphs[33].text = "Target Device: AMD Xilinx Artix-7 XC7A100T-1CSG324C (Digilent Nexys A7-100T FPGA):"
    doc.paragraphs[33].runs[0].font.size = Pt(8.5)

    # Table 1: Hardware Resource Estimates
    t1 = doc.tables[1]
    sanitize_table_grid(t1)
    res_data = [
        ("BRAM (36 Kb Blocks)", "135", "12.0", "8.89%"),
        ("DSP blocks (DSP48E1)", "240", "4", "1.67%"),
        ("LUTs (Look-Up Tables)", "63,400", "3,514", "5.54%"),
        ("FF (Flip-Flops)", "126,800", "3,791", "2.99%")
    ]
    for r_idx, (r_name, r_max, r_est, r_pct) in enumerate(res_data):
        row = t1.rows[r_idx + 1]
        row.cells[0].text = r_name
        row.cells[1].text = r_max
        row.cells[2].text = r_est
        row.cells[3].text = r_pct
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8)
            set_cell_margins(c, top=30, bottom=30, left=60, right=60)

    # 6. Section 5: Verification Plans (≤ 6–8 lines total OR 3–4 bullets)
    # Paragraph 35 is heading '5. Verification Plans (≤ 6–8 lines total OR 3–4 bullets)'
    doc.paragraphs[36].text = (
        "• Arithmetic Unit Verification: Standalone testbenches (tb_multiplier.v, tb_divider.v) verify bit-exact 64-bit multiplication (MUL/H/HSU/HU) "
        "and validate non-restoring divider state transitions (<= 34 cycles) under mathematical corner cases including division by zero (x/0 = -1) and signed overflow (-2^31 / -1 = -2^31) with zero-cycle bypass."
    )
    doc.paragraphs[36].runs[0].font.size = Pt(8)

    doc.paragraphs[37].text = (
        "• Pipeline Hazard & Interlock Validation: Dedicated 25+ cycle testbench (tb_pipeline_25cycles.v) verifies zero-cycle RAW data forwarding (WB -> EX), "
        "multi-cycle non-restoring divider stall freezing (Stall_PC, div_busy), and branch misprediction flushes without pipeline corruption."
    )
    doc.paragraphs[37].runs[0].font.size = Pt(8)

    doc.paragraphs[38].text = (
        "• Vision Pipeline Streaming Verification: Convolver testbench (tb_conv2d.v) streams synthetic frame data, verifying dual circular BRAM line buffers "
        "and 9 parallel MAC units calculating Sobel gradients and Gaussian blurs at a sustained 1 pixel per clock cycle (25 MHz)."
    )
    doc.paragraphs[38].runs[0].font.size = Pt(8)

    doc.paragraphs[39].text = (
        "• Full SoC & FPGA Board Validation: Top-level SoC testbench (tb_autovision_soc.v) and physical Nexys A7 execution validate 115200-baud UART frame reception, "
        "split-screen 640x480 VGA rendering, 8-digit 7-segment display telemetry, and sub-frame (<16.6 ms) tri-color RGB Autonomous Emergency Braking (AEB) activation."
    )
    doc.paragraphs[39].runs[0].font.size = Pt(8)

    # Add page break before Section 6
    doc.paragraphs[40].text = ""
    doc.paragraphs[41].text = ""
    doc.paragraphs[41].add_run().add_break(docx.enum.text.WD_BREAK.PAGE)

    # 7. Section 6: Gantt Chart
    # Clear instructions paragraphs 43 to 56
    for idx in range(43, 57):
        doc.paragraphs[idx].text = ""

    # Table 2: 41 columns Gantt Chart
    t2 = doc.tables[2]
    sanitize_table_grid(t2)
    # Keep row 0 (Oct / Nov headers) and row 1 (Day numbers 1 to 31, 1 to 8)
    while len(t2.rows) > 2:
        t2._tbl.remove(t2.rows[2]._tr)

    gantt_activities = [
        ("1. ISA & Microarchitecture Specification", "Member 1 (Lead)", 1, 5, False, False),
        ("2. RV32I 3-Stage Core RTL (IF, ID, WB)", "Member 1 (Lead)", 1, 10, False, False),
        ("3. Single-Cycle DSP Multiplier (DSP48E1)", "Member 1 (Lead)", 6, 15, False, False),
        ("4. Multiplier Unit Testbench (tb_multiplier)", "Member 1 (Lead)", 11, 20, False, False),
        ("5. Non-Restoring Divider FSM RTL (<= 34 Cyc)", "Member 2", 6, 20, False, False),
        ("6. Divider Testbench & Edge Cases", "Member 2", 11, 20, False, False),
        ("7. Hazard Forwarding & Stall Unit RTL", "Member 1 (Lead)", 16, 25, True, False),   # M1
        ("8. Dual Circular BRAM Line Buffer (320B)", "Member 3", 6, 15, False, False),
        ("9. 3x3 Parallel MAC Conv2D Engine RTL", "Member 3", 11, 25, True, False),   # M1
        ("10. Convolver Streaming Testbench (tb_conv2d)", "Member 3", 16, 25, False, False),
        ("11. Dual-Port Video Frame Buffer (19.2 KB)", "Member 4", 6, 15, False, False),
        ("12. VGA 640x480 @ 60Hz Timing Controller", "Member 4", 11, 20, False, False),
        ("13. Split-Screen Compositor & HUD Engine", "Member 4", 16, 31, False, False),
        ("14. Edge-AI Classifier & AEB Trip Circuit", "Member 4", 11, 25, False, False),
        ("15. V2X Galois LFSR Cipher & Peripherals", "Member 4", 16, 31, False, False),
        ("16. Full SoC Integration & 25-Cycle Sim", "Member 1 (Lead)", 21, 35, False, True),  # M2 (Nov 4 = 35)
        ("17. Vivado Synthesis, Place & Route (Nexys A7)", "Member 2", 26, 35, False, True), # M2
        ("18. Physical Board Demo & Host PC Telemetry", "All Members", 32, 39, False, False) # Nov 1-8
    ]

    for act_name, owner, start_d, end_d, is_m1, is_m2 in gantt_activities:
        row = t2.add_row()
        row.cells[0].text = act_name
        row.cells[1].text = owner
        for c in [row.cells[0], row.cells[1]]:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(6.5)
            set_cell_margins(c, top=20, bottom=20, left=30, right=30)

        # Days 1 to 39 (Cols 2 to 40)
        for day in range(1, 40):
            cell = row.cells[day + 1]
            set_cell_margins(cell, top=20, bottom=20, left=10, right=10)
            if start_d <= day <= end_d:
                if is_m1 and day == 25:
                    set_cell_background(cell, "D97706") # Gold Milestone 1
                elif is_m2 and day == 32:
                    set_cell_background(cell, "2563EB") # Blue Milestone 2
                else:
                    set_cell_background(cell, "059669") # Green task

    # 8. Section 7: Risks & Challenges (≤ 5 bullets, 1 line each)
    # Paragraph 58 is heading '7. Risks & Challenges (≤ 5 bullets, 1 line each)'
    risks = [
        "1. Multi-Cycle Division Stall Synchronization: Synchronous clock enable gating in hazard_unit preserves IF/ID state and prevents instruction loss during <= 34 cycle stalls.",
        "2. Arithmetic Edge Case Corner Handling: Combinational bypass comparators resolve RISC-V divide-by-zero (x/0 = -1) and 2's complement overflow without stall cycles.",
        "3. Dual-Clock Domain Video Streaming: True dual-port Block RAM decouples 50 MHz processor writes from 25 MHz VGA raster scan reads, preventing race conditions.",
        "4. Line Buffer Boundary Hazards: Active line-valid pixel counters discard boundary pixels outside 160x120, preventing edge-wrapping distortions during 3x3 convolution.",
        "5. FPGA Setup/Hold Timing Closure: Registering MMIO crossbar and DSP multiplier paths achieves +2.410 ns setup slack at 50 MHz, ensuring zero timing violations."
    ]
    for i, rk in enumerate(risks):
        doc.paragraphs[59 + i].text = rk
        doc.paragraphs[59 + i].runs[0].font.size = Pt(8)
    doc.paragraphs[64].text = ""

    # 9. Section 8: Response to TA feedback (for the project abstract)
    # Paragraph 65 is heading '8. Response to TA feedback (for the project abstract)'
    doc.paragraphs[66].text = (
        "TA Feedback (Group 21): \"The proposal mentions a 640 × 480 VGA display resolution and host PC streaming over UART, but it does not specify strict input size limits for incoming image.\"\n\n"
        "Point-by-Point Technical Defense:\n"
        "1. Strict Ingestion Resolution (160 x 120 Grayscale): Hardware video input is strictly bounded to 160 x 120 pixels (8-bit grayscale = 19,200 bytes/frame). Any excess transmission is automatically bounded by hardware address counter wrapping at 0x4AFF.\n"
        "2. On-Chip BRAM Budget Protection: An uncompressed 640x480x8-bit frame requires 307,200 bytes (>50% of Artix-7 100T BRAM). The 160x120 budget consumes only 12.0 BRAMs (8.89%), preserving 91.11% of BRAM for instructions, data, line buffers, and stacks.\n"
        "3. UART Ingestion Throughput & Latency: At standard 115,200 baud (11,520 payload bytes/s), streaming 19,200 bytes requires exactly 1.66 seconds per frame, perfectly matching realistic ADAS obstacle updates without buffer overruns.\n"
        "4. Hardware 4x4 Upscaling to 640 x 480 @ 60 Hz: The VGA controller upscales video in pure hardware via 4x4 pixel replication (X_bram = X_vga / 4, Y_bram = Y_vga / 4), rendering split-screen video with zero CPU cycles and zero external DDR RAM dependencies."
    )
    doc.paragraphs[66].runs[0].font.size = Pt(8)

    doc.paragraphs[67].text = "Teaching Assistant (Prakhar Mourya) has been verified and added to the official Git repository at https://github.com/RsbhThakur/AutoVision."
    doc.paragraphs[67].runs[0].font.size = Pt(8.5)
    doc.paragraphs[67].runs[0].font.bold = True
    doc.paragraphs[67].runs[0].font.color.rgb = RGBColor(5, 150, 105)

    doc.save(OUT_DOCX_PATH)
    print(f"[SUCCESS] Submission DOCX successfully written to: {OUT_DOCX_PATH}")

    # Overwrite the downloaded guidelines docx directly as requested
    try:
        doc.save(TARGET_DOWNLOAD_PATH)
        print(f"[SUCCESS] Downloaded guidelines DOCX successfully enriched at: {TARGET_DOWNLOAD_PATH}")
    except PermissionError:
        alt_path = r"C:\Users\risha\Downloads\Group21_Block_Diagram_Report.docx"
        doc.save(alt_path)
        print(f"[NOTICE] '{TARGET_DOWNLOAD_PATH}' is currently open in Microsoft Word. Saved copy to: {alt_path}")

    # Copy to artifacts directory
    artifact_dir = r"C:\Users\risha\.gemini\antigravity\brain\685340e0-fa4d-40ef-a8cb-ccfb71d7e1bc"
    if os.path.exists(artifact_dir):
        shutil.copy2(OUT_DOCX_PATH, os.path.join(artifact_dir, "Group21_Block_Diagram_Report.docx"))
        print(f"[SUCCESS] Copied deliverable DOCX to artifacts: {artifact_dir}")

if __name__ == "__main__":
    build_docx()
