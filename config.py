PIO_0 = "CS_S1"   # mux choose bl_uart
PIO_1 = "FET"     # power cycle the STK
PIO_2 = "DP12"    # GPIO DP12 of CC1350
PIO_3 = "RST"     # JTAG RST of CC1350
PIO_4 = "MUX_EN"  # HC/!E MUX enable to control who talk on the bus
PIO_5 = "DP11"    # GPIO DP11 of CC1350
PIO_6 = "RS422_EN"# DE_TVHD enable transmit
PIO_7 = "RS422_RE"# !RE_TVHD enable receive


from lightfinder.config import sensor_path as strip_path_order
