# Author: Bruce McAlister
# July 25, 2014
# This program returns the tram to its dock when it is run. It is called by the TramControl.py to return
# the tram either when it has finished a run or the bbxm sends an emergency code to the
# control computer that requires the tram to be re-docked. This class opens a modbus connection to the
# motor controller and writes a move signal to the IN register. The program then reads the OUT registers
# of the controller waiting (in a while loop) for the stop switch to send a high signal. When the high
# signal is recieved the computer writes zeros to all IN registers and the program returns True, thereby 
# signalling TramControl.py that the tram is now at position zero.

import minimalmodbus
import serial

class ReturnHome():

    instrument = minimalmodbus.Instrument('COM6', 1)
    instrument.serial.port = 'COM6'         # serial port
    instrument.serial.baudrate = 9600       # baud
    instrument.serial.bitsize = 8
    instrument.serial.parity   = serial.PARITY_EVEN
    instrument.serial.stopbits = 1          # used to indicate the end of data transmission
    instrument.serial.timeout  = 0.1        # time out length in seconds
    instrument.serial.address = 1           # this is the slave address number

    instrument.write_register(125, 16384)   # Writes a clock-wise (RVS) turn signal to the signal in regesters.
                                            # 16384 is 0b0100000000000000. The first position (1) is turn CW.
                                            # use 32768 (0b1000000000000000) to turn CCW
    print("Tram returning to dock...")

    
    # The while loop checks the status of the STOP_D bit. When the bit reads 1 the program writes 0
    # to the input register in order to stop the motor.
    while True:
        stopStatus = bin(instrument.read_register(127))[-5] # Converts motor controller signal-out-regesters' status
                                                            # from decimal to binary and stores the STOP_D bit in stopStatus

        if(stopStatus == '1'):                              # stopBit = 1 for STOP (from docking switch) signal high
            instrument.write_register(125, 0)               # write all low signals to the driver input command (see AR manual p.5-19)
            break
    return True