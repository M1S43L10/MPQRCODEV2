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
"""