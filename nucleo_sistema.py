"""Modelo en memoria de Software FJ."""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import sys


class ErrorSistema(Exception):
    """Error de operación controlado."""


class DatoInvalidoError(ErrorSistema):
    pass


class ServicioNoDisponibleError(ErrorSistema):
    pass


class ReservaError(ErrorSistema):
    pass


class RegistroLogs:
    def __init__(self, nombre_archivo=None):
        self.nombre_archivo = Path(nombre_archivo) if nombre_archivo else Path(__file__).with_name("eventos_fj.log")

    def guardar_log(self, tipo, mensaje):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.nombre_archivo.open("a", encoding="utf-8") as archivo:
                archivo.write(f"[{fecha}] [{tipo}] {mensaje}\n")
        except OSError as error:
            print(f"No se pudo escribir el registro de eventos: {error}", file=sys.stderr)


def texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise DatoInvalidoError(f"{campo} es obligatorio.")
    return valor.strip()


def numero(valor, campo, minimo=Decimal("0"), permitir_cero=False):
    try:
        if isinstance(valor, bool):
            raise InvalidOperation
        resultado = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise DatoInvalidoError(f"{campo} debe ser un número válido.") from error
    if not resultado.is_finite() or resultado < minimo or (not permitir_cero and resultado == minimo):
        comparacion = "mayor o igual a" if permitir_cero else "mayor que"
        raise DatoInvalidoError(f"{campo} debe ser {comparacion} {minimo}.")
    return resultado


def entero(valor, campo):
    resultado = numero(valor, campo)
    if resultado != resultado.to_integral_value():
        raise DatoInvalidoError(f"{campo} debe ser un número entero.")
    return int(resultado)


def dinero(valor):
    try:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except InvalidOperation as error:
        raise DatoInvalidoError("El importe excede el límite de cálculo.") from error


class Entidad(ABC):
    def __init__(self, codigo):
        self.__codigo = texto(codigo, "El código")

    def get_codigo(self):
        return self.__codigo

    @abstractmethod
    def mostrar_info(self):
        pass


class Cliente(Entidad):
    def __init__(self, codigo, nombre, documento, direccion):
        super().__init__(codigo)
        self.actualizar(nombre, documento, direccion)

    def actualizar(self, nombre, documento, direccion):
        nombre = texto(nombre, "El nombre")
        documento = texto(documento, "El documento")
        direccion = texto(direccion, "La dirección")
        if not documento.isdigit():
            raise DatoInvalidoError("El documento debe contener solo dígitos.")
        self.__nombre = nombre
        self.__documento = documento
        self.__direccion = direccion

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def direccion(self):
        return self.__direccion

    def mostrar_info(self):
        return f"{self.get_codigo()} | {self.nombre} | Documento: {self.documento} | {self.direccion}"


class Servicio(Entidad, ABC):
    def __init__(self, codigo, nombre, tarifa_inicial):
        super().__init__(codigo)
        self.__nombre = texto(nombre, "El nombre del servicio")
        self.__tarifa_inicial = numero(tarifa_inicial, "La tarifa inicial")
        self.__disponible = True

    def get_nombre(self):
        return self.__nombre

    def get_tarifa_inicial(self):
        return self.__tarifa_inicial

    def esta_disponible(self):
        return self.__disponible

    def set_disponible(self, estado):
        if not isinstance(estado, bool):
            raise DatoInvalidoError("La disponibilidad debe ser verdadera o falsa.")
        self.__disponible = estado

    @abstractmethod
    def validar_parametros(self):
        pass

    @abstractmethod
    def calcular_costo(self):
        pass

    @abstractmethod
    def describir(self):
        pass

    def calcular_total_con_impuesto(self, iva=Decimal("0.19"), descuento=0):
        iva = numero(iva, "El IVA", permitir_cero=True)
        descuento = numero(descuento, "El descuento", permitir_cero=True)
        if iva > 1:
            raise DatoInvalidoError("El IVA debe estar entre 0 y 1.")
        costo = self.calcular_costo()
        if descuento > costo:
            raise DatoInvalidoError("El descuento no puede superar el costo.")
        return dinero((costo - descuento) * (1 + iva))

    def mostrar_info(self):
        estado = "Disponible" if self.esta_disponible() else "Reservado"
        return f"{self.get_codigo()} | {self.describir()} | ${self.calcular_costo():,.2f} | {estado}"


class AlquilerSonido(Servicio):
    def __init__(self, codigo, tarifa_inicial, horas):
        super().__init__(codigo, "Sonido", tarifa_inicial)
        self.__horas = numero(horas, "Las horas")
        self.validar_parametros()

    def validar_parametros(self):
        numero(self.__horas, "Las horas")

    @property
    def horas(self):
        return self.__horas

    def calcular_costo(self):
        return dinero(self.get_tarifa_inicial() * self.__horas)

    def describir(self):
        return f"Sonido ({self.__horas} horas)"


