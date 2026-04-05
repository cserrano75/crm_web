import matplotlib.pyplot as plt #<--- NUEVO: Para los gráficos
import os
from datetime import datetime # <--- NUEVO IMPORT para la fecha
from fpdf import FPDF
from database import obtener_conexion
import pandas as pd # Para el Excel
import requests # <--- Nuevo Import

class GestorClientes:
    """Clase encargada EXCLUSIVAMENTE de hablar con MySQL"""
    @staticmethod
    def listar(filtro=""):
        con = obtener_conexion()
        cursor = con.cursor()
        
        if filtro:
            # Buscamos coincidencias en nombre O empresa
            query = "SELECT id, nombre, empresa, email FROM clientes WHERE nombre LIKE %s OR empresa LIKE %s"
            val = (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
            cursor.execute(query, val)
        else:
            cursor.execute("SELECT id, nombre, empresa, email FROM clientes")
            
        datos = cursor.fetchall()
        con.close()
        return datos

    @staticmethod
    def guardar(nombre, empresa, email): # <-- Agregamos email aquí
        con = obtener_conexion()
        if con:
            cursor = con.cursor()
            # Agregamos la columna 'email' y un tercer '%s'
            sql = "INSERT INTO clientes (nombre, empresa, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, empresa, email)) # <-- Incluimos email en la tupla
            con.commit()
            con.close()
            return True
        return False

    @staticmethod
    def borrar(id_cliente):
        con = obtener_conexion()
        if con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
            con.commit()
            con.close()
            return True
        return False

    @staticmethod
    def obtener_uno(id_cliente):
        con = obtener_conexion()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT nombre, empresa FROM clientes WHERE id = %s", (id_cliente,))
            res = cursor.fetchone()
            con.close()
            return res
        return None

    @staticmethod
    def actualizar(id_cliente, nombre, empresa, email):
        con = obtener_conexion()
        if con:
            try:
                cursor = con.cursor()
                # La clave aquí es el WHERE id = %s para no pisar a otros clientes
                sql = "UPDATE clientes SET nombre=%s, empresa=%s, email=%s WHERE id=%s"
                cursor.execute(sql, (nombre, empresa, email, id_cliente))
                con.commit()
                return True
            except Exception as e:
                print(f"Error al actualizar: {e}")
                return False
            finally:
                con.close()
        return False
    
    @staticmethod
    def generar_reporte_pdf(nombre_archivo="Reporte_Clientes.pdf"):
        try:
            # 1. Preparar Datos Dinámicos
            clientes = GestorClientes.listar()
            fecha_actual = datetime.now().strftime("%d/%m/%Y") # Formato: DD/MM/AAAA HH:MM
            ruta_logo = "logo_empresa.png" # <--- Ruta relativa (dinámica por archivo)
            
            pdf = FPDF()
            pdf.add_page()
            
            # 2. ENCABEZADO (Logo y Fecha)
            # --- Arriba a la Derecha: LA FECHA (Tamaño mínimo 8)
            pdf.set_font("Arial", "I", 8) # "I" de Itálica (cursiva) para que se vea sutil
            # Obtenemos el ancho de la página para alinear a la derecha
            ancho_pagina = pdf.w - 2 * pdf.l_margin
            pdf.cell(ancho_pagina, 5, f"Fecha Reporte: {fecha_actual}", ln=True, align="R")
            
            # --- Arriba a la Izquierda: EL LOGO (Dinámico)
            # Verificamos si el archivo de logo existe para evitar errores
            if os.path.exists(ruta_logo):
                # pdf.image(ruta, x, y, ancho, alto)
                # Lo ponemos en la esquina superior izquierda (x=10, y=10) con ancho 30
                pdf.image(ruta_logo, 10, 10, 20) 
            else:
                print(f"⚠️ Aviso: No se encontró el archivo de logo en '{ruta_logo}'. Se generará sin logo.")

            pdf.ln(20) # Salto de línea grande para bajar después del logo/fecha

            # 3. CUERPO DEL REPORTE (Título y Tabla)
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "REPORTE ESTRATÉGICO DE CLIENTES", ln=True, align="C")
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "CRM INDUSTRIAL - GESTIÓN B2B", ln=True, align="C")
            pdf.ln(10)

            # ENCABEZADOS DE TABLA (con estilo)
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(0, 92, 153) # Azul corporativo (como el de tu botón Editar)
            pdf.set_text_color(255, 255, 255) # Texto blanco
            pdf.cell(20, 10, "ID", border=1, fill=True, align="C")
            pdf.cell(85, 10, "NOMBRE DEL CONTACTO", border=1, fill=True, align="C")
            pdf.cell(85, 10, "EMPRESA", border=1, fill=True, align="C")
            pdf.ln()

            # DATOS DE LOS CLIENTES (con estilo alternado)
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(0, 0, 0) # Texto negro
            gris_alterno = False
            
            for (id_c, nombre, empresa) in clientes:
                # Efecto cebra para lectura ISO
                if gris_alterno:
                    pdf.set_fill_color(240, 240, 240) # Gris muy suave
                else:
                    pdf.set_fill_color(255, 255, 255) # Blanco
                
                pdf.cell(20, 10, str(id_c), border=1, fill=True, align="C")
                # Limitar texto largo para que no se superponga
                pdf.cell(85, 10, str(nombre)[:35], border=1, fill=True) 
                pdf.cell(85, 10, str(empresa)[:35], border=1, fill=True)
                pdf.ln()
                gris_alterno = not gris_alterno # Cambiar color para la siguiente fila

                pdf.ln(10) # Espacio después de la tabla

            # 3.5 INSERTAR GRÁFICO ESTADÍSTICO
            ruta_img = GestorClientes.generar_grafico_empresas()
            if ruta_img and os.path.exists(ruta_img):
                # Centramos el gráfico (Ancho 140 para que se vea bien)
                pdf.image(ruta_img, x=35, y=None, w=140)
                os.remove(ruta_img) # Borramos la imagen temporal por limpieza ISO

            # 4. FINALIZAR Y GUARDAR
            pdf.output(nombre_archivo)
            return True
        except Exception as e:
            print(f"❌ Error detallado en PDF: {e}")
            return False

    @staticmethod
    def importar_desde_excel(ruta_archivo="clientes.xlsx"):
        try:
            # 1. Leemos el Excel (Asumimos columnas: Nombre y Empresa)
            df = pd.read_excel(ruta_archivo)
            
            # Limpieza básica: Quitamos espacios en blanco
            df['Nombre'] = df['Nombre'].str.strip()
            df['Empresa'] = df['Empresa'].str.strip()

            con = obtener_conexion()
            if con:
                cursor = con.cursor()
                # 2. Inserción masiva
                for _, fila in df.iterrows():
                    cursor.execute(
                        "INSERT INTO clientes (nombre, empresa) VALUES (%s, %s)",
                        (fila['Nombre'], fila['Empresa'])
                    )
                con.commit()
                con.close()
                return True
            return False
        except Exception as e:
            print(f"❌ Error al importar Excel: {e}")
            return False
        
    @staticmethod
    def generar_grafico_empresas():
        try:
            con = obtener_conexion()
            # Consultamos la cuenta de clientes por empresa
            query = "SELECT empresa, COUNT(*) as total FROM clientes GROUP BY empresa"
            df = pd.read_sql(query, con)
            con.close()

            if df.empty: return None

            # Configuramos el gráfico
            plt.figure(figsize=(6, 4)) # Tamaño del gráfico
            plt.bar(df['empresa'], df['total'], color='#005C99') # Azul corporativo
            plt.title('Distribución de Clientes por Empresa', fontsize=12, fontweight='bold')
            plt.xlabel('Empresa')
            plt.ylabel('Cantidad de Contactos')
            plt.xticks(rotation=45, ha='right') # Rotamos nombres si son largos
            plt.tight_layout() # Ajuste automático para que no se corte nada

            # Guardamos el gráfico como imagen temporal
            ruta_grafico = "temp_grafico.png"
            plt.savefig(ruta_grafico)
            plt.close() # Cerramos el gráfico para liberar memoria
            return ruta_grafico
        except Exception as e:
            print(f"❌ Error al crear gráfico: {e}")
            return None

    @staticmethod
    def obtener_dolar_dia():
        try:
            url = "https://mindicador.cl/api/dolar"
            response = requests.get(url, timeout=5)
            data = response.json()
            valor_dolar = data['serie'][0]['valor']
            fecha = data['serie'][0]['fecha'][:10] # Tomamos solo AAAA-MM-DD
            return f"Dólar hoy: ${valor_dolar} ({fecha})"
        except Exception as e:
            print(f"⚠️ No se pudo conectar a mindicador.cl: {e}")
            return "Dólar: No disponible"

    @staticmethod
    def obtener_indicadores():
        try:
            # Consultamos la API (Trae todos los indicadores del día)
            url = "https://mindicador.cl/api"
            response = requests.get(url, timeout=5)
            datos = response.json()

            # Extraemos Dólar y UF
            dolar = datos["dolar"]["valor"]
            uf = datos["uf"]["valor"]
            
            return dolar, uf
        except Exception as e:
            # Si falla la API, devolvemos ceros para no romper la App
            return 0, 0
        
    @staticmethod
    def registrar_cotizacion(cliente_id, monto, dolar, uf, total):
        con = obtener_conexion()
        cursor = con.cursor()
        query = """INSERT INTO historial_cotizaciones 
                   (cliente_id, monto_original, valor_dolar, valor_uf, total_clp) 
                   VALUES (%s, %s, %s, %s, %s)"""
        val = (cliente_id, monto, dolar, uf, total)
        cursor.execute(query, val)
        con.commit()
        con.close()

    @staticmethod
    def obtener_historial():
        con = obtener_conexion()
        cursor = con.cursor()
        # Unimos las dos tablas para traer el nombre del cliente
        query = """
            SELECT h.*, c.nombre 
            FROM historial_cotizaciones h
            INNER JOIN clientes c ON h.cliente_id = c.id
            ORDER BY h.fecha_cotizacion DESC
            LIMIT 50
        """
        cursor.execute(query)
        datos = cursor.fetchall()
        con.close()
        return datos