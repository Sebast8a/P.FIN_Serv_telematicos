from socket import *
from sys import argv, exit

class ClienteUDP:

	def __init__(self, ip_proveedor, puerto_proveedor):
		self.ip_proveedor = ip_proveedor
		self.puerto_proveedor = int(puerto_proveedor)
		self.cliente = socket(AF_INET, SOCK_DGRAM)

	def iniciar(self):
		print("====================================")
		print("Cliente UDP conectado al proveedor")
		print(f"Proveedor: {self.ip_proveedor}:{self.puerto_proveedor}")
		print("Escribe HELP para conocer los comandos")
		print("Escribe SALIR para cerrar el cliente")
		print("====================================")

		while True:
			mensaje = input("> ").strip()

			if mensaje == "":
				print("ERROR No puede enviar una solicitud vacia")
				continue

			self.enviar(mensaje)
			respuesta = self.recibir()
			print(respuesta)

			if mensaje.upper() == "SALIR":
				self.cerrar()
				break

	def enviar(self, mensaje):
		self.cliente.sendto(mensaje.encode(), (self.ip_proveedor, self.puerto_proveedor))

	def recibir(self):
		respuesta, servidor = self.cliente.recvfrom(4096)
		return respuesta.decode().strip()

	def cerrar(self):
		self.cliente.close()
		print("Cliente cerrado correctamente")


if len(argv) != 3:
	print("Uso:")
	print("python3 ClienteUDP.py <ip_proveedor> <puerto_proveedor>")
	print("")
	print("Ejemplos:")
	print("python3 ClienteUDP.py 127.0.0.1 7001")
	print("python3 ClienteUDP.py 127.0.0.1 7002")
	print("python3 ClienteUDP.py 127.0.0.1 7003")
	exit(1)

ip_proveedor = argv[1]
puerto_proveedor = argv[2]

cliente = ClienteUDP(ip_proveedor, puerto_proveedor)
cliente.iniciar()
