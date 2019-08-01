# sensorfloor
[![Watch the video](https://flw.mb.tu-dortmund.de/wordpress/wp-content/uploads/2018/07/Rendering1.jpg)](https://flw.mb.tu-dortmund.de/wordpress/wp-content/uploads/2018/06/Boden.mp4)
Management software for PhyNetLab: sensor floor

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