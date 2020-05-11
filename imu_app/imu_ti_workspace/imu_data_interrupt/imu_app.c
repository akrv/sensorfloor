/***** Includes *****/
#include <stdint.h>
#include <stddef.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#include <ti/sysbios/BIOS.h>
#include <ti/sysbios/knl/Event.h>

#include <ti/drivers/UART.h>

#include "Board.h"

/* MPU Headers */
#include "sensors/SensorI2C.h"
#include "sensors/SensorMpu9250.h"

/* RF Headers */
#include <ti/drivers/rf/RF.h>
#include DeviceFamily_constructPath(driverlib/rf_prop_mailbox.h)
/* Application Header files */
#include "RFQueue.h"
#include "smartrf_settings/smartrf_settings.h"

/***** Defines *****/

/* Packet RX Configuration */
#define DATA_ENTRY_HEADER_SIZE 8  /* Constant header size of a Generic Data Entry */
#define MAX_LENGTH             10 /* Max length byte the radio will accept */
#define NUM_DATA_ENTRIES       2  /* NOTE: Only two data entries supported at the moment */
#define NUM_APPENDED_BYTES     2  /* The Data Entries data field will contain:
                                   * 1 Header byte (RF_cmdPropRx.rxConf.bIncludeHdr = 0x1)
                                   * Max 30 payload bytes
                                   * 1 status byte (RF_cmdPropRx.rxConf.bAppendStatus = 0x1) */

/* Events */
#define START_PRINT_EVT         Event_Id_00
#define RSSI_UPDATED_EVT        Event_Id_01

/* Application definitions */
#define BUFFER_SIZE 24
#define FREQ 6

/***** Variable declarations *****/

/* Button */
static PIN_Handle buttonPinHandle;
static PIN_State buttonPinState;

PIN_Config buttonPinTable[] = {
    IOID_16  | PIN_INPUT_EN | PIN_PULLUP | PIN_IRQ_NEGEDGE,
    Board_PIN_BUTTON1  | PIN_INPUT_EN | PIN_PULLUP | PIN_IRQ_NEGEDGE,
    PIN_TERMINATE
};

/* Events */
static Event_Handle event;
static Event_Params eventParams;
static Event_Struct structEvent;

/* RF */
static RF_Object rfObject;
static RF_Handle rfHandle;

static rfc_propRxOutput_t rxStatistics;

/* Buffer which contains all Data Entries for receiving data.
 * Pragmas are needed to make sure this buffer is 4 byte aligned (requirement from the RF Core) */
#pragma DATA_ALIGN (rxDataEntryBuffer, 4);
static uint8_t
rxDataEntryBuffer[RF_QUEUE_DATA_ENTRY_BUFFER_SIZE(NUM_DATA_ENTRIES,
                                                  MAX_LENGTH,
                                                  NUM_APPENDED_BYTES)];

/* Receive dataQueue for RF Core to fill in data */
static dataQueue_t dataQueue;
//static rfc_dataEntryGeneral_t* currentDataEntry;
//static uint8_t packetLength;
//static uint8_t* packetDataPointer;

//static uint8_t packet[MAX_LENGTH + NUM_APPENDED_BYTES - 1]; /* The length byte is stored in a separate variable */

/***** Callbacks *****/
/*  ======== RX callback function ======== */
void RxCallback(RF_Handle h, RF_CmdHandle ch, RF_EventMask e)
{
    if (e & RF_EventRxEntryDone)
    {
        /* Get current unhandled data entry */
        //currentDataEntry = RFQueue_getDataEntry();

        /* Handle the packet data, located at &currentDataEntry->data:
         * - Length is the first byte with the current configuration
         * - Data starts from the second byte */
        //packetLength      = *(uint8_t*)(&currentDataEntry->data);
        //packetDataPointer = (uint8_t*)(&currentDataEntry->data + 1);

        /* Copy the payload + the status byte to the packet variable */
        //memcpy(packet, packetDataPointer, (packetLength + 1));

        RFQueue_nextEntry();

        Event_post(event, RSSI_UPDATED_EVT);

        RF_postCmd(rfHandle, (RF_Op*)&RF_cmdPropRx, RF_PriorityNormal, &RxCallback, RF_EventRxEntryDone);
    }
}

