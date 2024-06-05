# librerias
from read_data.read import ArduinoReader
from modules.my_mongo_client import MyMongoClient
import streamlit as st
import pandas as pd
import requests
import numpy as np
from time import sleep
import json

# Configurar la conexión a MongoDB
uri = "mongodb+srv://santiagoruizp:NkDzXa3vfCoZjMSW@cluster0.kcsmfwl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
IOT_DB = MyMongoClient(uri, "Database_PF_IOT", "Collection_PF_IOT", "Arduino")
IOT_DB.connect()

# Función para obtener los datos del servidor
def fetch_data(sortby, lastest1st, skip, limit):
    """
    Obtiene datos del servidor mediante una solicitud HTTP GET.

    Args:
        sortby (str): Campo por el cual ordenar los resultados.
        lastest1st (bool): Indica si los resultados más recientes deben ir primero.
        skip (int): Número de documentos para omitir.
        limit (int): Número máximo de documentos a devolver.

    Returns:
        list: Lista de datos obtenidos del servidor en formato JSON.
    """
    url = f'https://backend-iot-9v93.onrender.com/sensordata/?sortby={sortby}&lastest1st={lastest1st}&skip={skip}&limit={limit}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Error al obtener los datos')
        return []

# Función para obtener los datos del servidor por tipo de medición
def fetch_data_measurement(measurement):
    """
    Obtiene datos del servidor filtrados por tipo de medición mediante una solicitud HTTP GET.

    Args:
        measurement (str): Nombre de la medición.

    Returns:
        list: Lista de datos obtenidos del servidor en formato JSON.
    """
    url = f'https://backend-iot-9v93.onrender.com/sensordata/measurement?measurement_name={measurement}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Error al obtener los datos')
        return []

# Función para calcular los promedios de los datos
def calculate_averages2(df):
    """
    Calcula los promedios de los datos de un DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame que contiene los datos.

    Returns:
        list: Lista de cadenas formateadas que representan los promedios de los datos.
    """
    if not df.empty:
        averages = {
            "Temperatura 1 (°C)": df["Temperatura 1 (°C)"].mean(),
            "Temperatura 2 (°C)": df["Temperatura 2 (°C)"].mean(),
            "Temperatura 3 (°C)": df["Temperatura 3 (°C)"].mean(),
            "Voltaje 1 (V)": df["Voltaje 1 (V)"].mean(),
            "Voltaje 2 (V)": df["Voltaje 2 (V)"].mean()
        }
        formatted_averages = {key: f"{value:.2f}" for key, value in averages.items()}
        return [f"{key}: {value}" for key, value in formatted_averages.items()]
    else:
        st.warning("No hay datos disponibles para calcular promedios.")
        return []

