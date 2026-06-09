from socket import *
from socketserver import ThreadingUDPServer, BaseRequestHandler
from datetime import datetime, timedelta
from sys import argv, exit

# ------------------ Servicios ------------------
class Servicio:

	def __init__(self, nombre, codigo, costo, ip, puerto_udp):
		self.nombre = nombre
		self.codigo = codigo.upper()
		self.costo = costo
		self.ip = ip
		self.puerto_udp = int(puerto_udp)

	def atender(self, partes):
		return "ERROR Servicio no implementado\n"

	def validar_comando(self, partes):
		if len(partes) == 0:
			return False

		return partes[0].upper() == self.codigo

class ServicioHoraMundial(Servicio):

	def atender(self, partes):
		if len(partes) != 2:
			return "ERROR Formato correcto: HM codigo_pais\n"

		pais = partes[1].upper()

		diferencias = {
			"CO": 0,
			"MX": -1,
			"AR": 2,
			"BR": 2,
			"US": -1,
			"DE": 6,
			"ES": 6,
			"JP": 14,
			"UK": 6
		}

		if pais not in diferencias:
			return "ERROR Pais no soportado\n"

		hora = datetime.now() + timedelta(hours=diferencias[pais])
		hora_texto = hora.strftime("%Y-%m-%d %H:%M:%S")

		return f"OK HM {pais} {hora_texto}\n"

class ServicioCifradoCesar(Servicio):

	def atender(self, partes):
		if len(partes) != 3:
			return "ERROR Formato correcto: CC texto desplazamiento\n"

		texto = partes[1]

		try:
			desplazamiento = int(partes[2])
		except ValueError:
			return "ERROR El desplazamiento debe ser numerico\n"

		texto_cifrado = self.cifrar_cesar(texto, desplazamiento)

		return f"OK CC {texto} {texto_cifrado}\n"

	def cifrar_cesar(self, texto, desplazamiento):
		resultado = ""

		for caracter in texto:
			if caracter.isalpha():
				if caracter.isupper():
					base = ord("A")
				else:
					base = ord("a")

				nuevo = chr((ord(caracter) - base + desplazamiento) % 26 + base)
				resultado += nuevo
			else:
				resultado += caracter

		return resultado

class ServicioDominioIP(Servicio):
	def __init__(self, nombre, codigo, costo, ip, puerto_udp):
		super().__init__(nombre, codigo, costo, ip, puerto_udp)

		self.tabla_dominios = {
			"A": {
				"www.ejemplo.com": "1.1.1.1",
				"www.google.com": "8.8.8.8",
				"www.unicauca.edu.co": "200.21.83.20",
				"www.facebook.com": "31.13.65.36",
				"www.youtube.com": "142.250.78.14"
			},
			"AAAA": {
				"www.ejemplo.com": "2606:4700:4700::1111",
				"www.google.com": "2001:4860:4860::8888"
			}
		}


	def atender(self, partes):
		if len(partes) != 3:
			return "ERROR Formato correcto: DIP <tipo_direccion> <dominio>\n"

		tipo_direccion = partes[1].upper()
		dominio = partes[2].strip().lower()
		dominio = self.limpiar_dominio(dominio)

		if tipo_direccion == "":
			return "ERROR Tipo de direccion invalido\n"

		if dominio == "":
			return "ERROR Dominio invalido\n"

		if tipo_direccion not in self.tabla_dominios:
			return "ERROR Tipo de direccion no soportado. Use A o AAAA\n"

		if dominio not in self.tabla_dominios[tipo_direccion]:
			return "ERROR Dominio no registrado en la tabla DIP\n"

		ip = self.tabla_dominios[tipo_direccion][dominio]

		return f"OK {dominio} : {ip}\n"

	def limpiar_dominio(self, dominio):
		if "://" in dominio:
			dominio = dominio.split("://")[1]

		dominio = dominio.split("/")[0]
		dominio = dominio.strip()

		return dominio


