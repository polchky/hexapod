import machine
import time
import struct

max_time_ms = 100
baud_rate = 115200

sticks = ['PSS_LX', 'PSS_LY', 'PSS_RX', 'PSS_RY']
l_buttons = ['PSB_PAD_UP', 'PSB_PAD_RIGHT', 'PSB_PAD_DOWN', 'PSB_PAD_LEFT', 'PSB_L1', 'PSB_L2', 'PSB_L3']
r_buttons = ['PSB_TRIANGLE', 'PSB_CIRCLE', 'PSB_CROSS', 'PSB_SQUARE', 'PSB_R1', 'PSB_R2', 'PSB_R3']
m_buttons = ['PSB_SELECT', 'PSB_START']

buttons = l_buttons + r_buttons + m_buttons

uart = machine.UART(2, baud)
uart.init(baud_rate, bits=8, parity=None, stop=1)

commands = {}
# init buttons state
for button in buttons:
    commands[button] = False
commands_prev = commands

def clicked(button):
    return not commands_prev[button] and commands[button]

def store_data(message):
    global commands
    global commands_prev
    commands_prev = commands
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

def update():
    message = []
    start = time.ticks_ms()
    #send request byte
    uart.write(bytes([0x00]))
    while(len(message) < 7):
        # timetout
        if time.ticks_ms() - start > max_time_ms:
            return False
        # read incoming bytes
        b = uart.read()
        f = 'B' * len(b)
        message += list(struct.unpack(f, b))
        # find message start
        while(len(message) and not message[0] >> 7):
            del message[0]
    # remove start bit
    message[0] &= 127
    store_data(message)
    #print(time.ticks_ms() - start)
    return True
