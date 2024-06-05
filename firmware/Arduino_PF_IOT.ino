// Incluye la biblioteca para el MAX6675
#include "max6675.h"

// Define los pines de conexión del termopar al Arduino para el Max6675 #1
int thermoSO_T1 = 2;
int thermoCS_T1 = 3;
int thermoSLK_T1 = 4;

// Define los pines de conexión del termopar al Arduino para el Max6675 #2
int thermoSO_T2 = 5;
int thermoCS_T2 = 6;
int thermoSLK_T2 = 7;

// Define los pines de conexión del termopar al Arduino para el Max6675 #3
int thermoSO_T3 = 8;
int thermoCS_T3 = 9;
int thermoSLK_T3 = 10;

// Define los pines para las lecturas de voltaje
int pinVoltaje1 = A0;
int pinVoltaje2 = A2;

// Crea una instancia del objeto MAX6675 con los pines definidos
MAX6675 thermocouple_T1(thermoSLK_T1, thermoCS_T1, thermoSO_T1);
MAX6675 thermocouple_T2(thermoSLK_T2, thermoCS_T2, thermoSO_T2);
MAX6675 thermocouple_T3(thermoSLK_T3, thermoCS_T3, thermoSO_T3);

// donde se guarda la temperatura
float T1 = 0 ; 
float T2 = 0 ;
float T3 = 0 ; 

bool send_data = false;

void setup() {
  // Inicia la comunicación serial a 9600 baudios
  Serial.begin(9600);
  
  // Espera a que el chip MAX estabilice (puede ser necesario en algunos casos)
  delay(500);
}

// Función para calcular el valor recalibrado
float recalibrateValue(float value) {
    if (value < 30) {
        return value - 2.00;
    } else if (value < 33) {
        return value - 1.50;
    } else if (value < 36) {
        return value - 1.0;
    } else if (value < 39) {
        return value - 0.50;
    } else {
        return value;
    }
}

void serialEvent(){
    char command = Serial.read();
    if (command == 's')
        send_data = true;
}

void loop() {
    T1 = thermocouple_T1.readCelsius();
    T2 = thermocouple_T2.readCelsius();
    T3 = thermocouple_T3.readCelsius();
    
    // Leer voltajes de los pines A0 y A1
    float voltaje1 = analogRead(pinVoltaje1) * (5.0 / 1023.0);
    float voltaje2 = analogRead(pinVoltaje2) * (5.0 / 1023.0);

  // Mostrar la temperatura y voltaje
  if (send_data){
    
    Serial.println(
        "{\"Temperatura 1 (°C)\":" + String(recalibrateValue(T1),2)
        + ",\"Temperatura 2 (°C)\":" + String(recalibrateValue(T2),2)
        + ",\"Temperatura 3 (°C)\":" + String(recalibrateValue(T3),2)
        + ",\"Voltaje 1 (V)\":" + String(voltaje1, 6) 
        + ",\"Voltaje 2 (V)\":" + String(voltaje2, 6) 
        + "}"
    );
    send_data = false;
  }

  delay(500); // Retardo de 2 segundos para evitar lecturas rápidas
}
