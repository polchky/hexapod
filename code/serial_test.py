import machine
import time
import struct

sticks = ['PSS_LX', 'PSS_LY', 'PSS_RX', 'PSS_RY']
l_buttons = ['PSB_PAD_UP', 'PSB_PAD_RIGHT', 'PSB_PAD_DOWN', 'PSB_PAD_LEFT', 'PSB_L1', 'PSB_L2', 'PSB_L3']
r_buttons = ['PSB_TRIANGLE', 'PSB_CIRCLE', 'PSB_CROSS', 'PSB_SQUARE', 'PSB_R1', 'PSB_R2', 'PSB_R3']
m_buttons = ['PSB_SELECT', 'PSB_START']

max_time_ms = 100

uart = machine.UART(2, 9600)
uart.init(9600, bits=8, parity=None, stop=1)
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
    checks = []
    message = []
    start = time.ticks_ms()
    #send request byte
    uart.write(bytes([0x00]))
    while(len(message) < 7):
        if(len(message)):
            print(message)
        # timetout
        if time.ticks_ms() - start > max_time_ms:
            return False
        # read incoming bytes
        checks.append(time.ticks_ms() - start)
        b = uart.read()
        checks.append(time.ticks_ms() - start)
        f = 'B' * len(b)
        message += list(struct.unpack(f, b))
        # find message start
        while(len(message) and not message[0] >> 7):
            del message[0]
    checks.append(time.ticks_ms() - start)
    # remove start bit
    message[0] &= 127
    store_s_data(message)
    checks.append(time.ticks_ms() - start)
    print(checks)
    print(commands)
    return True
'''
    return
    # search for message start
    while(uart.any() >= 7):
        if(time.ticks_ms() - start > max_time):
            return "timeout"
        b = struct.unpack('B', uart.read(1))[0]
        if(not b >> 7):
            continue
        # skip if newer message in serial
        if(uart.any() >= 13):
            print("skipping " + str(uart.any()))
            uart.read(6)
            continue
        # save message
        b &= 127
        message = [b] + list(struct.unpack('BBBBBB', uart.read(6)))
        store_s_data(message)
        print(time.ticks_ms() - start)
        return True
    print(uart.any())
    return "not enough"
    '''

def test(byte_ms):
    global uart
    uart.write(bytes([byte_ms]))
    for i in range(50):
        if(read_s_data()):
            print("read read")
        time.sleep_ms(20)
