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
		return (f"id:{self.id_proveedor} | "
			f"nombre:{self.nombre} | "
			f"servicio:{self.servicio} | "
			f"costo:${self.costo} COP")
#			f"ip:{self.ip}:{self.puerto}" )

	def datos_conexion(self):
		return (
			f"PROVEEDOR {self.id_proveedor} "
			f"{self.nombre} "
#			f"{self.servicio} "
#			f"{self.costo} "
			f"{self.ip} : "
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
		print("Conexion desde:", self.client_address)

		self.enviar_menu_inicial()

		rol = self.recibir_rol()

		if rol == "CLIENTE":
			self.atender_cliente()

		elif rol == "PROVEEDOR":
			self.atender_proveedor()

		else:
			self.enviar("Conexion cerrada\n")
			self.request.close()


	def enviar(self, mensaje):
		self.request.send(mensaje.encode())

	def recibir(self):
		return self.request.recv(1024).decode().strip()

	def enviar_menu_inicial(self):
		mensaje = (
			"====================================\n"
			"Bienvenido a Service Market\n"
			"Seleccione una opcion:\n"
			"CLIENTE\n"
			"PROVEEDOR\n"
			"SALIR\n"
			"====================================\n"
			"> "
		)
		self.enviar(mensaje)

	def recibir_rol(self):
		while True:
			mensaje = self.recibir()

			if mensaje == "":
				return "SALIR"

			rol = mensaje.upper()

			if rol == "CLIENTE":
				self.enviar(
					"\nModo CLIENTE seleccionado\n"
					"Escriba HELP para ver los comandos disponibles\n"
				)
				return "CLIENTE"

			if rol == "PROVEEDOR":
				self.enviar(
					"\nModo PROVEEDOR seleccionado\n"
					"Escriba HELP para ver los comandos disponibles\n"
				)
				return "PROVEEDOR"

			if rol == "SALIR":
				return "SALIR"

			self.enviar(
				"ERROR Opcion invalida\n"
				"Debe escribir CLIENTE, PROVEEDOR o SALIR\n"
				"> "
			)

	def atender_cliente(self):
		host, port = self.client_address

		while True:
			mensaje = self.recibir()

			if mensaje == "":
				continue

			partes = mensaje.split()
			comando = partes[0].upper()

			print("{", f"{host}:{port}", "} CLIENTE:", mensaje)

			if comando == "HELP":
				respuesta = (
					"Comandos disponibles para CLIENTE:\n"
					"LISTAR\n"
					"SELECCIONAR <id>\n"
					"SALIR\n"
				)

			elif comando == "LISTAR":
				respuesta = self.listar_proveedores()

			elif comando == "SELECCIONAR":
				respuesta = self.seleccionar_proveedor(partes)

			elif comando == "REGISTRAR":
				respuesta = "ERROR Un CLIENTE no puede registrar proveedores\n"

			elif comando == "SALIR":
				self.enviar("Conexion cerrada\n")
				print(f"Cliente salio {self.client_address}")
				self.request.close()
				break

			else:
				respuesta = "ERROR Comando no permitido para CLIENTE\n"

			self.enviar(respuesta)

	def atender_proveedor(self):
		host, port = self.client_address

		while True:
			mensaje = self.recibir()

			if mensaje == "":
				continue

			partes = mensaje.split()
			comando = partes[0].upper()

			print("{", f"{host}:{port}", "} PROVEEDOR:", mensaje)

			if comando == "HELP":
				respuesta = (
					"Comandos disponibles para PROVEEDOR:\n"
					"REGISTRAR <nombre> <servicio> <costo> <ip> <puerto>\n"
					"SALIR\n"
					"\n"
					"Servicios validos: HM, CC, DIP\n"
					"Ejemplo:\n"
					"REGISTRAR ProveedorHora HM 500 127.0.0.1 7001\n"
				)

			elif comando == "REGISTRAR":
				respuesta = self.registrar_proveedor(partes)

			elif comando == "LISTAR":
				respuesta = "ERROR Un PROVEEDOR no puede listar proveedores\n"

			elif comando == "SELECCIONAR":
				respuesta = "ERROR Un PROVEEDOR no puede seleccionar proveedores\n"

			elif comando == "SALIR":
				self.enviar("Conexion cerrada\n")
				print(f"Proveedor salio {self.client_address}")
				self.request.close()
				break

			else:
				respuesta = "ERROR Comando no permitido para PROVEEDOR\n"

			self.enviar(respuesta)

	def registrar_proveedor(self, partes):
		if len(partes) != 6:
			return "ERROR Formato correcto: REGISTRAR nombre servicio costo ip puerto\n"

		nombre = partes[1]
		servicio = partes[2].upper()
		costo = partes[3]
		ip = partes[4]
		puerto = partes[5]

		if servicio != "HM" and servicio != "CC" and servicio != "DIP":
			return "ERROR Servicio invalido. Use HM, CC o DIP\n"

		try:
			int(puerto)
		except ValueError:
			return "ERROR El puerto debe ser numerico\n"

		proveedor = bd.registrar(nombre, servicio, costo, ip, puerto)
		return f"OK Proveedor registrado con id {proveedor.id_proveedor}\n"

	def listar_proveedores(self):
		proveedores = bd.listar()

		if len(proveedores) == 0:
			return "ERROR No hay proveedores registrados\n"

		respuesta = "PROVEEDORES\n"

		for proveedor in proveedores:
			respuesta += str(proveedor) + "\n"

		return respuesta

	def seleccionar_proveedor(self, partes):
		if len(partes) != 2:
			return "ERROR Formato correcto: SELECCIONAR <id>\n"

		try:
			id_proveedor = int(partes[1])
		except ValueError:
			return "ERROR El id debe ser numerico\n"

		proveedor = bd.seleccionar(id_proveedor)

		if proveedor is None:
			return "ERROR Proveedor no encontrado\n"

		return proveedor.datos_conexion() + "\n"




bd = BaseDatosProveedores()

market = ThreadingTCPServer(("0.0.0.0", 5000), ServiceMarketServ)
print("Service Market iniciado en 0.0.0.0:5000")
market.serve_forever()

