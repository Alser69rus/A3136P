
char buf[7];

#define AD_CLOCK 4294967295/125000000

#define W_CLK 2
#define FQ_UD 1
#define DATA 3
#define RESET 0


#define pulseHigh(pin){digitalWrite(pin,HIGH);digitalWrite(pin,LOW);}

byte pinNum(unsigned int chanel, byte pin) {
  return chanel * 4 + pin;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }
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
  if (Serial.available()) {
    switch (Serial.read()) {


      case '@':
        if (Serial.readBytes(buf, 7) != 7) {
          Serial.println("Err Cmd Length");
          break;
        }
        if (!checkCRC()) {
          Serial.println("CRC Err");
          break;
        }
        setFreq();
        break;


      case '!':
        if (Serial.readBytes(buf, 2) != 2) {
          Serial.println("Err Cmd Length");
          break;
        }
        if (buf[0] == 'S' and buf[1] == 't') {
          Serial.println("Ok");
          break;
        }
        else {
          Serial.println("CRC Err");
          break;
        }


      default:
        Serial.println("Unknown Cmd");
        break;
    }
  }
  delay(1);
}

boolean checkCRC() {
  byte crc = 0;
  for (int i = 0; i < 6; i++) {
    crc += buf[i];
  }
  crc += '@';
  if (buf[6] == crc) {
    return true;
  }
  else {
    return false;
  }
}

void setFreq() {
  unsigned long freq = String(buf).toInt();
  unsigned int chanel = freq / 100000;
  freq %=  100000;
  Serial.println("Chan " + String(chanel, DEC) + " Freq " + String(freq, DEC));

  freq *= AD_CLOCK;
  for (int i = 0; i < 4; i++, freq >>= 8) {
    sendByte(pinNum(chanel, DATA), pinNum(chanel, W_CLK), freq & 0xFF);
  }
  sendByte(pinNum(chanel, DATA), pinNum(chanel, W_CLK), freq & 0x00);
  pulseHigh(pinNum(chanel, FQ_UD));
}

void sendByte(byte dataPin, byte clkPin, byte data) {
  for (int i = 0; i < 8; i++, data >>= 1) {
    digitalWrite(dataPin, data & 0x01);
    pulseHigh(clkPin);
  }
}

