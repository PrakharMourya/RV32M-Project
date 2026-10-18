import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Destination Paths
OUT_PPTX_REPO  = r"C:\Users\risha\OneDrive\Desktop\AutoVision\docs\AutoVision_Presentation.pptx"
OUT_PPTX_DL    = r"C:\Users\risha\Downloads\AutoVision_Presentation.pptx"
OUT_PPTX_BRAIN = r"C:\Users\risha\.gemini\antigravity\brain\685340e0-fa4d-40ef-a8cb-ccfb71d7e1bc\AutoVision_Presentation.pptx"

HAND_CORE_IMG   = r"C:\Users\risha\OneDrive\Desktop\AutoVision\docs\handdrawn_core_clean.png"
HAND_VIS_IMG    = r"C:\Users\risha\OneDrive\Desktop\AutoVision\docs\handdrawn_vision_clean.png"
HAND_TIMING_IMG = r"C:\Users\risha\OneDrive\Desktop\AutoVision\docs\handdrawn_timing_clean.png"

# Color Palette: Clean, Executive Academic Light Theme
C_BG_PAGE      = RGBColor(248, 250, 252)  # Slate-50 (Clean soft white background)
C_BG_HEADER    = RGBColor(15, 23, 42)     # Deep Navy 900 (Authoritative anchor)
C_BG_CARD      = RGBColor(255, 255, 255)  # Pure White
C_BG_CARD_SUB  = RGBColor(241, 245, 249)  # Slate-100 (Subtle card header / tag)
C_BORDER_CARD  = RGBColor(203, 213, 225)  # Slate-300 (Crisp outline)
C_BORDER_LIGHT = RGBColor(226, 232, 240)  # Slate-200

# Typography Colors
C_TEXT_TITLE   = RGBColor(255, 255, 255)  # White on Navy header
C_TEXT_SUB     = RGBColor(56, 189, 248)   # Sky-400 subtitle on Navy header
C_TEXT_MAIN    = RGBColor(15, 23, 42)     # Deep Charcoal 900
C_TEXT_BODY    = RGBColor(51, 65, 85)     # Slate-700
C_TEXT_MUTED   = RGBColor(100, 116, 139)  # Slate-500

# Accent Colors
C_BLUE         = RGBColor(30, 64, 175)    # Blue-800
C_BLUE_LIGHT   = RGBColor(239, 246, 255)  # Blue-50
C_GREEN        = RGBColor(5, 150, 105)    # Emerald-600
C_GREEN_LIGHT  = RGBColor(236, 253, 245)  # Emerald-50
C_AMBER        = RGBColor(217, 119, 6)    # Amber-600
C_AMBER_LIGHT  = RGBColor(254, 243, 199)  # Amber-100
C_RED          = RGBColor(220, 38, 38)    # Red-600
C_RED_LIGHT    = RGBColor(254, 242, 242)  # Red-50
C_PURPLE       = RGBColor(124, 58, 237)   # Purple-600
C_PURPLE_LIGHT = RGBColor(245, 243, 255)  # Purple-50

def set_slide_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG_PAGE
    bg.line.fill.background()
    return bg

def add_header(slide, slide_num, title_text, subtitle_text):
    # Top banner bar
    header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.35), Inches(12.333), Inches(0.95))
    header_box.fill.solid()
    header_box.fill.fore_color.rgb = C_BG_HEADER
    header_box.line.fill.background()

    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.3)
    tf.margin_top = Inches(0.12)
    tf.margin_right = Inches(0.3)
    tf.margin_bottom = Inches(0.08)

    p0 = tf.paragraphs[0]
    p0.text = f"SLIDE {slide_num} OF 7  |  {subtitle_text.upper()}"
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = C_TEXT_SUB

    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(21)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_TITLE

    # Right side group / affiliation badge
    tag_box = slide.shapes.add_textbox(Inches(9.2), Inches(0.38), Inches(3.4), Inches(0.85))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_top = Inches(0.08)
    tf_tag.margin_right = Inches(0.2)

    p_tag1 = tf_tag.paragraphs[0]
    p_tag1.alignment = PP_ALIGN.RIGHT
    p_tag1.text = "GROUP 21  |  IIT GUWAHATI"
    p_tag1.font.name = "Segoe UI"
    p_tag1.font.size = Pt(11)
    p_tag1.font.bold = True
    p_tag1.font.color.rgb = RGBColor(251, 191, 36) # Amber-400

    p_tag2 = tf_tag.add_paragraph()
    p_tag2.alignment = PP_ALIGN.RIGHT
    p_tag2.text = "Digilent Nexys A7-100T (XC7A100T)"
    p_tag2.font.name = "Segoe UI"
    p_tag2.font.size = Pt(9.5)
    p_tag2.font.color.rgb = RGBColor(148, 163, 184) # Slate-400

def add_card(slide, left, top, width, height, bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_rgb
    card.line.color.rgb = border_rgb
    card.line.width = Pt(border_pt)
    return card

def add_card_header(slide, left, top, width, height, title_text, badge_bg=C_BLUE_LIGHT, badge_text_rgb=C_BLUE):
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    badge.fill.solid()
    badge.fill.fore_color.rgb = badge_bg
    badge.line.color.rgb = badge_text_rgb
    badge.line.width = Pt(1)
    tf = badge.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.15)
    tf.margin_top = Inches(0.06)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = title_text.upper()
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = badge_text_rgb
    return badge

