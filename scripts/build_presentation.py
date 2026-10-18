import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
OUT_PPTX_REPO  = r"C:\Users\risha\OneDrive\Desktop\AutoVision\docs\AutoVision_Presentation.pptx"
OUT_PPTX_DL    = r"C:\Users\risha\Downloads\AutoVision_Presentation.pptx"
OUT_PPTX_BRAIN = r"C:\Users\risha\.gemini\antigravity\brain\685340e0-fa4d-40ef-a8cb-ccfb71d7e1bc\AutoVision_Presentation.pptx"

BLOCK_IMG  = r"C:\Users\risha\OneDrive\Desktop\AutoVision\docs\autovision_block_diagram.png"
TIMING_IMG = r"C:\Users\risha\OneDrive\Desktop\AutoVision\docs\autovision_timing_diagram.png"

# Color Palette (Dark Professional IIT/Engineering Theme)
C_BG_PAGE      = RGBColor(15, 23, 42)     # Slate 900
C_BG_CARD      = RGBColor(30, 41, 59)     # Slate 800
C_BG_CARD_ALT  = RGBColor(51, 65, 85)     # Slate 700
C_BORDER_CARD  = RGBColor(71, 85, 105)    # Slate 600
C_BORDER_ACC   = RGBColor(2, 132, 199)    # Sky 600

C_TEXT_WHITE   = RGBColor(255, 255, 255)  # White
C_TEXT_MUTED   = RGBColor(148, 163, 184)  # Slate 400
C_TEXT_DARK    = RGBColor(15, 23, 42)     # Slate 900

C_CYAN         = RGBColor(14, 165, 233)   # Sky 500
C_GREEN        = RGBColor(16, 185, 129)   # Emerald 500
C_AMBER        = RGBColor(245, 158, 11)   # Amber 500
C_RED          = RGBColor(239, 68, 68)    # Red 500
C_PURPLE       = RGBColor(168, 85, 247)   # Purple 500

def set_slide_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG_PAGE
    bg.line.fill.background()
    return bg

def add_header(slide, slide_num, title_text, subtitle_text):
    header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.35), Inches(12.133), Inches(0.95))
    header_box.fill.solid()
    header_box.fill.fore_color.rgb = C_BG_CARD
    header_box.line.color.rgb = C_BORDER_CARD
    header_box.line.width = Pt(1)

    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_top = Inches(0.12)
    tf.margin_right = Inches(0.25)
    tf.margin_bottom = Inches(0.08)

    p0 = tf.paragraphs[0]
    p0.text = f"SLIDE {slide_num} OF 7  |  {subtitle_text.upper()}"
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN

    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.size = Pt(21)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_WHITE

    tag_box = slide.shapes.add_textbox(Inches(9.6), Inches(0.4), Inches(3.0), Inches(0.85))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_top = Inches(0.06)
    p_tag1 = tf_tag.paragraphs[0]
    p_tag1.alignment = PP_ALIGN.RIGHT
    p_tag1.text = "GROUP 21  |  IIT GUWAHATI"
    p_tag1.font.size = Pt(11)
    p_tag1.font.bold = True
    p_tag1.font.color.rgb = C_AMBER

    p_tag2 = tf_tag.add_paragraph()
    p_tag2.alignment = PP_ALIGN.RIGHT
    p_tag2.text = "Digilent Nexys A7-100T (XC7A100T)"
    p_tag2.font.size = Pt(9.5)
    p_tag2.font.color.rgb = C_TEXT_MUTED

