from flask import Flask, render_template, request
# Importamos la clase de tu archivo crm_backend.py
from crm_backend import GestorClientes 

app = Flask(__name__)

@app.route('/')
def inicio():
    # Capturamos lo que viene de la barra de búsqueda (si existe)
    termino_busqueda = request.args.get('q', '')
    
    try:
        # Pasamos el filtro a tu método listar que ya lo soporta
        datos_clientes = GestorClientes.listar(filtro=termino_busqueda)
    except Exception as e:
        print(f"Error al buscar: {e}")
        datos_clientes = []
    
    return render_template('index.html', 
                           nombre_usuario="Claudio", 
                           clientes=datos_clientes)

from flask import Flask, render_template, request, redirect, url_for # Agregamos redirect y url_for

# ... (tus otras rutas)

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    empresa = request.form.get('empresa')
    nombre = request.form.get('nombre')
    email = request.form.get('email')  # <-- Agregamos esta línea
    
    try:
        # Ahora enviamos los 3 datos a la función guardar
        exito = GestorClientes.guardar(nombre, empresa, email) 
        if exito:
            print(f"✅ Guardado: {nombre} ({email})")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    # El debug=True es vital para ver los errores en pantalla
    app.run(debug=True)