/*  ======== button callback function ======== */
void buttonCallbackFxn(PIN_Handle handle, PIN_Id pinId) {
    //CPUdelay(30000); //TODO use it to when debugging to prevent button debounce
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
    UART_Handle uart;
    UART_Params uartParams;

    // buffer 100 readings (3 accel, 3 gyro, 3 mag)
    uint16_t imu_buffer[BUFFER_SIZE][6];
    int16_t mag_buffer[BUFFER_SIZE][3];
    int8_t rssi_buffer[BUFFER_SIZE];
    //char msg[5] = 0;

    //uint16_t accel_x, accel_y, accel_z;
    //float accelx, accely, accelz;
    //uint16_t gyro_x, gyro_y, gyro_z;
    //float gyrox, gyroy, gyroz;
    //uint16_t mag_x, mag_y, mag_z;
    uint8_t data[6];
    int16_t data_mag[3];
    uint8_t mag_status;

    uint8_t index = 255; //overflow when increment to skip increment for first time
    uint32_t loop_time, loop_delay_count, delay_count, no_of_loops;
    bool event_status = false;
    bool buffer_overflowed = false;
    uint8_t start_index, flushed_count = 0, last_index;
    uint16_t no_of_readings;
    int i;

    RF_Params rfParams;
    RF_Params_init(&rfParams);

    if( RFQueue_defineQueue(&dataQueue,
                            rxDataEntryBuffer,
                            sizeof(rxDataEntryBuffer),
                            NUM_DATA_ENTRIES,
                            MAX_LENGTH + NUM_APPENDED_BYTES))
    {
        /* Failed to allocate space for all data entries */
        while(1);
    }

    /* Modify CMD_PROP_RX command for application needs */
    /* Set the Data Entity queue for received data */
    RF_cmdPropRx.pQueue = &dataQueue;
    /* Discard ignored packets from Rx queue */
    RF_cmdPropRx.rxConf.bAutoFlushIgnored = 1;
    /* Discard packets with CRC error from Rx queue */
    RF_cmdPropRx.rxConf.bAutoFlushCrcErr = 1;
    /* Implement packet length filtering to avoid PROP_ERROR_RXBUF */
    RF_cmdPropRx.maxPktLen = MAX_LENGTH;
    RF_cmdPropRx.pktConf.bRepeatOk = 1;
    RF_cmdPropRx.pktConf.bRepeatNok = 1;

    RF_cmdPropRx.pOutput = (uint8_t*)&rxStatistics;

    /* Request access to the radio */
    rfHandle = RF_open(&rfObject, &RF_prop, (RF_RadioSetup*)&RF_cmdPropRadioDivSetup, &rfParams);

    /* Set the frequency */
    RF_postCmd(rfHandle, (RF_Op*)&RF_cmdFs, RF_PriorityNormal, NULL, 0);

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
    uartParams.baudRate = 921600;

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

    /* call RX and callback will schedule next Rx cmds */
    RF_postCmd(rfHandle, (RF_Op*)&RF_cmdPropRx, RF_PriorityNormal, &RxCallback, RF_EventRxEntryDone);

    /* buffer data and check for event*/
    // timeout input in Event_pend function controls the buffer time
    loop_time = (uint32_t) 16000000/FREQ; /* in cycles */ /* CPU_delay takes 3 cycles - CPU clock 48MHz - 48MHz/3=16MHz */
    no_of_loops = 1000;
    loop_delay_count = (uint32_t)loop_time/no_of_loops;

    while(1) {
        //UART_write(uart, "loop: ", 6); ltoa(loop_delay_count, msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, "\r\n", 2);

        while(1) {
            if (event_status == true) {break;}

            if(index == BUFFER_SIZE-1) {index = 0; buffer_overflowed=true;}
            else                       {index++;}

            /* Accel */
            SensorMpu9250_accRead((uint16_t*) &data);
            imu_buffer[index][0] = (((int16_t)data[1]) << 8) | data[0];
            imu_buffer[index][1] = (((int16_t)data[3]) << 8) | data[2];
            imu_buffer[index][2] = (((int16_t)data[5]) << 8) | data[4];
            /* Gyro */
            SensorMpu9250_gyroRead((uint16_t*) &data);
            imu_buffer[index][3] = (((int16_t)data[1]) << 8) | data[0];
            imu_buffer[index][4] = (((int16_t)data[3]) << 8) | data[2];
            imu_buffer[index][5] = (((int16_t)data[5]) << 8) | data[4];
            /* Mag */
            mag_status = SensorMpu9250_magRead((int16_t*) &data_mag);
            if (mag_status == MAG_STATUS_OK)
            {
                mag_buffer[index][0] = data_mag[0];
                mag_buffer[index][1] = data_mag[1];
                mag_buffer[index][2] = data_mag[2];
            }
            else
            {
                mag_buffer[index][0] = 0;
                mag_buffer[index][1] = 0;
                mag_buffer[index][2] = 0;
            }

            /* RSSI */
            if (Event_pend(event, Event_Id_NONE, RSSI_UPDATED_EVT, 0)) { rssi_buffer[index] = rxStatistics.lastRssi; }
            else                                                       { rssi_buffer[index] = 0; }

            for(delay_count = 0; delay_count < no_of_loops; delay_count++)
            {
                if (Event_pend(event, Event_Id_NONE, START_PRINT_EVT, 0))
                {
                    event_status = true;
                    break;
                } else  {
                    CPUdelay(loop_delay_count);
                }
            }
        }

        /* flush the buffer */
        // handling buffer_overflow
        // no overflow {0:last}
        // overflowed  {last+1:BUFFER_SIZE-1 and 0:last}
        if      (!buffer_overflowed) {start_index=0; last_index=index; no_of_readings = index+1; }
        else if (buffer_overflowed)  {start_index=index+1; no_of_readings = BUFFER_SIZE; }
        i = start_index;

        UART_write(uart, "[[", 2);

        UART_write(uart, &no_of_readings, 2);

        while(1)
        {
            /* Accel */
            UART_write(uart, &imu_buffer[i][0], 2);
            UART_write(uart, &imu_buffer[i][1], 2);
            UART_write(uart, &imu_buffer[i][2], 2);
            /* Gyro */
            UART_write(uart, &imu_buffer[i][3], 2);
            UART_write(uart, &imu_buffer[i][4], 2);
            UART_write(uart, &imu_buffer[i][5], 2);
            /* Mag */
            UART_write(uart, &mag_buffer[i][0], 2);
            UART_write(uart, &mag_buffer[i][1], 2);
            UART_write(uart, &mag_buffer[i][2], 2);
            /* RSSI */
            UART_write(uart, &rssi_buffer[i], 1);

            i++;

            // no overflow
            if (!buffer_overflowed && i == last_index+1) {break;}
            // overflow
            if (buffer_overflowed && i==BUFFER_SIZE) {i = 0;}
            flushed_count++;
            if (flushed_count == BUFFER_SIZE) {break;}
        }
        UART_write(uart, "]]", 2);
        UART_write(uart, "\n", 2);

        //UART_write(uart, "No: ", 4); ltoa(no_of_prints, msg); UART_write(uart, msg, strlen(msg)); UART_write(uart, "\r\n", 2);

        //reset
        event_status = false;
        index = 255;
        start_index = 0;
        flushed_count = 0;
        buffer_overflowed = false;
    }
}
