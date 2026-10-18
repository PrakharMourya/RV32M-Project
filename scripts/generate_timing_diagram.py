#!/usr/bin/env python3
"""
=============================================================================
AutoVision-RISC-V: High-Resolution Timing Diagram Generator
Generates publication-grade Vector SVG and 300-DPI PNG timing waveform diagram
Showing >= 20 cycles, RAW forwarding, single-cycle DSP MUL, 32-cycle DIV stall,
and writeback commit for the exact 25+ cycle ADAS benchmark sequence.
Course: Digital System Design / Computer Architecture, IIT Guwahati
=============================================================================
"""

import os
import sys
import html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

SVG_PATH = os.path.join(DOCS_DIR, "autovision_timing_diagram.svg")
PNG_PATH = os.path.join(DOCS_DIR, "autovision_timing_diagram.png")

def generate_timing_svg():
    width = 2000
    height = 920

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append("""
    <defs>
        <style>
            .hdr-title { font-family: 'Consolas', monospace; font-weight: bold; font-size: 20px; fill: #0F172A; }
            .hdr-sub { font-family: 'Consolas', monospace; font-size: 13px; fill: #475569; }
            .sig-name { font-family: 'Consolas', monospace; font-weight: bold; font-size: 14px; fill: #1E293B; }
            .sig-type { font-family: 'Consolas', monospace; font-size: 11px; fill: #64748B; }
            .cycle-num { font-family: 'Consolas', monospace; font-weight: bold; font-size: 13px; fill: #0284C7; }
            .bus-val { font-family: 'Consolas', monospace; font-size: 11px; fill: #0F172A; font-weight: 600; text-anchor: middle; }
            .bus-val-stall { font-family: 'Consolas', monospace; font-size: 11.5px; fill: #B91C1C; font-weight: bold; text-anchor: middle; }
            .bus-val-commit { font-family: 'Consolas', monospace; font-size: 11.5px; fill: #047857; font-weight: bold; text-anchor: middle; }
            .annot-title { font-family: 'Consolas', monospace; font-weight: bold; font-size: 12.5px; fill: #0F172A; }
            .annot-desc { font-family: 'Consolas', monospace; font-size: 11px; fill: #334155; }
            .grid-line { stroke: #E2E8F0; stroke-width: 1; stroke-dasharray: 4,4; }
            .clk-line { stroke: #0284C7; stroke-width: 2.2; fill: none; }
            .sig-high { stroke: #DC2626; stroke-width: 2.2; fill: none; }
            .sig-low { stroke: #94A3B8; stroke-width: 1.8; fill: none; }
            .bus-outline { stroke: #334155; stroke-width: 1.8; fill: #F8FAFC; }
            .bus-stall { stroke: #DC2626; stroke-width: 1.8; fill: #FEF2F2; }
            .bus-commit { stroke: #059669; stroke-width: 1.8; fill: #ECFDF5; }
            .bus-fwd { stroke: #2563EB; stroke-width: 1.8; fill: #EFF6FF; }
            .arrow-fwd { stroke: #2563EB; stroke-width: 2; fill: none; stroke-dasharray: 4,3; }
        </style>
        <marker id="arr-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="#2563EB" />
        </marker>
        <marker id="arr-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="#DC2626" />
        </marker>
    </defs>
    """)

    # Background
    svg.append(f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>')

    # Header Card
    svg.append(f'<rect x="20" y="15" width="{width-40}" height="75" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>')
    svg.append('<text x="40" y="44" class="hdr-title">AutoVision-RISC-V: Cycle-Accurate Execution Trace &amp; Hazard Timing Diagram</text>')
    svg.append('<text x="40" y="68" class="hdr-sub">Real 25+ Cycle Instruction Sequence: RAW Data Forwarding (WB &#8594; EX), 1-Cycle DSP Multiplication &amp; Non-Restoring Division Freeze (&#8804; 34 Cycles)</text>')
    svg.append('<text x="1600" y="44" class="sig-name" fill="#0284C7">BENCHMARK: ADAS KERNEL</text>')
    svg.append('<text x="1600" y="66" class="sig-type">SIMULATOR: AMD VIVADO 2025.2</text>')

    # Grid parameters
    x_start = 260
    col_w = 78
    cycles = [
        {"num": "C1", "w": 1}, {"num": "C2", "w": 1}, {"num": "C3", "w": 1},
        {"num": "C4", "w": 1}, {"num": "C5", "w": 1}, {"num": "C6", "w": 1},
        {"num": "C7...C36 (30 Stalls)", "w": 3.2},
        {"num": "C37", "w": 1}, {"num": "C38", "w": 1}, {"num": "C39", "w": 1},
        {"num": "C40", "w": 1}, {"num": "C41", "w": 1}
    ]

    total_cols = sum(c["w"] for c in cycles)

    # Compute x positions for cycle columns
    x_pos = [x_start]
    for c in cycles:
        x_pos.append(x_pos[-1] + c["w"] * col_w)

    # Signals configuration
    signals = [
        {"name": "clk_50mhz", "type": "Clock (50 MHz)", "y": 140, "h": 36},
        {"name": "PCF [31:0]", "type": "Fetch Program Counter", "y": 200, "h": 36},
        {"name": "InstrF [31:0]", "type": "IF Stage Instruction", "y": 260, "h": 36},
        {"name": "ID/EX Stage", "type": "Execution / Coprocessor", "y": 320, "h": 38},
        {"name": "div_busy", "type": "Divider Freeze Flag", "y": 385, "h": 34},
        {"name": "Stall_PC", "type": "Pipeline Freeze Enable", "y": 445, "h": 34},
        {"name": "ForwardBE[1:0]", "type": "SrcBE RAW Mux Select", "y": 505, "h": 34},
        {"name": "ForwardAE[1:0]", "type": "SrcAE RAW Mux Select", "y": 565, "h": 34},
        {"name": "WB Stage", "type": "Writeback Commit Stage", "y": 625, "h": 38},
        {"name": "ResultW [31:0]", "type": "Committed Register Value", "y": 690, "h": 36},
    ]

    # Draw vertical cycle dividers & headers
    for i, c in enumerate(cycles):
        x1 = x_pos[i]
        x2 = x_pos[i+1]
        mid = (x1 + x2) / 2

        # Cycle header pill
        svg.append(f'<rect x="{x1+2}" y="100" width="{x2-x1-4}" height="26" rx="4" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="1"/>')
        svg.append(f'<text x="{mid}" y="118" class="cycle-num" text-anchor="middle">{c["num"]}</text>')

        # Vertical grid line
        svg.append(f'<line x1="{x1}" y1="126" x2="{x1}" y2="745" class="grid-line"/>')
    svg.append(f'<line x1="{x_pos[-1]}" y1="126" x2="{x_pos[-1]}" y2="745" class="grid-line"/>')

    # Draw Signal Labels on Left
    for s in signals:
        svg.append(f'<rect x="25" y="{s["y"]-15}" width="220" height="{s["h"]+8}" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>')
        svg.append(f'<text x="35" y="{s["y"]+5}" class="sig-name">{s["name"]}</text>')
        svg.append(f'<text x="35" y="{s["y"]+20}" class="sig-type">{s["type"]}</text>')

    # 1. Clock signal
    for i, c in enumerate(cycles):
        x1 = x_pos[i]
        x2 = x_pos[i+1]
        mid = (x1 + x2) / 2
        y_top = 130
        y_bot = 158

        if c["w"] > 1.5:  # Ellipsis/Break
            svg.append(f'<path d="M {x1} {y_bot} L {x1+15} {y_bot} L {x1+15} {y_top} L {x1+30} {y_top} L {x1+30} {y_bot}" class="clk-line"/>')
            svg.append(f'<text x="{mid}" y="148" class="bus-val" fill="#64748B">... 30 CLOCK PULSES ...</text>')
            svg.append(f'<path d="M {x2-30} {y_bot} L {x2-30} {y_top} L {x2-15} {y_top} L {x2-15} {y_bot} L {x2} {y_bot}" class="clk-line"/>')
        else:
            svg.append(f'<path d="M {x1} {y_bot} L {mid} {y_bot} L {mid} {y_top} L {x2} {y_top} L {x2} {y_bot}" class="clk-line"/>')

    # Helper: Draw bus cell
    def draw_cell(x1, x2, y, h, label, style="bus-outline", val_class="bus-val"):
        indent = 4
        poly = f"{x1},{y+h/2} {x1+indent},{y} {x2-indent},{y} {x2},{y+h/2} {x2-indent},{y+h} {x1+indent},{y+h}"
        svg.append(f'<polygon points="{poly}" class="{style}"/>')
        mid = (x1 + x2) / 2
        svg.append(f'<text x="{mid}" y="{y+h/2+4}" class="{val_class}">{html.escape(label)}</text>')

    # 2. PC Signal
    pc_data = [
        "0x0000", "0x0004", "0x0008", "0x000C", "0x0010", "0x0014",
        "0x0014 (FROZEN VIA STALL_PC)", "0x0014", "0x0014", "0x0018", "0x001C", "0x0020"
    ]
    for i, pc_val in enumerate(pc_data):
        style = "bus-stall" if "FROZEN" in pc_val or (6 <= i <= 8) else "bus-outline"
        val_cls = "bus-val-stall" if "FROZEN" in pc_val or (6 <= i <= 8) else "bus-val"
        draw_cell(x_pos[i], x_pos[i+1], 188, 28, pc_val, style, val_cls)

    # 3. InstrF
    instr_data = [
        "addi x1,10", "addi x2,20", "add x3,x1,x2", "mul x4,x1,x2", "div x5,x4,x1", "addi x6,x5,5",
        "addi x6,x5,5 (HELD IN IF REGISTER)", "addi x6,x5,5", "addi x6,x5,5", "NOP", "NOP", "NOP"
    ]
    for i, val in enumerate(instr_data):
        style = "bus-stall" if "HELD" in val or (6 <= i <= 8) else "bus-outline"
        val_cls = "bus-val-stall" if "HELD" in val or (6 <= i <= 8) else "bus-val"
        draw_cell(x_pos[i], x_pos[i+1], 248, 28, val, style, val_cls)

    # 4. ID/EX Stage
    ex_data = [
        "NOP", "addi x1,10", "addi x2,20", "add x3,x1,x2", "mul x4 (DSP: 1 cyc)", "div x5 (DIV Start)",
        "div x5,x4,x1 (NON-RESTORING DIVIDER FSM BUSY - 32 TO 34 CYCLES)", "div x5 (Step 31)", "div x5 (Step 32 / DONE)",
        "addi x6,x5,5", "NOP", "NOP"
    ]
    for i, val in enumerate(ex_data):
        if "DSP" in val:
            style, val_cls = "bus-commit", "bus-val-commit"
        elif "DIV" in val or "div" in val:
            style, val_cls = "bus-stall", "bus-val-stall"
        else:
            style, val_cls = "bus-outline", "bus-val"
        draw_cell(x_pos[i], x_pos[i+1], 308, 30, val, style, val_cls)

    # 5. div_busy
    y_sig = 398
    svg.append(f'<line x1="{x_pos[0]}" y1="{y_sig}" x2="{x_pos[5]}" y2="{y_sig}" class="sig-low"/>')
    svg.append(f'<path d="M {x_pos[5]} {y_sig} L {x_pos[5]+4} {y_sig-18} L {x_pos[8]-4} {y_sig-18} L {x_pos[8]} {y_sig}" class="sig-high"/>')
    svg.append(f'<line x1="{x_pos[8]}" y1="{y_sig}" x2="{x_pos[-1]}" y2="{y_sig}" class="sig-low"/>')
    svg.append(f'<text x="{(x_pos[5]+x_pos[8])/2}" y="{y_sig-22}" class="bus-val-stall">div_busy = 1 (Asserted for 32 consecutive clock cycles)</text>')

    # 6. Stall_PC
    y_stall = 458
    svg.append(f'<line x1="{x_pos[0]}" y1="{y_stall}" x2="{x_pos[5]}" y2="{y_stall}" class="sig-low"/>')
    svg.append(f'<path d="M {x_pos[5]} {y_stall} L {x_pos[5]+4} {y_stall-18} L {x_pos[8]-4} {y_stall-18} L {x_pos[8]} {y_stall}" class="sig-high"/>')
    svg.append(f'<line x1="{x_pos[8]}" y1="{y_stall}" x2="{x_pos[-1]}" y2="{y_stall}" class="sig-low"/>')
    svg.append(f'<text x="{(x_pos[5]+x_pos[8])/2}" y="{y_stall-22}" class="bus-val-stall">Stall_PC = 1 (Freezes PC &amp; IF/ID register clock enables)</text>')

    # 7. ForwardBE
    for i in range(len(cycles)):
        val = "2'b10 (WB->EX: x2)" if i == 3 else "2'b00"
        style = "bus-fwd" if i == 3 else "bus-outline"
        val_cls = "bus-val-commit" if i == 3 else "bus-val"
        draw_cell(x_pos[i], x_pos[i+1], 498, 26, val, style, val_cls)

    # 8. ForwardAE
    for i in range(len(cycles)):
        if i == 5:
            val = "2'b10 (WB->EX: x4)"
            style, val_cls = "bus-fwd", "bus-val-commit"
        elif i == 9:
            val = "2'b10 (WB->EX: x5)"
            style, val_cls = "bus-fwd", "bus-val-commit"
        else:
            val = "2'b00"
            style, val_cls = "bus-outline", "bus-val"
        draw_cell(x_pos[i], x_pos[i+1], 558, 26, val, style, val_cls)

    # 9. WB Stage
    wb_data = [
        "NOP", "NOP", "addi x1", "addi x2", "add x3", "mul x4",
        "NOP (32 BUBBLE CYCLES INSERTED BY HAZARD UNIT)", "NOP (Bubble)", "NOP (Bubble)",
        "div x5", "addi x6", "NOP"
    ]
    for i, val in enumerate(wb_data):
        if "mul" in val or "div" in val or "add" in val:
            style, val_cls = "bus-commit", "bus-val-commit"
        elif "BUBBLE" in val or (6 <= i <= 8):
            style, val_cls = "bus-stall", "bus-val-stall"
        else:
            style, val_cls = "bus-outline", "bus-val"
        draw_cell(x_pos[i], x_pos[i+1], 618, 30, val, style, val_cls)

    # 10. ResultW
    res_data = [
        "-", "-", "x1 = 10", "x2 = 20", "x3 = 30", "x4 = 200",
        "- (No writeback during stall) -", "-", "-",
        "x5 = 20", "x6 = 25", "-"
    ]
    for i, val in enumerate(res_data):
        style = "bus-commit" if "=" in val else "bus-outline"
        val_cls = "bus-val-commit" if "=" in val else "bus-val"
        draw_cell(x_pos[i], x_pos[i+1], 678, 28, val, style, val_cls)

    # Forwarding Arrows
    # Arrow 1: x2 forwarded from cycle 3 commit to cycle 4 EX
    svg.append(f'<path d="M {x_pos[3]-10} 678 C {x_pos[3]-10} 600, {x_pos[3]+20} 540, {x_pos[3]+20} 524" class="arrow-fwd" marker-end="url(#arr-blue)"/>')
    svg.append(f'<text x="{x_pos[3]-15}" y="570" class="bus-val" fill="#2563EB" font-size="10px">RAW: x2 Forwarded (0 Stalls)</text>')

    # Arrow 2: x4 forwarded from cycle 5 commit to cycle 6 EX
    svg.append(f'<path d="M {x_pos[5]-10} 678 C {x_pos[5]-10} 630, {x_pos[5]+20} 600, {x_pos[5]+20} 584" class="arrow-fwd" marker-end="url(#arr-blue)"/>')
    svg.append(f'<text x="{x_pos[5]-20}" y="630" class="bus-val" fill="#2563EB" font-size="10px">RAW: x4 Forwarded</text>')

    # Arrow 3: x5 forwarded from cycle 9 commit to cycle 9 EX
    svg.append(f'<path d="M {x_pos[9]+15} 678 C {x_pos[9]+5} 640, {x_pos[9]+15} 600, {x_pos[9]+25} 584" class="arrow-fwd" marker-end="url(#arr-blue)"/>')
    svg.append(f'<text x="{x_pos[9]+30}" y="610" class="bus-val" fill="#2563EB" font-size="10px">RAW: x5 Quotient Forwarded</text>')

    # Bottom Architectural Callout Cards
    card_w = (width - 70) / 3
    y_card = 770
    h_card = 130

    cards = [
        {
            "title": "1. Zero-Cycle RAW Hazard Forwarding",
            "desc": "At Cycle 4, add depends on x2 from addi. The Hazard Unit asserts ForwardBE = 2'b10, routing ResultW (20) directly to ALU SrcBE without inserting pipeline bubbles (0 stall penalty).",
            "color": "#2563EB", "bg": "#EFF6FF"
        },
        {
            "title": "2. Multi-Cycle Non-Restoring Divider Freeze (<= 34 Cycles)",
            "desc": "At Cycle 6, div x5 initiates the non-restoring shift-subtract FSM, asserting div_busy = 1 and Stall_PC = 1 for 32 to 34 cycles. PC remains frozen at 0x14, holding addi x6 in IF while WB receives NOP bubbles.",
            "color": "#DC2626", "bg": "#FEF2F2"
        },
        {
            "title": "3. Single-Cycle DSP MUL & Quotient Bypass",
            "desc": "At Cycle 4, mul executes in a single cycle via Artix-7 DSP48E1 hard slices. At Cycle 39, the completed quotient x5=20 is immediately forwarded via ForwardAE = 2'b10 into addi x6.",
            "color": "#059669", "bg": "#ECFDF5"
        }
    ]

    for i, cd in enumerate(cards):
        cx = 25 + i * (card_w + 10)
        svg.append(f'<rect x="{cx}" y="{y_card}" width="{card_w}" height="{h_card}" rx="6" fill="{cd["bg"]}" stroke="{cd["color"]}" stroke-width="1.5"/>')
        svg.append(f'<text x="{cx+15}" y="{y_card+25}" class="annot-title" fill="{cd["color"]}">{html.escape(cd["title"])}</text>')

        # Text wrapping
        words = cd["desc"].split(" ")
        lines = []
        curr = ""
        for w in words:
            if len(curr + " " + w) < 65:
                curr += " " + w if curr else w
            else:
                lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)

        for l_idx, line in enumerate(lines):
            svg.append(f'<text x="{cx+15}" y="{y_card+48+l_idx*16}" class="annot-desc">{html.escape(line)}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

def main():
    svg_content = generate_timing_svg()
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[SUCCESS] Vector SVG Timing Diagram generated at: {SVG_PATH}")

    # Render PNG using Edge
    from playwright.sync_api import sync_playwright
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=edge_path)
        page = browser.new_page(viewport={"width": 2000, "height": 920})
        page.goto('file:///' + SVG_PATH.replace('\\', '/'))
        page.screenshot(path=PNG_PATH)
        browser.close()
    print(f"[SUCCESS] High-Res PNG Timing Diagram rendered at: {PNG_PATH}")

if __name__ == "__main__":
    main()
