# sensorfloor
[![Watch the video](https://flw.mb.tu-dortmund.de/wordpress/wp-content/uploads/2018/07/Rendering1.jpg)](https://flw.mb.tu-dortmund.de/wordpress/wp-content/uploads/2018/06/Boden.mp4)
Management software for PhyNetLab: sensor floor

## addr_finder
This program will provide you with a output like below. The IEEE address of the node, the ID as to which place of the 15 nodes it takes and finally the 1wire sensor path.
If the ID is 0, there is an error. Causes could be: Wrong hex file loaded, UART connection issues, Sensortag is not fully pushed into the motherboard.

If the IEEE is EE:E:... then device is not going into serial bootloader mode. Causes: UART lines are not correctly soldered, wrong HEX file config.
```
{'IEEE': '00:12:4B:00:0F:2A:45:83', 'id': 1, 'wire1': '/29.EF992F000000'}
{'IEEE': '00:12:4B:00:0F:2A:4C:01', 'id': 2, 'wire1': '/29.4F992F000000'}
{'IEEE': '00:12:4B:00:13:E1:F9:02', 'id': 3, 'wire1': '/29.46992F000000'}
{'IEEE': '00:12:4B:00:0F:2A:4A:03', 'id': 4, 'wire1': '/29.A5992F000000'}
{'IEEE': '00:12:4B:00:13:E1:E9:06', 'id': 5, 'wire1': '/29.279A2F000000'}
{'IEEE': '00:12:4B:00:0F:2A:4F:80', 'id': 6, 'wire1': '/29.8F992F000000'}
{'IEEE': '00:12:4B:00:0F:2A:4E:04', 'id': 7, 'wire1': '/29.D4992F000000'}
{'IEEE': '00:12:4B:00:0F:2A:40:03', 'id': 8, 'wire1': '/29.E4992F000000'}
{'IEEE': '00:12:4B:00:0F:2A:4F:82', 'id': 9, 'wire1': '/29.CC992F000000'}
{'IEEE': '00:12:4B:00:13:E2:07:87', 'id': 10, 'wire1': '/29.DC992F000000'}
{'IEEE': '00:12:4B:00:0F:2A:41:07', 'id': 11, 'wire1': '/29.DF992F000000'}
{'IEEE': '00:12:4B:00:0F:2A:41:06', 'id': 12, 'wire1': '/29.0F9A2F000000'}
{'IEEE': 'EE:EE:EE:EE:EE:EE:EE:EE', 'id': 13, 'wire1': '/29.8C992F000000'}
{'IEEE': '00:12:4B:00:13:E1:FD:07', 'id': 14, 'wire1': '/29.84992F000000'}
{'IEEE': '00:12:4B:00:0D:2A:CE:00', 'id': 15, 'wire1': '/29.CF992F000000'}
ID 0 means the device ID was not found 
IEEE address is EE:EE:... there is problems with bootloader mode.
```

```
//#####################################
// Bootloader settings
//#####################################

#ifndef SET_CCFG_BL_CONFIG_BOOTLOADER_ENABLE
// #define SET_CCFG_BL_CONFIG_BOOTLOADER_ENABLE            0x00       // Disable ROM boot loader
#define SET_CCFG_BL_CONFIG_BOOTLOADER_ENABLE         0xC5       // Enable ROM boot loader
#endif

#ifndef SET_CCFG_BL_CONFIG_BL_LEVEL
#define SET_CCFG_BL_CONFIG_BL_LEVEL                  0x0        // Active low to open boot loader backdoor
// #define SET_CCFG_BL_CONFIG_BL_LEVEL                     0x1        // Active high to open boot loader backdoor
#endif

#ifndef SET_CCFG_BL_CONFIG_BL_PIN_NUMBER
#define SET_CCFG_BL_CONFIG_BL_PIN_NUMBER                0x10       // DIO number for boot loader backdoor
#endif

#ifndef SET_CCFG_BL_CONFIG_BL_ENABLE
#define SET_CCFG_BL_CONFIG_BL_ENABLE                 0xC5       // Enabled boot loader backdoor
// #define SET_CCFG_BL_CONFIG_BL_ENABLE                    0xFF       // Disabled boot loader backdoor
#endif
```