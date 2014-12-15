#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"

#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

volatile uint8_t f_wdt=0;
ISR(WDT_vect)
{
    f_wdt++;
}

void enterSleep(void)
{
  set_sleep_mode(SLEEP_MODE_PWR_SAVE);   /* EDIT: could also use SLEEP_MODE_PWR_DOWN for lowest power consumption. */
  sleep_enable();
  
  /* Now enter sleep mode. */
  sleep_mode();
  
  /* The program will continue from here after the WDT timeout*/
  sleep_disable(); /* First thing to do is disable sleep. */
  
  /* Re-enable the peripherals. */
  power_all_enable();
}


#define RF_SETUP 0x17

// Set up nRF24L01 radio on SPI pin for CE, CSN
RF24 radio(9,10);

const uint8_t temp_pin = A5;
const uint8_t light_pin = A4;
const uint8_t dial_pin = 3;

const uint8_t nodeID = 3;

const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0x7365727631LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E2LL, 0xF0F0F0F0E2LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E3LL, 0xF0F0F0F0E3LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E4LL, 0xF0F0F0F0E4LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E5LL, 0xF0F0F0F0E5LL };
// Pipe0 is F0F0F0F0D2 ( same as reading pipe )

const boolean debug = true;

void setup(void)
{
  pinMode(temp_pin, INPUT);
  pinMode(light_pin, INPUT);
  pinMode(dial_pin, OUTPUT);
  
  if(debug) Serial.begin(9600);
  radio.begin();

  // Enable this seems to work better
  radio.enableDynamicPayloads();

  radio.setDataRate(RF24_1MBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(76);
  radio.setRetries(15,15);

  radio.openWritingPipe(pipes[0]); 
  //radio.openReadingPipe(1,pipes[1]);
  //radio.stopListening();
  
   /*** Setup the WDT ***/
  
  /* Clear the reset flag. */
  MCUSR &= ~(1<<WDRF);
  
  /* In order to change WDE or the prescaler, we need to
   * set WDCE (This will allow updates for 4 clock cycles).
   */
  WDTCSR |= (1<<WDCE) | (1<<WDE);

  /* set new watchdog timeout prescaler value */
  WDTCSR = 1<<WDP0 | 1<<WDP3; /* 8.0 seconds */
  
  /* Enable the WD interrupt (note no reset). */
  WDTCSR |= _BV(WDIE); 
}

long readVcc() {
  long result;
  // Read 1.1V reference against AVcc
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Convert
  while (bit_is_set(ADCSRA,ADSC));
  result = ADCL;
  result |= ADCH<<8;
  //result = 1126400L / result; // Back-calculate AVcc in mV
  return result;
}

void send(void)
{   
  // Stop listening and write to radio 
  uint8_t tries = 0;
  boolean did_it_send = false;
  char outBuffer[16];
  uint16_t temp; uint16_t light; uint16_t v_bat;
  
  while(did_it_send == false & tries < 20)
  {
    tries++;
    //String payload = String(nodeID) + ", " + String(tries) + ", " + String(analogRead(temp_pin));
    //payload.toCharArray(outBuffer, 16);
    temp = analogRead(temp_pin);
    light = analogRead(light_pin);
    v_bat = readVcc();
    outBuffer[0] = nodeID; outBuffer[1] = tries; outBuffer[2] = highByte(temp); outBuffer[3] = lowByte(temp); 
    outBuffer[4] = highByte(v_bat); outBuffer[5] = lowByte(v_bat); outBuffer[6] = highByte(light); outBuffer[7] = lowByte(light);
    did_it_send = radio.write(outBuffer, strlen(outBuffer));
  }
  if(debug) Serial.println(String(light) + ', ' + temp);
  }

const uint8_t n = 1;

void loop(void)
{
  if(f_wdt >= n) {
    f_wdt = 0;
    send();
  }
  radio.powerDown();
  if(debug) {
  analogWrite(dial_pin, analogRead(light_pin));
  analogWrite(dial_pin, analogRead(light_pin));
  //analogWrite(dial_pin, 50.0 * (220.0/100.0));
  delay(1);
  send();
  f_wdt++;
  }
  else {
  enterSleep();
  }
}




