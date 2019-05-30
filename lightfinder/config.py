PIO_0 = "CS_S1"   # mux choose bl_uart
PIO_1 = "FET"     # power cycle the STK
PIO_2 = "DP12"    # GPIO DP12 of CC1350
PIO_3 = "RST"     # JTAG RST of CC1350
PIO_4 = "MUX_EN"  # HC/!E MUX enable to control who talk on the bus
PIO_5 = "DP11"    # GPIO DP11 of CC1350
PIO_6 = "RS422_EN"# DE_TVHD enable transmit
PIO_7 = "RS422_RE"# !RE_TVHD enable receive


sensor_path = ['/29.CF992F000000',  # closest to the RPi
               '/29.84992F000000',
               '/29.8C992F000000',
               '/29.0F9A2F000000',
               '/29.DF992F000000',
               '/29.DC992F000000',
               '/29.CC992F000000',
               '/29.E4992F000000',
               '/29.D4992F000000',
               '/29.8F992F000000',
               '/29.279A2F000000',
               '/29.A5992F000000',
               '/29.46992F000000',
               '/29.4F992F000000',
               '/29.EF992F000000'   # farthest to the RPi
               ]