# ------------------ Proveedor ------------------
class ProveedorServicio:

	def __init__(self, servicio, ip_market, puerto_market):
		self.servicio = servicio
		self.ip_market = ip_market
		self.puerto_market = int(puerto_market)

	def registrarse(self):
		cliente_tcp = socket(AF_INET, SOCK_STREAM)
		cliente_tcp.connect((self.ip_market, self.puerto_market))

		bienvenida = cliente_tcp.recv(1024).decode()
		print(bienvenida)

		cliente_tcp.send("PROVEEDOR".encode())

		respuesta_rol = cliente_tcp.recv(1024).decode()
		print(respuesta_rol)

		mensaje = (
			f"REGISTRAR {self.servicio.nombre} "
			f"{self.servicio.codigo} "
			f"{self.servicio.costo} "
			f"{self.servicio.ip} "
			f"{self.servicio.puerto_udp}"
		)

		cliente_tcp.send(mensaje.encode())

		respuesta = cliente_tcp.recv(1024).decode()
		print("Respuesta del ServiceMarket:", respuesta)

		cliente_tcp.send("SALIR".encode())
		cliente_tcp.close()

	def iniciar_servidor_udp(self):
		ProveedorUDPHandler.servicio = self.servicio

		servidor_udp = ProveedorUDPServer((self.servicio.ip, self.servicio.puerto_udp),
				ProveedorUDPHandler)

		print(f"{self.servicio.nombre} escuchando UDP en {self.servicio.ip}:{self.servicio.puerto_udp}")
		print(f"Servicio ofrecido: {self.servicio.codigo}")

		servidor_udp.serve_forever()

# ------------------ Handler UDP ------------------
class ProveedorUDPHandler(BaseRequestHandler):

	servicio = None

	def handle(self):
		data, socket_udp = self.request
		mensaje = data.decode().strip()

		print("Solicitud UDP desde", self.client_address, ":", mensaje)

		respuesta = self.procesar_solicitud(mensaje)

		socket_udp.sendto(respuesta.encode(), self.client_address)

	def procesar_solicitud(self, mensaje):
		partes = mensaje.split()

		if len(partes) == 0:
			return "ERROR Solicitud vacia\n"

		comando = partes[0].upper()

		if self.servicio is None:
			return "ERROR Servicio no configurado en el proveedor\n"

		if comando == "HELP":
			return self.obtener_ayuda()

		if comando == "SALIR":
			return "Conexion UDP cerrada para este cliente\n"

		if comando != self.servicio.codigo:
			return f"ERROR Este proveedor solo ofrece {self.servicio.codigo}\n"

		return self.servicio.atender(partes)

	def obtener_ayuda(self):
		if self.servicio.codigo == "HM":
			return ("Bienvenido al proveedor de Hora Mundial\n"
				"Comandos disponibles:\n"
				"HELP\n"
				"HM <codigo_pais>\n"
				"SALIR\n"
				"\n"
				"Ejemplo:\n"
				"HM CO\n")

		if self.servicio.codigo == "CC":
			return ("Bienvenido al proveedor de Cifrado Cesar\n"
				"Comandos disponibles:\n"
				"HELP\n"
				"CC <texto> <desplazamiento>\n"
				"SALIR\n"
				"\n"
				"Ejemplo:\n"
				"CC hola 3\n")

		if self.servicio.codigo == "DIP":
			return ("Bienvenido al proveedor de Dominio IP\n"
				"Comandos disponibles:\n"
				"HELP\n"
				"DIP tipo_direccion dominio\n"
				"SALIR\n"
				"\n"
				"Tipos de direccion disponibles:\n"
				"A    -> IPv4\n"
				"AAAA -> IPv6\n"
				"\n"
				"Ejemplos:\n"
				"DIP A www.ejemplo.com\n"
				"DIP A www.google.com\n"
				"DIP AAAA www.ejemplo.com\n")

		return "HELP no disponible\n"

class ProveedorUDPServer(ThreadingUDPServer):
	allow_reuse_address = True

# ------------------ Función principal ------------------
def run_proveedor(nombre, codigo, costo, ip_udp, puerto_udp, ip_market, puerto_market):
    codigo = codigo.upper()
    if codigo == "HM":
        servicio = ServicioHoraMundial(nombre, codigo, costo, ip_udp, puerto_udp)
    elif codigo == "CC":
        servicio = ServicioCifradoCesar(nombre, codigo, costo, ip_udp, puerto_udp)
    elif codigo == "DIP":
        servicio = ServicioDominioIP(nombre, codigo, costo, ip_udp, puerto_udp)
    else:
        print("ERROR Servicio invalido. Use HM, CC o DIP")
        return
    proveedor = ProveedorServicio(servicio, ip_market, puerto_market)
    proveedor.registrarse()
    proveedor.iniciar_servidor_udp()



if len(argv) != 8:
	print("Uso:")
	print("python3 Proveedor.py <nombre> <codigo> <costo> <ip_udp> <puerto_udp>"
		" <ip_market> <puerto_market>")
	print("Servicios disponibles: HM, CC, DIP")
	exit(1)

nombre = argv[1]
codigo = argv[2]
costo = argv[3]
ip_udp = argv[4]
puerto_udp = argv[5]
ip_market = argv[6]
puerto_market = argv[7]

run_proveedor(nombre, codigo, costo, ip_udp, puerto_udp, ip_market, puerto_market)


