# main.py
# librerias
from time import sleep
from streamlit_data.code_streamlit import StreamlitHandler
from modules.my_mongo_client import MyMongoClient
import streamlit as st
import json

# Configurar la conexión a MongoDB
uri = "mongodb+srv://santiagoruizp:NkDzXa3vfCoZjMSW@cluster0.kcsmfwl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
IOT_DB = MyMongoClient(uri, "Database_PF_IOT", "Collection_PF_IOT", "Arduino")
IOT_DB.connect()

def main():
    """
    Función principal del programa.
    """
    # Instancia del manejador de Streamlit para la interfaz de usuario
    handler = StreamlitHandler()
    
    # Llama a la función para agregar elementos adicionales a la interfaz de usuario
    handler.additional_ui()  

    try:
        while True:
            # Actualiza los datos en la interfaz de usuario
            handler.update_data()
            
            # Verifica si se ha iniciado la medición desde la interfaz de usuario
            if st.session_state.start_button:
                data_dict = st.session_state.arduino_reader.read_data()
                if data_dict:
                    # Agrega el nombre de la medida a los datos
                    data_dict['measurement_name'] = st.session_state.measurement_name
                    
                    # Convierte los datos a JSON y los inserta en MongoDB
                    data_json = json.dumps(data_dict)
                    result = IOT_DB.insert_data(data_json)
                    if result.inserted_id:
                        print("Documento insertado exitosamente. ID:", result.inserted_id)
                    else:
                        print("Error al insertar el documento.")
            
            sleep(1)  # Espera un segundo antes de la próxima iteración

    except Exception as error:
        print(f"Ocurrió un error: {error}")

    except KeyboardInterrupt:
        # Maneja la interrupción de teclado para cerrar el lector Arduino y desconectar la base de datos
        if st.session_state.arduino_reader:
            st.session_state.arduino_reader.close()
        IOT_DB.disconnect()

if __name__ == '__main__':
    main()

