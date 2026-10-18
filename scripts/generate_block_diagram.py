#!/usr/bin/env python3
"""
=============================================================================
AutoVision-RISC-V: Architectural Block Diagram Generator
Generates high-resolution Vector SVG and 300-DPI PNG microarchitecture diagram
Matching the textbook datapath style of Patterson & Hennessy / Harris & Harris
Course: Digital System Design / Computer Architecture, IIT Guwahati
=============================================================================
"""

import os
import sys
import html
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

SVG_PATH = os.path.join(DOCS_DIR, "autovision_block_diagram.svg")
PNG_PATH = os.path.join(DOCS_DIR, "autovision_block_diagram.png")

def esc(text):
    """Safely escape text for XML/SVG rendering."""
    return html.escape(str(text), quote=True)

def generate_svg():
    width = 2400
    height = 1450

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append("""
    <defs>
        <style>
            .title { font-family: 'Consolas', 'Courier New', monospace; font-weight: bold; font-size: 26px; fill: #0F172A; }
            .subtitle { font-family: 'Consolas', 'Courier New', monospace; font-size: 15px; fill: #475569; }
            .box-title { font-family: 'Consolas', 'Courier New', monospace; font-weight: bold; font-size: 17px; fill: #1E293B; }
            .sub-box-title { font-family: 'Consolas', 'Courier New', monospace; font-weight: bold; font-size: 13px; fill: #334155; }
            .label { font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; fill: #1E293B; }
            .label-bold { font-family: 'Consolas', 'Courier New', monospace; font-weight: bold; font-size: 13px; fill: #0F172A; }
            .ctrl-label { font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; fill: #0284C7; font-weight: 600; }
            .hazard-label { font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; fill: #DC2626; font-weight: bold; }
            .bus-width { font-family: 'Consolas', 'Courier New', monospace; font-size: 10px; fill: #64748B; font-weight: bold; }
            .stage-hdr { font-family: 'Consolas', 'Courier New', monospace; font-weight: bold; font-size: 18px; fill: #FFFFFF; }
            .datapath-line { stroke: #1E293B; stroke-width: 2.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }
            .ctrl-line { stroke: #0284C7; stroke-width: 1.8; fill: none; stroke-linecap: round; stroke-linejoin: round; }
            .hazard-line { stroke: #DC2626; stroke-width: 2.0; stroke-dasharray: 6,4; fill: none; }
            .vision-line { stroke: #059669; stroke-width: 2.2; fill: none; }
            .video-line { stroke: #7C3AED; stroke-width: 2.2; fill: none; }
            .grid-bg { fill: #F8FAFC; }
        </style>
        <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="#1E293B" />
        </marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="#0284C7" />
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="#DC2626" />
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="#059669" />
        </marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="#7C3AED" />
        </marker>
        <linearGradient id="pipeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#E2E8F0" />
            <stop offset="50%" stop-color="#CBD5E1" />
            <stop offset="100%" stop-color="#94A3B8" />
        </linearGradient>
    </defs>
    """)

    # Background canvas
    svg.append(f'<rect width="{width}" height="{height}" fill="#F8FAFC"/>')
    svg.append(f'<rect x="15" y="15" width="{width-30}" height="{height-30}" rx="12" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>')

    # Header Banner
    svg.append(f'<rect x="15" y="15" width="{width-30}" height="85" rx="12" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1.5"/>')
    svg.append(f'<text x="45" y="52" class="title">AutoVision-RISC-V: An RV32IM SoC with Hardware-Accelerated 2D Spatial Conv2D &amp; Edge-AI Classifier</text>')
    svg.append(f'<text x="45" y="78" class="subtitle">Complete 3-Stage RV32IM Core, Non-Restoring Divider FSM (&le; 34 Cyc), MMIO Crossbar, Line Buffers &amp; Split-Screen VGA</text>')
    svg.append(f'<text x="1850" y="52" class="sub-box-title" fill="#0F172A">GROUP 21 | TARGET: Digilent Nexys A7-100T (XC7A100T)</text>')
    svg.append(f'<text x="1850" y="74" class="subtitle">DEPT OF CSE, IIT GUWAHATI | OCT 2026</text>')

    # Major Stage Header Tabs
    stages = [
        {"name": "INSTRUCTION FETCH (IF)", "x": 40, "w": 410, "color": "#0284C7"},
        {"name": "INSTRUCTION DECODE &amp; REGFILE (ID)", "x": 490, "w": 440, "color": "#0284C7"},
        {"name": "EXECUTION &amp; COPROCESSORS (EX)", "x": 970, "w": 520, "color": "#0284C7"},
        {"name": "MEMORY, MMIO &amp; VISION ACCELERATION", "x": 1530, "w": 820, "color": "#059669"}
    ]

    for st in stages:
        svg.append(f'<rect x="{st["x"]}" y="115" width="{st["w"]}" height="32" rx="6" fill="{st["color"]}"/>')
        svg.append(f'<text x="{st["x"] + st["w"]/2}" y="137" text-anchor="middle" class="stage-hdr">{st["name"]}</text>')

    # =========================================================================
    # PIPELINE REGISTERS (Vertical Slices with Clock Headers)
    # =========================================================================
    def draw_pipe_reg(x, y, w, h, label):
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="url(#pipeGrad)" stroke="#64748B" stroke-width="2"/>')
        svg.append(f'<polygon points="{x+w/2-10},{y} {x+w/2},{y-12} {x+w/2+10},{y}" fill="#0284C7" stroke="#0369A1" stroke-width="1.5"/>')
        svg.append(f'<text x="{x+w/2}" y="{y-16}" text-anchor="middle" class="ctrl-label">CLK</text>')
        svg.append(f'<text x="{x+w/2}" y="{y+h/2}" text-anchor="middle" class="box-title" fill="#1E293B" transform="rotate(-90 {x+w/2} {y+h/2})">{label}</text>')

    draw_pipe_reg(455, 170, 24, 780, "IF / ID PIPELINE REGISTER")
    draw_pipe_reg(935, 170, 24, 780, "ID / EX PIPELINE REGISTER")
    draw_pipe_reg(1495, 170, 24, 780, "EX / WB PIPELINE REGISTER")

    # Helper: Bus width slash
    def draw_bus_slash(x, y, width_str="32"):
        svg.append(f'<line x1="{x-4}" y1="{y+4}" x2="{x+4}" y2="{y-4}" stroke="#64748B" stroke-width="1.5"/>')
        svg.append(f'<text x="{x+2}" y="{y-6}" class="bus-width">{width_str}</text>')

    # Helper: Multiplexer
    def draw_mux(x, y, w, h, label0="0", label1="1", title="MUX"):
        points = f"{x},{y} {x+w},{y+h*0.2} {x+w},{y+h*0.8} {x},{y+h}"
        svg.append(f'<polygon points="{points}" fill="#FFFFFF" stroke="#1E293B" stroke-width="2"/>')
        svg.append(f'<text x="{x+6}" y="{y+h*0.35}" class="label">{label0}</text>')
        svg.append(f'<text x="{x+6}" y="{y+h*0.75}" class="label">{label1}</text>')

    # =========================================================================
    # STAGE 1: INSTRUCTION FETCH (IF)
    # =========================================================================
    draw_mux(65, 340, 32, 110, "0", "1")
    svg.append('<text x="81" y="328" text-anchor="middle" class="sub-box-title">PCMux</text>')
    # Select line for PCMux
    svg.append('<line x1="81" y1="180" x2="81" y2="340" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<text x="88" y="215" class="ctrl-label">PCSrcE</text>')

    # PC Register
    svg.append('<rect x="135" y="360" width="55" height="70" rx="4" fill="#F8FAFC" stroke="#1E293B" stroke-width="2"/>')
    svg.append('<polygon points="135,390 145,395 135,400" fill="none" stroke="#1E293B" stroke-width="1.5"/>')
    svg.append('<text x="162" y="395" text-anchor="middle" class="box-title">PC</text>')
    svg.append('<text x="162" y="415" text-anchor="middle" class="label">Reg</text>')
    # Reset line
    svg.append('<line x1="162" y1="460" x2="162" y2="430" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<text x="168" y="455" class="ctrl-label">rst_n</text>')

    # PC + 4 Adder
    def draw_adder(x, y, w, h, label="+4"):
        svg.append(f'<polygon points="{x},{y} {x+w},{y+h*0.3} {x+w},{y+h*0.7} {x},{y+h}" fill="#F8FAFC" stroke="#1E293B" stroke-width="2"/>')
        svg.append(f'<text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" class="label-bold">{label}</text>')

    draw_adder(220, 230, 45, 70, "+4")

    # Instruction Memory BRAM
    svg.append('<rect x="230" y="340" width="180" height="150" rx="6" fill="#F8FAFC" stroke="#1E293B" stroke-width="2.2"/>')
    svg.append('<text x="320" y="370" text-anchor="middle" class="box-title">Instruction Memory</text>')
    svg.append('<text x="320" y="390" text-anchor="middle" class="subtitle">16 KB BRAM (4096 x 32)</text>')
    svg.append('<text x="245" y="425" class="label-bold">A [13:2]</text>')
    svg.append('<text x="370" y="425" class="label-bold">RD</text>')

    # IF Wires
    svg.append('<line x1="97" y1="395" x2="135" y2="395" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="108" y="388" class="label">PC\'</text>')
    draw_bus_slash(116, 395, "32")

    svg.append('<line x1="190" y1="395" x2="230" y2="395" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="202" y="388" class="label">PCF</text>')
    draw_bus_slash(208, 395, "32")

    svg.append('<line x1="205" y1="395" x2="205" y2="280" class="datapath-line"/>')
    svg.append('<line x1="205" y1="280" x2="220" y2="280" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<line x1="210" y1="245" x2="220" y2="245" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="195" y="250" class="label">4</text>')

    svg.append('<line x1="265" y1="265" x2="455" y2="265" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="320" y="258" class="label">PCPlus4F [31:0]</text>')
    svg.append('<circle cx="300" cy="265" r="3.5" fill="#1E293B"/>')
    svg.append('<line x1="300" y1="265" x2="300" y2="190" class="datapath-line"/>')
    svg.append('<line x1="300" y1="190" x2="45" y2="190" class="datapath-line"/>')
    svg.append('<line x1="45" y1="190" x2="45" y2="365" class="datapath-line"/>')
    svg.append('<line x1="45" y1="365" x2="65" y2="365" class="datapath-line" marker-end="url(#arrow)"/>')

    svg.append('<line x1="410" y1="420" x2="455" y2="420" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="418" y="412" class="label-bold">InstrF [31:0]</text>')
    draw_bus_slash(432, 420, "32")

    # =========================================================================
    # STAGE 2: INSTRUCTION DECODE & REGISTER FILE (ID)
    # =========================================================================
    svg.append('<line x1="479" y1="420" x2="520" y2="420" class="datapath-line"/>')
    svg.append('<circle cx="520" cy="420" r="3.5" fill="#1E293B"/>')

    # Control Unit Box
    svg.append('<rect x="520" y="180" width="140" height="200" rx="25" fill="#F0F9FF" stroke="#0284C7" stroke-width="2.2"/>')
    svg.append('<text x="590" y="210" text-anchor="middle" class="box-title" fill="#0369A1">Control</text>')
    svg.append('<text x="590" y="230" text-anchor="middle" class="box-title" fill="#0369A1">Unit</text>')
    svg.append('<text x="532" y="275" class="label">Op [6:0]</text>')
    svg.append('<text x="532" y="305" class="label">Funct3 [14:12]</text>')
    svg.append('<text x="532" y="335" class="label">Funct7 [31:25]</text>')

    ctrl_outs = [
        {"y": 200, "name": "PCSrcD", "pipe_y": 200},
        {"y": 220, "name": "RegWriteD", "pipe_y": 220},
        {"y": 240, "name": "MemtoRegD", "pipe_y": 240},
        {"y": 260, "name": "MemWriteD", "pipe_y": 260},
        {"y": 280, "name": "ALUControlD[3:0]", "pipe_y": 280},
        {"y": 300, "name": "BranchD", "pipe_y": 300},
        {"y": 320, "name": "ALUSrcD", "pipe_y": 320},
        {"y": 340, "name": "MulValidD", "pipe_y": 340},
        {"y": 360, "name": "DivValidD", "pipe_y": 360},
    ]
    for c in ctrl_outs:
        svg.append(f'<line x1="660" y1="{c["y"]}" x2="935" y2="{c["pipe_y"]}" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
        svg.append(f'<text x="668" y="{c["y"]-4}" class="ctrl-label">{c["name"]}</text>')

    svg.append('<line x1="520" y1="420" x2="520" y2="300" class="datapath-line"/>')
    svg.append('<line x1="520" y1="300" x2="525" y2="300" class="datapath-line" marker-end="url(#arrow)"/>')

    # Register File
    svg.append('<rect x="690" y="440" width="210" height="220" rx="8" fill="#F8FAFC" stroke="#1E293B" stroke-width="2.2"/>')
    svg.append('<text x="795" y="470" text-anchor="middle" class="box-title">Register File</text>')
    svg.append('<text x="795" y="490" text-anchor="middle" class="subtitle">32 x 32-bit (x0=0)</text>')
    svg.append('<text x="702" y="525" class="label-bold">A1 (rs1) [19:15]</text>')
    svg.append('<text x="702" y="565" class="label-bold">A2 (rs2) [24:20]</text>')
    svg.append('<text x="702" y="605" class="label-bold">A3 (rd)  [11:7]</text>')
    svg.append('<text x="702" y="640" class="label-bold">WD3</text>')
    svg.append('<text x="850" y="525" class="label-bold">RD1</text>')
    svg.append('<text x="850" y="575" class="label-bold">RD2</text>')
    svg.append('<text x="780" y="448" class="ctrl-label">WE3</text>')
    # Control wire into WE3
    svg.append('<line x1="795" y1="220" x2="795" y2="440" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<text x="802" y="430" class="ctrl-label">RegWriteW</text>')

    svg.append('<line x1="520" y1="420" x2="520" y2="520" class="datapath-line"/>')
    svg.append('<line x1="520" y1="520" x2="690" y2="520" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="545" y="514" class="label">InstrD[19:15]</text>')
    draw_bus_slash(640, 520, "5")

    svg.append('<line x1="500" y1="420" x2="500" y2="560" class="datapath-line"/>')
    svg.append('<circle cx="500" cy="420" r="3" fill="#1E293B"/>')
    svg.append('<line x1="500" y1="560" x2="690" y2="560" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="545" y="554" class="label">InstrD[24:20]</text>')
    draw_bus_slash(640, 560, "5")

    # Immediate Extension Unit
    svg.append('<polygon points="690,700 850,715 850,765 690,780" fill="#F8FAFC" stroke="#1E293B" stroke-width="2"/>')
    svg.append('<text x="770" y="745" text-anchor="middle" class="box-title">Imm Extend</text>')
    svg.append('<text x="585" y="735" class="label">Instr[31:7]</text>')
    draw_bus_slash(660, 740, "25")

    svg.append('<line x1="485" y1="420" x2="485" y2="740" class="datapath-line"/>')
    svg.append('<circle cx="485" cy="420" r="3" fill="#1E293B"/>')
    svg.append('<line x1="485" y1="740" x2="690" y2="740" class="datapath-line" marker-end="url(#arrow)"/>')

    svg.append('<line x1="850" y1="740" x2="935" y2="740" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="858" y="732" class="label">ExtImmD [31:0]</text>')
    draw_bus_slash(900, 740, "32")

    svg.append('<line x1="900" y1="520" x2="935" y2="520" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="902" y="512" class="label">RD1</text>')
    draw_bus_slash(918, 520, "32")

    svg.append('<line x1="900" y1="570" x2="935" y2="570" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="902" y="562" class="label">RD2</text>')
    draw_bus_slash(918, 570, "32")

    # rd destination forwarding
    svg.append('<line x1="510" y1="560" x2="510" y2="600" class="datapath-line"/>')
    svg.append('<line x1="510" y1="600" x2="650" y2="600" class="datapath-line"/>')
    svg.append('<line x1="650" y1="600" x2="650" y2="660" class="datapath-line"/>')
    svg.append('<line x1="650" y1="660" x2="935" y2="660" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="660" y="654" class="label">rdD [11:7]</text>')
    draw_bus_slash(880, 660, "5")

    # =========================================================================
    # STAGE 3: EXECUTION & ARITHMETIC COPROCESSORS (EX)
    # =========================================================================
    draw_mux(990, 480, 28, 80, "0", "1")
    svg.append('<text x="1004" y="472" text-anchor="middle" class="sub-box-title">FwdA</text>')
    # ForwardAE select line
    svg.append('<line x1="1004" y1="440" x2="1004" y2="480" class="hazard-line" marker-end="url(#arrow-red)"/>')
    svg.append('<text x="965" y="445" class="hazard-label">ForwardAE[1:0]</text>')

    draw_mux(990, 580, 28, 80, "0", "1")
    svg.append('<text x="1004" y="572" text-anchor="middle" class="sub-box-title">FwdB</text>')
    # ForwardBE select line
    svg.append('<line x1="1004" y1="560" x2="1004" y2="580" class="hazard-line" marker-end="url(#arrow-red)"/>')
    svg.append('<text x="965" y="565" class="hazard-label">ForwardBE[1:0]</text>')

    svg.append('<line x1="959" y1="520" x2="990" y2="505" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<line x1="959" y1="570" x2="990" y2="600" class="datapath-line" marker-end="url(#arrow)"/>')

    draw_mux(1070, 620, 28, 80, "0", "1")
    svg.append('<text x="1084" y="612" text-anchor="middle" class="sub-box-title">ALUSrc</text>')
    # ALUSrcE select line
    svg.append('<line x1="1084" y1="320" x2="1084" y2="620" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<text x="1090" y="340" class="ctrl-label">ALUSrcE</text>')

    svg.append('<line x1="1018" y1="620" x2="1070" y2="640" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<circle cx="1040" cy="625" r="3" fill="#1E293B"/>')
    svg.append('<line x1="1040" y1="625" x2="1040" y2="820" class="datapath-line"/>')
    svg.append('<line x1="1040" y1="820" x2="1495" y2="820" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="1050" y="812" class="label">WriteDataE [31:0]</text>')
    draw_bus_slash(1250, 820, "32")

    svg.append('<line x1="959" y1="740" x2="1050" y2="740" class="datapath-line"/>')
    svg.append('<line x1="1050" y1="740" x2="1050" y2="680" class="datapath-line"/>')
    svg.append('<line x1="1050" y1="680" x2="1070" y2="680" class="datapath-line" marker-end="url(#arrow)"/>')

    # ALU Symbol
    def draw_alu_symbol(x, y, w, h, label="ALU"):
        points = f"{x},{y} {x+w},{y+h*0.3} {x+w},{y+h*0.7} {x},{y+h} {x},{y+h*0.62} {x+w*0.25},{y+h*0.5} {x},{y+h*0.38}"
        svg.append(f'<polygon points="{points}" fill="#F8FAFC" stroke="#1E293B" stroke-width="2.2"/>')
        svg.append(f'<text x="{x+w*0.58}" y="{y+h*0.55}" text-anchor="middle" class="box-title">{label}</text>')

    draw_alu_symbol(1140, 480, 85, 150, "ALU")
    svg.append('<text x="1145" y="470" class="ctrl-label">ALUControlE[3:0]</text>')
    svg.append('<line x1="1170" y1="280" x2="1170" y2="480" class="ctrl-line" marker-end="url(#arrow-blue)"/>')

    svg.append('<line x1="1018" y1="520" x2="1140" y2="520" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="1060" y="512" class="label-bold">SrcAE</text>')
    draw_bus_slash(1080, 520, "32")
    svg.append('<circle cx="1090" cy="520" r="3.5" fill="#1E293B"/>')

    svg.append('<line x1="1098" y1="660" x2="1140" y2="610" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="1105" y="645" class="label-bold">SrcBE</text>')
    draw_bus_slash(1115, 635, "32")

    # Multiplier Subsystem
    svg.append('<rect x="1260" y="220" width="180" height="90" rx="8" fill="#FEF3C7" stroke="#D97706" stroke-width="2.2"/>')
    svg.append('<text x="1350" y="245" text-anchor="middle" class="box-title" fill="#B45309">RV32M Multiplier</text>')
    svg.append('<text x="1350" y="265" text-anchor="middle" class="sub-box-title" fill="#92400E">SINGLE-CYCLE DSP48E1</text>')
    svg.append('<text x="1350" y="285" text-anchor="middle" class="label">MUL, MULH, MULHSU, MULHU</text>')
    svg.append('<text x="1350" y="302" text-anchor="middle" class="label-bold" fill="#B45309">1 Clock Cycle Latency</text>')

    # Divider Subsystem
    svg.append('<rect x="1260" y="330" width="180" height="110" rx="8" fill="#FEE2E2" stroke="#DC2626" stroke-width="2.2"/>')
    svg.append('<text x="1350" y="355" text-anchor="middle" class="box-title" fill="#B91C1C">RV32M Divider FSM</text>')
    svg.append('<text x="1350" y="375" text-anchor="middle" class="sub-box-title" fill="#991B1B">NON-RESTORING FSM (&le; 34 CYC)</text>')
    svg.append('<text x="1350" y="395" text-anchor="middle" class="label">DIV, DIVU, REM, REMU</text>')
    svg.append('<text x="1350" y="415" text-anchor="middle" class="label">Non-Restoring Shift-Subtract</text>')
    svg.append('<text x="1350" y="432" text-anchor="middle" class="hazard-label">Asserts div_busy Stall</text>')

    # Input feeds to Multiplier and Divider
    svg.append('<line x1="1090" y1="520" x2="1090" y2="250" class="datapath-line"/>')
    svg.append('<line x1="1090" y1="250" x2="1260" y2="250" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<circle cx="1090" cy="370" r="3" fill="#1E293B"/>')
    svg.append('<line x1="1090" y1="370" x2="1260" y2="370" class="datapath-line" marker-end="url(#arrow)"/>')

    svg.append('<circle cx="1115" cy="580" r="3" fill="#1E293B"/>')
    svg.append('<line x1="1115" y1="580" x2="1115" y2="280" class="datapath-line"/>')
    svg.append('<line x1="1115" y1="280" x2="1260" y2="280" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<circle cx="1115" cy="400" r="3" fill="#1E293B"/>')
    svg.append('<line x1="1115" y1="400" x2="1260" y2="400" class="datapath-line" marker-end="url(#arrow)"/>')

    # ExResMux
    draw_mux(1455, 480, 30, 130, "A", "M")
    svg.append('<text x="1470" y="470" text-anchor="middle" class="sub-box-title">ExResMux</text>')
    # ExResSel select line
    svg.append('<line x1="1470" y1="360" x2="1470" y2="480" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<text x="1475" y="450" class="ctrl-label">ExResSel[1:0]</text>')

    svg.append('<line x1="1225" y1="555" x2="1455" y2="520" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<line x1="1440" y1="275" x2="1450" y2="275" class="datapath-line"/>')
    svg.append('<line x1="1450" y1="275" x2="1450" y2="560" class="datapath-line"/>')
    svg.append('<line x1="1450" y1="560" x2="1455" y2="560" class="datapath-line" marker-end="url(#arrow)"/>')

    svg.append('<line x1="1440" y1="390" x2="1445" y2="390" class="datapath-line"/>')
    svg.append('<line x1="1445" y1="390" x2="1445" y2="590" class="datapath-line"/>')
    svg.append('<line x1="1445" y1="590" x2="1455" y2="590" class="datapath-line" marker-end="url(#arrow)"/>')

    svg.append('<line x1="1485" y1="545" x2="1495" y2="545" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="1465" y="535" class="label-bold">ALUResultE [31:0]</text>')
    draw_bus_slash(1490, 545, "32")

    # Hazard unit
    svg.append('<rect x="990" y="870" width="460" height="120" rx="10" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.2"/>')
    svg.append('<text x="1220" y="900" text-anchor="middle" class="box-title" fill="#B91C1C">Hazard, Forwarding &amp; Interlock Stall Unit</text>')
    svg.append('<text x="1220" y="920" text-anchor="middle" class="subtitle" fill="#991B1B">Zero-Cycle RAW Forwarding &amp; Multi-Cycle Stall Interlock</text>')
    svg.append('<text x="1005" y="955" class="label-bold" fill="#B91C1C">ForwardAE = 2\'b10 (WB to EX)</text>')
    svg.append('<text x="1005" y="975" class="label-bold" fill="#B91C1C">ForwardBE = 2\'b10 (WB to EX)</text>')
    svg.append('<text x="1240" y="955" class="hazard-label">Stall_IF &amp; Stall_ID on div_busy</text>')
    svg.append('<text x="1240" y="975" class="hazard-label">Flush_ID on BranchMispredict</text>')

    svg.append('<line x1="1350" y1="440" x2="1350" y2="870" class="hazard-line" marker-end="url(#arrow-red)"/>')
    svg.append('<text x="1355" y="460" class="hazard-label">div_busy (32 cyc)</text>')

    svg.append('<line x1="990" y1="940" x2="160" y2="940" class="hazard-line"/>')
    svg.append('<line x1="160" y1="940" x2="160" y2="430" class="hazard-line" marker-end="url(#arrow-red)"/>')
    svg.append('<text x="165" y="445" class="hazard-label">Stall_PC</text>')

    # =========================================================================
    # STAGE 4: MEMORY, MMIO & HARDWARE VISION ACCELERATORS
    # =========================================================================
    svg.append('<rect x="1540" y="200" width="790" height="110" rx="8" fill="#F1F5F9" stroke="#334155" stroke-width="2.2"/>')
    svg.append('<text x="1935" y="230" text-anchor="middle" class="box-title" fill="#0F172A">32-Bit Memory-Mapped I/O (MMIO) Interconnect Crossbar</text>')
    svg.append('<text x="1935" y="250" text-anchor="middle" class="subtitle">Decodes 0x0000_4000 (DMEM), 0x1000_0000 (VRAM), 0x2000_0000 (UART), 0x2000_0100 (CONV), 0x2000_0200 (AI)</text>')
    svg.append('<text x="1550" y="285" class="label-bold">cpu_addr [31:0]</text>')
    svg.append('<text x="1690" y="285" class="label-bold">cpu_wdata [31:0]</text>')
    svg.append('<text x="1840" y="285" class="label-bold">cpu_read_req</text>')
    svg.append('<text x="1980" y="285" class="label-bold">cpu_write_req</text>')
    svg.append('<text x="2150" y="285" class="label-bold">cpu_rdata [31:0]</text>')

    svg.append('<line x1="1519" y1="545" x2="1530" y2="545" class="datapath-line"/>')
    svg.append('<line x1="1530" y1="545" x2="1530" y2="260" class="datapath-line"/>')
    svg.append('<line x1="1530" y1="260" x2="1540" y2="260" class="datapath-line" marker-end="url(#arrow)"/>')

    # Data Memory (DMEM)
    svg.append('<rect x="1540" y="350" width="160" height="150" rx="6" fill="#F8FAFC" stroke="#1E293B" stroke-width="2"/>')
    svg.append('<text x="1620" y="380" text-anchor="middle" class="box-title">Data Memory</text>')
    svg.append('<text x="1620" y="400" text-anchor="middle" class="subtitle">16 KB BRAM</text>')
    svg.append('<text x="1548" y="435" class="label">A [13:2]</text>')
    svg.append('<text x="1548" y="465" class="label">WD [31:0]</text>')
    svg.append('<text x="1655" y="435" class="label-bold">RD</text>')
    svg.append('<text x="1590" y="342" class="ctrl-label">MemWriteM</text>')
    svg.append('<line x1="1620" y1="310" x2="1620" y2="350" class="ctrl-line" marker-end="url(#arrow-blue)"/>')

    # Dual-Port Frame Buffer
    svg.append('<rect x="1730" y="350" width="180" height="150" rx="6" fill="#F5F3FF" stroke="#7C3AED" stroke-width="2.2"/>')
    svg.append('<text x="1820" y="375" text-anchor="middle" class="box-title" fill="#6D28D9">Dual-Port Frame Buffer</text>')
    svg.append('<text x="1820" y="395" text-anchor="middle" class="subtitle" fill="#7C3AED">19,200 Bytes (160x120)</text>')
    svg.append('<text x="1738" y="430" class="label">Port A: CPU/UART W</text>')
    svg.append('<text x="1738" y="460" class="label">Port B: VGA Stream R</text>')
    svg.append('<text x="1738" y="485" class="sub-box-title" fill="#6D28D9">TRUE DUAL-PORT BRAM</text>')
    svg.append('<line x1="1780" y1="310" x2="1780" y2="350" class="video-line" marker-end="url(#arrow-purple)"/>')

    # Conv2D Accelerator
    svg.append('<rect x="1940" y="350" width="230" height="230" rx="8" fill="#ECFDF5" stroke="#059669" stroke-width="2.2"/>')
    svg.append('<text x="2055" y="375" text-anchor="middle" class="box-title" fill="#047857">2D Conv2D Accelerator</text>')
    svg.append('<text x="2055" y="395" text-anchor="middle" class="sub-box-title" fill="#065F46">CIRCULAR BUFFER &amp; 9-MAC</text>')
    svg.append('<rect x="1955" y="410" width="200" height="45" rx="4" fill="#D1FAE5" stroke="#059669" stroke-width="1.5"/>')
    svg.append('<text x="2055" y="430" text-anchor="middle" class="label-bold" fill="#047857">Dual BRAM Line Buffers</text>')
    svg.append('<text x="2055" y="445" text-anchor="middle" class="bus-width">2 Rows x 160 Pixels (Circular FIFO)</text>')
    svg.append('<rect x="1955" y="465" width="200" height="55" rx="4" fill="#D1FAE5" stroke="#059669" stroke-width="1.5"/>')
    svg.append('<text x="2055" y="485" text-anchor="middle" class="label-bold" fill="#047857">3x3 Parallel MAC Engine</text>')
    svg.append('<text x="2055" y="500" text-anchor="middle" class="bus-width">Sobel Gx, Gy &amp; Gaussian Blur</text>')
    svg.append('<text x="2055" y="513" text-anchor="middle" class="hazard-label" fill="#047857">1 Pixel / Clock Cycle (25 MHz)</text>')
    svg.append('<text x="2055" y="555" text-anchor="middle" class="label-bold" fill="#065F46">Measured Speedup: 180.0x</text>')
    svg.append('<line x1="2055" y1="310" x2="2055" y2="350" class="vision-line" marker-end="url(#arrow-green)"/>')

    # Edge AI Classifier
    svg.append('<rect x="2195" y="350" width="140" height="230" rx="8" fill="#EFF6FF" stroke="#2563EB" stroke-width="2.2"/>')
    svg.append('<text x="2265" y="375" text-anchor="middle" class="box-title" fill="#1D4ED8">Edge-AI</text>')
    svg.append('<text x="2265" y="395" text-anchor="middle" class="box-title" fill="#1D4ED8">Classifier</text>')
    svg.append('<text x="2265" y="420" text-anchor="middle" class="sub-box-title" fill="#1E40AF">SPATIAL FEATURE</text>')
    svg.append('<text x="2265" y="450" text-anchor="middle" class="label">Quadrant Density</text>')
    svg.append('<text x="2265" y="475" text-anchor="middle" class="label">Centroid X/Y</text>')
    svg.append('<text x="2265" y="500" text-anchor="middle" class="label">Aspect Ratio</text>')
    svg.append('<text x="2265" y="530" text-anchor="middle" class="label-bold" fill="#1D4ED8">STOP (Octagon)</text>')
    svg.append('<text x="2265" y="550" text-anchor="middle" class="label-bold" fill="#1D4ED8">YIELD (Triangle)</text>')
    svg.append('<text x="2265" y="570" text-anchor="middle" class="label-bold" fill="#1D4ED8">SPEED (Circle)</text>')
    svg.append('<line x1="2265" y1="310" x2="2265" y2="350" class="ctrl-line" marker-end="url(#arrow-blue)"/>')

    # Compositor & VGA Controller
    svg.append('<rect x="1730" y="620" width="290" height="150" rx="8" fill="#FAF5FF" stroke="#7C3AED" stroke-width="2.2"/>')
    svg.append('<text x="1875" y="645" text-anchor="middle" class="box-title" fill="#6D28D9">Split-Screen Compositor &amp; HUD</text>')
    svg.append('<text x="1875" y="665" text-anchor="middle" class="sub-box-title" fill="#7C3AED">HARDWARE VIDEO PIPELINE</text>')
    svg.append('<text x="1745" y="695" class="label">Left: Raw Camera Feed (160x120)</text>')
    svg.append('<text x="1745" y="715" class="label">Center: Cyan Dividing Laser Line</text>')
    svg.append('<text x="1745" y="735" class="label">Right: Real-Time Sobel Laser Edges</text>')
    svg.append('<text x="1745" y="755" class="label-bold" fill="#7C3AED">Top Banner: Heads-Up Display (HUD)</text>')

    svg.append('<rect x="2045" y="620" width="140" height="150" rx="8" fill="#F8FAFC" stroke="#1E293B" stroke-width="2"/>')
    svg.append('<text x="2115" y="645" text-anchor="middle" class="box-title">VGA Controller</text>')
    svg.append('<text x="2115" y="665" text-anchor="middle" class="subtitle">640x480 @ 60Hz</text>')
    svg.append('<text x="2115" y="700" text-anchor="middle" class="label">Pixel Clk: 25 MHz</text>')
    svg.append('<text x="2115" y="725" text-anchor="middle" class="label-bold">HSYNC, VSYNC</text>')
    svg.append('<text x="2115" y="750" text-anchor="middle" class="label-bold">12-Bit RGB DAC</text>')

    svg.append('<rect x="1540" y="620" width="160" height="150" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.2"/>')
    svg.append('<text x="1620" y="645" text-anchor="middle" class="box-title" fill="#991B1B">Actuator System</text>')
    svg.append('<text x="1620" y="665" text-anchor="middle" class="sub-box-title" fill="#DC2626">AEB Brake &amp; 7-Seg</text>')
    svg.append('<text x="1548" y="695" class="label-bold" fill="#DC2626">RGB1: AEB Brake</text>')
    svg.append('<text x="1548" y="715" class="label-bold" fill="#2563EB">RGB2: V2X Link</text>')
    svg.append('<text x="1548" y="735" class="label">8-Digit 7-Segment</text>')
    svg.append('<text x="1548" y="755" class="label">16 Switches &amp; LEDs</text>')

    svg.append('<line x1="1820" y1="500" x2="1820" y2="620" class="video-line" marker-end="url(#arrow-purple)"/>')
    svg.append('<text x="1825" y="560" class="label" fill="#7C3AED">vga_raw_pixel</text>')

    svg.append('<line x1="2055" y1="580" x2="2055" y2="600" class="vision-line"/>')
    svg.append('<line x1="2055" y1="600" x2="1950" y2="600" class="vision-line"/>')
    svg.append('<line x1="1950" y1="600" x2="1950" y2="620" class="vision-line" marker-end="url(#arrow-green)"/>')
    svg.append('<text x="1955" y="612" class="label" fill="#059669">sobel_edges</text>')

    svg.append('<line x1="2170" y1="465" x2="2195" y2="465" class="vision-line" marker-end="url(#arrow-green)"/>')

    svg.append('<line x1="2265" y1="580" x2="2265" y2="820" class="hazard-line"/>')
    svg.append('<line x1="2265" y1="820" x2="1620" y2="820" class="hazard-line"/>')
    svg.append('<line x1="1620" y1="820" x2="1620" y2="770" class="hazard-line" marker-end="url(#arrow-red)"/>')
    svg.append('<text x="1900" y="812" class="hazard-label">EMERGENCY BRAKE TRIP (AEB ACTIVE &lt; 16.6 ms)</text>')

    # Writeback Mux
    draw_mux(1640, 520, 30, 80, "0", "1")
    svg.append('<text x="1655" y="512" text-anchor="middle" class="sub-box-title">WBMux</text>')
    # MemtoRegW select line
    svg.append('<line x1="1655" y1="240" x2="1655" y2="520" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<text x="1660" y="510" class="ctrl-label">MemtoRegW</text>')

    svg.append('<line x1="1519" y1="545" x2="1640" y2="540" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<line x1="1620" y1="500" x2="1620" y2="580" class="datapath-line"/>')
    svg.append('<line x1="1620" y1="580" x2="1640" y2="580" class="datapath-line" marker-end="url(#arrow)"/>')

    svg.append('<line x1="1670" y1="560" x2="1710" y2="560" class="datapath-line"/>')
    svg.append('<text x="1680" y="552" class="label-bold">ResultW [31:0]</text>')
    draw_bus_slash(1690, 560, "32")

    svg.append('<circle cx="1710" cy="560" r="3.5" fill="#1E293B"/>')
    svg.append('<line x1="1710" y1="560" x2="1710" y2="1010" class="datapath-line"/>')
    svg.append('<line x1="1710" y1="1010" x2="670" y2="1010" class="datapath-line"/>')
    svg.append('<line x1="670" y1="1010" x2="670" y2="640" class="datapath-line"/>')
    svg.append('<line x1="670" y1="640" x2="690" y2="640" class="datapath-line" marker-end="url(#arrow)"/>')
    svg.append('<text x="1100" y="1002" class="label-bold">ResultW Writeback Bus [31:0] (Commits to RegFile WD3 &amp; Forwarding Unit)</text>')
    draw_bus_slash(1350, 1010, "32")

    svg.append('<circle cx="1220" cy="1010" r="3.5" fill="#1E293B"/>')
    svg.append('<line x1="1220" y1="1010" x2="1220" y2="990" class="datapath-line" marker-end="url(#arrow)"/>')

    svg.append('<line x1="975" y1="910" x2="975" y2="540" class="ctrl-line"/>')
    svg.append('<line x1="975" y1="540" x2="990" y2="540" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<line x1="975" y1="640" x2="990" y2="640" class="ctrl-line" marker-end="url(#arrow-blue)"/>')
    svg.append('<text x="960" y="532" class="ctrl-label">FwdA</text>')
    svg.append('<text x="960" y="632" class="ctrl-label">FwdB</text>')

    # Footer Specs Cards (5 Core Subsystems)
    svg.append(f'<rect x="40" y="1050" width="{width-80}" height="350" rx="10" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>')
    svg.append('<text x="65" y="1085" class="box-title" fill="#0F172A">AutoVision-RISC-V Subsystem Architecture &amp; Hardware Technologies:</text>')

    specs = [
        {
            "num": "1", "lead": "DSP MULTIPLIER",
            "title": "RV32M Multiplier &amp; ALU",
            "desc": "1-cycle combinational DSP array multiplier using Artix-7 DSP48E1 slices. Computes MUL, MULH, MULHSU, MULHU with bit-exact 64-bit precision.",
            "color": "#B45309"
        },
        {
            "num": "2", "lead": "NON-RESTORING DIVIDER",
            "title": "RV32M Divider &amp; Hazard Unit",
            "desc": "&le; 34-cycle non-restoring shift-subtract divider FSM computing DIV, DIVU, REM, REMU with zero-cycle bypass on divide-by-zero (x/0=-1) and overflow. Zero-bubble RAW hazard forwarding.",
            "color": "#B91C1C"
        },
        {
            "num": "3", "lead": "CONV2D ACCELERATOR",
            "title": "2D Spatial Conv2D Engine",
            "desc": "Dual circular BRAM line buffers (320 bytes) sliding 3x3 window over 160x120 frame. Parallel MAC computing Sobel gradients &amp; Gaussian smoothing at 1 pixel/cycle (180.0x CPU speedup).",
            "color": "#047857"
        },
        {
            "num": "4", "lead": "VIDEO COMPOSITOR",
            "title": "VGA Controller &amp; Compositor",
            "desc": "Dual-port video BRAM (19.2 KB), 640x480 @ 60Hz 25 MHz timing generator, split-screen compositor (raw camera on left, laser edges on right, HUD on top, cyan divider line).",
            "color": "#6D28D9"
        },
        {
            "num": "5", "lead": "EDGE-AI &amp; SECURITY",
            "title": "Edge Classifier &amp; V2X Cipher",
            "desc": "Real-time shape classifier (STOP, YIELD, SPEED LIMIT), 16-bit Galois LFSR symmetric stream cipher engine, 8-digit multiplexed 7-segment driver, and tri-color RGB brake actuators.",
            "color": "#1D4ED8"
        },
    ]

    col_w = (width - 120) / 5
    for i, sp in enumerate(specs):
        bx = 60 + i * col_w
        svg.append(f'<rect x="{bx}" y="1105" width="{col_w-15}" height="270" rx="6" fill="#FFFFFF" stroke="{sp["color"]}" stroke-width="1.8"/>')
        svg.append(f'<rect x="{bx}" y="1105" width="{col_w-15}" height="32" rx="6" fill="{sp["color"]}"/>')
        svg.append(f'<text x="{bx+(col_w-15)/2}" y="1127" text-anchor="middle" class="label-bold" fill="#FFFFFF">SUBSYSTEM {sp["num"]}: {sp["lead"]}</text>')
        svg.append(f'<text x="{bx+12}" y="1160" class="sub-box-title" fill="{sp["color"]}">{sp["title"]}</text>')

        # Text wrapping
        words = sp["desc"].split(" ")
        lines = []
        curr = ""
        for w in words:
            if len(curr + " " + w) < 30:
                curr += (" " if curr else "") + w
            else:
                lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)

        for l_idx, line in enumerate(lines[:8]):
            svg.append(f'<text x="{bx+12}" y="{1185 + l_idx*18}" class="label">{line}</text>')

    svg.append('</svg>')

    content = "\n".join(svg)
    # Ensure XML well-formedness: escape any dangling unescaped &
    content = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', content)

    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[SUCCESS] Vector SVG generated at: {SVG_PATH}")

