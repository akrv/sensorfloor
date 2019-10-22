/*
 * Copyright (c) 2015-2019, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 *  ======== uartecho.c ========
 */

#include <stdint.h>
#include <stddef.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

/* Driver Header files */
//#include <ti/drivers/GPIO.h>
#include <ti/drivers/UART.h>

#include "sensors/SensorI2C.h"
#include "sensors/SensorMpu9250.h"

/* Example/Board Header files */
#include "Board.h"


/* Pin driver handles */
static PIN_Handle buttonPinHandle;

/* Global memory storage for a PIN_Config table */
static PIN_State buttonPinState;

/*
 * Application button pin configuration table:
 *   - Buttons interrupts are configured to trigger on falling edge.
 */
PIN_Config buttonPinTable[] = {
    IOID_16  | PIN_INPUT_EN | PIN_PULLUP | PIN_IRQ_NEGEDGE,
    Board_PIN_BUTTON1  | PIN_INPUT_EN | PIN_PULLUP | PIN_IRQ_NEGEDGE,
    PIN_TERMINATE
};

static bool print = false; //TODO change to thread sync

/*  ======== buttonCallbackFxn ======== */
void buttonCallbackFxn(PIN_Handle handle, PIN_Id pinId) {
    uint32_t currVal = 0;

    /* Debounce logic, only toggle if the button is still pushed (low) */
    CPUdelay(8000*50);
    if (!PIN_getInputValue(pinId)) {
        /* Toggle LED based on the button pressed */
        switch (pinId) {
            case IOID_16:
                currVal =  PIN_getOutputValue(Board_PIN_LED0);
                print = true;
                break;

            case Board_PIN_BUTTON1:
                currVal =  PIN_getOutputValue(Board_PIN_LED1);
                print = true;
                break;

            default:
                /* Do nothing */
                break;
        }
    }
}
/*
 *  ======== mainThread ========
 */
void *mainThread(void *arg0)
{
    const char  progStart[] = "Prog Start\r\n";
    const char  ISRInfo[] = "ISR called\r\n";
    const char  printInfo[] = "Print finished\r\n";
    UART_Handle uart;
    UART_Params uartParams;
    char msg[5] = 0;

    uint16_t accel_x, accel_y, accel_z;
    float accelx, accely, accelz;
    uint16_t gyro_x, gyro_y, gyro_z;
    float gyrox, gyroy, gyroz;
    uint16_t mag_x, mag_y, mag_z;
    uint8_t data[6];

    /* Call driver init functions */
    //GPIO_init();
    UART_init();

    /* Configure the LED pin */
    //GPIO_setConfig(Board_GPIO_LED0, GPIO_CFG_OUT_STD | GPIO_CFG_OUT_LOW);

    /* Turn on user LED */
    //GPIO_write(Board_GPIO_LED0, Board_GPIO_LED_ON);

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

    UART_write(uart, progStart, sizeof(progStart));

    if (SensorI2C_open())
    {
        SensorMpu9250_init();           // Gyroscope and accelerometer
        SensorMpu9250_powerOn();
        SensorMpu9250_enable(0x003F);
        //SensorMpu9250_enable(0x0);
        SensorMpu9250_accSetRange(ACC_RANGE_2G);
    }

    /* Loop forever */
    while(1) {
        while(print == false) {
            usleep(1);
        }
        UART_write(uart, ISRInfo, sizeof(ISRInfo));
        print = false;

        SensorMpu9250_accRead((uint16_t*) &data);
        UART_write(uart, "accel,", 6);
        accel_x = (((int16_t)data[1]) << 8) | data[0];
        ltoa(accel_x, msg);
        UART_write(uart, msg, sizeof(msg));
        UART_write(uart, ",", 1);


        accel_y = (((int16_t)data[3]) << 8) | data[2]; ltoa(accel_y, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart,","  , 1);
        accel_z = (((int16_t)data[5]) << 8) | data[4]; ltoa(accel_z, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart,",\r\n", 3);
        //TODO convert in host
        accelx = SensorMpu9250_accConvert(accel_x);
        accely = SensorMpu9250_accConvert(accel_y);
        accelz = SensorMpu9250_accConvert(accel_z);

        SensorMpu9250_gyroRead((uint16_t*) &data);
        UART_write(uart, "gyro,", 5);
        gyro_x = (((int16_t)data[1]) << 8) | data[0]; ltoa(gyro_x, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart, ","  , 1);
        gyro_y = (((int16_t)data[3]) << 8) | data[2]; ltoa(gyro_x, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart, ","  , 1);
        gyro_z = (((int16_t)data[5]) << 8) | data[4]; ltoa(gyro_x, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart, ", \r\n", 3);
        //TODO convert in host
        //gyrox = SensorMpu9250_gyroConvert(gyro_x);
        //gyroy = SensorMpu9250_gyroConvert(gyro_y);
        //gyroz = SensorMpu9250_gyroConvert(gyro_z);

        SensorMpu9250_gyroRead((uint16_t*) &data);
        UART_write(uart, "mag,", 4);
        mag_x = (((int16_t)data[1]) << 8) | data[0]; ltoa(mag_x, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart, ","  , 1);
        mag_y = (((int16_t)data[3]) << 8) | data[2]; ltoa(mag_y, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart, ","  , 1);
        mag_z = (((int16_t)data[5]) << 8) | data[4]; ltoa(mag_z, msg); UART_write(uart, msg, sizeof(msg));  UART_write(uart, ",\r\n", 3);
        //magx = SensorMpu9250_magConvert(mag_x);
        //magy = SensorMpu9250_gyroConvert(mag_y);
        //magz = SensorMpu9250_gyroConvert(mag_z);

        UART_write(uart, printInfo, sizeof(printInfo));
    }
}
