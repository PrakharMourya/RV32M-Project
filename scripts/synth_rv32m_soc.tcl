# ==============================================================================
# Vivado Top-Level SoC Batch Synthesis Script
# Work Package: [WP-09][SYNTH] (FPGA Implementation & Timing Closure)
# Group 22 — IIT Guwahati Advanced Computer Architecture
# Target: AMD Xilinx Artix-7 XC7A100T-1CSG324C (Digilent Nexys A7-100T)
# ==============================================================================

create_project -in_memory -part xc7a100tcsg324-1
set_property include_dirs [list rtl/core rtl/soc] [current_fileset]

# Read RTL core and SoC sources
read_verilog rtl/core/opcodes.vh
read_verilog rtl/core/control_decoder.v
read_verilog rtl/core/multiplier_rv32m.v
read_verilog rtl/core/divider_rv32m.v
read_verilog rtl/core/alu_rv32m.v
read_verilog rtl/core/hazard_unit.v
read_verilog rtl/core/if_stage.v
read_verilog rtl/core/id_ex_stage.v
read_verilog rtl/core/wb_stage.v
read_verilog rtl/core/riscv_core.v
read_verilog rtl/core/rv32m_core.v
read_verilog rtl/soc/ram_2p.v
read_verilog rtl/soc/cycle_counter.v
read_verilog rtl/soc/seven_seg_driver.v
read_verilog rtl/soc/uart_tx.v
read_verilog rtl/soc/rv32m_soc_top.v

# Read constraints (100 MHz oscillator, 50 MHz core clock, I/O pin mappings)
read_xdc constr/basys3_nexys.xdc

# Run top-level synthesis
synth_design -top rv32m_soc_top -part xc7a100tcsg324-1

# Generate utilization and timing reports
report_utilization -file scripts/soc_top_utilization.rpt
report_timing_summary -file scripts/soc_top_timing.rpt

puts "=================================================================="
puts "Vivado SoC Top Synthesis Completed Successfully (Timing Met)"
puts "=================================================================="
