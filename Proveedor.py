from socket import *
from socketserver import ThreadingUDPServer, BaseRequestHandler


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
		print(f"{self.nombre} escuchando UDP en {self.ip}:{self.puerto_udp}")
		servidor_udp.serve_forever()


class ProveedorUDPHandler(BaseRequestHandler):
	def handle(self):
		data, socket_udp = self.request
		mensaje = data.decode().strip()

		print("Solicitud UDP desde",self.client_address,":",mensaje)

		respuesta = ("OK|Proveedor recibio|"+ mensaje)

		socket_udp.sendto(respuesta.encode(),self.client_address)


proveedor = ProveedorServicio("ProveedorHora","HM","500","127.0.0.1",7001,"127.0.0.1",5000)

proveedor.registrarse()

proveedor.iniciar_servidor_udp()
