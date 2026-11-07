# Fase-4-Programacion

Inicialmente se creo el archivo Sotfware_FJ.py el cual esta disponible para editar entre todos.
Propongo realizar una estructura inicial.

nos enfocamos en una empresa donde los servicios sean los siguientes
Alquiler de sonido
Alquiler de pantallas
Alquiler de luces
transporte colectivo para pasajeros
Alquieler de salones
Sesión fotográfica

El desarrollo puede cumplir con las siguientes etapas:

Sección clientes
  nuevo cliente
  editar cliente
  eliminar cliente
en estas secciones del cliente se pueden aplicar las excepciones. 

Sección sevicios
  todos los servicios tiene una tarifa inicial la cual puede ser diferente para cada servicio
  unos servicios se cobran por hora otros por cantidad, otros según paquete elegido
  
  Alquiler de sonido - por hora
  Alquiler de pantallas - cantidad de pantallas
  Alquiler de luces - según paquete
  transporte colectivo para pasajeros - cantidad de pasajeros y distancia recorrida
  Alquieler de salones - metros caudrados
  Sesión fotográfica - según el paquete
En la seccion de servicios se pueden apicar abstracción, herencia, polimorfismo y encapsulación

Sección reservas
  una vez elegido un servicio debe transferir la información a esta seccion
  aquí se guardara la información por cliente 
  se da la opción de regresar a otro servicio o pasar a facturacion

Sección facturacion
  se recibe la información recolectada en reservas
  se totaliza los servicios y se genera la factura

Sección registro de log
  se recibe la información del evento y se guarda en el archivo de log's


