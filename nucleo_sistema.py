from abc import ABC, abstractmethod
from datetime import datetime

# Excepciones personalizadas del sistema
class ErrorSistema(Exception):
    # Excepción general para errores de Software FJ
    pass

class DatoInvalidoError(ErrorSistema):
    # Se lanza cuando un dato está vacío o no cumple el formato
    pass

class ServicioNoDisponibleError(ErrorSistema):
    # Se lanza cuando un servicio está ocupado o tiene parámetros incorrectos
    pass

class ReservaError(ErrorSistema):
    # Se lanza cuando falla la creación o el proceso de una reserva
    pass

# Clase para guardar eventos y errores en un archivo de texto
class RegistroLogs:
    def __init__(self, nombre_archivo="eventos_fj.log"):
        self.nombre_archivo = nombre_archivo

    def guardar_log(self, tipo, mensaje):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        texto = f"[{fecha}] [{tipo}] {mensaje}\n"

        archivo = None
        try:
            # Abre el archivo en modo agregar para no borrar registros anteriores
            archivo = open(self.nombre_archivo, "a", encoding="utf-8")
            archivo.write(texto)
        except Exception as error:
            print("Error al escribir en el archivo de logs:", error)
        finally:
            # Asegura que el archivo siempre se cierre
            if archivo is not None:
                archivo.close()

# Clase abstracta base para las entidades del sistema
class Entidad(ABC):
    def __init__(self, codigo):
        if codigo == "":
            raise DatoInvalidoError("El código no puede estar vacío.")
        self.__codigo = codigo

    def get_codigo(self):
        return self.__codigo

    @abstractmethod
    def mostrar_info(self):
        pass


# Clase abstracta para los servicios de Software FJ
class Servicio(Entidad, ABC):
    def __init__(self, codigo, nombre, tarifa_inicial):
        super().__init__(codigo)
        if tarifa_inicial <= 0:
            raise DatoInvalidoError("La tarifa inicial debe ser mayor a 0.")
        self.__nombre = nombre
        self.__tarifa_inicial = tarifa_inicial
        self.__disponible = True

    def get_nombre(self):
        return self.__nombre

    def get_tarifa_inicial(self):
        return self.__tarifa_inicial

    def esta_disponible(self):
        return self.__disponible

    def set_disponible(self, estado):
        self.__disponible = estado

    @abstractmethod
    def calcular_costo(self):
        # Método que cada servicio especializado debe implementar
        pass

    # Calcula el total aplicando IVA y descuento opcional
    def calcular_total_con_impuesto(self, iva=0.19, descuento=0):
        costo = self.calcular_costo()
        if descuento < 0 or descuento > costo:
            raise DatoInvalidoError("El descuento no es válido.")
        subtotal = costo - descuento
        total = subtotal + (subtotal * iva)
        return total

    def mostrar_info(self):
        return f"Servicio: {self.__nombre} | Tarifa base: ${self.__tarifa_inicial}"
