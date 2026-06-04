from socketserver import ThreadingTCPServer,BaseRequestHandler

class Proveedor:
	def __init__(self, id, nombre, servicio, costo, ip, puerto):
		self.id_proveedor = id
		self.nombre = nombre
		self.servicio = servicio
		self.costo = costo
		self.ip = ip
		self.puerto = puerto

	def __str__(self):
		return (f"id:{self.id_proveedor}. "
			f"nombre:{self.nombre} | "
			f"servicio:{self.servicio} | "
			f"costo:${self.costo} COP | "
			f"ip:{self.ip}:{self.puerto}" )

class BaseDatosProveedores:
	def __init__(self):
		self.proveedores = []
		self.siguiente_id = 1

	def registrar(self, nombre, servicio, costo, ip, puerto):
		proveedor = Proveedor(self.siguiente_id, nombre, servicio, costo, ip, puerto)
		self.proveedores.append(proveedor)
		self.siguiente_id +=1
		return proveedor

	def listar(self):
		return self.proveedores


class ServiceMarketServ(BaseRequestHandler):
	def handle(self):

		msg = "Bienvenido a Service Market\n Escribe HELP para conocer "\
			"los posibles comandos que dispones\n"
		self.request.send(msg.encode())

		print("Conexión desde:", self.client_address)
		host, port = self.client_address
		while True:
			mensaje = self.request.recv(1024).decode().strip()
			if mensaje == "":
				continue
			partes = mensaje.split()
			comando = partes[0].upper()
			print("{",f"{host}:{port}","}:", mensaje)
			if comando == "HELP":
				respuesta = f"Para esta app puedes usar:\n" \
					"Registrar <device>\n"\
					"Listar\n" \
					"Salir\n"

			elif  comando == "REGISTRAR":
				proveedor = bd.registrar(partes[1], partes[2], partes[3], partes [4], partes[5])
				respuesta = "OK Proveedor registrado"

			elif comando == "LISTAR":
				respuesta = "PROVEEDORES\n"
				for proveedor in bd.listar():
					respuesta += str(proveedor) + "\n"

			elif comando == "SALIR":
				respuesta = "Conexión cerrada"
				print(f"Client left {self.client_address} \r\n")
				self.request.send(respuesta.encode())
				self.request.close()
				break


			else:
				respuesta = "ERROR, comando no encontrado \r\n"
			self.request.send(respuesta.encode())



bd = BaseDatosProveedores()

market = ThreadingTCPServer(("0.0.0.0", 5000), ServiceMarketServ)
print("Service Market iniciado en 0.0.0.0:5000")
market.serve_forever()

