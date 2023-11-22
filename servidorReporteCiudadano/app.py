from flask import Flask, request, render_template
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Configuración de la base de datos SQLite
DATABASE = 'reportes.db'

# Función para conectar a la base de datos y crear la tabla si no existe
def connect_db():
    connection = sqlite3.connect(DATABASE)
    with connection:
        cursor = connection.cursor()
        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_reporte TEXT,
                descripcion TEXT,
                coordenadas TEXT,
                imagen_path TEXT,
                fecha_hora DATETIME,
                estado_evento TEXT
            )
        ''')
    return connection

# Ruta principal para manejar la solicitud POST
@app.route('/enviar_reporte', methods=['POST'])
def recibir_reporte():
    try:
        # Obtener datos del formulario
        tipo_reporte = request.form['tipo_reporte']
        descripcion = request.form['descripcion']
        coordenadas = request.form['coordenadas']
        estado_evento = request.form['estado_evento']

        # Obtener la imagen y guardarla en el servidor
        imagen = request.files['imagen']
        imagen_filename = f"imagen_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        imagen_path = os.path.join('imagenes', imagen_filename)
        imagen.save(imagen_path)

        # Guardar los datos en la base de datos
        with connect_db() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO reportes (tipo_reporte, descripcion, coordenadas, imagen_path, fecha_hora, estado_evento)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tipo_reporte, descripcion, coordenadas, imagen_path, datetime.now(), estado_evento))
            connection.commit()

        return 'Reporte recibido y guardado correctamente.'

    except Exception as e:
        return f'Error al procesar el reporte: {str(e)}'

# Ruta para mostrar los reportes almacenados
@app.route('/ver_reportes')
def ver_reportes():
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM reportes')
        reportes = cursor.fetchall()
    return render_template('reportes.html', reportes=reportes)

if __name__ == '__main__':
    app.run(debug=True)

# Ruta para mostrar el detalle de un reporte
@app.route('/detalle_reporte/<int:reporte_id>')
def detalle_reporte(reporte_id):
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM reportes WHERE id = ?', (reporte_id,))
        reporte = cursor.fetchone()
    return render_template('detalle_reporte.html', reporte=reporte)