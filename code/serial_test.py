import machine
import time
import struct

sticks = ['PSS_LX', 'PSS_LY', 'PSS_RX', 'PSS_RY']
l_buttons = ['PSB_PAD_UP', 'PSB_PAD_RIGHT', 'PSB_PAD_DOWN', 'PSB_PAD_LEFT', 'PSB_L1', 'PSB_L2', 'PSB_L3']
r_buttons = ['PSB_TRIANGLE', 'PSB_CIRCLE', 'PSB_CROSS', 'PSB_SQUARE', 'PSB_R1', 'PSB_R2', 'PSB_R3']
m_buttons = ['PSB_SELECT', 'PSB_START']

max_time = 50

uart = machine.UART(2, 57600)
uart.init(57600, bits=8, parity=None, stop=1)
commands = {}

def store_s_data(message):
    global commands
    commands = {}
    # joysticks
    for i in range(4):
        lb = message[6] >> 4-i & 1
        commands[sticks[i]] = message[i] << 1 | lb
    # left and right buttons
    for i in range(7):
        commands[l_buttons[i]] = message[4] >> 6 - i & 1
        commands[r_buttons[i]] = message[5] >> 6 - i & 1
    # middle buttons
    commands[m_buttons[0]] = message[6] >> 6
    commands[m_buttons[1]] = message[6] >> 5 & 1

    return


def read_s_data():

    start = time.ticks_ms()

    # search for message start
    while(uart.any() >= 7):
        if(time.ticks_ms() - start > max_time):
            return False
        b = struct.unpack('B', uart.read(1))[0]
        if(not b >> 7):
            continue
        # skip if newer message in serial
        if(uart.any() >= 13):
            uart.read(6)
            continue
        # save message
        b &= 127
        message = [b] + list(struct.unpack('BBBBBB', uart.read(6)))
        store_s_data(message)
        return True
    return False

while(True):
    read_s_data()
    time.sleep_ms(50)
