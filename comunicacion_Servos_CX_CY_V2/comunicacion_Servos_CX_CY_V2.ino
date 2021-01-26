/*
 the public domain.

 http://www.arduino.cc/en/Tutorial/LiquidCrystalSerialDisplay

*/

// include the library code:
//#include <LiquidCrystal.h>
#include <Servo.h>
Servo cx;
Servo cy;
int valorE = 90;
int valorA = 90;
long positions[2];

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
//const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
//LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  cx.attach(9);
  cy.attach(10);
  // set up the LCD's number of columns and rows:
//  lcd.begin(16, 2);
  // initialize the serial communications:
  Serial.begin(9600);
}

void loop() {
  // when characters arrive over the serial port...
  if (Serial.available()) {

     // wait a bit for the entire message to arrive
    delay(100);
    // clear the screen
 //   lcd.clear();
    // read all the available characters
   while (Serial.available() > 1) {
      // display each character to the LCD
  //    lcd.write(Serial.read());
      int valorE = Serial.parseInt();
      int valorA = Serial.parseInt();
     // Serial.print(valorA);
     // Serial.println(valorE);
     positions[0] =  (convierte_x(valorE));
     positions[1] = (convierte_y(valorA)) ;
    cx.write( positions[0]);
   // Serial.print(positions[0]);
    cy.write(positions[1]);
    // Serial.println(positions[1]);
    }
  }
}
//....................................................................
/*
Gus esta es una funcion que cambia un valor de x por otro que vos cargas en la tabla. te puse un ejemplo con 10 valores para no escribir 180 valores.
Esp te lo dejo a vos como trabajo practico. Para hacer la conversion en el programa haces:
xcambiado=convierte_x(7);   por ejemplo
*/
int convierte_x(unsigned int xoriginal) {
  int resultado = 0;
  int tabla[]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,36,37,39,40,41,42,44,44,46,48,49,50,52,53,54,55,57,58,59,61,62,63,64,66,67,68,70,71,72,74,75,76,78,79,80,81,82,84,85,86,88,89,90,92,93,94,96,97,98,100,101,102,103,104,106,107,108,110,111,113,114,115,117,118,119,120,122,123,124,125,127,128,129,131,132,133,135,136,137,139,140,141,142,144,145,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,147,148,149,150,151,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185};
   //pixeles   0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,  97,  98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185
  // convierte valor de entrada en valor de salida
  resultado = tabla[xoriginal];
  return (resultado);
}
int convierte_y(unsigned int yoriginal) {
  int resultado = 0;
  int tabla[]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,37,39,40,41,43,44,46,47,48,50,52,53,54,55,57,58,60,61,62,64,65,67,68,70,71,72,74,76,77,78,79,80,81,83,84,85,87,88,89,91,92,93,94,96,98,99,101,102,103,104,105,107,108,109,110,112,113,114,115,117,118,119,121,122,123,124,126,127,128,129,130,132,133,134,135,137,138,139,140,142,143,144,145,145,145,145,145,145,145,146,147,148,149,150,151,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185};
   //pixe 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185};
  // convierte valor de entrada en valor de salida
  resultado = tabla[yoriginal];
  return (resultado);
}
//....................................................................
