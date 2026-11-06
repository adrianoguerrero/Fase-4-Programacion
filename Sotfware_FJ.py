import tkinter as tk

class Cliente ():
    def __init__(self):
            self.no_cliente = 0
            self.df_cliente = []
            pass

    def nombre(self, nombre):
          self.nombre = nombre

    def documento(self, documento):
          self.documento = documento

    def direccion (self, direccion):
          self.direccion = direccion

    def guardar_cliente(self, nombre, documento, direccion):
          self.nombre=nombre
          self.documento=documento
          self.direccion=direccion
          self.df_cliente.append({
                "nombre": self.nombre,
                "documento": self.documento,
                "direccion": self.direccion
          })

def ventana_cliente ():
      cliente = Cliente()
      def guardar_cliente( nombre, documento, direccion):
            cliente.guardar_cliente(nombre, documento, direccion)
            clientes.destroy()
      clientes = tk.Tk()
      clientes.title("Clientes")
      clientes.geometry("300x200")
      nombre_label = tk.Label(clientes, text="Nombre")
      nombre_label.pack()
      nombre_entry = tk.Entry(clientes)
      nombre_entry.pack()
      documento_label = tk.Label(clientes, text="Documento")
      documento_label.pack()
      documento_entry = tk.Entry(clientes)
      documento_entry.pack()
      direccion_label = tk.Label(clientes, text="Direccion")
      direccion_label.pack()
      direccion_entry = tk.Entry(clientes)
      direccion_entry.pack()
      guardar_button = tk.Button(
            clientes, text="Guardar", command=lambda: guardar_cliente(
            nombre_entry.get(),
            documento_entry.get(),
            direccion_entry.get()
            ))
      
      guardar_button.pack()
      clientes.mainloop()



ventana_cliente()
