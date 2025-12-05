# hosts_store.py
# Importamos sqlite3 para manejar la base de datos de logs
import sqlite3
# Importamos os para manejar rutas de archivos y directorios
import os
# Importamos time para obtener la marca de tiempo actual
import time

# Definimos la ruta absoluta a la base de datos 'logs.db'
# Se ubica en la carpeta 'data' un nivel arriba de 'src'
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs.db')
# Definimos la ruta absoluta al directorio donde están los archivos hosts
HOSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'hosts')

# Función para asegurar que la base de datos y la tabla existen
def ensure_db():
    # Crea el directorio de la base de datos si no existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # Conecta a la base de datos (la crea si no existe)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Ejecuta la sentencia SQL para crear la tabla 'blocked_events' si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS blocked_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            client_ip TEXT,
            qname TEXT,
            qtype TEXT
        )
    ''')
    # Guarda los cambios
    conn.commit()
    # Cierra la conexión
    conn.close()

# Función para registrar un evento de bloqueo
def log_block(client_ip, qname, qtype='A'):
    # Primero nos aseguramos de que la DB esté lista
    ensure_db()
    # Obtenemos el tiempo actual en segundos (Unix timestamp)
    ts = int(time.time())
    # Conectamos a la base de datos
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Insertamos el registro del bloqueo
    c.execute('INSERT INTO blocked_events (timestamp, client_ip, qname, qtype) VALUES (?,?,?,?)',
              (ts, client_ip, qname, qtype))
    # Guardamos y cerramos
    conn.commit()
    conn.close()

# Función para cargar todas las listas negras en memoria
def load_blacklist():
    # Creamos un conjunto (set) vacío para almacenar los dominios únicos
    # Usamos set porque la búsqueda es mucho más rápida que en una lista
    s = set()
    # Aseguramos que el directorio de hosts exista
    os.makedirs(HOSTS_DIR, exist_ok=True)
    
    # Recorremos todos los archivos en el directorio de hosts
    for fname in os.listdir(HOSTS_DIR):
        # Solo procesamos archivos que terminen en .txt
        if not fname.endswith('.txt'):
            continue
        
        # Abrimos el archivo en modo lectura
        with open(os.path.join(HOSTS_DIR, fname), 'r', encoding='utf-8', errors='ignore') as f:
            # Leemos línea por línea
            for line in f:
                # Eliminamos espacios en blanco al inicio y final
                line=line.strip()
                # Ignoramos líneas vacías o comentarios (que empiezan con #)
                if not line or line.startswith('#'):
                    continue
                
                # Procesamos líneas típicas de hosts: "0.0.0.0 ejemplo.com" o "127.0.0.1 ejemplo.com"
                parts = line.split()
                # Tomamos la última parte que suele ser el dominio
                domain = parts[-1].lower()
                
                # Si hay un dominio válido, lo añadimos al conjunto
                if domain:
                    s.add(domain)
    # Devolvemos el conjunto completo de dominios bloqueados
    return s