def add_bullet(tf, bold_prefix, text_content, font_size=Pt(13.5), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(6)):
    if len(tf.paragraphs) == 1 and tf.paragraphs[0].text.strip() == "":
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.alignment = PP_ALIGN.LEFT
    p.font.name = "Segoe UI"
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
# PRESENTATION BUILDER
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

    # Top Summary Card: Problem Statement (1 line) & System Description (2 lines)
    c_overview = add_card(s1, Inches(0.5), Inches(1.42), Inches(12.333), Inches(1.85), bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1.5)
    tf_ov = c_overview.text_frame
    tf_ov.word_wrap = True
    tf_ov.margin_left = Inches(0.25)
    tf_ov.margin_top = Inches(0.12)
    tf_ov.margin_right = Inches(0.25)

    # Problem Statement
    p_prob_hdr = tf_ov.paragraphs[0]
    p_prob_hdr.alignment = PP_ALIGN.LEFT
    p_prob_hdr.text = "PROBLEM STATEMENT (1 LINE)"
    p_prob_hdr.font.name = "Segoe UI"
    p_prob_hdr.font.size = Pt(10.5)
    p_prob_hdr.font.bold = True
    p_prob_hdr.font.color.rgb = C_RED

    p_prob = tf_ov.add_paragraph()
    p_prob.alignment = PP_ALIGN.LEFT
    p_prob.text = "Real-time edge ADAS demands deterministic <16.6 ms spatial filtering and immediate emergency braking that exceeds pure software capabilities of embedded RISC-V cores."
    p_prob.font.name = "Segoe UI"
    p_prob.font.size = Pt(14)
    p_prob.font.bold = True
    p_prob.font.color.rgb = C_TEXT_MAIN
    p_prob.space_after = Pt(8)

    # System Description
    p_sys_hdr = tf_ov.add_paragraph()
    p_sys_hdr.alignment = PP_ALIGN.LEFT
    p_sys_hdr.text = "SYSTEM DESCRIPTION (2–3 LINES)"
    p_sys_hdr.font.name = "Segoe UI"
    p_sys_hdr.font.size = Pt(10.5)
    p_sys_hdr.font.bold = True
    p_sys_hdr.font.color.rgb = C_BLUE

    p_sys = tf_ov.add_paragraph()
    p_sys.alignment = PP_ALIGN.LEFT
    p_sys.text = "• AutoVision-RISC-V tightly couples a 3-stage RV32IM processor core with memory-mapped 2D spatial convolution accelerators and an Edge-AI geometric obstacle classifier on Nexys A7 FPGA.\n• Implements live split-screen 640x480 VGA rendering, hardware Galois LFSR cipher descrambling, and autonomous emergency braking (AEB) with visual multi-digit telemetry."
    p_sys.font.name = "Segoe UI"
    p_sys.font.size = Pt(13)
    p_sys.font.color.rgb = C_TEXT_BODY

    # 3 Scope Cards: Commitment, Goal, Stretch
    # Commitment
    c_com = add_card(s1, Inches(0.5), Inches(3.42), Inches(3.95), Inches(3.65), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    add_card_header(s1, Inches(0.7), Inches(3.55), Inches(3.55), Inches(0.38), "COMMITMENT (MINIMUM ACCEPTABLE)", badge_bg=C_GREEN_LIGHT, badge_text_rgb=C_GREEN)
    tf_com = c_com.text_frame
    tf_com.word_wrap = True
    tf_com.margin_left = Inches(0.2)
    tf_com.margin_top = Inches(0.65)
    tf_com.margin_right = Inches(0.2)
    tf_com.paragraphs[0].text = "" # Blank top
    add_bullet(tf_com, "• 3-Stage RV32IM Core:", "Functional IF/ID, EX, and WB pipeline with 1-cycle DSP multiplier, <= 34-cycle non-restoring divider FSM, and zero-cycle RAW hazard forwarding.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(10))
    add_bullet(tf_com, "• 2D Conv2D Engine:", "Hardware 3x3 Sobel edge detector with dual circular BRAM line buffers (1 px/cyc) and live split-screen 640x480 VGA display on Nexys A7.", font_size=Pt(13), prefix_color=C_GREEN, space_after=Pt(0))

    # Goal
    c_goal = add_card(s1, Inches(4.69), Inches(3.42), Inches(3.95), Inches(3.65), bg_rgb=C_BG_CARD, border_rgb=C_BLUE, border_pt=1.5)
    add_card_header(s1, Inches(4.89), Inches(3.55), Inches(3.55), Inches(0.38), "GOAL (EXPECTED TARGET)", badge_bg=C_BLUE_LIGHT, badge_text_rgb=C_BLUE)
    tf_goal = c_goal.text_frame
    tf_goal.word_wrap = True
    tf_goal.margin_left = Inches(0.2)
    tf_goal.margin_top = Inches(0.65)
    tf_goal.margin_right = Inches(0.2)
    tf_goal.paragraphs[0].text = ""
    add_bullet(tf_goal, "• Edge-AI Classifier:", "Real-time quadrant density sign classifier triggering physical AEB emergency brake trip on tri-color RGB LED.", font_size=Pt(13), prefix_color=C_BLUE, space_after=Pt(10))
    add_bullet(tf_goal, "• UART Video Pipeline:", "End-to-end 115200-baud frame streaming (160x120) with live 7-segment display and Host PC telemetry logging.", font_size=Pt(13), prefix_color=C_BLUE, space_after=Pt(0))

    # Stretch
    c_str = add_card(s1, Inches(8.88), Inches(3.42), Inches(3.95), Inches(3.65), bg_rgb=C_BG_CARD, border_rgb=C_PURPLE, border_pt=1.5)
    add_card_header(s1, Inches(9.08), Inches(3.55), Inches(3.55), Inches(0.38), "STRETCH (ADVANCED TARGET)", badge_bg=C_PURPLE_LIGHT, badge_text_rgb=C_PURPLE)
    tf_str = c_str.text_frame
    tf_str.word_wrap = True
    tf_str.margin_left = Inches(0.2)
    tf_str.margin_top = Inches(0.65)
    tf_str.margin_right = Inches(0.2)
    tf_str.paragraphs[0].text = ""
    add_bullet(tf_str, "• Hardware V2X Cipher:", "16-bit Galois LFSR symmetric cryptographic stream cipher descrambler with modular AES-128 secure key interface for encrypted camera feeds.", font_size=Pt(13), prefix_color=C_PURPLE, space_after=Pt(10))
    add_bullet(tf_str, "• Sub-Frame Latency:", "Zero-wait-state DMA streaming pipeline achieving complete frame classification in <16.6 ms (full 60 fps line rate).", font_size=Pt(13), prefix_color=C_PURPLE, space_after=Pt(0))

    # =========================================================
    # SLIDE 2: SYSTEM ARCHITECTURE (HANDWRITTEN BLOCK DIAGRAMS) (2 min)
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, 2, "System Architecture: Processor Pipeline & Coprocessors", "Handwritten Microarchitecture Schematics (Report Fig. 1 & 2)")

    # Left Column: Core Processor Pipeline Datapath (Stages 1 to 3)
    c_core = add_card(s2, Inches(0.5), Inches(1.42), Inches(6.0), Inches(5.68), bg_rgb=C_BG_CARD, border_rgb=C_BLUE, border_pt=1.5)
    add_card_header(s2, Inches(0.65), Inches(1.50), Inches(5.70), Inches(0.32), "1. CORE PROCESSOR PIPELINE (STAGES 1–3)", badge_bg=C_BLUE_LIGHT, badge_text_rgb=C_BLUE)
    
    # Hand-drawn Core Pipeline Diagram (Cleaned & High-Res)
    # Aspect ratio ~ 1.54:1 -> width 5.25", height 3.40"
    s2.shapes.add_picture(HAND_CORE_IMG, Inches(0.88), Inches(1.88), width=Inches(5.25), height=Inches(3.40))

    # Core Pipeline Datapath Breakdown Box
    tb_core = s2.shapes.add_textbox(Inches(0.65), Inches(5.32), Inches(5.70), Inches(1.70))
    tf_core = tb_core.text_frame
    tf_core.word_wrap = True
    tf_core.margin_left = Inches(0.1)
    tf_core.margin_right = Inches(0.1)
    tf_core.margin_top = Inches(0.04)
    add_bullet(tf_core, "• 3-Stage Pipeline:", "16 KB I-BRAM, 32-reg regfile with internal bypass, 16 KB D-BRAM & MMIO.", font_size=Pt(10), prefix_color=C_BLUE, space_after=Pt(3))
    add_bullet(tf_core, "• Coprocessors:", "1-cyc DSP48E1 multiplier (MUL/MULH), <=34 cyc divider FSM (DIV/DIVU).", font_size=Pt(10), prefix_color=C_BLUE, space_after=Pt(3))
    add_bullet(tf_core, "• Hazard Control:", "Zero-penalty RAW bypass (WB -> EX) and synchronous div_busy clock freeze.", font_size=Pt(10), prefix_color=C_BLUE, space_after=Pt(0))

    # Right Column: Vision Acceleration & Peripheral Subsystem
    c_vis = add_card(s2, Inches(6.83), Inches(1.42), Inches(6.0), Inches(5.68), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    add_card_header(s2, Inches(6.98), Inches(1.50), Inches(5.70), Inches(0.32), "2. VISION ACCELERATOR & PERIPHERAL SUBSYSTEM", badge_bg=C_GREEN_LIGHT, badge_text_rgb=C_GREEN)

    # Hand-drawn Vision Subsystem Diagram (Cleaned & High-Res)
    # Aspect ratio ~ 1.39:1 -> width 4.75", height 3.40"
    s2.shapes.add_picture(HAND_VIS_IMG, Inches(7.45), Inches(1.88), width=Inches(4.75), height=Inches(3.40))

    # Vision Subsystem Datapath Breakdown Box
    tb_vis = s2.shapes.add_textbox(Inches(6.98), Inches(5.32), Inches(5.70), Inches(1.70))
    tf_vis = tb_vis.text_frame
    tf_vis.word_wrap = True
    tf_vis.margin_left = Inches(0.1)
    tf_vis.margin_right = Inches(0.1)
    tf_vis.margin_top = Inches(0.04)
    add_bullet(tf_vis, "• Video Ingest:", "115200-baud UART -> 16-bit Galois LFSR descrambler -> 19.2 KB frame store.", font_size=Pt(10), prefix_color=C_GREEN, space_after=Pt(3))
    add_bullet(tf_vis, "• 2D Spatial Filter:", "Dual circular line buffers (320 B), 9-MAC Sobel filter at 1 px/cyc line rate.", font_size=Pt(10), prefix_color=C_GREEN, space_after=Pt(3))
    add_bullet(tf_vis, "• Edge-AI & HUD:", "Quadrant density classifier, AEB trip on RGB LED, split-screen 60 Hz VGA.", font_size=Pt(10), prefix_color=C_GREEN, space_after=Pt(0))

    # =========================================================
    # SLIDE 3: TIMING DIAGRAM (HANDWRITTEN VIVADO TRACE) (2 min)
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, 3, "Cycle-Accurate Timing Diagram: Execution & Hazards", "Handwritten Waveform Execution Trace (Report Fig. 3)")

    # Top Instruction Sequence Card
    c_seq = add_card(s3, Inches(0.5), Inches(1.42), Inches(12.333), Inches(0.70), bg_rgb=C_BG_CARD, border_rgb=C_BLUE, border_pt=1)
    tf_seq = c_seq.text_frame
    tf_seq.word_wrap = True
    tf_seq.margin_left = Inches(0.2)
    tf_seq.margin_top = Inches(0.06)
    p = tf_seq.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.text = "REAL 25+ CYCLE ADAS INSTRUCTION SEQUENCE (VERIFIED IN AMD VIVADO 2025.2):"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p2 = tf_seq.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    p2.text = "0x00: addi x1, 10  |  0x04: addi x2, 20  |  0x08: add x3, x1, x2 (RAW Forwarding, 0 stalls)  |  0x0C: mul x4, x1, x2 (1-Cyc DSP)  |  0x10: div x5, x4, x1 (<=34 Cyc FSM Stall)  |  0x14: addi x6, x5, 5"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = C_TEXT_MAIN

    # Center: Timing Diagram Box with Side Flanks
    c_timg = add_card(s3, Inches(0.5), Inches(2.18), Inches(12.333), Inches(3.68), bg_rgb=RGBColor(255, 255, 255), border_rgb=C_BORDER_CARD, border_pt=1)
    
    # Left Flank: Signal Glossary Box
    c_gloss = add_card(s3, Inches(0.62), Inches(2.26), Inches(2.45), Inches(3.52), bg_rgb=C_BLUE_LIGHT, border_rgb=C_BLUE, border_pt=1)
    tf_gl = c_gloss.text_frame
    tf_gl.word_wrap = True
    tf_gl.margin_left = Inches(0.12)
    tf_gl.margin_right = Inches(0.10)
    tf_gl.margin_top = Inches(0.10)
    p_gl = tf_gl.paragraphs[0]
    p_gl.alignment = PP_ALIGN.LEFT
    p_gl.text = "SIGNAL GLOSSARY"
    p_gl.font.name = "Segoe UI"
    p_gl.font.size = Pt(10.5)
    p_gl.font.bold = True
    p_gl.font.color.rgb = C_BLUE
    p_gl.space_after = Pt(4)
    add_bullet(tf_gl, "• Clk_50mhz:", "50 MHz Master Clock", font_size=Pt(9.5), prefix_color=C_BLUE, space_after=Pt(2))
    add_bullet(tf_gl, "• PCF [31:0]:", "Program Counter (Fetch)", font_size=Pt(9.5), prefix_color=C_BLUE, space_after=Pt(2))
    add_bullet(tf_gl, "• InstrF [31:0]:", "Fetched Instruction", font_size=Pt(9.5), prefix_color=C_BLUE, space_after=Pt(2))
    add_bullet(tf_gl, "• ID/Ex stage:", "Execute Stage Opcode", font_size=Pt(9.5), prefix_color=C_BLUE, space_after=Pt(2))
    add_bullet(tf_gl, "• div_busy:", "Divider FSM Busy Flag", font_size=Pt(9.5), prefix_color=C_RED, space_after=Pt(2))
    add_bullet(tf_gl, "• Stall_PC:", "Freeze PC & IF/ID Enable", font_size=Pt(9.5), prefix_color=C_RED, space_after=Pt(0))

    # Center: Hand-drawn Timing Diagram Waveform (Cleaned & High-Res)
    # Ratio ~ 1.95:1 -> width 6.80", height 3.50"
    s3.shapes.add_picture(HAND_TIMING_IMG, Inches(3.18), Inches(2.26), width=Inches(6.80), height=Inches(3.50))

    # Right Flank: Bus Values & Register Log Box
    c_log = add_card(s3, Inches(10.10), Inches(2.26), Inches(2.62), Inches(3.52), bg_rgb=C_GREEN_LIGHT, border_rgb=C_GREEN, border_pt=1)
    tf_log = c_log.text_frame
    tf_log.word_wrap = True
    tf_log.margin_left = Inches(0.12)
    tf_log.margin_right = Inches(0.10)
    tf_log.margin_top = Inches(0.10)
    p_log = tf_log.paragraphs[0]
    p_log.alignment = PP_ALIGN.LEFT
    p_log.text = "EXECUTION & COMMITS"
    p_log.font.name = "Segoe UI"
    p_log.font.size = Pt(10.5)
    p_log.font.bold = True
    p_log.font.color.rgb = C_GREEN
    p_log.space_after = Pt(4)
    add_bullet(tf_log, "• C3 Commit:", "ResultW = x1 = 10", font_size=Pt(9.5), prefix_color=C_GREEN, space_after=Pt(2))
    add_bullet(tf_log, "• C4 RAW Bypass:", "ForwardBE = 2'b10 (x2 = 20)", font_size=Pt(9.5), prefix_color=C_BLUE, space_after=Pt(2))
    add_bullet(tf_log, "• C5 1-Cyc DSP:", "mul x4 executes (x3 = 30)", font_size=Pt(9.5), prefix_color=C_GREEN, space_after=Pt(2))
    add_bullet(tf_log, "• C6 Div Freeze:", "div x5 asserts div_busy=1", font_size=Pt(9.5), prefix_color=C_RED, space_after=Pt(2))
    add_bullet(tf_log, "• C39 Div Commit:", "ResultW = x5 = 20 -> x6", font_size=Pt(9.5), prefix_color=C_GREEN, space_after=Pt(2))
    add_bullet(tf_log, "• C40 Final Add:", "ResultW = x6 = 25", font_size=Pt(9.5), prefix_color=C_GREEN, space_after=Pt(0))

    # Bottom 3 Callout Cards
    c_t1 = add_card(s3, Inches(0.5), Inches(5.96), Inches(3.95), Inches(1.15), bg_rgb=C_BG_CARD, border_rgb=C_BLUE, border_pt=1.5)
    tf_t1 = c_t1.text_frame
    tf_t1.word_wrap = True
    tf_t1.margin_left = Inches(0.15)
    tf_t1.margin_top = Inches(0.08)
    p = tf_t1.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.text = "1. ZERO-CYCLE RAW FORWARDING"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p2 = tf_t1.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    p2.text = "At Cycle 4, add depends on x2. Hazard Unit asserts ForwardBE = 2'b10, bypassing ResultW (20) directly into ALU with 0 stall cycles."
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = C_TEXT_BODY

    c_t2 = add_card(s3, Inches(4.69), Inches(5.96), Inches(3.95), Inches(1.15), bg_rgb=C_BG_CARD, border_rgb=C_RED, border_pt=1.5)
    tf_t2 = c_t2.text_frame
    tf_t2.word_wrap = True
    tf_t2.margin_left = Inches(0.15)
    tf_t2.margin_top = Inches(0.08)
    p = tf_t2.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.text = "2. MULTI-CYCLE DIVIDER FREEZE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p2 = tf_t2.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    p2.text = "At Cycle 6, div x5 asserts div_busy=1 & Stall_PC=1. Clock enables freeze PC & IF/ID for 32 cycles while WB commits bubbles."
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = C_TEXT_BODY

    c_t3 = add_card(s3, Inches(8.88), Inches(5.96), Inches(3.95), Inches(1.15), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_t3 = c_t3.text_frame
    tf_t3.word_wrap = True
    tf_t3.margin_left = Inches(0.15)
    tf_t3.margin_top = Inches(0.08)
    p = tf_t3.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.text = "3. 1-CYC DSP MUL & COMMIT"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p2 = tf_t3.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    p2.text = "mul x4 completes in 1 cycle via DSP48E1. At Cycle 39, the final quotient x5=20 is bypassed via ForwardAE=2'b10 into addi x6."
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = C_TEXT_BODY

    # =========================================================
    # SLIDE 4: DESIGN + VERIFICATION PLAN (1.5–2 min)
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, 4, "Design Implementation & Multi-Tier Verification Plan", "Concrete Methodology & Simulation Coverage")

    # Left Column: Implementation Plan (4 Concrete Steps)
    c_impl = add_card(s4, Inches(0.5), Inches(1.42), Inches(6.0), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_BLUE, border_pt=1.5)
    add_card_header(s4, Inches(0.7), Inches(1.55), Inches(5.6), Inches(0.38), "IMPLEMENTATION PLAN (4 CONCRETE PHASES)", badge_bg=C_BLUE_LIGHT, badge_text_rgb=C_BLUE)
    tf_impl = c_impl.text_frame
    tf_impl.word_wrap = True
    tf_impl.margin_left = Inches(0.25)
    tf_impl.margin_top = Inches(0.58)
    tf_impl.margin_right = Inches(0.25)
    tf_impl.paragraphs[0].text = ""

    add_bullet(tf_impl, "• Phase 1: Core Arithmetic & Hazards", "RV32I ALU + 1-cycle DSP multiplier + divider FSM + RAW forwarding unit.\n  Gate Deliverable: Passed tb_multiplier.v & tb_divider.v (10,000 cyc).", font_size=Pt(11.5), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(6))
    add_bullet(tf_impl, "• Phase 2: Vision Acceleration Datapath", "Dual circular BRAM line buffers (320 B) + 9-MAC Conv2D engine (1 px/cyc).\n  Gate Deliverable: Passed tb_conv2d.v streaming testbench.", font_size=Pt(11.5), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(6))
    add_bullet(tf_impl, "• Phase 3: Video RAM & Split-Screen VGA", "True dual-port VRAM (19.2 KB) + 640x480 @ 60 Hz VGA controller + Edge-AI.\n  Gate Deliverable: Passed dual-clock split-screen simulation.", font_size=Pt(11.5), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(6))
    add_bullet(tf_impl, "• Phase 4: Full SoC Integration & Bitstream", "32-bit MMIO crossbar connecting core, VRAM, and peripherals on Nexys A7.\n  Gate Deliverable: Passed tb_autovision_soc.v & bitstream generated.", font_size=Pt(11.5), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(0))

    # Right Column: Verification Plan (3 Multi-Tier Levels)
    c_verif = add_card(s4, Inches(6.83), Inches(1.42), Inches(6.0), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    add_card_header(s4, Inches(7.03), Inches(1.55), Inches(5.6), Inches(0.38), "VERIFICATION PLAN (3-TIER VALIDATION)", badge_bg=C_GREEN_LIGHT, badge_text_rgb=C_GREEN)
    tf_verif = c_verif.text_frame
    tf_verif.word_wrap = True
    tf_verif.margin_left = Inches(0.25)
    tf_verif.margin_top = Inches(0.58)
    tf_verif.margin_right = Inches(0.25)
    tf_verif.paragraphs[0].text = ""

    add_bullet(tf_verif, "• Tier 1: Unit-Level Verification (Bit-Exact RTL vs Python)", "\n  – Multiplier: 10,000 randomized 32-bit signed/unsigned multiplications.\n  – Divider: Cycle-accurate non-restoring quotient convergence.\n  – Conv2D: Sobel Gx/Gy edge gradients verified on synthetic patterns.", font_size=Pt(11), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(6))
    add_bullet(tf_verif, "• Tier 2: Edge-Case Corner Handling (Hardware Boundary Tests)", "\n  – Divide-by-zero (x/0 = -1) and signed overflow (-2^31 / -1).\n  – Boundary clipping: Discarding padding pixels outside 160x120 frame.\n  – Pipeline hazards: Back-to-back RAW dependencies with zero bubbles.", font_size=Pt(11), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(6))
    add_bullet(tf_verif, "• Tier 3: Processor & System Integration (C Firmware on Core)", "\n  – Perception runtime (adas_runtime.c) compiled via RISC-V GCC.\n  – Validates MMIO loops, <16.6 ms AEB trip, and UART camera reception.", font_size=Pt(11), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(0))

    # =========================================================
    # SLIDE 5: TIMELINE & MILESTONES (1–1.5 min)
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, 5, "Project Schedule, Milestones & Deadlines", "Rigorous 5-Week Plan (Oct 1 – Nov 8) with Hard Quality Gates")

    # Top Milestone Badges
    c_m1 = add_card(s5, Inches(0.5), Inches(1.42), Inches(6.0), Inches(1.1), bg_rgb=C_BG_CARD, border_rgb=C_AMBER, border_pt=1.5)
    tf_m1 = c_m1.text_frame
    tf_m1.word_wrap = True
    tf_m1.margin_left = Inches(0.2)
    tf_m1.margin_top = Inches(0.1)
    p = tf_m1.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.text = "MILESTONE 1 (BY 25 OCT): CORE & ACCELERATORS TESTED"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p2 = tf_m1.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    p2.text = "At least one module implemented + verified: Single-cycle DSP multiplier, divider FSM (<=34 cyc), and 2D Conv2D line buffer passed in simulation."
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MAIN

    c_m2 = add_card(s5, Inches(6.83), Inches(1.42), Inches(6.0), Inches(1.1), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    tf_m2 = c_m2.text_frame
    tf_m2.word_wrap = True
    tf_m2.margin_left = Inches(0.2)
    tf_m2.margin_top = Inches(0.1)
    p = tf_m2.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.text = "MILESTONE 2 (BY 1 NOV): MINIMUM SYSTEM WORKING"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p2 = tf_m2.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    p2.text = "Minimum system operational: 3-stage RV32IM core integrated with MMIO crossbar, video BRAM, and split-screen 640x480 VGA display on Nexys A7 FPGA."
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MAIN

    # 3 Work Packages: Phase 1, Phase 2, Phase 3
    c_p1 = add_card(s5, Inches(0.5), Inches(2.68), Inches(3.95), Inches(4.45), bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1)
    add_card_header(s5, Inches(0.65), Inches(2.8), Inches(3.65), Inches(0.35), "PHASE 1: UNIT RTL & TESTS", badge_bg=C_BLUE_LIGHT, badge_text_rgb=C_BLUE)
    tf_p1 = c_p1.text_frame
    tf_p1.word_wrap = True
    tf_p1.margin_left = Inches(0.2)
    tf_p1.margin_top = Inches(0.55)
    p_dt = tf_p1.paragraphs[0]
    p_dt.alignment = PP_ALIGN.LEFT
    p_dt.text = "OCT 1 – OCT 25 (WEEKS 1–3)"
    p_dt.font.name = "Segoe UI"
    p_dt.font.size = Pt(10.5)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_TEXT_MUTED
    p_dt.space_after = Pt(6)
    add_bullet(tf_p1, "• Oct 1–5:", "Microarchitecture & ISA specification freeze.", font_size=Pt(13), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p1, "• Oct 6–15:", "DSP multiplier, non-restoring divider FSM, and dual line buffer RTL.", font_size=Pt(13), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p1, "• Oct 16–25:", "3x3 MAC Conv2D engine RTL and Hazard unit forwarding logic.", font_size=Pt(13), prefix_color=C_BLUE, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p1, "• Gate Check:", "tb_multiplier, tb_divider, and tb_conv2d 100% test pass rate.", font_size=Pt(13), prefix_color=C_AMBER, text_color=C_TEXT_MAIN, space_after=Pt(0))

    c_p2 = add_card(s5, Inches(4.69), Inches(2.68), Inches(3.95), Inches(4.45), bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1)
    add_card_header(s5, Inches(4.84), Inches(2.8), Inches(3.65), Inches(0.35), "PHASE 2: SOC INTEGRATION", badge_bg=C_GREEN_LIGHT, badge_text_rgb=C_GREEN)
    tf_p2 = c_p2.text_frame
    tf_p2.word_wrap = True
    tf_p2.margin_left = Inches(0.2)
    tf_p2.margin_top = Inches(0.55)
    p_dt = tf_p2.paragraphs[0]
    p_dt.alignment = PP_ALIGN.LEFT
    p_dt.text = "OCT 26 – NOV 1 (WEEK 4)"
    p_dt.font.name = "Segoe UI"
    p_dt.font.size = Pt(10.5)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_TEXT_MUTED
    p_dt.space_after = Pt(6)
    add_bullet(tf_p2, "• Oct 26–28:", "32-bit MMIO crossbar interconnect connecting core and VRAM.", font_size=Pt(13), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p2, "• Oct 29–30:", "True dual-port video BRAM (19.2 KB) + 640x480 VGA controller.", font_size=Pt(13), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p2, "• Oct 31–Nov 1:", "Vivado Synthesis, Place & Route, and timing closure at 50 MHz.", font_size=Pt(13), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p2, "• Gate Check:", "Bitstream running on Nexys A7 FPGA with live split-screen VGA.", font_size=Pt(13), prefix_color=C_GREEN, text_color=C_TEXT_MAIN, space_after=Pt(0))

    c_p3 = add_card(s5, Inches(8.88), Inches(2.68), Inches(3.95), Inches(4.45), bg_rgb=C_BG_CARD, border_rgb=C_BORDER_CARD, border_pt=1)
    add_card_header(s5, Inches(9.03), Inches(2.8), Inches(3.65), Inches(0.35), "PHASE 3: PERIPHERALS & DEMO", badge_bg=C_PURPLE_LIGHT, badge_text_rgb=C_PURPLE)
    tf_p3 = c_p3.text_frame
    tf_p3.word_wrap = True
    tf_p3.margin_left = Inches(0.2)
    tf_p3.margin_top = Inches(0.55)
    p_dt = tf_p3.paragraphs[0]
    p_dt.alignment = PP_ALIGN.LEFT
    p_dt.text = "NOV 2 – NOV 8 (WEEK 5)"
    p_dt.font.name = "Segoe UI"
    p_dt.font.size = Pt(10.5)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_TEXT_MUTED
    p_dt.space_after = Pt(6)
    add_bullet(tf_p3, "• Nov 2–4:", "Edge-AI quadrant classifier & AEB emergency brake trip logic.", font_size=Pt(13), prefix_color=C_PURPLE, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p3, "• Nov 5–6:", "16-bit Galois LFSR descrambler & 7-segment display telemetry.", font_size=Pt(13), prefix_color=C_PURPLE, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p3, "• Nov 7–8:", "End-to-end UART camera streaming from Host PC + AEB demo.", font_size=Pt(13), prefix_color=C_PURPLE, text_color=C_TEXT_BODY, space_after=Pt(5))
    add_bullet(tf_p3, "• Gate Check:", "100% functional live board demo for course evaluation.", font_size=Pt(13), prefix_color=C_BLUE, text_color=C_TEXT_MAIN, space_after=Pt(0))

    # =========================================================
    # SLIDE 6: TEAM RESPONSIBILITIES (1 min)
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, 6, "Team Member Responsibilities & Work Packages", "Clear, Non-Overlapping Architecture Partitioning")

    # Table of Responsibilities (Width: 12.333", Height: 5.6")
    rows = 7
    cols = 4
    t_shape = s6.shapes.add_table(rows, cols, Inches(0.5), Inches(1.42), Inches(12.333), Inches(5.6))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(1.8)
    tbl.columns[1].width = Inches(3.2)
    tbl.columns[2].width = Inches(4.433)
    tbl.columns[3].width = Inches(2.9)

    headers = ["Member", "Module Responsibility", "Key Architectural Deliverables", "Verification Focus"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_BG_HEADER
        cell.text_frame.word_wrap = True
        cell.text_frame.margin_left = Inches(0.15)
        cell.text_frame.margin_right = Inches(0.15)
        cell.text_frame.margin_top = Inches(0.12)
        cell.text_frame.margin_bottom = Inches(0.12)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Segoe UI"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

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
            cell.fill.fore_color.rgb = C_BG_CARD if r_idx % 2 == 0 else C_BG_CARD_SUB
            cell.text_frame.word_wrap = True
            cell.text_frame.margin_left = Inches(0.15)
            cell.text_frame.margin_right = Inches(0.15)
            cell.text_frame.margin_top = Inches(0.08)
            cell.text_frame.margin_bottom = Inches(0.08)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Segoe UI"
            p.font.size = Pt(12)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_BLUE if "Lead" in val else C_TEXT_MAIN
            elif c_idx == 1:
                p.font.bold = True
                p.font.color.rgb = C_BLUE
            else:
                p.font.color.rgb = C_TEXT_BODY

    # =========================================================
    # SLIDE 7: DEMO PLAN + CHALLENGES (1–1.5 min)
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, 7, "Physical FPGA Demonstration Plan & Technical Challenges", "End-to-End Validation (Input -> Processing -> Output) & Risk Mitigation")

    # Left Column: Demo Plan (Input -> Processing -> Output)
    c_demo = add_card(s7, Inches(0.5), Inches(1.42), Inches(6.0), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_GREEN, border_pt=1.5)
    add_card_header(s7, Inches(0.7), Inches(1.55), Inches(5.6), Inches(0.38), "DEMONSTRATION PLAN (INPUT -> PROCESSING -> OUTPUT)", badge_bg=C_GREEN_LIGHT, badge_text_rgb=C_GREEN)
    tf_demo = c_demo.text_frame
    tf_demo.word_wrap = True
    tf_demo.margin_left = Inches(0.25)
    tf_demo.margin_top = Inches(0.65)
    tf_demo.margin_right = Inches(0.25)
    tf_demo.paragraphs[0].text = ""

    add_bullet(tf_demo, "1. Input Stream (Host PC)", "Host PC streams real driving scene frames (160x120 grayscale = 19,200 B/frame) via USB-UART at 115,200 baud.", font_size=Pt(13.5), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(8))
    add_bullet(tf_demo, "2. Processing (Nexys A7)", "• LFSR cipher descrambles encrypted video stream.\n• Circular line buffers stream pixels to 9-MAC Conv2D engine (1 px/cyc).\n• Edge-AI classifier categorizes sign geometry (STOP, YIELD, SPEED) in <16.6 ms.", font_size=Pt(13.5), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(8))
    add_bullet(tf_demo, "3. Physical FPGA Outputs", "Visible outputs verified live on board:\n• VGA Monitor (640x480): Real-time split-screen (raw camera on left, Sobel edges on right).\n• Tri-Color RGB LED: Instant RED illumination on AEB emergency brake trip (STOP sign).\n• 7-Segment Display: Displays active sign ID & recognized speed limit.", font_size=Pt(13.5), prefix_color=C_GREEN, text_color=C_TEXT_BODY, space_after=Pt(0))

    # Right Column: Technical Challenges & Solutions
    c_chal = add_card(s7, Inches(6.83), Inches(1.42), Inches(6.0), Inches(5.7), bg_rgb=C_BG_CARD, border_rgb=C_RED, border_pt=1.5)
    add_card_header(s7, Inches(7.03), Inches(1.55), Inches(5.6), Inches(0.38), "TECHNICAL CHALLENGES & MITIGATION", badge_bg=C_RED_LIGHT, badge_text_rgb=C_RED)
    tf_chal = c_chal.text_frame
    tf_chal.word_wrap = True
    tf_chal.margin_left = Inches(0.25)
    tf_chal.margin_top = Inches(0.65)
    tf_chal.margin_right = Inches(0.25)
    tf_chal.paragraphs[0].text = ""

    add_bullet(tf_chal, "1. Multi-Cycle Division Stalls", "Synchronous clock enable gating freezes PC & IF/ID registers during <=34 cycle division without corrupting pipeline state.", font_size=Pt(13.5), prefix_color=C_RED, text_color=C_TEXT_BODY, space_after=Pt(8))
    add_bullet(tf_chal, "2. Arithmetic Edge Cases", "Combinational bypass comparators handle divide-by-zero (x/0 = -1) and signed overflow (-2^31 / -1) without stall penalty.", font_size=Pt(13.5), prefix_color=C_RED, text_color=C_TEXT_BODY, space_after=Pt(8))
    add_bullet(tf_chal, "3. Dual-Clock Domain Video", "True dual-port Block RAM decouples 50 MHz processor writes from 25 MHz VGA raster scan reads, preventing video tearing.", font_size=Pt(13.5), prefix_color=C_RED, text_color=C_TEXT_BODY, space_after=Pt(8))
    add_bullet(tf_chal, "4. FPGA Timing Closure (50 MHz)", "Registering MMIO crossbar and DSP multiplier paths achieves +2.410 ns setup slack on Artix-7 (zero timing violations).", font_size=Pt(13.5), prefix_color=C_RED, text_color=C_TEXT_BODY, space_after=Pt(0))

    # Save to all target locations
    for pth in [OUT_PPTX_REPO, OUT_PPTX_DL, OUT_PPTX_BRAIN]:
        os.makedirs(os.path.dirname(pth), exist_ok=True)
        prs.save(pth)
        print(f"[SUCCESS] Presentation saved to: {pth}")

if __name__ == "__main__":
    build_presentation()
