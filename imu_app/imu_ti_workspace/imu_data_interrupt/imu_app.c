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

#define BUFFER_SIZE 28
#define FREQ 7

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
    CPUdelay(50); //TODO maybe it after testing
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

    uint16_t buffer[BUFFER_SIZE][9]; // buffer 100 readings (3 accel, 3 gyro, 3 mag)

    //uint16_t accel_x, accel_y, accel_z;
    //float accelx, accely, accelz;
    //uint16_t gyro_x, gyro_y, gyro_z;
    //float gyrox, gyroy, gyroz;
    //uint16_t mag_x, mag_y, mag_z;
    uint8_t data[6];

    uint8_t index = 255; //overflow when increment to skip increment for first time
    uint32_t loop_time;
    bool buffer_overflowed = false;
    uint8_t print_index, print_last;
    bool second_half_printed = false;

    uint16_t no_of_prints = 0;

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

    /* buffer data and check for event*/
    // timeout input in Event_pend function controls the buffer time
    loop_time = (uint32_t) 16000000/FREQ; /* in cycles */
    while(1) {
        while(1) {
            if (Event_pend(event, Event_Id_NONE, START_PRINT_EVT, 0)) {break;}

            if(index == BUFFER_SIZE-1) {index = 0; buffer_overflowed=true;}
            else                       {index++;}

            /* Accel */
            SensorMpu9250_accRead((uint16_t*) &data);
            buffer[index][0] = (((int16_t)data[1]) << 8) | data[0];
            buffer[index][1] = (((int16_t)data[3]) << 8) | data[2];
            buffer[index][2] = (((int16_t)data[5]) << 8) | data[4];
            /* Mag */
            SensorMpu9250_gyroRead((uint16_t*) &data);
            buffer[index][3] = (((int16_t)data[1]) << 8) | data[0];
            buffer[index][4] = (((int16_t)data[3]) << 8) | data[2];
            buffer[index][5] = (((int16_t)data[5]) << 8) | data[4];
            /* Gyro */
            SensorMpu9250_gyroRead((uint16_t*) &data);
            buffer[index][6] = (((int16_t)data[1]) << 8) | data[0];
            buffer[index][7] = (((int16_t)data[3]) << 8) | data[2];
            buffer[index][8] = (((int16_t)data[5]) << 8) | data[4];

            CPUdelay(loop_time);
        }

        /* flush the buffer */
        // handling buffer_overflow
        // no overflow {0:last}
        // overflowed  {last+1:BUFFER_SIZE-1 and 0:last}
        if      (!buffer_overflowed) {print_index=0; print_last=index;}
        else if (buffer_overflowed)  {print_index=index+1; print_last=BUFFER_SIZE-1;}
        UART_write(uart, "[", 1);
        while(1) {
            /* Accel */
            UART_write(uart, "{", 1);
            UART_write(uart, "\"a\":[", 5);
            ltoa(buffer[print_index][0], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, ",",  1);
            ltoa(buffer[print_index][1], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, ",",  1);
            ltoa(buffer[print_index][2], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, "],", 2);
            /* Mag */
            UART_write(uart, "\"m\":[", 5);
            ltoa(buffer[print_index][3], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, ",",  1);
            ltoa(buffer[print_index][4], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, ",",  1);
            ltoa(buffer[print_index][5], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, "],",  2);
            /* Gyro */
            UART_write(uart, "\"g\":[", 5);
            ltoa(buffer[print_index][6], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, ",",  1);
            ltoa(buffer[print_index][7], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, ",",  1);
            ltoa(buffer[print_index][8], msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, "]",  1);
            UART_write(uart, "}", 1);

            no_of_prints++;

            print_index++;
            if      (!buffer_overflowed) {if(print_index>print_last) {break;}}
            else if (buffer_overflowed)  {
                if(second_half_printed && print_index>print_last) {
                    break;
                }
                else if(print_index>print_last) {
                    second_half_printed=true; print_index=0; print_last=index;
                }
            }
            UART_write(uart, ",", 1);
        }
        UART_write(uart, "]\r\n", 3);

        //UART_write(uart, "No: ", 4); ltoa(no_of_prints, msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, "\r\n", 2);

        //reset
        no_of_prints = 0;
        index = 255;
        buffer_overflowed = false;
        second_half_printed = false;
    }
}
