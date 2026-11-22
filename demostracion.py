"""Demostración reproducible de operaciones válidas y fallidas."""

from decimal import DecimalException

from nucleo_sistema import (
    AlquilerLuces, AlquilerPantallas, AlquilerSalon, AlquilerSonido,
    ErrorSistema, SesionFotografica, Sistema, TransporteColectivo,
)


def ejecutar_demo(sistema=None):
    sistema = sistema if sistema is not None else Sistema()
    operaciones = [
        ("Cliente válido", lambda: sistema.registrar_cliente("C1", "Ana Pérez", "12345", "Calle 1")),
        ("Cliente sin nombre", lambda: sistema.registrar_cliente("C2", "", "23456", "Calle 2")),
        ("Documento inválido", lambda: sistema.registrar_cliente("C2", "Luis", "ABC", "Calle 2")),
        ("Segundo cliente válido", lambda: sistema.registrar_cliente("C2", "Luis", "23456", "Calle 2")),
        ("Documento duplicado", lambda: sistema.registrar_cliente("C3", "Marta", "12345", "Calle 3")),
        ("Editar cliente", lambda: sistema.editar_cliente("C2", "Luis Gómez", "23456", "Calle 3")),
        ("Servicio con tarifa inválida", lambda: sistema.agregar_servicio(AlquilerSonido("S0", -1, 2))),
        ("Paquete inválido", lambda: sistema.agregar_servicio(AlquilerLuces("S0", 100, "oro"))),
        ("Servicio de sonido", lambda: sistema.agregar_servicio(AlquilerSonido("S1", 50000, 2))),
        ("Servicio de pantallas", lambda: sistema.agregar_servicio(AlquilerPantallas("S2", 80000, 2))),
        ("Servicio de luces", lambda: sistema.agregar_servicio(AlquilerLuces("S3", 100000, "estandar"))),
        ("Servicio de transporte", lambda: sistema.agregar_servicio(TransporteColectivo("S4", 1000, 10, 5))),
        ("Servicio de salón", lambda: sistema.agregar_servicio(AlquilerSalon("S5", 2000, 50))),
        ("Servicio de fotografía", lambda: sistema.agregar_servicio(SesionFotografica("S6", 150000, "premium"))),
        ("Reserva con cliente inexistente", lambda: sistema.crear_reserva("R0", "C9", "S1", 2)),
        ("Reserva de sonido", lambda: sistema.crear_reserva("R1", "C1", "S1", 2)),
        ("Reserva de servicio ocupado", lambda: sistema.crear_reserva("R2", "C2", "S1", 2)),
        ("Reserva de pantallas", lambda: sistema.crear_reserva("R2", "C1", "S2", 4)),
        ("Reserva de luces", lambda: sistema.crear_reserva("R3", "C2", "S3", 4)),
        ("Cancelación de reserva", lambda: sistema.cancelar_reserva("R3")),
        ("Descuento inválido", lambda: sistema.facturar("C1", descuento=99999999)),
        ("Factura de dos servicios", lambda: sistema.facturar("C1", descuento=10000).mostrar()),
        ("Facturación duplicada", lambda: sistema.facturar("C1")),
        ("Nueva reserva tras facturar", lambda: sistema.crear_reserva("R4", "C2", "S1", 2)),
    ]
    try:
        for indice, (descripcion, operacion) in enumerate(operaciones, 1):
            try:
                resultado = operacion()
            except (ErrorSistema, DecimalException) as error:
                sistema.registro.guardar_log("ERROR", f"Demostración: {descripcion}: {type(error).__name__}: {error}")
                print(f"{indice:02d}. {descripcion}: ERROR CONTROLADO - {error}")
            else:
                print(f"{indice:02d}. {descripcion}: OK")
                if isinstance(resultado, str):
                    print(resultado)
    finally:
        sistema.registro.guardar_log("INFO", "Demostración finalizada")
        print("Demostración finalizada.")
    return sistema


if __name__ == "__main__":
    ejecutar_demo()
