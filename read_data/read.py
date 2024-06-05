# librerias
import serial
from time import sleep

class ArduinoReader:
    def __init__(self, port, baud_rate, timeout=1):
        """
        Inicializa un nuevo lector de datos desde Arduino.

        Args:
            port (str): Puerto serial al que está conectado el Arduino.
            baud_rate (int): Velocidad de baudios de la comunicación serial.
            timeout (float, opcional): Tiempo de espera en segundos para las operaciones de lectura. Por defecto, 1 segundo.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.dev = None

    def connect(self):
        """
        Establece la conexión con el Arduino a través del puerto serial.
        """
        try:
            self.dev = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            sleep(2)  # Esperar un momento para que el dispositivo esté listo
            self.dev.flushInput()  # Limpiar el buffer de entrada
        except serial.SerialException as e:
            print(f"Error abriendo o usando el puerto serial: {e}")
        except Exception as e:
            print(f"Ocurrió un error al conectar: {e}")

    def read_data(self):
        """
        Lee los datos del Arduino.

        Returns:
            dict: Diccionario con los datos leídos, o None si no se pudo leer.
        """
        if self.dev is None or not self.dev.is_open:
            print("El dispositivo no está conectado.")
            return None

        try:
            self.dev.write(b"s")  # Enviar el comando 's'
            raw_data = self.dev.readline()
            data = raw_data.decode('utf-8').strip()  # Leer y decodificar los datos
            if data:
                print(f"Received: {data}")
                data_dict = eval(data)  # Convertir el string JSON a un diccionario
                for key, value in data_dict.items():
                    if isinstance(value, float) and value != value:  # Comprobar si es NaN
                        data_dict[key] = 0  # Reemplazar NaN por cero
                return data_dict
        except UnicodeDecodeError as e:
            print(f"Error decoding data: {e}")
            print(f"Raw data: {raw_data}")
        except Exception as e:
            print(f"Ocurrió un error al leer datos: {e}")
        return None

    def close(self):
        """
        Cierra la conexión con el Arduino.
        """
        if self.dev and self.dev.is_open:
            self.dev.close()
