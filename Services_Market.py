from socketserver import ThreadingTCPServer,BaseRequestHandler

class proveedor:
	def __init__(self, id, nombre, codigo, costo, ip, puerto):
		self.id_proveedor = id
		self.nombre = nombre
		self.codigo = codigo
		self.costo = costo
		self.ip = ip
		self.puerto = puerto

	def __str__(self):
		return (
			f"{self.id_proveedor}. "
			f"{self.nombre} | "
			f"{self.codigo} | "
			f"${self.costo} COP | "
			f"{self.ip}:{self.puerto}" )

