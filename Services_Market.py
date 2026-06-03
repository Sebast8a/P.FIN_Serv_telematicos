from socketserver import ThreadingTCPServer,BaseRequestHandler

class proveedor:
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