def render_png():
    """Renders the SVG to high-res PNG using Playwright and Microsoft Edge."""
    try:
        from playwright.sync_api import sync_playwright
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if not os.path.exists(edge_path):
            edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

        with sync_playwright() as p:
            launch_args = {}
            if os.path.exists(edge_path):
                launch_args["executable_path"] = edge_path

            browser = p.chromium.launch(**launch_args)
            page = browser.new_page(viewport={"width": 2400, "height": 1450}, device_scale_factor=1.5)
            file_url = "file:///" + SVG_PATH.replace("\\", "/")
            page.goto(file_url)
            page.screenshot(path=PNG_PATH)
            browser.close()
            print(f"[SUCCESS] High-Res PNG rendered at: {PNG_PATH}")
            return
    except Exception as e:
        print(f"[WARNING] Playwright render failed: {e}. Falling back to Matplotlib.")

    # Fallback to matplotlib if playwright ever fails
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    fig, ax = plt.subplots(figsize=(24, 14.5), dpi=150)
    ax.set_xlim(0, 2400)
    ax.set_ylim(0, 1450)
    ax.invert_yaxis()
    ax.axis('off')
    ax.text(1200, 725, "Please view docs/autovision_block_diagram.svg for native vector graphics", ha='center', va='center')
    plt.savefig(PNG_PATH, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    generate_svg()
    render_png()
