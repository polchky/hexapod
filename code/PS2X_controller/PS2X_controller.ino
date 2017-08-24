#include <PS2X_lib.h>  //for v1.6

/******************************************************************
 * set pins connected to PS2 controller
 ******************************************************************/
#define PS2_DAT        7    
#define PS2_CMD        5  
#define PS2_SEL        4  
#define PS2_CLK        6  

#define DELAY_MS       20 // Delay between gamepad readings

/******************************************************************
 * select modes of PS2 controller:
 *   - pressures = analog reading of push-butttons 
 *   - rumble    = motor rumbling
 ******************************************************************/
#define pressures   false
#define rumble      false

PS2X ps2x; // create PS2 Controller Class

byte sticks[] = {PSS_LX, PSS_LY, PSS_RX, PSS_RY};
unsigned int l_buttons[] = {PSB_PAD_UP, PSB_PAD_RIGHT, PSB_PAD_DOWN, PSB_PAD_LEFT, PSB_L1, PSB_L2, PSB_L3};
unsigned int r_buttons[] = {PSB_TRIANGLE, PSB_CIRCLE, PSB_CROSS, PSB_SQUARE, PSB_R1, PSB_R2, PSB_R3};
unsigned int m_buttons[] = {PSB_SELECT, PSB_START};

byte s_data[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}; // bytes to send

int error = 0;
byte type = 0;
byte vibrate = 0;

void ps2_connect(){
  do{
    delay(500);
    error = ps2x.config_gamepad(PS2_CLK, PS2_CMD, PS2_SEL, PS2_DAT, pressures, rumble);
  }while(error != 0 && error != 3);
}

void set_s_data(){
  
  // joysticks
  s_data[6] = 0x00;
  for (int i=0; i<4; i++){
    s_data[i] = ps2x.Analog(sticks[i]) >> 1;
    s_data[6] = s_data[6] << 1 | ps2x.Analog(sticks[i]) >> 7;
  }

  // left and right buttons
  s_data[4] = s_data[5] = 0x00;
  for (int i=0; i<7; i++){
    s_data[4] = s_data[4] << 1 | ps2x.Button(l_buttons[i]);
    s_data[5] = s_data[5] << 1 | ps2x.Button(r_buttons[i]);
  }

  // middle buttons
  s_data[6] = s_data[6] << 2 | ps2x.Button(m_buttons[0]) << 1| ps2x.Button(m_buttons[1]);

  // set message starting bit
  s_data[0] |= 1 << 7;
}

void setup(){
 
  Serial.begin(57600);
  
  ps2_connect();
}

void loop() {
  
  // read controller
  if(!ps2x.read_gamepad(false, vibrate)){
    ps2_connect();
    return;
  }

  // set and send data
  set_s_data();
  if(Serial.availableForWrite() >= 7){
    for (int i=0; i<7; i++){
      Serial.write(s_data[i]);
    }
  }
  delay(DELAY_MS);  
}
