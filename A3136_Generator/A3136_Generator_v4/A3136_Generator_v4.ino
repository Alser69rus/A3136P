#include <EEPROM.h>
#include <SimpleModbusSlave.h>


#define AD_CLOCK 4294967295/125000000

#define W_CLK 1
#define FQ_UD 2
#define DATA 0
#define RESET 3


#define pulseHigh(pin){digitalWrite(pin,HIGH);digitalWrite(pin,LOW);}

byte pinNum(unsigned int chanel, byte pin) {
  return chanel * 4 + pin;
}

enum {
  FREQ1H, FREQ1L,
  FREQ2H, FREQ2L,
  FREQ3H, FREQ3L,
  BAUD, DEV_ID,
  TOTAL_ERRORS,
  TOTAL_REGS_SIZE
};

unsigned int holdingRegs[TOTAL_REGS_SIZE];
word baud;
byte devID;
unsigned long freq[3];

void setup() {
  if (EEPROM.read(487) != 100) {
    EEPROM.write(485, 4);
    EEPROM.write(486, 128);
    EEPROM.write(487, 100);
  };

  baud = EEPROM.read(485) * 256 + EEPROM.read(486);

  if (baud == 0 || baud > 1152) {
    baud = 96;
    EEPROM.write(485, highByte(baud));
    EEPROM.write(486, lowByte(baud));
  };
  holdingRegs[BAUD] = baud;

  devID = EEPROM.read(487);
  holdingRegs[DEV_ID] = devID;

  modbus_configure(baud * 100, devID, 0, TOTAL_REGS_SIZE, 0);

  for (int i = 0; i < 3; i++) {
    freq[i] = 0;
  };

  pinMode(pinNum(0, W_CLK) , OUTPUT);
  pinMode(pinNum(0, FQ_UD) , OUTPUT);
  pinMode(pinNum(0, DATA), OUTPUT);
  pinMode(pinNum(0, RESET), OUTPUT);

  pinMode(pinNum(1, W_CLK) , OUTPUT);
  pinMode(pinNum(1, FQ_UD) , OUTPUT);
  pinMode(pinNum(1, DATA), OUTPUT);
  pinMode(pinNum(1, RESET), OUTPUT);

  pinMode(pinNum(2, W_CLK) , OUTPUT);
  pinMode(pinNum(2, FQ_UD) , OUTPUT);
  pinMode(pinNum(2, DATA), OUTPUT);
  pinMode(pinNum(2, RESET), OUTPUT);

  pulseHigh(pinNum(0, RESET));
  pulseHigh(pinNum(0, W_CLK));
  pulseHigh(pinNum(0, FQ_UD));

  pulseHigh(pinNum(1, RESET));
  pulseHigh(pinNum(1, W_CLK));
  pulseHigh(pinNum(1, FQ_UD));

  pulseHigh(pinNum(2, RESET));
  pulseHigh(pinNum(2, W_CLK));
  pulseHigh(pinNum(2, FQ_UD));

}

void loop() {
  holdingRegs[TOTAL_ERRORS] = modbus_update(holdingRegs);
  for (int i = 0; i < 3; i++) {
    unsigned long f = holdingRegs[2 * i] * 65536 + holdingRegs[2 * i + 1];
    if (f != freq[i]) {
      freq[i] = f;
      setFreq(i, f);
    };
  };

  long b = holdingRegs[BAUD];
  if (b != baud) {
    baud = b;
    EEPROM.write(485, highByte(holdingRegs[BAUD]));
    EEPROM.write(486, lowByte(holdingRegs[BAUD]));
  };

  byte id = holdingRegs[DEV_ID];
  if (id != devID) {
    devID = id;
    EEPROM.write(487, devID);
  };


}



void setFreq(int chanel, unsigned long frequency) {

  unsigned long f = frequency * AD_CLOCK;
  for (int i = 0; i < 4; i++, f >>= 8) {
    sendByte(pinNum(chanel, DATA), pinNum(chanel, W_CLK), f & 0xFF);
  }
  sendByte(pinNum(chanel, DATA), pinNum(chanel, W_CLK), f & 0x00);
  pulseHigh(pinNum(chanel, FQ_UD));
}

void sendByte(byte dataPin, byte clkPin, byte data) {
  for (int i = 0; i < 8; i++, data >>= 1) {
    digitalWrite(dataPin, data & 0x01);
    pulseHigh(clkPin);
  }
}

