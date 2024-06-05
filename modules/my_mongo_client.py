# librerias
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from json import loads

class MyMongoClient:
    def __init__(self, uri, database, collection, publisher="Undefined"):
        """
        Inicializa un nuevo cliente de MongoDB.

        Args:
            uri (str): URI de conexión a MongoDB.
            database (str): Nombre de la base de datos.
            collection (str): Nombre de la colección.
            publisher (str, opcional): Editor predeterminado para los datos insertados. Por defecto, "Undefined".
        """
        self.uri = uri
        self.database_name = database
        self.collection_name = collection
        self.publisher = publisher
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """
        Establece una conexión con MongoDB Atlas.
        """
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print("Conexión a MongoDB Atlas establecida.")
        except Exception as e:
            print(f"No se pudo establecer la conexión a MongoDB Atlas: {e}")

    def insert_data(self, data):
        """
        Inserta datos en la colección especificada.

        Args:
            data (str): Datos a ser insertados, en formato JSON.

        Returns:
            pymongo.results.InsertOneResult: Resultado de la inserción.
        """
        if not self.client:
            print("Error: No se ha establecido una conexión a MongoDB Atlas.")
            return 0
        try:
            data_formated = loads(data)
            data_formated["device"] = self.publisher
            data_formated["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = self.collection.insert_one(data_formated)
            return result

        except Exception as e:
            print(f"Error al insertar datos en MongoDB Atlas: {e}")

    def disconnect(self):
        """
        Cierra la conexión con MongoDB Atlas.
        """
        if self.client:
            self.client.close()
            print("Conexión a MongoDB Atlas cerrada.")
