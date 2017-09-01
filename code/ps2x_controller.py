import machine
import time
import struct

STICKS = ['PSS_LX', 'PSS_LY', 'PSS_RX', 'PSS_RY']
L_BUTTONS = ['PSB_PAD_UP', 'PSB_PAD_RIGHT', 'PSB_PAD_DOWN', 'PSB_PAD_LEFT', 'PSB_L1', 'PSB_L2', 'PSB_L3']
R_BUTTONS = ['PSB_TRIANGLE', 'PSB_CIRCLE', 'PSB_CROSS', 'PSB_SQUARE', 'PSB_R1', 'PSB_R2', 'PSB_R3']
M_BUTTONS = ['PSB_SELECT', 'PSB_START']
BUTTONS = L_BUTTONS + R_BUTTONS + M_BUTTONS

class Controller:
    def __init__(self, baud_rate, uart_channel = 2, max_time_ms = 50):
        self.uart = machine.UART(2, baud_rate)
        self.uart.init(baud_rate, bits=8, parity=None, stop=1)
        self.max_time_ms = max_time_ms

        self.commands = {}
        # init buttons state
        for button in BUTTONS:
            self.commands[button] = False
        self.commands_prev = self.commands

    def _store_message(self, message):
        self.commands_prev = self.commands
        self.commands = {}

        # joysticks
        for i in range(4):
            lb = message[6] >> 4-i & 1
            self.commands[STICKS[i]] = message[i] << 1 | lb
        # left and right buttons
        for i in range(7):
            self.commands[L_BUTTONS[i]] = message[4] >> 6 - i & 1
            self.commands[R_BUTTONS[i]] = message[5] >> 6 - i & 1
        # middle buttons
        self.commands[M_BUTTONS[0]] = message[6] >> 6
        self.commands[M_BUTTONS[1]] = message[6] >> 5 & 1

    def update(self):
        message = []
        start = time.ticks_ms()
        # send request byte
        self.uart.write(bytes([0x00]))
        while(len(message) < 7):
            # timetout
            if time.ticks_ms() - start > self.max_time_ms:
                return False
            # read incoming bytes
            b = self.uart.read()
            f = 'B' * len(b)
            message += list(struct.unpack(f, b))
            # find message start
            while(len(message) and not message[0] >> 7):
                del message[0]
        # remove start bit
        message[0] &= 127
        self._store_message(message)
        return True

    def clicked(self, button):
        return not self.commands_prev[button] and self.commands[button]

    def test(self):
        # ensure keyboard interrupt did not empty the commands
        self.commands = self.commands_prev
        while(True):
            if not self.update():
                continue
            for button in BUTTONS:
                if self.clicked(button):
                    print(button)
