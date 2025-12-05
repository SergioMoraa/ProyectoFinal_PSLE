# adblock_dns.py
# Importamos la librería argparse para manejar argumentos de línea de comandos
import argparse
# Importamos socket para realizar conexiones de red a bajo nivel (UDP)
import socket
# Importamos clases necesarias de dnslib para crear el servidor DNS y resolver peticiones
from dnslib.server import DNSServer, BaseResolver
# Importamos tipos de registros DNS (RR, QTYPE, A) para construir respuestas
from dnslib import RR, QTYPE, A
# Importamos os para operaciones del sistema operativo (aunque no se usa mucho aquí directamente)
import os
# Importamos funciones de nuestro módulo hosts_store para cargar la lista negra y registrar bloqueos
from hosts_store import load_blacklist, log_block

# Definimos la dirección del servidor DNS "upstream" (al que consultaremos si no bloqueamos)
# En este caso usamos Cloudflare (1.1.1.1) en el puerto 53
UPSTREAM = ('1.1.1.1', 53)   
BLACKLIST = None

# Clase principal que implementa la lógica de resolución de nombres
# Hereda de BaseResolver de la librería dnslib
class AdblockResolver(BaseResolver):
    def __init__(self):
        # Al inicializar, cargamos la lista negra de dominios en memoria
        self.blacklist = load_blacklist()

    # Método que se llama cada vez que llega una petición DNS
    def resolve(self, request, handler):
        # Obtenemos el nombre de dominio consultado (qname), lo convertimos a string,
        # quitamos el punto final si lo tiene y lo pasamos a minúsculas
        qname = str(request.q.qname).rstrip('.').lower()
        
        # Obtenemos el tipo de consulta (A, AAAA, MX, etc.)
        qtype = QTYPE[request.q.qtype]
        
        # Intentamos obtener la IP del cliente que hace la petición para el log
        client = handler.client_address[0] if handler and hasattr(handler, 'client_address') else 'unknown'
        
        # Lógica de bloqueo: verificamos el dominio exacto y sus dominios padre
        # Ejemplo: si piden "ads.google.com", verificamos "ads.google.com", "google.com", "com"
        parts = qname.split('.')
        check = ['.'.join(parts[i:]) for i in range(len(parts))]
        
        # Recorremos las posibles variantes del dominio
        for d in check:
            # Si alguna variante está en nuestra lista negra
            if d in self.blacklist:
                # Preparamos una respuesta DNS
                reply = request.reply()
                # Añadimos una respuesta tipo A apuntando a 0.0.0.0 (bloqueo)
                # TTL (Time To Live) de 300 segundos
                reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=300))
                # Registramos el evento de bloqueo en la base de datos
                log_block(client, qname, qtype)
                # Devolvemos la respuesta de bloqueo y terminamos
                return reply
        
        # Si no está bloqueado, reenviamos la petición al servidor upstream (Cloudflare)
        # Creamos un socket UDP (SOCK_DGRAM) para IPv4 (AF_INET)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Establecemos un tiempo de espera de 2 segundos para no bloquear el hilo si falla
        sock.settimeout(2)
        try:
            # Enviamos el paquete de la petición original al servidor upstream
            sock.sendto(request.pack(), UPSTREAM)
            # Esperamos la respuesta (hasta 4096 bytes)
            resp, _ = sock.recvfrom(4096)
            # Importamos DNSRecord para parsear la respuesta binaria
            from dnslib import DNSRecord
            # Devolvemos la respuesta parseada al cliente original
            return DNSRecord.parse(resp)
        except Exception as e:
            # Si ocurre cualquier error (timeout, red caída), devolvemos una respuesta vacía
            # Esto evita que el servidor se caiga
            reply = request.reply()
            return reply
        finally:
            # Cerramos el socket siempre, haya error o no, para liberar recursos
            sock.close()

# Bloque principal de ejecución
if __name__ == '__main__':
    # Configuramos el parser de argumentos
    parser = argparse.ArgumentParser()
    # Permitimos especificar el puerto con --port (por defecto 53)
    parser.add_argument('--port', type=int, default=53)
    args = parser.parse_args()
    
    # Instanciamos nuestro resolver personalizado
    resolver = AdblockResolver()
    # Creamos el servidor DNS escuchando en todas las interfaces (0.0.0.0) y el puerto elegido
    server = DNSServer(resolver, port=args.port, address='0.0.0.0')
    
    print("Starting DNS server on port", args.port)
    # Iniciamos el servidor en un hilo separado para que no bloquee
    server.start_thread()
    
    try:
        # Mantenemos el programa principal corriendo en un bucle infinito
        import time
        while True:
            # Dormimos 1 segundo en cada iteración para no consumir CPU
            time.sleep(1)
    except KeyboardInterrupt:
        # Si el usuario pulsa Ctrl+C, salimos silenciosamente
        pass
