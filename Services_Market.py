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

	def datos_conexion(self):
		return (
			f"PROVEEDOR {self.id_proveedor} "
			f"{self.nombre} "
			f"{self.servicio} "
			f"{self.costo} "
			f"{self.ip} "
			f"{self.puerto}"
		)


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

	def seleccionar(self, id_proveedor):
		for proveedor in self.proveedores:
			if proveedor.id_proveedor == id_proveedor:
				return proveedor

		return None


class ServiceMarketServ(BaseRequestHandler):
	def handle(self):

		msg = "Bienvenido a Service Market\n Escribe HELP para conocer "\
			"los posibles comandos que dispones\n"
		self.request.send(msg.encode())

		print("Conexión desde:", self.client_address)
		host, port = self.client_address
		while True:
			mensaje = self.request.recv(1024).decode().strip()
			#Si no se ingresa nada continua, para que el programa siga funcionando
			if mensaje == "":
				continue

			partes = mensaje.split()
			comando = partes[0].upper()
			print("{",f"{host}:{port}","}:", mensaje)
			if comando == "HELP":
				respuesta = (
					"Para esta app puedes usar:\n"
					"REGISTRAR nombre servicio costo ip puerto\n"
					"LISTAR\n"
					"SELECCIONAR id\n"
					"SALIR\n"
					)

			elif comando == "REGISTRAR":
				if len(partes) != 6:
					respuesta = "ERROR Formato correcto: REGISTRAR nombre servicio costo ip puerto\n"

				else:
					nombre = partes[1]
					servicio = partes[2].upper()
					costo = partes[3]
					ip = partes[4]
					puerto = partes[5]

					if servicio != "HM" and servicio != "CC" and servicio != "DIP":
						respuesta = "ERROR Servicio invalido. Use HM, CC o DIP\n"

					else:
						proveedor = bd.registrar(nombre, servicio, costo, ip, puerto)
						respuesta = f"OK Proveedor registrado con id {proveedor.id_proveedor}\n"

			elif comando == "LISTAR":
				proveedores = bd.listar()

				if len(proveedores) == 0:
					respuesta = "ERROR No hay proveedores registrados\n"

				else:
					respuesta = "PROVEEDORES\n"

					for proveedor in proveedores:
						respuesta += str(proveedor) + "\n"

			elif comando == "SELECCIONAR":
				if len(partes) != 2:
					respuesta = "ERROR Formato correcto: SELECCIONAR id\n"

				else:
					try:
						id_proveedor = int(partes[1])
						proveedor = bd.seleccionar(id_proveedor)

						if proveedor is None:
							respuesta = "ERROR Proveedor no encontrado\n"

						else:
							respuesta = proveedor.datos_conexion() + "\n"

					except ValueError:
						respuesta = "ERROR El id debe ser numerico\n"

			elif comando == "SALIR":
				respuesta = "Conexion cerrada\n"
				print(f"Client left {self.client_address} \r\n")
				self.request.send(respuesta.encode())
				self.request.close()
				break

			else:
				respuesta = "ERROR Comando no encontrado\n"

			self.request.send(respuesta.encode())





bd = BaseDatosProveedores()

market = ThreadingTCPServer(("0.0.0.0", 5000), ServiceMarketServ)
print("Service Market iniciado en 0.0.0.0:5000")
market.serve_forever()

