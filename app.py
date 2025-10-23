from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# === Inicializar base de datos ===
def crear_tabla():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                detalles TEXT NOT NULL,
                estado INTEGER DEFAULT 0
            )
        """)
crear_tabla()


@app.route('/')
def menu():
    return render_template('menu.html')


@app.route('/cocina')
def cocina():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, nombre, detalles FROM pedidos WHERE estado = 0")
        pendientes = [{'id': row[0], 'nombre': row[1], 'detalles': row[2]} for row in cursor.fetchall()]

        cursor.execute("SELECT id, nombre, detalles, estado FROM pedidos WHERE estado IN (1, 2)")
        historial = [{'id': row[0], 'nombre': row[1], 'detalles': row[2], 'estado': row[3]} for row in cursor.fetchall()]

    return render_template('cocina.html', pendientes=pendientes, historial=historial)


@app.route('/pedido', methods=['POST'])
def pedido():
    nombre = request.form['nombre']
    detalles = request.form['detalles']

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pedidos (nombre, detalles, estado) VALUES (?, ?, 0)", (nombre, detalles))
        conn.commit()
        pedido_id = cursor.lastrowid

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

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (estado, pedido_id))
        conn.commit()

    return jsonify({"status": "ok", "estado": estado})


if __name__ == '__main__':
    socketio.run(app, debug=True)
