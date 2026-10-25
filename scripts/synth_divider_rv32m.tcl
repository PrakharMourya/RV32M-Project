# ==============================================================================
# Vivado Synthesis & Timing Validation Script for divider_rv32m.v
# Group 22 — IIT Guwahati Advanced Computer Architecture
# Target: AMD Xilinx Artix-7 XC7A100T-1CSG324C
# ==============================================================================

create_project -in_memory -part xc7a100tcsg324-1
set_property include_dirs [list rtl/core] [current_fileset]

# Read RTL files
read_verilog rtl/core/divider_rv32m.v

# Synthesize out-of-context
synth_design -top divider_rv32m -part xc7a100tcsg324-1 -mode out_of_context

# Create 50 MHz clock constraint (20 ns period)
create_clock -period 20.000 -name clk [get_ports clk]
set_input_delay -clock clk 0.0 [get_ports [list start funct3* dividend* divisor* rst_n]]
set_output_delay -clock clk 0.0 [get_ports [list quotient* remainder* result* busy done]]

# Report resource utilization and timing
report_utilization -file scripts/divider_rv32m_utilization.rpt
report_timing_summary -file scripts/divider_rv32m_timing.rpt
report_timing -delay_type max -max_paths 5 -file scripts/divider_rv32m_path_timing.rpt

puts "=================================================================="
puts "Vivado Synthesis & Timing Check for divider_rv32m Completed"
puts "=================================================================="