class AlquilerPantallas(Servicio):
    def __init__(self, codigo, tarifa_inicial, cantidad):
        super().__init__(codigo, "Pantallas", tarifa_inicial)
        self.__cantidad = entero(cantidad, "La cantidad de pantallas")
        self.validar_parametros()

    def validar_parametros(self):
        entero(self.__cantidad, "La cantidad de pantallas")

    def calcular_costo(self):
        return dinero(self.get_tarifa_inicial() * self.__cantidad)

    def describir(self):
        return f"Pantallas ({self.__cantidad} unidades)"


class ServicioPaquete(Servicio, ABC):
    FACTORES = {"basico": Decimal("1"), "estandar": Decimal("1.5"), "premium": Decimal("2")}

    def __init__(self, codigo, nombre, tarifa_inicial, paquete):
        super().__init__(codigo, nombre, tarifa_inicial)
        self.__paquete = texto(paquete, "El paquete").lower()
        self.validar_parametros()

    def validar_parametros(self):
        if self.__paquete not in self.FACTORES:
            raise DatoInvalidoError("El paquete debe ser basico, estandar o premium.")

    def calcular_costo(self):
        return dinero(self.get_tarifa_inicial() * self.FACTORES[self.__paquete])

    def describir(self):
        return f"{self.get_nombre()} (paquete {self.__paquete})"


class AlquilerLuces(ServicioPaquete):
    def __init__(self, codigo, tarifa_inicial, paquete):
        super().__init__(codigo, "Luces", tarifa_inicial, paquete)


class TransporteColectivo(Servicio):
    def __init__(self, codigo, tarifa_inicial, pasajeros, distancia):
        super().__init__(codigo, "Transporte", tarifa_inicial)
        self.__pasajeros = entero(pasajeros, "La cantidad de pasajeros")
        self.__distancia = numero(distancia, "La distancia")
        self.validar_parametros()

    def validar_parametros(self):
        entero(self.__pasajeros, "La cantidad de pasajeros")
        numero(self.__distancia, "La distancia")

    def calcular_costo(self):
        return dinero(self.get_tarifa_inicial() * self.__pasajeros * self.__distancia)

    def describir(self):
        return f"Transporte ({self.__pasajeros} pasajeros, {self.__distancia} km)"


class AlquilerSalon(Servicio):
    def __init__(self, codigo, tarifa_inicial, metros):
        super().__init__(codigo, "Salón", tarifa_inicial)
        self.__metros = numero(metros, "Los metros cuadrados")
        self.validar_parametros()

    def validar_parametros(self):
        numero(self.__metros, "Los metros cuadrados")

    def calcular_costo(self):
        return dinero(self.get_tarifa_inicial() * self.__metros)

    def describir(self):
        return f"Salón ({self.__metros} m²)"


class SesionFotografica(ServicioPaquete):
    def __init__(self, codigo, tarifa_inicial, paquete):
        super().__init__(codigo, "Fotografía", tarifa_inicial, paquete)


class Reserva(Entidad):
    def __init__(self, codigo, cliente, servicio, duracion):
        super().__init__(codigo)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un cliente y un servicio válidos.")
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = numero(duracion, "La duración en horas")
        if isinstance(servicio, AlquilerSonido) and self.__duracion != servicio.horas:
            raise ReservaError("La duración de la reserva debe coincidir con las horas del sonido.")
        self.__estado = "pendiente"

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    def confirmar(self):
        if self.estado != "pendiente":
            raise ReservaError("Solo se pueden confirmar reservas pendientes.")
        if not self.servicio.esta_disponible():
            raise ServicioNoDisponibleError("El servicio ya está reservado.")
        self.servicio.validar_parametros()
        self.servicio.calcular_costo()
        self.servicio.set_disponible(False)
        self.__estado = "confirmada"

    def cancelar(self):
        if self.estado not in ("pendiente", "confirmada"):
            raise ReservaError("Solo se pueden cancelar reservas pendientes o confirmadas.")
        if self.estado == "confirmada":
            self.servicio.set_disponible(True)
        self.__estado = "cancelada"

    def procesar(self):
        if self.estado != "confirmada":
            raise ReservaError("Solo se pueden procesar reservas confirmadas.")
        self.__estado = "procesada"
        self.servicio.set_disponible(True)

    def mostrar_info(self):
        return (f"{self.get_codigo()} | {self.cliente.nombre} | {self.servicio.describir()} | "
                f"{self.duracion} h | {self.estado}")


