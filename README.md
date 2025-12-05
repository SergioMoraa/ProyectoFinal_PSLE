# AdBlock Pi - DNS Sinkhole en Python

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

**AdBlock Pi** es un servidor DNS ligero y personalizado diseñado para bloquear publicidad, rastreadores y sitios maliciosos a nivel de red. Funciona interceptando las peticiones DNS de los dispositivos conectados y filtrando aquellas que coinciden con listas negras conocidas, devolviendo una dirección nula (`0.0.0.0`) para los dominios bloqueados.

Este proyecto fue desarrollado como una solución educativa para entender el funcionamiento de los protocolos DNS, el manejo de sockets en Python y la integración de servicios web para monitoreo.

##  Características

- **Servidor DNS Personalizado**: Implementado con `dnslib`, capaz de resolver peticiones y bloquear dominios en tiempo real.
- **Bloqueo Inteligente**: Soporta bloqueo exacto y de subdominios (ej. si bloqueas `google.com`, también bloquea `ads.google.com`).
- **Logs y Estadísticas**: Almacena eventos de bloqueo en una base de datos SQLite para su análisis.
- **Interfaz Web / API**: Incluye un servidor Flask (`webui.py`) que expone estadísticas de uso y estado del bloqueo.
- **Actualizador Automático**: Script (`updater.py`) para descargar y consolidar listas de hosts desde fuentes externas (como StevenBlack).
- **Ligero y Portable**: Diseñado para correr en Raspberry Pi o cualquier entorno Linux/Windows con Python.

##  Requisitos

- Python 3.x
- Permisos de administrador/root (necesario para escuchar en el puerto 53).

Las dependencias de Python se encuentran en `requirements.txt`:
- `dnslib`
- `flask`
- `requests`

##  Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/adblock-pi.git
   cd adblock-pi
   ```

2. **Instalar dependencias:**
   Se recomienda usar un entorno virtual.
   ```bash
   pip install -r requirements.txt
   ```

3. **Preparar directorios y listas:**
   Ejecuta el actualizador por primera vez para descargar las listas de bloqueo.
   ```bash
   python src/updater.py
   ```

##  Uso

El sistema consta de tres componentes principales que pueden ejecutarse según necesidad.

### 1. Iniciar el Servidor DNS
Este es el núcleo del proyecto. Debe ejecutarse con permisos elevados para usar el puerto 53.

```bash
# En Linux/Mac (requiere sudo)
sudo python src/adblock_dns.py --port 53

# En Windows (ejecutar terminal como Administrador)
python src/adblock_dns.py --port 53
```
*Nota: Si el puerto 53 está ocupado, puedes probar con otro puerto (ej. 5353) para pruebas locales.*

### 2. Iniciar la Interfaz Web
Para ver las estadísticas de bloqueo y el estado del sistema.

```bash
python src/webui.py
```
Accede desde tu navegador a: `http://localhost:8080/stats`

### 3. Actualizar Listas de Bloqueo
Para mantener la base de datos de dominios actualizada.

```bash
python src/updater.py
```

##  Estructura del Proyecto

```
adblock-pi/
├── data/                   # Almacenamiento de datos
│   ├── hosts/              # Archivos de texto con dominios a bloquear
│   └── logs.db             # Base de datos SQLite con historial de bloqueos
├── src/                    # Código fuente
│   ├── adblock_dns.py      # Servidor DNS principal (UDP Socket)
│   ├── hosts_store.py      # Lógica de base de datos y carga de hosts
│   ├── updater.py          # Gestor de descargas de listas externas
│   └── webui.py            # API/Webserver Flask para monitoreo
├── systemd/                # Archivos de configuración para servicio (Linux)
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación
```

##  Configuración de Clientes

Para que el bloqueo funcione en tus dispositivos (PC, Móvil, Tablet), debes configurar su servidor DNS apuntando a la dirección IP de la máquina donde corre **AdBlock Pi**.

1. Averigua la IP de tu servidor (ej. `ipconfig` en Windows o `ip a` en Linux).
2. En el dispositivo cliente, ve a la configuración de red.
3. Cambia el DNS primario por la IP de tu servidor (ej. `192.168.1.X`).

##  Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir qué te gustaría cambiar.

##  Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para detalles.
