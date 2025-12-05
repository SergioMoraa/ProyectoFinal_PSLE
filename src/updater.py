# updater.py
# Importamos requests para descargar archivos de internet
import requests
# Importamos os para manejar rutas y archivos
import os

# Definimos la ruta donde se guardarán las listas descargadas
HOSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'hosts')

# Lista de URLs de donde descargaremos los archivos hosts
# Puedes añadir más URLs a esta lista
ADLISTS = [
    # Lista popular unificada de StevenBlack (adware + malware)
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
]

# Función auxiliar para descargar una lista individual
def download_list(url, outpath):
    try:
        # Hacemos la petición GET con un timeout de 30 segundos
        r = requests.get(url, timeout=30)
        # Si la respuesta no es 200 OK, lanzamos una excepción
        r.raise_for_status()
        # Guardamos el contenido en el archivo de destino
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(r.text)
        return True
    except Exception as e:
        # Si falla, imprimimos el error pero no detenemos el programa
        print("Error downloading", url, e)
        return False

# Función principal que actualiza todas las listas
def update_all():
    # Crea el directorio de destino si no existe
    os.makedirs(HOSTS_DIR, exist_ok=True)
    
    # Recorremos la lista de URLs
    for i, url in enumerate(ADLISTS):
        # Generamos un nombre de archivo único para cada lista (adlist_0.txt, adlist_1.txt...)
        fname = f'adlist_{i}.txt'
        outpath = os.path.join(HOSTS_DIR, fname)
        
        print("Downloading", url)
        # Llamamos a la función de descarga
        download_list(url, outpath)
        
    print("Update done.")

# Si ejecutamos este script directamente, corre la actualización
if __name__ == '__main__':
    update_all()
