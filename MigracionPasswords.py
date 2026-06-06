# migrar_passwords.py  (ejecutar UNA sola vez)
import jaydebeapi
import bcrypt

jar_file = r".\lib\mssql-jdbc-13.4.0.jre11.jar"
jdbc_driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
url = "jdbc:sqlserver://localhost:1433;databaseName=KURA;encrypt=true;trustServerCertificate=true;"

conn = jaydebeapi.connect(jdbc_driver, url, ['sa', 'Ademar07'], jar_file)
cursor = conn.cursor()

cursor.execute("SELECT id_empleado, password_ FROM Personal")
rows = cursor.fetchall()

for id_empleado, password_plana in rows:
    if not password_plana.startswith("$2b$"):  # evitar re-hashear
        hash_nuevo = bcrypt.hashpw(
            password_plana.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        cursor.execute(
            "UPDATE Personal SET password_ = ? WHERE id_empleado = ?",
            (hash_nuevo, id_empleado)
        )
        print(f"Migrado empleado {id_empleado}")

conn.commit()
conn.close()
print("Migración completada.")