class Sistema:
    def __init__(self, registro=None):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        self.__facturas = []
        self.registro = registro if registro is not None else RegistroLogs()

    @property
    def clientes(self):
        return tuple(self.__clientes)

    @property
    def servicios(self):
        return tuple(self.__servicios)

    @property
    def reservas(self):
        return tuple(self.__reservas)

    @property
    def facturas(self):
        return tuple(self.__facturas)

    def _buscar(self, elementos, codigo, tipo):
        codigo = texto(codigo, f"El código de {tipo}")
        for elemento in elementos:
            if elemento.get_codigo() == codigo:
                return elemento
        raise DatoInvalidoError(f"No existe {tipo} con código {codigo}.")

    def buscar_cliente(self, codigo):
        return self._buscar(self.__clientes, codigo, "cliente")

    def buscar_servicio(self, codigo):
        return self._buscar(self.__servicios, codigo, "servicio")

    def buscar_reserva(self, codigo):
        return self._buscar(self.__reservas, codigo, "reserva")

    def _codigo_nuevo(self, elementos, codigo):
        codigo = texto(codigo, "El código")
        if any(elemento.get_codigo() == codigo for elemento in elementos):
            raise DatoInvalidoError(f"El código {codigo} ya existe.")

    def _documento_unico(self, documento, excepto=None):
        if any(c.documento == documento for c in self.__clientes if c is not excepto):
            raise DatoInvalidoError("El documento ya está registrado.")

    def registrar_cliente(self, codigo, nombre, documento, direccion):
        self._codigo_nuevo(self.__clientes, codigo)
        cliente = Cliente(codigo, nombre, documento, direccion)
        self._documento_unico(cliente.documento)
        self.__clientes.append(cliente)
        self.registro.guardar_log("INFO", f"Cliente registrado: {cliente.get_codigo()}")
        return cliente

    def editar_cliente(self, codigo, nombre, documento, direccion):
        cliente = self.buscar_cliente(codigo)
        documento = texto(documento, "El documento")
        self._documento_unico(documento, cliente)
        cliente.actualizar(nombre, documento, direccion)
        self.registro.guardar_log("INFO", f"Cliente editado: {codigo}")

    def eliminar_cliente(self, codigo):
        cliente = self.buscar_cliente(codigo)
        if any(r.cliente is cliente for r in self.__reservas):
            raise ReservaError("No se puede eliminar un cliente con historial de reservas.")
        self.__clientes.remove(cliente)
        self.registro.guardar_log("INFO", f"Cliente eliminado: {codigo}")

    def agregar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El servicio no es válido.")
        self._codigo_nuevo(self.__servicios, servicio.get_codigo())
        servicio.validar_parametros()
        servicio.calcular_costo()
        self.__servicios.append(servicio)
        self.registro.guardar_log("INFO", f"Servicio creado: {servicio.get_codigo()}")

    def crear_reserva(self, codigo, codigo_cliente, codigo_servicio, duracion):
        self._codigo_nuevo(self.__reservas, codigo)
        cliente = self.buscar_cliente(codigo_cliente)
        servicio = self.buscar_servicio(codigo_servicio)
        reserva = Reserva(codigo, cliente, servicio, duracion)
        reserva.confirmar()
        self.__reservas.append(reserva)
        self.registro.guardar_log("INFO", f"Reserva confirmada: {reserva.get_codigo()}")
        return reserva

    def cancelar_reserva(self, codigo):
        reserva = self.buscar_reserva(codigo)
        reserva.cancelar()
        self.registro.guardar_log("INFO", f"Reserva cancelada: {codigo}")

    def facturar(self, codigo_cliente, iva=Decimal("0.19"), descuento=0):
        cliente = self.buscar_cliente(codigo_cliente)
        reservas = [r for r in self.__reservas if r.cliente is cliente and r.estado == "confirmada"]
        if not reservas:
            raise ReservaError("El cliente no tiene reservas confirmadas para facturar.")
        iva = numero(iva, "El IVA", permitir_cero=True)
        descuento = numero(descuento, "El descuento", permitir_cero=True)
        if iva > 1:
            raise DatoInvalidoError("El IVA debe estar entre 0 y 1.")
        lineas = [(r.get_codigo(), r.servicio.describir(), r.servicio.calcular_costo()) for r in reservas]
        subtotal = dinero(sum((linea[2] for linea in lineas), Decimal("0")))
        if descuento > subtotal:
            raise DatoInvalidoError("El descuento no puede superar el subtotal.")
        impuesto = dinero((subtotal - descuento) * iva)
        total = dinero(subtotal - descuento + impuesto)
        factura = Factura(cliente.nombre, cliente.documento, tuple(lineas), subtotal, descuento, impuesto, total)
        for reserva in reservas:
            reserva.procesar()
        self.__facturas.append(factura)
        self.registro.guardar_log("INFO", f"Factura generada para cliente {cliente.get_codigo()}: ${total}")
        return factura


class Factura:
    def __init__(self, nombre, documento, lineas, subtotal, descuento, impuesto, total):
        self.nombre = nombre
        self.documento = documento
        self.lineas = lineas
        self.subtotal = subtotal
        self.descuento = descuento
        self.impuesto = impuesto
        self.total = total

    def mostrar(self):
        detalle = "\n".join(f"  {codigo}: {descripcion} - ${costo:,.2f}" for codigo, descripcion, costo in self.lineas)
        return (f"Factura Software FJ\nCliente: {self.nombre} | Documento: {self.documento}\n"
                f"{detalle}\nSubtotal: ${self.subtotal:,.2f}\nDescuento: ${self.descuento:,.2f}\n"
                f"IVA: ${self.impuesto:,.2f}\nTOTAL: ${self.total:,.2f}")
