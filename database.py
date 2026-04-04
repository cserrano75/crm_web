import mysql.connector

def obtener_conexion():
    try:
        # Aquí definimos los parámetros de tu BD
        conexion = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="TuNuevaPassword123",  # Pon tu clave real
            database="matriz_proyectos"
        )
        if conexion.is_connected():
            # print("✅ Conexión exitosa a la base de datos")
            return conexion
            
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None

# Prueba rápida: si ejecutas este archivo solo, intentará conectar
if __name__ == "__main__":
    con = obtener_conexion()
    if con:
        con.close()