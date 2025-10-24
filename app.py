from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import psycopg2
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# === Conexión a base de datos PostgreSQL ===
DATABASE_URL = os.environ.get("DATABASE_URL")

# Render a veces usa postgres:// en lugar de postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# === Función para obtener conexión ===
def get_connection():
    return psycopg2.connect(DATABASE_URL)

# === Inicializar tabla ===
def crear_tabla():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    detalles TEXT NOT NULL,
                    estado INTEGER DEFAULT 0
                )
            """)
        conn.commit()

crear_tabla()

# === Rutas ===
@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/cocina')
def cocina():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre, detalles FROM pedidos WHERE estado = 0")
            pendientes = [{'id': row[0], 'nombre': row[1], 'detalles': row[2]} for row in cursor.fetchall()]

            cursor.execute("SELECT id, nombre, detalles, estado FROM pedidos WHERE estado IN (1, 2)")
            historial = [{'id': row[0], 'nombre': row[1], 'detalles': row[2], 'estado': row[3]} for row in cursor.fetchall()]

    return render_template('cocina.html', pendientes=pendientes, historial=historial)

@app.route('/pedido', methods=['POST'])
def pedido():
    nombre = request.form['nombre']
    detalles = request.form['detalles']

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pedidos (nombre, detalles, estado) VALUES (%s, %s, 0) RETURNING id",
                (nombre, detalles)
            )
            pedido_id = cursor.fetchone()[0]
        conn.commit()

    nuevo_pedido = {"id": pedido_id, "nombre": nombre, "detalles": detalles}
    socketio.emit('nuevo_pedido', nuevo_pedido)
    return jsonify({"status": "ok"})

@app.route('/actualizar_estado', methods=['POST'])
def actualizar_estado():
    data = request.get_json()
    pedido_id = data.get('id')
    estado = data.get('estado')

    if not pedido_id or estado not in [1, 2]:
        return jsonify({"status": "error", "message": "Datos inválidos"}), 400

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (estado, pedido_id))
        conn.commit()

    return jsonify({"status": "ok", "estado": estado})

if __name__ == '__main__':
    socketio.run(app, debug=True)
