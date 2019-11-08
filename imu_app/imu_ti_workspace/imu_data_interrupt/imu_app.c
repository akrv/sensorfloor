/* Includes */
#include <stdint.h>
#include <stddef.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#include <ti/sysbios/BIOS.h>
#include <ti/sysbios/knl/Event.h>

#include <ti/drivers/UART.h>

#include "sensors/SensorI2C.h"
#include "sensors/SensorMpu9250.h"

#include "Board.h"


#define START_PRINT_EVT         Event_Id_00

/* Variable Declaration */
static PIN_Handle buttonPinHandle;
static PIN_State buttonPinState;

PIN_Config buttonPinTable[] = {
    IOID_16  | PIN_INPUT_EN | PIN_PULLUP | PIN_IRQ_NEGEDGE,
    Board_PIN_BUTTON1  | PIN_INPUT_EN | PIN_PULLUP | PIN_IRQ_NEGEDGE,
    PIN_TERMINATE
};

static Event_Handle event;
static Event_Params eventParams;
static Event_Struct structEvent;

/*  ======== buttonCallbackFxn ======== */
void buttonCallbackFxn(PIN_Handle handle, PIN_Id pinId) {
    /* Debounce logic, only toggle if the button is still pushed */
    CPUdelay(5);
    if (!PIN_getInputValue(pinId)) {
        switch (pinId) {
            case IOID_16:
                Event_post(event, START_PRINT_EVT);
                break;
            case Board_PIN_BUTTON1:
                Event_post(event, START_PRINT_EVT);
                break;
            default:
                break;
        }
    }
}
/*
 *  ======== mainThread ========
 */
void *mainThread(void *arg0)
{
    //const char  progStart[] = "Prog Start\r\n";
    //const char  ISRInfo[] = "ISR called\r\n";
    //const char  printInfo[] = "Print finished\r\n";
    UART_Handle uart;
    UART_Params uartParams;
    char msg[5] = 0;

    uint16_t accel_x, accel_y, accel_z;
    float accelx, accely, accelz;
    uint16_t gyro_x, gyro_y, gyro_z;
    float gyrox, gyroy, gyroz;
    uint16_t mag_x, mag_y, mag_z;
    uint8_t data[6];

    Event_Params_init(&eventParams);
    Event_construct(&structEvent, &eventParams);
    event = Event_handle(&structEvent);

    /* Call driver init functions */
    UART_init();

    /* Create a UART with data processing off. */
    UART_Params_init(&uartParams);
    uartParams.writeDataMode = UART_DATA_BINARY;
    uartParams.readDataMode = UART_DATA_BINARY;
    uartParams.readReturnMode = UART_RETURN_FULL;
    uartParams.readEcho = UART_ECHO_OFF;
    uartParams.baudRate = 115200;

    uart = UART_open(Board_UART0, &uartParams);

    if (uart == NULL) {
        /* UART_open() failed */
        while (1);
    }

    buttonPinHandle = PIN_open(&buttonPinState, buttonPinTable);
    if(!buttonPinHandle) {
       /* Error initializing button pins */
       while(1);
    }

    /* Setup callback for button pins */
    if (PIN_registerIntCb(buttonPinHandle, &buttonCallbackFxn) != 0) {
       /* Error registering button callback function */
       while(1);
    }

    //UART_write(uart, progStart, sizeof(progStart));

    if (SensorI2C_open())
    {
        SensorMpu9250_init();           // Gyroscope and accelerometer
        SensorMpu9250_powerOn();
        SensorMpu9250_enable(0x003F); //enable all Axes for acc and gyro
        SensorMpu9250_accSetRange(ACC_RANGE_2G);
    }

    /* Loop forever */
    while(1) {
        Event_pend(event,
                          Event_Id_NONE,
                          START_PRINT_EVT,
                          BIOS_WAIT_FOREVER);
        //UART_write(uart, ISRInfo, sizeof(ISRInfo));

        /* Accel */
        SensorMpu9250_accRead((uint16_t*) &data);
        UART_write(uart, "accel,", 6);
        accel_x = (((int16_t)data[1]) << 8) | data[0]; ltoa(accel_x, msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, ",", 1);
        accel_y = (((int16_t)data[3]) << 8) | data[2]; ltoa(accel_y, msg); UART_write(uart, msg, strlen(msg)); UART_write(uart,","  , 1);
        accel_z = (((int16_t)data[5]) << 8) | data[4]; ltoa(accel_z, msg); UART_write(uart, msg, strlen(msg)); UART_write(uart,",\r\n", 3);
        //TODO comment out after debugging and convert in host
        accelx = SensorMpu9250_accConvert(accel_x);
        accely = SensorMpu9250_accConvert(accel_y);
        accelz = SensorMpu9250_accConvert(accel_z);

        /* Gyro */
        SensorMpu9250_gyroRead((uint16_t*) &data);
        UART_write(uart, "gyro,", 5);
        gyro_x = (((int16_t)data[1]) << 8) | data[0]; ltoa(gyro_x, msg); UART_write(uart, msg, strlen(msg));  UART_write(uart, ","  , 1);
        gyro_y = (((int16_t)data[3]) << 8) | data[2]; ltoa(gyro_y, msg); UART_write(uart, msg, strlen(msg));  UART_write(uart, ","  , 1);
        gyro_z = (((int16_t)data[5]) << 8) | data[4]; ltoa(gyro_z, msg); UART_write(uart, msg, strlen(msg));  UART_write(uart, ", \r\n", 3);
        //TODO comment out after debugging and convert in host
        gyrox = SensorMpu9250_gyroConvert(gyro_x);
        gyroy = SensorMpu9250_gyroConvert(gyro_y);
        gyroz = SensorMpu9250_gyroConvert(gyro_z);

        /* Mag */
        SensorMpu9250_gyroRead((uint16_t*) &data);
        UART_write(uart, "mag,", 4);
        mag_x = (((int16_t)data[1]) << 8) | data[0]; ltoa(mag_x, msg); UART_write(uart, msg, strlen(msg));  UART_write(uart, ","  , 1);
        mag_y = (((int16_t)data[3]) << 8) | data[2]; ltoa(mag_y, msg); UART_write(uart, msg, strlen(msg));  UART_write(uart, ","  , 1);
        mag_z = (((int16_t)data[5]) << 8) | data[4]; ltoa(mag_z, msg); UART_write(uart, msg, strlen(msg));  UART_write(uart, ",\r\n", 3);
        //magx = SensorMpu9250_magConvert(mag_x);
        //magy = SensorMpu9250_gyroConvert(mag_y);
        //magz = SensorMpu9250_gyroConvert(mag_z);

        //UART_write(uart, printInfo, sizeof(printInfo));
    }
}
