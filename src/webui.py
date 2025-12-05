# webui.py
# Importamos Flask y funciones auxiliares para crear la API web
from flask import Flask, jsonify, request
# Importamos librerías estándar
import sqlite3, os, time
# Importamos la función para cargar la blacklist y mostrar estadísticas
from hosts_store import load_blacklist

# Definimos la ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs.db')

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Función auxiliar para conectar a la base de datos
def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Ruta '/stats': Devuelve estadísticas de bloqueo en formato JSON
@app.route('/stats')
def stats():
    conn = get_db()
    c = conn.cursor()
    
    # Consulta 1: Contar el total de eventos bloqueados
    c.execute('SELECT COUNT(*) FROM blocked_events')
    # Obtenemos el resultado (si es None, devolvemos 0)
    total = c.fetchone()[0] if c.fetchone() is not None else 0
    
    # Consulta 2: Obtener los últimos 20 eventos bloqueados para mostrar en tiempo real
    c.execute('SELECT timestamp, client_ip, qname FROM blocked_events ORDER BY timestamp DESC LIMIT 20')
    rows = c.fetchall()
    
    conn.close()
    
    # Devolvemos un JSON con el total y la lista de últimos eventos
    return jsonify({
        "total_blocks": total,
        "last": [{"time": r[0], "client": r[1], "domain": r[2]} for r in rows]
    })

# Ruta '/blacklist': Muestra información sobre la lista negra cargada
@app.route('/blacklist')
def bl():
    # Cargamos la lista negra actual en memoria
    s = list(load_blacklist())
    # Devolvemos el total de dominios y una muestra de los primeros 20
    return jsonify({"count": len(s), "sample": s[:20]})

# Si ejecutamos este script, iniciamos el servidor web en el puerto 8080
if __name__ == '__main__':
    # host='0.0.0.0' permite conexiones desde cualquier IP de la red
    app.run(host='0.0.0.0', port=8080)
