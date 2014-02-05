#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"

#define RF_SETUP 0x17

// Set up nRF24L01 radio on SPI pin for CE, CSN
RF24 radio(9,10);

const uint8_t green = 2;
const uint8_t red = 4;
const uint8_t temp_pin = A5;

const uint8_t nodeID = 1;

const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0x7365727631LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E2LL, 0xF0F0F0F0E2LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E3LL, 0xF0F0F0F0E3LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E4LL, 0xF0F0F0F0E4LL };
// const uint64_t pipes[2] = { 0xF0F0F0F0E5LL, 0xF0F0F0F0E5LL };
// Pipe0 is F0F0F0F0D2 ( same as reading pipe )

char receivePayload[32];

void setup(void)
{
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(temp_pin, INPUT);
  
  
  Serial.begin(9600);
  printf_begin();
  printf("Sending nodeID & 4 sensor data\n\r");

  radio.begin();

  // Enable this seems to work better
  radio.enableDynamicPayloads();

  radio.setDataRate(RF24_1MBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(76);
  radio.setRetries(15,15);

  radio.openWritingPipe(pipes[0]); 
  radio.openReadingPipe(1,pipes[1]); 

      
  // Send only, ignore listening mode
  //radio.startListening();

  // Dump the configuration of the rf unit for debugging
  radio.printDetails(); 
  delay(1000); 
}

void loop(void)
{
  String payload = String(nodeID) + ", " + String(analogRead(temp_pin));
  char outBuffer[16];
  payload.toCharArray(outBuffer, 16);
  Serial.println(outBuffer);
    
    // Stop listening and write to radio 
    radio.stopListening();
    boolean did_it_send = radio.write(outBuffer, strlen(outBuffer));
    digitalWrite(did_it_send ? green : red, HIGH);
    radio.startListening();
    
    delay(1000);
    digitalWrite(red,LOW); // Off the buzzer
    digitalWrite(green,LOW);
  }