class StreamlitHandler:
    def __init__(self):
        """
        Inicializa un nuevo manejador de Streamlit.
        """
        self.setup_session_state()
        self.setup_ui()

    def setup_session_state(self):
        """
        Configura las variables de estado de la sesión de Streamlit.
        """
        if 'data_list' not in st.session_state:
            st.session_state.data_list = []
        if 'start_button' not in st.session_state:
            st.session_state.start_button = False
        if 'stop_button' not in st.session_state:
            st.session_state.stop_button = False
        if 'arduino_reader' not in st.session_state:
            st.session_state.arduino_reader = None
        if 'measurement_name' not in st.session_state:
            st.session_state.measurement_name = ""
        if 'previous_measurement_name' not in st.session_state:
            st.session_state.previous_measurement_name = ""
        if 'measurement_running' not in st.session_state:
            st.session_state.measurement_running = False
        if 'averages_list' not in st.session_state:
            st.session_state.averages_list = []

    def setup_ui(self):
        """
        Configura la interfaz de usuario de Streamlit.
        """
        st.markdown("""
    <div style='text-align: center; margin-top: 20px;'>
        <h1 style='color: yellow;'>Proyecto: Efecto Seebeck por espines</h1>
        <p>Version: 1.0.0</p>
        <p>Author: Santiago Ruiz</p>
        <p>Copyright 2024</p>
    </div>
    """, unsafe_allow_html=True)
        
        st.write("")  # Espacio adicional
        
        st.markdown("<h1 style='color: lime;'>Registro de datos en tiempo real</h1>", unsafe_allow_html=True)
        
        # Cuadro de texto para el nombre de la medida
        st.session_state.measurement_name = st.text_input("Nombre de la medida:", st.session_state.measurement_name)
        
        st.write("")  # Espacio adicional
        st.markdown("<h2 style='color: deepskyblue;'>Lecturas de los sensores en tiempo real</h2>", unsafe_allow_html=True)

        # Crear columnas para colocar los botones uno al lado del otro
        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("Iniciar medida", on_click=self.start_measurement)
        with col2:
            st.button("Detener medida", on_click=self.stop_measurement)
        with col3:
            st.button("Reiniciar medida", on_click=self.reset_measurement)

        # Agregar un nuevo botón para sacar promedios
        st.button("Sacar promedios", on_click=self.calculate_averages)

        # Contenedor para mostrar los promedios en color dorado
        st.markdown("<h3 style='color:gold;'>Promedios:</h3>", unsafe_allow_html=True)
        for line in st.session_state.averages_list:
            st.write(line)

        self.data_placeholder = st.empty()
        st.markdown("<h2 style='color: deepskyblue;'>Gráfica datos de temperatura en tiempo real</h2>", unsafe_allow_html=True)
        self.chart_placeholder_temperaturas = st.empty()
        st.markdown("<h2 style='color: deepskyblue;'>Gráfica datos de voltaje en tiempo real</h2>", unsafe_allow_html=True)
        self.chart_placeholder_voltajes = st.empty()

    def calculate_averages(self):
        """
        Calcula los promedios de los datos.
        """
        if st.session_state.data_list:
            data_df = pd.DataFrame(st.session_state.data_list)
            averages = {
                "Temperatura 1 (°C)": data_df["Temperatura 1 (°C)"].mean(),
                "Temperatura 2 (°C)": data_df["Temperatura 2 (°C)"].mean(),
                "Temperatura 3 (°C)": data_df["Temperatura 3 (°C)"].mean(),
                "Voltaje 1 (V)": data_df["Voltaje 1 (V)"].mean(),
                "Voltaje 2 (V)": data_df["Voltaje 2 (V)"].mean()
            }
            formatted_averages = {key: f"{value:.2f}" for key, value in averages.items()}
            st.session_state.averages_list = [f"{key}: {value}" for key, value in formatted_averages.items()]
        else:
            st.warning("No hay datos disponibles para calcular promedios.")


    def start_measurement(self):
        """
        Inicia la adquisición de datos si no se está ejecutando actualmente.
        """
        if not st.session_state.measurement_running:
            st.session_state.start_button = True
            st.session_state.stop_button = False
            if st.session_state.arduino_reader is None:
                st.session_state.arduino_reader = ArduinoReader("COM4", 9600)
                st.session_state.arduino_reader.connect()
            st.session_state.measurement_running = True

    def stop_measurement(self):
        """
        Detiene la adquisición de datos si se está ejecutando actualmente.
        """
        st.session_state.start_button = False
        st.session_state.stop_button = True
        if st.session_state.arduino_reader is not None:
            st.session_state.arduino_reader.close()
            st.session_state.arduino_reader = None
        st.session_state.measurement_running = False

    def reset_measurement(self):
        """
        Reinicia la adquisición de datos y borra los datos actuales.
        """
        if st.session_state.measurement_running:
            self.stop_measurement()  # Detener la medida antes de borrar los datos
        st.session_state.data_list = []  # Borra los datos independientemente del nombre de la medida
        st.session_state.previous_measurement_name = st.session_state.measurement_name
        if st.session_state.measurement_name == st.session_state.previous_measurement_name:
            st.error("Por favor, cambie el nombre de la medida antes de reiniciar.")
            st.session_state.measurement_running = False
        else:
            st.warning("Por favor, cambie el nombre de la medida antes de iniciar una nueva medición.")

    def update_data(self):
        """
        Actualiza los datos y los gráficos en la interfaz de usuario.
        """
        try:
            if st.session_state.start_button:
                data_dict = st.session_state.arduino_reader.read_data()
                if data_dict:
                    data_dict['measurement_name'] = st.session_state.measurement_name
                    st.session_state.data_list.append(data_dict)

            df = pd.DataFrame(st.session_state.data_list)

            while len(df) < 10:
                df = pd.concat([df, pd.DataFrame([{
                    "Temperatura 1 (°C)": None,
                    "Temperatura 2 (°C)": None,
                    "Temperatura 3 (°C)": None,
                    "Voltaje 1 (V)": None,
                    "Voltaje 2 (V)": None,
                    "measurement_name": st.session_state.measurement_name
                }])], ignore_index=True)

            self.data_placeholder.write(df)

            chart_data_temperaturas = pd.DataFrame({
                "Tiempo": np.arange(len(df)),
                "Temperatura 1 (°C)": df["Temperatura 1 (°C)"],
                "Temperatura 2 (°C)": df["Temperatura 2 (°C)"],
                "Temperatura 3 (°C)": df["Temperatura 3 (°C)"]
            }).dropna()

            chart_data_voltajes = pd.DataFrame({
                "Tiempo": np.arange(len(df)),
                "Voltaje 1 (V)": df["Voltaje 1 (V)"],
                "Voltaje 2 (V)": df["Voltaje 2 (V)"]
            }).dropna()

            self.chart_placeholder_temperaturas.line_chart(
                chart_data_temperaturas.set_index("Tiempo"), use_container_width=True)

            self.chart_placeholder_voltajes.line_chart(
                chart_data_voltajes.set_index("Tiempo"), use_container_width=True)
        except Exception as e:
            print(f"Ocurrió un error: {e}")

    def additional_ui(self):
        """
        Genera la interfaz de usuario adicional para la visualización y filtrado de datos guardados en la base de datos.
        """
        # Encabezado para el registro de datos guardados
        st.markdown("<h1 style='color: lime;'>Registro de datos guardados - Base de datos</h1>", unsafe_allow_html=True)

        # Sección para mostrar todos los datos
        st.write("")  # Espacio adicional
        st.markdown("<h2 style='color: deepskyblue;'>Todos los datos</h2>", unsafe_allow_html=True)

        # Elementos para el filtrado de datos
        col1, col2, col3 = st.columns(3)
        with col1:
            limit = st.number_input('Límite', min_value=0, value=10)
        with col2:
            skip = st.number_input('Omitir', min_value=0, value=0)
        with col3:
            sortby = st.selectbox('Ordenar por', ['None', 'Temperatura 1 (°C)', 'Temperatura 2 (°C)', 'Temperatura 3 (°C)', 'Voltaje 1 (V)', 'Voltaje 2 (V)', 'measurement_name', 'device', 'date'])
        lastest1st = st.checkbox('Últimos primero', value=True)

        # Botón para obtener datos filtrados
        if st.button("Obtener Datos"):
            data = fetch_data(sortby, lastest1st, skip, limit)
            data_placeholder = st.empty()
            if data:
                df = pd.DataFrame(data)
                data_placeholder.write(df)
            else:
                st.write("No se han encontrado datos")

        # Sección para filtrar por nombre de la medida
        st.markdown("<h2 style='color: deepskyblue;'>Filtrar por medida</h2>", unsafe_allow_html=True)
        measurement_name2 = st.text_input("Consulta con el nombre de la medida:", "")
        
        # Botón para obtener datos filtrados por nombre de la medida
        if st.button("Obtener Datos por medida"):
            data2 = fetch_data_measurement(measurement_name2)
            data2_placeholder = st.empty()
            
            # Gráficas de datos de temperatura y voltaje
            st.markdown("<h2 style='color: deepskyblue;'>Gráfica datos de temperatura</h2>", unsafe_allow_html=True)
            chart_placeholder_temperaturas = st.empty()
            st.markdown("<h2 style='color: deepskyblue;'>Gráfica datos de voltaje</h2>", unsafe_allow_html=True)
            chart_placeholder_voltajes = st.empty()

            if data2:
                df = pd.DataFrame(data2)
                data2_placeholder.write(df)

                chart_data_temperaturas = pd.DataFrame({
                    "Tiempo": np.arange(len(df)),
                    "Temperatura 1 (°C)": df["Temperatura 1 (°C)"],
                    "Temperatura 2 (°C)": df["Temperatura 2 (°C)"],
                    "Temperatura 3 (°C)": df["Temperatura 3 (°C)"]
                }).dropna()

                chart_data_voltajes = pd.DataFrame({
                    "Tiempo": np.arange(len(df)),
                    "Voltaje 1 (V)": df["Voltaje 1 (V)"],
                    "Voltaje 2 (V)": df["Voltaje 2 (V)"]
                }).dropna()

                chart_placeholder_temperaturas.line_chart(
                    chart_data_temperaturas.set_index("Tiempo"), use_container_width=True)

                chart_placeholder_voltajes.line_chart(
                    chart_data_voltajes.set_index("Tiempo"), use_container_width=True)

                # Contenedor para mostrar los promedios 
                st.markdown("<h3 style='color:gold;'>Promedios:</h3>", unsafe_allow_html=True)
                averaged_data = calculate_averages2(df)
                if averaged_data:
                    for line in averaged_data:
                        st.write(line)
                else:
                    st.warning("No hay datos disponibles para calcular promedios.")
            else:
                st.write("No se han encontrado datos")

