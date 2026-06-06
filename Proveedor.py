from socket import *
from socketserver import ThreadingUDPServer, BaseRequestHandler
import string
from datetime import datetime, timedelta



class ProveedorServicio:

	def __init__(self, nombre, servicio, costo, ip, puerto_udp,ip_market, puerto_market):
		self.nombre = nombre
		self.servicio = servicio
		self.costo = costo
		self.ip = ip
		self.puerto_udp = puerto_udp
		self.ip_market = ip_market
		self.puerto_market = puerto_market

	def registrarse(self):

		cliente_tcp = socket(AF_INET, SOCK_STREAM)
		cliente_tcp.connect((self.ip_market, self.puerto_market))

		bienvenida = cliente_tcp.recv(1024).decode()
		print(bienvenida)

		mensaje = (f"REGISTRAR {self.nombre} {self.servicio} {self.costo} {self.ip} "
			f"{self.puerto_udp}")
		cliente_tcp.send(mensaje.encode())

		respuesta = cliente_tcp.recv(1024).decode()
		print("Respuesta del ServiceMarket:",respuesta)

		cliente_tcp.close()

	def iniciar_servidor_udp(self):
		servidor_udp = ThreadingUDPServer((self.ip, self.puerto_udp),
			ProveedorUDPHandler)
		print(f"{self.nombre} escuchando UDP en {self.ip}:{self.puerto_udp}\n")
		servidor_udp.serve_forever()


class ProveedorUDPHandler(BaseRequestHandler):

	servicio = ""

	def handle(self):
		data, socket_udp = self.request
		mensaje = data.decode().strip()

		print("Solicitud UDP desde",self.client_address,":",mensaje)

		respuesta = ("OK Proveedor recibio"+ mensaje)

		socket_udp.sendto(respuesta.encode(),self.client_address)

	def procesar_solicitud(self, mensaje):
		partes = mensaje.split()

		if len(partes) == 0:
			return "Error Solicitud vacía \n"

		comando = partes[0].upper()

		if comando != self.servicio:
			return f"Error Este proveedor solo ofrece el servicio {self.servicio}\n"

		if comando == "HM":
			return self.servicio_hora_mundial(partes)

		if comando == "CC":
			return self.servicio_cifrado_cesar(partes)

		if comando == "DIP":
			return self.servicio_dominio_ip(partes)

		return "Error servicio no soportado"

	def servicio_hora_mundial(self, partes):
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
			"JP": 14
		}

		if pais not in diferencias:
			return "ERROR Pais no soportado\n"

		hora = datetime.now() + timedelta(hours=diferencias[pais])
		hora_texto = hora.strftime("%Y-%m-%d %H:%M:%S")

		return f"OK HM {pais} {hora_texto}\n"

	def servicio_cifrado_cesar(self, partes):
		if len(partes) != 3:
			return "ERROR Formato incorrecto: CC texto desplazamiento\n"

		texto = partes[1].lower()

		desplazamiento = int(partes[2])

		texto_cifrado = self.cifrar_cesar(texto, desplazamiento)

		return f"OK CC {texto}{texto_cifrado}\n"

	def cifrar_cesar(self, texto, desplzamaiento):
		resultado = ""

		for caracter in texto:
			if caracter.isalpha():
				base = ord('A') if caracter.isupper() else ord('a')
				nuevo = chr((ord(caracter) - base + desplazamiento) % 26 + base)
				resultado += nuevo
			else:
				resultado += caracter

		return resultado

	def servicio_dominio_ip(self, partes):
		if len(partes) != 2:
			return "ERROR Formato correcto: DIP dominio\n"

		dominio = partes[1]

		ip = nslookup(dominio)

		return "OK DIP {dominio} {IP}\n"





proveedor = ProveedorServicio("ProveedorHora","HM","500","127.0.0.1",7001,"127.0.0.1",5000)

proveedor.registrarse()

proveedor.iniciar_servidor_udp()
