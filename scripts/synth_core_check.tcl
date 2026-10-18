# ==============================================================================
# Vivado Synthesis & Timing Validation Script for riscv_core.v
# Target: AMD Xilinx Artix-7 XC7A100T-1CSG324C
# ==============================================================================

create_project -in_memory -part xc7a100tcsg324-1
set_property include_dirs [list rtl/core] [current_fileset]

# Read all RTL files in rtl/core
read_verilog rtl/core/opcodes.vh
read_verilog rtl/core/alu.v
read_verilog rtl/core/multiplier.v
read_verilog rtl/core/hazard_unit.v
read_verilog rtl/core/if_stage.v
read_verilog rtl/core/id_ex_stage.v
read_verilog rtl/core/wb_stage.v
read_verilog rtl/core/riscv_core.v

# Synthesize out-of-context for 50 MHz target clock
synth_design -top riscv_core -part xc7a100tcsg324-1 -mode out_of_context

# 50 MHz clock constraint (20.000 ns period)
create_clock -period 20.000 -name clk [get_ports clk]

# Report resource utilization and timing
report_utilization -file scripts/core_utilization.rpt
report_timing_summary -file scripts/core_timing.rpt
report_timing -delay_type max -max_paths 10 -file scripts/core_path_timing.rpt

puts "=================================================================="
puts "Vivado riscv_core Synthesis & Timing Check Completed"
puts "=================================================================="
