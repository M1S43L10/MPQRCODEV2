from Conf.GUIENLACECREARORDENV2 import EnlaceCrearOrden

__version__ = "5.0.0"


if __name__ == "__main__":
    config = EnlaceCrearOrden(__version__)
    
    
"""
2.0.0 Nueva version, mejor funcionamiento, se agregaroon la funcionalidad de threading, se usa tkbootstrap. Solo
se puede crear un orden de pago.

3.0.0 Se agrega la funcion de reembolso ademas del pago.

4.0.0 Se agrega la funcion para generar ordenes al POINT y Obtener ordenes, comparar los resultados y asegurar lo recibido...

4.5.0 Se agrega la funcion para buscar una Orden Manual x ID.

4.6.0 La funcion para busqueda Manual y Reembolso han cambiado ahora preguntan el tipo de pago que desean buscar o delvolver.
    NUEVA VARIABLE = MP_POINT >
    MP_POINT_PRINT >
    pref_tkt_MP > POR DEFECTO ES TKT. SIRVE PARA INDICAR EL PREFIJO EN EL NªTICKET. MIN 1 CARACTER MAX 5 CARACTERES. OBS AGREGAR 6 CARACTERES 
4.6.32 Se agrego el aviso a la BASE para los errores tendria que notificar y cancelar.
4.6.33 Errores al dar NoteType en el Point >  Monto_recibido = self.datos_pagos["transaction_amount"]
4.6.38 Errores que no tomaba el MP_POINT_PRINT, se cambio que las variables vallan a la base de las cajas
4.7.9 En el reembolso ya no pregunta mas de donde es el reembolso automaticamente va y lo busca en la base
4.7.16 En la busqueda manual de un pago mandando la opcion 9, ya no pregunta más solo pide ID.
4.8.25 Se agrego el modulo personalizado de Messagebox, para poder definir los font y el geomtry
4.9.12 Se agrego el modulo de tecladohasar, para poder dar uso a los teclado viejos y nuevos, y tiene mas versatilidad el modulo
4.10.0 Se implementó reintento automático de hasta 3 veces en el envío de órdenes de pago, órdenes al POINT y reembolsos para mejorar la estabilidad del sistema ante errores de conexión o API.  
        Se agregaron logs detallados en los principales puntos de interacción del usuario y errores críticos para mejorar el seguimiento y depuración.  
        Se mejoró la gestión de cierres forzados, permitiendo matar el proceso incluso si hay hilos en ejecución.  
        Se añadieron mejoras menores en validaciones internas y mensajes al usuario.
4.10.1 Solucion a bugs que no avisaba al facturador...
4.11.4 Solucion cuando se corta ARCA y se guarda con la factura del CAE y tiene que cambiar a CAE-A
4.12.0 Validación de medios de pago PBS:
    Se agregó una función de verificación (comprobación_PBS) que valida si el método y tipo de pago son compatibles con los disponibles para PBS.
    En caso de no ser válidos, el sistema devuelve el error 15 e interrumpe la operación con un mensaje explicativo.

    Nuevo código de error 15:
    Se agregó al listado de errores un mensaje que informa al usuario si el medio de pago no está habilitado para descuentos de PBS.
    Se incluyen los métodos de pago válidos detectados dinámicamente.

    Refactor en flujo de comparación de pagos:
    La validación PBS fue integrada al inicio del proceso de comparación para asegurar coherencia antes de validar monto, fecha y referencia externa.

    Manejo de errores mejorado:
    Se agregó control de excepción para errores internos al validar PBS y se asigna el código 1001 en caso de error no registrado.
4.12.1 Se corrigio error de funcion mal llamada, "ejecutar_sentencia" en modulo QR
4.12.2 Se corrigio error de funcion mal llamada, "ejecutar_sentencia" en Modulo POINT y BuscarPago
5.0.0 Se agrega la conjunción del modulo de Clover para trabajar con ellos.
"""