def add_card(slide, left, top, width, height, bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_rgb
    card.line.color.rgb = border_rgb
    card.line.width = Pt(border_pt)
    return card

def add_bullet(tf, bold_prefix, text_content, font_size=Pt(14), prefix_color=C_CYAN, text_color=C_TEXT_WHITE, space_after=Pt(6)):
    p = tf.add_paragraph()
    p.font.size = font_size
    p.space_after = space_after
    if bold_prefix:
        r_pre = p.add_run()
        r_pre.text = bold_prefix + " "
        r_pre.font.bold = True
        r_pre.font.color.rgb = prefix_color
        r_pre.font.size = font_size
    if text_content:
        r_txt = p.add_run()
        r_txt.text = text_content
        r_txt.font.bold = False
        r_txt.font.color.rgb = text_color
        r_txt.font.size = font_size
    return p

# -------------------------------------------------------------
# BUILD SLIDES
# -------------------------------------------------------------

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================
    # SLIDE 1: PROJECT OVERVIEW + SCOPE (1–1.5 min)
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    add_header(s1, 1, "Project Overview & Architectural Scope", "AutoVision-RISC-V System Specification")

    # Problem Statement Card
    c_prob = add_card(s1, Inches(0.6), Inches(1.42), Inches(12.133), Inches(0.85), bg_rgb=C_BG_CARD, border_rgb=C_RED, border_pt=1.5)
    tf_prob = c_prob.text_frame
    tf_prob.word_wrap = True
    tf_prob.margin_left = Inches(0.2)
    tf_prob.margin_top = Inches(0.08)
    p = tf_prob.paragraphs[0]
    p.text = "PROBLEM STATEMENT (1 LINE)"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p2 = tf_prob.add_paragraph()
    p2.text = "Real-time edge ADAS requires high-throughput spatial filtering and deterministic sub-frame (<16.6 ms) emergency braking that exceeds pure software execution on embedded edge CPU cores."
    p2.font.size = Pt(14.5)
    p2.font.bold = True
    p2.font.color.rgb = C_TEXT_WHITE

    # System Description Card
    c_desc = add_card(s1, Inches(0.6), Inches(2.38), Inches(12.133), Inches(1.0), bg_rgb=C_BG_CARD, border_rgb=C_CYAN, border_pt=1.5)
    tf_desc = c_desc.text_frame
    tf_desc.word_wrap = True
    tf_desc.margin_left = Inches(0.2)
    tf_desc.margin_top = Inches(0.08)
    p = tf_desc.paragraphs[0]
    p.text = "SYSTEM DESCRIPTION (2–3 LINES)"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p2 = tf_desc.add_paragraph()
    p2.text = "• AutoVision-RISC-V integrates a custom 3-stage RV32IM processor core with memory-mapped 2D spatial convolution accelerators and an Edge-AI geometric obstacle classifier."
    p2.font.size = Pt(13.5)
    p2.font.color.rgb = C_TEXT_WHITE
    p3 = tf_desc.add_paragraph()
    p3.text = "• Features real-time 640x480 split-screen VGA rendering, hardware Galois LFSR descrambling, and autonomous emergency braking (AEB) with visual telemetry on Nexys A7 FPGA."
    p3.font.size = Pt(13)
    p3.font.color.rgb = C_TEXT_MUTED

    # 3 Scope Columns: Commitment, Goal, Stretch
    # Commitment
    c_com = add_card(s1, Inches(0.6), Inches(3.5), Inches(3.9), Inches(3.6), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_com = c_com.text_frame
    tf_com.word_wrap = True
    tf_com.margin_left = Inches(0.2)
    tf_com.margin_top = Inches(0.12)
    p = tf_com.paragraphs[0]
    p.text = "COMMITMENT (MINIMUM SYSTEM)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(8)
    add_bullet(tf_com, "• 3-Stage RV32IM Core:", "Functional IF/ID, EX, and WB pipeline with 1-cycle DSP multiplier, <= 34-cycle non-restoring divider FSM, and RAW hazard forwarding unit.", font_size=Pt(13.5), prefix_color=C_GREEN, space_after=Pt(10))
    add_bullet(tf_com, "• 2D Conv2D Engine:", "Hardware 3x3 Sobel edge detector with dual circular BRAM line buffers (1 px/cyc) and split-screen 640x480 VGA display on Nexys A7.", font_size=Pt(13.5), prefix_color=C_GREEN, space_after=Pt(0))

    # Goal
    c_goal = add_card(s1, Inches(4.7), Inches(3.5), Inches(3.9), Inches(3.6), bg_rgb=C_BG_CARD, border_rgb=C_CYAN, border_pt=1.5)
    tf_goal = c_goal.text_frame
    tf_goal.word_wrap = True
    tf_goal.margin_left = Inches(0.2)
    tf_goal.margin_top = Inches(0.12)
    p = tf_goal.paragraphs[0]
    p.text = "GOAL (EXPECTED TARGET)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(8)
    add_bullet(tf_goal, "• Edge-AI Classifier:", "Real-time quadrant density sign classifier triggering physical AEB emergency brake trip on tri-color RGB LED.", font_size=Pt(13.5), prefix_color=C_CYAN, space_after=Pt(10))
    add_bullet(tf_goal, "• UART Video Pipeline:", "End-to-end 115200-baud frame streaming (160x120) with live 7-segment display and Host PC telemetry logging.", font_size=Pt(13.5), prefix_color=C_CYAN, space_after=Pt(0))

    # Stretch
    c_str = add_card(s1, Inches(8.8), Inches(3.5), Inches(3.933), Inches(3.6), bg_rgb=C_BG_CARD, border_rgb=C_PURPLE, border_pt=1.5)
    tf_str = c_str.text_frame
    tf_str.word_wrap = True
    tf_str.margin_left = Inches(0.2)
    tf_str.margin_top = Inches(0.12)
    p = tf_str.paragraphs[0]
    p.text = "STRETCH (ADVANCED TARGET)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_PURPLE
    p.space_after = Pt(8)
    add_bullet(tf_str, "• Hardware V2X Cipher:", "16-bit Galois LFSR symmetric cryptographic stream cipher descrambler with modular AES-128 secure key interface for encrypted camera feeds.", font_size=Pt(13.5), prefix_color=C_PURPLE, space_after=Pt(10))
    add_bullet(tf_str, "• Sub-Frame Latency:", "Zero-wait-state DMA streaming pipeline achieving complete frame classification in <16.6 ms (full 60 fps line rate).", font_size=Pt(13.5), prefix_color=C_PURPLE, space_after=Pt(0))

    # =========================================================
    # SLIDE 2: SYSTEM ARCHITECTURE (BLOCK DIAGRAM) (2 min)
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, 2, "System Architecture: Processor Pipeline & Coprocessors", "Hardware Microarchitecture & Interconnect")

    # Left: Block Diagram Image Box (Prominent and crisp!)
    c_diag = add_card(s2, Inches(0.6), Inches(1.42), Inches(8.2), Inches(5.7), bg_rgb=RGBColor(255, 255, 255), border_rgb=C_BORDER_CARD, border_pt=1)
    s2.shapes.add_picture(BLOCK_IMG, Inches(0.65), Inches(1.47), width=Inches(8.1), height=Inches(5.6))

    # Right Column: 3 Non-Overlapping Structured Cards (Total height: 5.7")
    # Card 1: Pipeline
    c_pipe = add_card(s2, Inches(9.0), Inches(1.42), Inches(3.733), Inches(1.78), bg_rgb=C_BG_CARD, border_rgb=C_CYAN, border_pt=1.5)
    tf_pipe = c_pipe.text_frame
    tf_pipe.word_wrap = True
    tf_pipe.margin_left = Inches(0.18)
    tf_pipe.margin_top = Inches(0.08)
    p = tf_pipe.paragraphs[0]
    p.text = "3-STAGE RV32IM PIPELINE"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    add_bullet(tf_pipe, "• Stage 1 (IF/ID):", "16 KB instruction BRAM, 32-reg file with same-cycle internal bypass.", font_size=Pt(12), prefix_color=C_CYAN, space_after=Pt(2))
    add_bullet(tf_pipe, "• Stage 2 (EX):", "32-bit ALU, 1-cyc DSP multiplier, <=34 cyc divider FSM, branch eval.", font_size=Pt(12), prefix_color=C_CYAN, space_after=Pt(2))
    add_bullet(tf_pipe, "• Stage 3 (MEM/WB):", "16 KB data RAM & 32-bit MMIO result select writeback.", font_size=Pt(12), prefix_color=C_CYAN, space_after=Pt(0))

    # Card 2: Custom Coprocessors & Hazards
    c_cop = add_card(s2, Inches(9.0), Inches(3.35), Inches(3.733), Inches(1.82), bg_rgb=C_BG_CARD, border_rgb=C_AMBER, border_pt=1.5)
    tf_cop = c_cop.text_frame
    tf_cop.word_wrap = True
    tf_cop.margin_left = Inches(0.18)
    tf_cop.margin_top = Inches(0.08)
    p = tf_cop.paragraphs[0]
    p.text = "ARITHMETIC & HAZARD UNIT"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    add_bullet(tf_cop, "• 1-Cycle Multiplier:", "Single-cycle DSP48E1 array computing bit-exact 64-bit MUL/MULH.", font_size=Pt(12), prefix_color=C_AMBER, space_after=Pt(2))
    add_bullet(tf_cop, "• Non-Restoring Divider:", "FSM (<= 34 cyc) with zero-cycle divide-by-zero bypass (x/0 = -1).", font_size=Pt(12), prefix_color=C_AMBER, space_after=Pt(2))
    add_bullet(tf_cop, "• Hazard Forwarding:", "Zero-penalty RAW bypass (WB->EX) and multi-cycle stall interlock.", font_size=Pt(12), prefix_color=C_AMBER, space_after=Pt(0))

    # Card 3: Vision Subsystem
    c_vis = add_card(s2, Inches(9.0), Inches(5.32), Inches(3.733), Inches(1.8), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_vis = c_vis.text_frame
    tf_vis.word_wrap = True
    tf_vis.margin_left = Inches(0.18)
    tf_vis.margin_top = Inches(0.08)
    p = tf_vis.paragraphs[0]
    p.text = "VISION ACCELERATORS & MMIO"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    add_bullet(tf_vis, "• Memory-Mapped Crossbar:", "32-bit decoder at 0x1000_0000 (VRAM), 0x2000_0100 (Conv), 0x2000_0200 (AI).", font_size=Pt(11.5), prefix_color=C_GREEN, space_after=Pt(2))
    add_bullet(tf_vis, "• 9-MAC Conv2D Streamer:", "Dual circular line buffers (320 B) computing Sobel edges at 1 px/cyc.", font_size=Pt(11.5), prefix_color=C_GREEN, space_after=Pt(2))
    add_bullet(tf_vis, "• Split-Screen VGA:", "Dual-port 19.2 KB VRAM scaled 4x4 to 640x480 @ 60 Hz with AEB trip.", font_size=Pt(11.5), prefix_color=C_GREEN, space_after=Pt(0))

    # =========================================================
    # SLIDE 3: TIMING DIAGRAM (2 min)
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, 3, "Cycle-Accurate Timing Diagram: Execution & Hazards", "ADAS Spatial Kernel Waveform (AMD Vivado Verified)")

    # Top Instruction Sequence Card
    c_seq = add_card(s3, Inches(0.6), Inches(1.42), Inches(12.133), Inches(0.75), bg_rgb=C_BG_CARD, border_rgb=C_CYAN, border_pt=1)
    tf_seq = c_seq.text_frame
    tf_seq.word_wrap = True
    tf_seq.margin_left = Inches(0.2)
    tf_seq.margin_top = Inches(0.06)
    p = tf_seq.paragraphs[0]
    p.text = "REAL 25+ CYCLE ADAS INSTRUCTION SEQUENCE (VERIFIED IN SIMULATION):"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p2 = tf_seq.add_paragraph()
    p2.text = "0x00: addi x1, 10  |  0x04: addi x2, 20  |  0x08: add x3, x1, x2 (RAW Forwarding, 0 stalls)  |  0x0C: mul x4, x1, x2 (1-Cyc DSP)  |  0x10: div x5, x4, x1 (<=34 Cyc FSM Stall)  |  0x14: addi x6, x5, 5"
    p2.font.size = Pt(12.5)
    p2.font.bold = True
    p2.font.color.rgb = C_TEXT_WHITE

    # Center: High-Res Timing Diagram Image Box
    c_timg = add_card(s3, Inches(0.6), Inches(2.28), Inches(12.133), Inches(3.6), bg_rgb=RGBColor(255, 255, 255), border_rgb=C_BORDER_CARD, border_pt=1)
    s3.shapes.add_picture(TIMING_IMG, Inches(0.65), Inches(2.32), width=Inches(12.033), height=Inches(3.52))

    # Bottom 3 Callout Cards
    c_t1 = add_card(s3, Inches(0.6), Inches(6.0), Inches(3.9), Inches(1.15), bg_rgb=C_BG_CARD, border_rgb=C_CYAN, border_pt=1.5)
    tf_t1 = c_t1.text_frame
    tf_t1.word_wrap = True
    tf_t1.margin_left = Inches(0.15)
    tf_t1.margin_top = Inches(0.08)
    p = tf_t1.paragraphs[0]
    p.text = "1. ZERO-CYCLE RAW FORWARDING"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p2 = tf_t1.add_paragraph()
    p2.text = "At Cycle 4, add depends on x2. Hazard Unit asserts ForwardBE = 2'b10, bypassing ResultW (20) directly into ALU with 0 stall cycles."
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_MUTED

    c_t2 = add_card(s3, Inches(4.7), Inches(6.0), Inches(3.9), Inches(1.15), bg_rgb=C_BG_CARD, border_rgb=C_RED, border_pt=1.5)
    tf_t2 = c_t2.text_frame
    tf_t2.word_wrap = True
    tf_t2.margin_left = Inches(0.15)
    tf_t2.margin_top = Inches(0.08)
    p = tf_t2.paragraphs[0]
    p.text = "2. MULTI-CYCLE DIVIDER FREEZE"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p2 = tf_t2.add_paragraph()
    p2.text = "At Cycle 6, div x5 asserts div_busy=1 & Stall_PC=1. Clock enables freeze PC & IF/ID for 32 cycles while WB commits bubbles."
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_MUTED

    c_t3 = add_card(s3, Inches(8.8), Inches(6.0), Inches(3.933), Inches(1.15), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_t3 = c_t3.text_frame
    tf_t3.word_wrap = True
    tf_t3.margin_left = Inches(0.15)
    tf_t3.margin_top = Inches(0.08)
    p = tf_t3.paragraphs[0]
    p.text = "3. 1-CYC DSP MUL & COMMIT"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p2 = tf_t3.add_paragraph()
    p2.text = "mul x4 completes in 1 cycle via DSP48E1. At Cycle 39, the final quotient x5=20 is bypassed via ForwardAE=2'b10 into addi x6."
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_MUTED

    # =========================================================
    # SLIDE 4: DESIGN + VERIFICATION PLAN (1.5–2 min)
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, 4, "Design Implementation & Multi-Tier Verification Plan", "Concrete Methodology & Simulation Coverage")

    # Left Column: Implementation Plan (4 Concrete Steps)
    c_impl = add_card(s4, Inches(0.6), Inches(1.42), Inches(5.9), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_CYAN, border_pt=1.5)
    tf_impl = c_impl.text_frame
    tf_impl.word_wrap = True
    tf_impl.margin_left = Inches(0.25)
    tf_impl.margin_top = Inches(0.15)
    p = tf_impl.paragraphs[0]
    p.text = "IMPLEMENTATION PLAN (4 CONCRETE PHASES)"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(8)

    add_bullet(tf_impl, "• Phase 1: Core Arithmetic & Hazards", "RV32I ALU + 1-cycle DSP multiplier + divider FSM + RAW forwarding unit.\n--> Deliverable: Passed tb_multiplier.v & tb_divider.v.", font_size=Pt(13.5), prefix_color=C_CYAN, space_after=Pt(8))
    add_bullet(tf_impl, "• Phase 2: Vision Acceleration Datapath", "Dual circular BRAM line buffers (320 B) + 9-MAC Conv2D engine (1 px/cyc).\n--> Deliverable: Passed tb_conv2d.v streaming testbench.", font_size=Pt(13.5), prefix_color=C_CYAN, space_after=Pt(8))
    add_bullet(tf_impl, "• Phase 3: Video RAM & Split-Screen VGA", "True dual-port VRAM (19.2 KB) + 640x480 @ 60 Hz VGA controller + Edge-AI.\n--> Deliverable: Passed dual-clock split-screen simulation.", font_size=Pt(13.5), prefix_color=C_CYAN, space_after=Pt(8))
    add_bullet(tf_impl, "• Phase 4: Full SoC Integration & Bitstream", "32-bit MMIO crossbar connecting core, VRAM, and peripherals on Nexys A7.\n--> Deliverable: tb_autovision_soc.v verified & bitstream generated.", font_size=Pt(13.5), prefix_color=C_CYAN, space_after=Pt(0))

    # Right Column: Verification Plan (3 Multi-Tier Levels)
    c_verif = add_card(s4, Inches(6.8), Inches(1.42), Inches(5.933), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_verif = c_verif.text_frame
    tf_verif.word_wrap = True
    tf_verif.margin_left = Inches(0.25)
    tf_verif.margin_top = Inches(0.15)
    p = tf_verif.paragraphs[0]
    p.text = "VERIFICATION PLAN (3-TIER VALIDATION)"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(8)

    add_bullet(tf_verif, "• Tier 1: Module-Level Unit Testing", "Standalone testbenches verify bit-exact outputs against Python models:\n- tb_multiplier: 10,000 randomized 32-bit signed/unsigned multiplications.\n- tb_divider: Complete cycle-accurate non-restoring quotient convergence.\n- tb_conv2d: Sobel Gx/Gy edge gradients on synthetic test patterns.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(8))
    add_bullet(tf_verif, "• Tier 2: Edge-Case Corner Handling", "Exhaustive hardware boundary tests:\n- Divide-by-zero (x/0 = -1) and signed overflow (-2^31 / -1).\n- Image boundary clipping: Discarding padding pixels outside 160x120.\n- Pipeline hazards: Back-to-back RAW dependencies with zero bubbles.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(8))
    add_bullet(tf_verif, "• Tier 3: Processor-Level Validation", "Full embedded C firmware (adas_runtime.c) compiled via RISC-V GCC:\n- Validates memory-mapped perception loops and sub-frame (<16.6 ms) AEB trip.\n- In-circuit FPGA execution verifying live camera UART reception.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(0))

    # =========================================================
    # SLIDE 5: TIMELINE & MILESTONES (1–1.5 min)
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, 5, "Project Schedule, Milestones & Deadlines", "Rigorous 5-Week Plan (Oct 1 – Nov 8) with Hard Quality Gates")

    # Top Milestone Badges
    c_m1 = add_card(s5, Inches(0.6), Inches(1.42), Inches(5.9), Inches(1.05), bg_rgb=C_BG_CARD, border_rgb=C_AMBER, border_pt=1.5)
    tf_m1 = c_m1.text_frame
    tf_m1.word_wrap = True
    tf_m1.margin_left = Inches(0.2)
    tf_m1.margin_top = Inches(0.08)
    p = tf_m1.paragraphs[0]
    p.text = "MILESTONE 1 (BY 25 OCT): CORE & ACCELERATORS TESTED"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p2 = tf_m1.add_paragraph()
    p2.text = "At least one module implemented + verified: Single-cycle DSP multiplier, divider FSM (<=34 cyc), and 2D Conv2D line buffer passed in simulation."
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_WHITE

    c_m2 = add_card(s5, Inches(6.8), Inches(1.42), Inches(5.933), Inches(1.05), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_m2 = c_m2.text_frame
    tf_m2.word_wrap = True
    tf_m2.margin_left = Inches(0.2)
    tf_m2.margin_top = Inches(0.08)
    p = tf_m2.paragraphs[0]
    p.text = "MILESTONE 2 (BY 1 NOV): MINIMUM SYSTEM WORKING"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p2 = tf_m2.add_paragraph()
    p2.text = "Minimum system operational: 3-stage RV32IM core integrated with MMIO crossbar, video BRAM, and split-screen 640x480 VGA display on Nexys A7 FPGA."
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_WHITE

    # 3 Work Packages: Phase 1, Phase 2, Phase 3
    c_p1 = add_card(s5, Inches(0.6), Inches(2.62), Inches(3.9), Inches(4.5), bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1)
    tf_p1 = c_p1.text_frame
    tf_p1.word_wrap = True
    tf_p1.margin_left = Inches(0.2)
    tf_p1.margin_top = Inches(0.12)
    p = tf_p1.paragraphs[0]
    p.text = "PHASE 1: UNIT RTL & TESTS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p_dt = tf_p1.add_paragraph()
    p_dt.text = "OCT 1 – OCT 25 (WEEKS 1–3)"
    p_dt.font.size = Pt(10.5)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_TEXT_MUTED
    p_dt.space_after = Pt(6)
    add_bullet(tf_p1, "• Oct 1–5:", "Microarchitecture & ISA specification freeze.", font_size=Pt(13), prefix_color=C_CYAN, space_after=Pt(5))
    add_bullet(tf_p1, "• Oct 6–15:", "DSP multiplier, non-restoring divider FSM, and dual line buffer RTL.", font_size=Pt(13), prefix_color=C_CYAN, space_after=Pt(5))
    add_bullet(tf_p1, "• Oct 16–25:", "3x3 MAC Conv2D engine RTL and Hazard unit forwarding logic.", font_size=Pt(13), prefix_color=C_CYAN, space_after=Pt(5))
    add_bullet(tf_p1, "• Gate Check:", "tb_multiplier, tb_divider, and tb_conv2d 100% test pass rate.", font_size=Pt(13), prefix_color=C_AMBER, space_after=Pt(0))

    c_p2 = add_card(s5, Inches(4.7), Inches(2.62), Inches(3.9), Inches(4.5), bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1)
    tf_p2 = c_p2.text_frame
    tf_p2.word_wrap = True
    tf_p2.margin_left = Inches(0.2)
    tf_p2.margin_top = Inches(0.12)
    p = tf_p2.paragraphs[0]
    p.text = "PHASE 2: SOC INTEGRATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p_dt = tf_p2.add_paragraph()
    p_dt.text = "OCT 26 – NOV 1 (WEEK 4)"
    p_dt.font.size = Pt(10.5)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_TEXT_MUTED
    p_dt.space_after = Pt(6)
    add_bullet(tf_p2, "• Oct 26–28:", "32-bit MMIO crossbar interconnect connecting core and VRAM.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(5))
    add_bullet(tf_p2, "• Oct 29–30:", "True dual-port video BRAM (19.2 KB) + 640x480 VGA controller.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(5))
    add_bullet(tf_p2, "• Oct 31–Nov 1:", "Vivado Synthesis, Place & Route, and timing closure at 50 MHz.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(5))
    add_bullet(tf_p2, "• Gate Check:", "Bitstream running on Nexys A7 FPGA with live split-screen VGA.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(0))

    c_p3 = add_card(s5, Inches(8.8), Inches(2.62), Inches(3.933), Inches(4.5), bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1)
    tf_p3 = c_p3.text_frame
    tf_p3.word_wrap = True
    tf_p3.margin_left = Inches(0.2)
    tf_p3.margin_top = Inches(0.12)
    p = tf_p3.paragraphs[0]
    p.text = "PHASE 3: PERIPHERALS & DEMO"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_PURPLE
    p_dt = tf_p3.add_paragraph()
    p_dt.text = "NOV 2 – NOV 8 (WEEK 5)"
    p_dt.font.size = Pt(10.5)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_TEXT_MUTED
    p_dt.space_after = Pt(6)
    add_bullet(tf_p3, "• Nov 2–4:", "Edge-AI quadrant classifier & AEB emergency brake trip logic.", font_size=Pt(13), prefix_color=C_PURPLE, space_after=Pt(5))
    add_bullet(tf_p3, "• Nov 5–6:", "16-bit Galois LFSR descrambler & 7-segment display telemetry.", font_size=Pt(13), prefix_color=C_PURPLE, space_after=Pt(5))
    add_bullet(tf_p3, "• Nov 7–8:", "End-to-end UART camera streaming from Host PC + AEB demo.", font_size=Pt(13), prefix_color=C_PURPLE, space_after=Pt(5))
    add_bullet(tf_p3, "• Gate Check:", "100% functional live board demo for course evaluation.", font_size=Pt(13), prefix_color=C_CYAN, space_after=Pt(0))

    # =========================================================
    # SLIDE 6: TEAM RESPONSIBILITIES (1 min)
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, 6, "Team Member Responsibilities & Work Packages", "Clear, Non-Overlapping Architecture Partitioning")

    # Table of Responsibilities (Width: 12.133", Height: 5.6")
    rows = 7
    cols = 4
    t_shape = s6.shapes.add_table(rows, cols, Inches(0.6), Inches(1.42), Inches(12.133), Inches(5.6))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(1.8)
    tbl.columns[1].width = Inches(3.2)
    tbl.columns[2].width = Inches(4.333)
    tbl.columns[3].width = Inches(2.8)

    headers = ["Member", "Module Responsibility", "Key Architectural Deliverables", "Verification Focus"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_BG_CARD_ALT
        cell.text_frame.word_wrap = True
        cell.text_frame.margin_left = Inches(0.12)
        cell.text_frame.margin_right = Inches(0.12)
        cell.text_frame.margin_top = Inches(0.1)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = C_CYAN

    data = [
        ("Rohit\n(Lead)", "Core Pipeline, Hazards & Full SoC Integration", "RV32I 3-stage core RTL (riscv_core.v), Hazard Unit forwarding logic, branch evaluation, top SoC assembly.", "RAW hazard forwarding, branch flush, MMIO routing (tb_autovision_soc.v)"),
        ("Prakhar", "DSP Multiplier Coprocessor & Unit Testbench", "Single-cycle 64-bit DSP array multiplier leveraging Artix-7 DSP48E1 slices (multiplier.v), standalone testbench.", "Bit-exact 64-bit precision, signed/unsigned MUL/MULH (tb_multiplier.v)"),
        ("Sajan", "Non-Restoring Divider FSM & Security Cipher", "32-bit non-restoring shift-subtract divider FSM (<= 34 cyc, divider.v), 16-bit Galois LFSR cipher, Vivado P&R.", "Divide-by-zero bypass (x/0 = -1), multi-cycle stall handshake, P&R closure"),
        ("Rishabh", "2D Spatial Convolution Hardware Engine", "Dual circular BRAM line buffers (320 B, line_buffer.v), 9-MAC parallel Sobel/Gaussian convolver (conv2d_engine.v).", "1 px/cyc streaming throughput, line buffer boundary clipping (tb_conv2d.v)"),
        ("Sarthak", "Video Subsystem, Compositor & Edge-AI", "Dual-port video BRAM (19.2 KB, frame_buffer.v), 640x480 VGA controller, split-screen HUD, Edge-AI sign classifier.", "Dual-clock domain timing, 60 Hz sync, sub-frame (<16.6 ms) AEB trip"),
        ("All Members", "System Integration, Board Demo & Telemetry", "Physical Nexys A7 FPGA bitstream flashing, Host PC UART streaming bridge, 7-segment display, emergency brake demo.", "End-to-end hardware demo validation, live fault injection, final slides")
    ]

    for r_idx, row_data in enumerate(data):
        for c_idx, val in enumerate(row_data):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_BG_CARD if r_idx % 2 == 0 else C_BG_PAGE
            cell.text_frame.word_wrap = True
            cell.text_frame.margin_left = Inches(0.12)
            cell.text_frame.margin_right = Inches(0.12)
            cell.text_frame.margin_top = Inches(0.08)
            cell.text_frame.margin_bottom = Inches(0.08)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(12)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_AMBER if "Lead" in val else C_TEXT_WHITE
            elif c_idx == 1:
                p.font.bold = True
                p.font.color.rgb = C_CYAN
            else:
                p.font.color.rgb = C_TEXT_WHITE

    # =========================================================
    # SLIDE 7: DEMO PLAN + CHALLENGES (1–1.5 min)
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, 7, "Physical FPGA Demonstration Plan & Technical Challenges", "End-to-End Validation (Input -> Processing -> Output) & Risk Mitigation")

    # Left Column: Demo Plan (Input -> Processing -> Output)
    c_demo = add_card(s7, Inches(0.6), Inches(1.42), Inches(5.9), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_demo = c_demo.text_frame
    tf_demo.word_wrap = True
    tf_demo.margin_left = Inches(0.25)
    tf_demo.margin_top = Inches(0.15)
    p = tf_demo.paragraphs[0]
    p.text = "DEMONSTRATION PLAN (INPUT -> PROCESSING -> OUTPUT)"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(8)

    add_bullet(tf_demo, "1. Input Stream (Host PC)", "Host PC streams real driving scene frames (160x120 grayscale = 19,200 B/frame) via USB-UART at 115,200 baud.", font_size=Pt(13.5), prefix_color=C_GREEN, space_after=Pt(8))
    add_bullet(tf_demo, "2. Processing (Nexys A7)", "• LFSR cipher descrambles encrypted video stream.\n• Circular line buffers stream pixels to 9-MAC Conv2D engine (1 px/cyc).\n• Edge-AI classifier categorizes sign geometry (STOP, YIELD, SPEED) in <16.6 ms.", font_size=Pt(13.5), prefix_color=C_GREEN, space_after=Pt(8))
    add_bullet(tf_demo, "3. Physical FPGA Outputs", "Visible outputs verified live on board:\n• VGA Monitor (640x480): Real-time split-screen (raw camera on left, Sobel edges on right).\n• Tri-Color RGB LED: Instant RED illumination on AEB emergency brake trip (STOP sign).\n• 7-Segment Display: Displays active sign ID & recognized speed limit.", font_size=Pt(13.5), prefix_color=C_GREEN, space_after=Pt(0))

    # Right Column: Technical Challenges & Solutions
    c_chal = add_card(s7, Inches(6.8), Inches(1.42), Inches(5.933), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_RED, border_pt=1.5)
    tf_chal = c_chal.text_frame
    tf_chal.word_wrap = True
    tf_chal.margin_left = Inches(0.25)
    tf_chal.margin_top = Inches(0.15)
    p = tf_chal.paragraphs[0]
    p.text = "TECHNICAL CHALLENGES & MITIGATION"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.space_after = Pt(8)

    add_bullet(tf_chal, "1. Multi-Cycle Division Stalls", "Synchronous clock enable gating freezes PC & IF/ID registers during <=34 cycle division without corrupting pipeline state.", font_size=Pt(13.5), prefix_color=C_RED, space_after=Pt(8))
    add_bullet(tf_chal, "2. Arithmetic Edge Cases", "Combinational bypass comparators handle divide-by-zero (x/0 = -1) and signed overflow (-2^31 / -1) without stall penalty.", font_size=Pt(13.5), prefix_color=C_RED, space_after=Pt(8))
    add_bullet(tf_chal, "3. Dual-Clock Domain Video", "True dual-port Block RAM decouples 50 MHz processor writes from 25 MHz VGA raster scan reads, preventing video tearing.", font_size=Pt(13.5), prefix_color=C_RED, space_after=Pt(8))
    add_bullet(tf_chal, "4. FPGA Timing Closure (50 MHz)", "Registering MMIO crossbar and DSP multiplier paths achieves +2.410 ns setup slack on Artix-7 (zero timing violations).", font_size=Pt(13.5), prefix_color=C_RED, space_after=Pt(0))

    # Save to all target locations
    for pth in [OUT_PPTX_REPO, OUT_PPTX_DL, OUT_PPTX_BRAIN]:
        os.makedirs(os.path.dirname(pth), exist_ok=True)
        prs.save(pth)
        print(f"[SUCCESS] Presentation saved to: {pth}")

if __name__ == "__main__":
    build_presentation()
