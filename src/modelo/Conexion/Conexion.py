import jaydebeapi
import os
os.environ["JAVA_HOME"] = r"C:\Users\isma3\anaconda3\pkgs\openjdk-22.0.1-h57928b3_1\Library\lib\jvm"

class Conexion:
    def __init__(self, host='localhost', database='KURA', user='sa', password='Ademar07'):
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self.conexion = self.createConnection()

    def createConnection(self):
        try:
            jar_file = r"C:\Users\isma3\OneDrive - unileon.es\2 DATOS e IA\Ing del Software\Proyecto\lib\mssql-jdbc-13.4.0.jre11.jar"
            jdbc_driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            url = f"jdbc:sqlserver://{self._host}:1433;databaseName=KURA;encrypt=true;trustServerCertificate=true;" 

            self.conexion = jaydebeapi.connect(
                jdbc_driver,
                url,
                [self._user, self._password],
                jar_file
            )
            print("Conexión creada con éxito")
            return self.conexion
        
        except Exception as e:
            print("Error creando conexión:", e)
            return None

    """Un cursor es una estructura de control que permite recorrer los resultados de una 
    consulta SQL y manipular fila por fila los datos recuperados desde una base de datos."""
    def getCursor(self):
        if self.conexion is None:
            self.createConnection()
        return self.conexion.cursor()

    def closeConnection(self):
        try:
            if self.conexion:
                self.conexion.close()
                self.conexion = None
        except Exception as e:
            print("Error cerrando conexión:", e)

if __name__ == "__main__":
    print("--- Iniciando conexión con Base de Datos ---")
    
    db = Conexion() 

    
    

    


