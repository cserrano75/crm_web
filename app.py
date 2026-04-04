from flask import Flask, render_template, request
# Importamos la clase de tu archivo crm_backend.py
from crm_backend import GestorClientes 
from flask import Flask, render_template, request, redirect, url_for # Agregamos redirect y url_for

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
    # Capturamos todos los campos del formulario
    id_cliente = request.form.get('id_cliente')  # Este vendrá del modal de edición
    empresa = request.form.get('empresa')
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    
    try:
        # LÓGICA DE RECICLAJE:
        if id_cliente:
            # Si tiene ID, es un cliente que ya existe -> ACTUALIZAMOS
            exito = GestorClientes.actualizar(id_cliente, nombre, empresa, email)
            accion = "Actualizado"
        else:
            # Si no tiene ID, es uno nuevo -> GUARDAMOS
            exito = GestorClientes.guardar(nombre, empresa, email)
            accion = "Guardado"

        if exito:
            print(f"✅ {accion}: {nombre} ({empresa})")
            
    except Exception as e:
        print(f"⚠️ Error en el procesamiento: {e}")
    
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    # El debug=True es vital para ver los errores en pantalla
    app.run(debug=True)