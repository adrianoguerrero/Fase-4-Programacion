"""Interfaz gráfica y punto de entrada de Software FJ."""

import argparse
from decimal import DecimalException
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import traceback

from nucleo_sistema import (
    AlquilerLuces, AlquilerPantallas, AlquilerSalon, AlquilerSonido,
    DatoInvalidoError, ErrorSistema, RegistroLogs, SesionFotografica,
    Sistema, TransporteColectivo,
)


TIPOS = {
    "Sonido": (AlquilerSonido, "Horas"),
    "Pantallas": (AlquilerPantallas, "Cantidad"),
    "Luces": (AlquilerLuces, "Paquete"),
    "Transporte": (TransporteColectivo, "Pasajeros y kilómetros"),
    "Salón": (AlquilerSalon, "Metros cuadrados"),
    "Fotografía": (SesionFotografica, "Paquete"),
}


def crear_servicio(tipo, codigo, tarifa, parametro, distancia=""):
    if tipo not in TIPOS:
        raise DatoInvalidoError("Seleccione un tipo de servicio.")
    clase = TIPOS[tipo][0]
    if tipo == "Transporte":
        return clase(codigo, tarifa, parametro, distancia)
    return clase(codigo, tarifa, parametro)


class Aplicacion:
    def __init__(self, raiz, sistema):
        self.raiz = raiz
        self.sistema = sistema
        raiz.title("Software FJ")
        raiz.geometry("900x650")
        raiz.report_callback_exception = self.error_inesperado
        pestanas = ttk.Notebook(raiz)
        pestanas.pack(fill="both", expand=True, padx=10, pady=10)
        self.clientes = ttk.Frame(pestanas, padding=10)
        self.servicios = ttk.Frame(pestanas, padding=10)
        self.reservas = ttk.Frame(pestanas, padding=10)
        self.facturacion = ttk.Frame(pestanas, padding=10)
        for marco, nombre in ((self.clientes, "Clientes"), (self.servicios, "Servicios"),
                              (self.reservas, "Reservas"), (self.facturacion, "Facturación")):
            pestanas.add(marco, text=nombre)
        self.crear_clientes()
        self.crear_servicios()
        self.crear_reservas()
        self.crear_facturacion()
        self.actualizar_listas()

    def error_inesperado(self, tipo, error, traza):
        detalle = "".join(traceback.format_exception(tipo, error, traza))
        self.sistema.registro.guardar_log("ERROR", f"Error inesperado en interfaz:\n{detalle}")
        messagebox.showerror("Error inesperado", f"No se pudo completar la operación: {error}")

    def ejecutar(self, operacion):
        try:
            resultado = operacion()
        except (ErrorSistema, DecimalException) as error:
            self.sistema.registro.guardar_log("ERROR", f"{type(error).__name__}: {error}")
            messagebox.showerror("Operación no realizada", str(error))
        else:
            self.actualizar_listas()
            return resultado

    @staticmethod
    def campos(marco, etiquetas):
        entradas = {}
        for fila, etiqueta in enumerate(etiquetas):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=3)
            entrada = ttk.Entry(marco, width=35)
            entrada.grid(row=fila, column=1, sticky="ew", padx=8, pady=3)
            entradas[etiqueta] = entrada
        marco.columnconfigure(1, weight=1)
        return entradas

    @staticmethod
    def lista(marco, fila):
        lista = tk.Listbox(marco, height=12)
        lista.grid(row=fila, column=0, columnspan=4, sticky="nsew", pady=10)
        marco.rowconfigure(fila, weight=1)
        return lista

    def crear_clientes(self):
        self.campos_cliente = self.campos(self.clientes, ("Código", "Nombre", "Documento", "Dirección"))
        botones = ttk.Frame(self.clientes)
        botones.grid(row=4, column=0, columnspan=2, sticky="w")
        for texto, accion in (("Registrar", self.registrar_cliente), ("Editar", self.editar_cliente),
                              ("Eliminar", self.eliminar_cliente)):
            ttk.Button(botones, text=texto, command=lambda a=accion: self.ejecutar(a)).pack(side="left", padx=3)
        self.lista_clientes = self.lista(self.clientes, 5)

    def datos_cliente(self):
        return [self.campos_cliente[campo].get() for campo in ("Código", "Nombre", "Documento", "Dirección")]

    def registrar_cliente(self):
        self.sistema.registrar_cliente(*self.datos_cliente())

    def editar_cliente(self):
        self.sistema.editar_cliente(*self.datos_cliente())

    def eliminar_cliente(self):
        self.sistema.eliminar_cliente(self.campos_cliente["Código"].get())

    def crear_servicios(self):
        ttk.Label(self.servicios, text="Tipo").grid(row=0, column=0, sticky="w")
        self.tipo_servicio = ttk.Combobox(self.servicios, values=list(TIPOS), state="readonly")
        self.tipo_servicio.grid(row=0, column=1, sticky="ew", padx=8)
        self.tipo_servicio.current(0)
        marco = ttk.Frame(self.servicios)
        marco.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.campos_servicio = self.campos(marco, ("Código", "Tarifa", "Parámetro", "Kilómetros (solo transporte)"))
        ttk.Label(self.servicios, text="Parámetro: horas, cantidad, metros, pasajeros o paquete (basico/estandar/premium).").grid(
            row=2, column=0, columnspan=2, sticky="w")
        ttk.Button(self.servicios, text="Crear servicio", command=lambda: self.ejecutar(self.registrar_servicio)).grid(
            row=3, column=0, sticky="w")
        self.servicios.columnconfigure(1, weight=1)
        self.lista_servicios = self.lista(self.servicios, 4)

    def registrar_servicio(self):
        c = self.campos_servicio
        servicio = crear_servicio(self.tipo_servicio.get(), c["Código"].get(), c["Tarifa"].get(),
                                  c["Parámetro"].get(), c["Kilómetros (solo transporte)"].get())
        self.sistema.agregar_servicio(servicio)

    def crear_reservas(self):
        self.campos_reserva = self.campos(self.reservas, ("Código reserva", "Código cliente", "Código servicio", "Duración en horas"))
        ttk.Label(self.reservas, text="La duración de sonido debe coincidir con las horas del servicio.").grid(
            row=4, column=0, columnspan=2, sticky="w")
        botones = ttk.Frame(self.reservas)
        botones.grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Button(botones, text="Reservar y confirmar", command=lambda: self.ejecutar(self.registrar_reserva)).pack(side="left")
        ttk.Button(botones, text="Cancelar reserva", command=lambda: self.ejecutar(self.cancelar_reserva)).pack(side="left", padx=5)
        self.lista_reservas = self.lista(self.reservas, 6)

    def registrar_reserva(self):
        c = self.campos_reserva
        self.sistema.crear_reserva(c["Código reserva"].get(), c["Código cliente"].get(),
                                   c["Código servicio"].get(), c["Duración en horas"].get())

    def cancelar_reserva(self):
        self.sistema.cancelar_reserva(self.campos_reserva["Código reserva"].get())

    def crear_facturacion(self):
        self.campos_factura = self.campos(self.facturacion, ("Código cliente", "IVA (ej. 0.19)", "Descuento"))
        self.campos_factura["IVA (ej. 0.19)"].insert(0, "0.19")
        self.campos_factura["Descuento"].insert(0, "0")
        ttk.Button(self.facturacion, text="Generar factura", command=lambda: self.ejecutar(self.generar_factura)).grid(
            row=3, column=0, sticky="w")
        self.texto_factura = tk.Text(self.facturacion, height=18, width=70, state="disabled")
        self.texto_factura.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
        self.facturacion.rowconfigure(4, weight=1)

    def generar_factura(self):
        c = self.campos_factura
        factura = self.sistema.facturar(c["Código cliente"].get(), c["IVA (ej. 0.19)"].get(),
                                        c["Descuento"].get())
        self.texto_factura.configure(state="normal")
        self.texto_factura.delete("1.0", "end")
        self.texto_factura.insert("1.0", factura.mostrar())
        self.texto_factura.configure(state="disabled")

    def actualizar_listas(self):
        for lista, elementos in ((self.lista_clientes, self.sistema.clientes),
                                 (self.lista_servicios, self.sistema.servicios),
                                 (self.lista_reservas, self.sistema.reservas)):
            lista.delete(0, "end")
            for elemento in elementos:
                lista.insert("end", elemento.mostrar_info())


def main():
    parser = argparse.ArgumentParser(description="Sistema de gestión Software FJ")
    parser.add_argument("--demo", action="store_true", help="Ejecutar demostración por consola")
    argumentos = parser.parse_args()
    if argumentos.demo:
        from demostracion import ejecutar_demo
        ejecutar_demo()
        return
    registro = RegistroLogs()
    try:
        raiz = tk.Tk()
    except tk.TclError as error:
        registro.guardar_log("ERROR", f"No se pudo iniciar la interfaz: {error}")
        print(f"No se pudo iniciar la interfaz gráfica: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    Aplicacion(raiz, Sistema(registro))
    raiz.mainloop()


if __name__ == "__main__":
    main()
