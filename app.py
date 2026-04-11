from flask import Flask, render_template, request
# Importamos la clase de tu archivo crm_backend.py
from crm_backend import GestorClientes 
from flask import Flask, render_template, request, redirect, url_for # Agregamos redirect y url_for
from flask import send_file

app = Flask(__name__)

@app.route('/')
def inicio():
    termino_busqueda = request.args.get('q', '')
    
    # Valor de la UF (puedes actualizarlo según el valor real de hoy)
    uf_del_dia = "38.450,21" 
    
    try:
        datos_clientes = GestorClientes.listar(filtro=termino_busqueda)
    except Exception as e:
        print(f"Error: {e}")
        datos_clientes = []
    
    return render_template('index.html', 
                           nombre_usuario="Claudio", 
                           clientes=datos_clientes,
                           valor_uf=uf_del_dia) # <-- Pasamos la variable aquí

@app.route('/procesar_cliente', methods=['POST'])
def procesar_cliente():
    # Recibimos los datos del formulario (vengan del modal "Nuevo" o "Detalles")
    id_cliente = request.form.get('id_cliente') 
    nombre = request.form.get('nombre')
    empresa = request.form.get('empresa')
    email = request.form.get('email')

    if id_cliente:
        # Si hay ID, estamos EDITANDO
        GestorClientes.actualizar(id_cliente, nombre, empresa, email)
    else:
        # Si NO hay ID, estamos CREANDO
        GestorClientes.guardar(nombre, empresa, email)

    return redirect(url_for('inicio'))

@app.route('/calcular_uf', methods=['POST'])
def calcular_uf():
    # El valor de la UF que ya tienes definido (limpiamos puntos y comas para operar)
    valor_uf_limpio = 38450.21  
    
    monto_pesos = request.form.get('pesos', 0)
    
    try:
        # Convertimos a float para poder dividir
        resultado_uf = float(monto_pesos) / valor_uf_limpio
        # Redondeamos a 2 decimales, como se usa en minería
        resultado_final = round(resultado_uf, 2)
    except:
        resultado_final = 0

    # Por ahora lo imprimimos en consola para probar, luego lo llevamos al HTML
    print(f"Calculando: {monto_pesos} pesos son {resultado_final} UF")
    return redirect(url_for('inicio'))

@app.route('/descargar_reporte')
def descargar_reporte():
    nombre_pdf = "Reporte_Clientes.pdf"
    exito = GestorClientes.generar_reporte_pdf(nombre_pdf)
    
    if exito:
        return send_file(nombre_pdf, as_attachment=True)
    else:
        return "Error al generar el reporte", 500

if __name__ == '__main__':
    # El debug=True es vital para ver los errores en pantalla
    app.run(debug=True)