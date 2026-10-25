# ==============================================================================
# Vivado Synthesis & Timing Validation Script for rv32m_core.v
# Group 22 — IIT Guwahati Advanced Computer Architecture
# Target: AMD Xilinx Artix-7 XC7A100T-1CSG324C
# ==============================================================================

create_project -in_memory -part xc7a100tcsg324-1
set_property include_dirs [list rtl/core] [current_fileset]

# Read RTL files
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

# Synthesize out-of-context
synth_design -top rv32m_core -part xc7a100tcsg324-1 -mode out_of_context

# Create 50 MHz clock constraint (20 ns period)
create_clock -period 20.000 -name clk [get_ports clk]
set_input_delay -clock clk 0.0 [get_ports [list reset_n imem_data* dmem_rdata* coproc_busy]]
set_output_delay -clock clk 0.0 [get_ports [list imem_addr* dmem_read_req dmem_write_req dmem_byte_enable* dmem_addr* dmem_wdata* debug_*]]

# Report complete resource utilization and timing
report_utilization -file scripts/rv32m_core_utilization.rpt
report_timing_summary -file scripts/rv32m_core_timing.rpt
report_timing -delay_type max -max_paths 10 -file scripts/rv32m_core_path_timing.rpt

puts "=================================================================="
puts "Vivado Synthesis & Timing Check for rv32m_core Completed"
puts "=================================================================="
