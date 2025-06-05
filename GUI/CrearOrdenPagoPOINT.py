from GUI.BarraProgreso import BarraProgreso
from GUI.BuscarOrdenPago import Ventana_BuscarPagoManual
from Func.guardar_json import guardar_json_respuesta
from Func.log_errorsV2 import log_error
import keyboard
from pprint import pprint
from tkinter import messagebox
import tkinter as tk
import json
import threading
import time
import traceback

from GUI.GUI.MessageBox import CustomMessageBox


class CrearOrdenPagoPOINT(BarraProgreso):
    def __init__(self, frame, DICT_WIDGETS, DICT_DATOS_ORDEN, DICT_CONEXION):
        try:
            # Inicializar correctamente la clase base ttk.Progressbar
            super().__init__(frame)
            
            self.error_flags = {
                "focus_in": False,
                "focus_out": False,
                "click_outside": False
            }
            
            #self.mostrar_error = None
            self.NRO_ERROR = None
            self.id_pago = None
            self.datos_dispositivo = None
            self.esperando_pago = True
            self.ID_PAGO = None
            self.pago_manual = True
            self.ventana_buscarpagomanual = None
            self.ventana_buscarpagomanual_abierta = False
            self.datos_pagos = None
            self.combination = []
            

            
            #------------------------------------------- DICCIONARIOS CON DATOS -------------------------------------------
            self.DICT_WIDGETS = DICT_WIDGETS
            self.DICT_CONEXION = DICT_CONEXION
            self.DICT_DATOS_ORDEN = DICT_DATOS_ORDEN
            self.condicion_teclado =  self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "teclado_km84", False)
            pprint(self.DICT_DATOS_ORDEN)
            
            self.datos_obtener_pago = {
                'NOMCAJA': self.DICT_DATOS_ORDEN["NomCaja"],
                'NUMCAJERO': self.DICT_DATOS_ORDEN["NumCajero"],
                'NOMBRECAJERO': self.DICT_DATOS_ORDEN["NombreCajero"]
            }
            self.DICT_PROGRESO = {
                "widgets": DICT_WIDGETS,
                "text_label_aviso": f"Buscando POINT de {self.datos_obtener_pago["NOMCAJA"]}",
                "carga": 15,
                "command": self.buscar_point
            }
            
            #self.cronometro = Cronometro(self.DICT_WIDGETS, 280, self.cancelar_orden_pasado_segundos)
            #threading.Thread(target=self.iniciar_orden).start()
            
            self.progreso(**self.DICT_PROGRESO)
            
            
        except Exception as e:
            log_error(e, "CrearOrdenPago")
            
    def buscar_point(self):
        try:
            # Obtener la lista de dispositivos
            dispositivos_data = self.DICT_CONEXION["conexionAPIPOINT"].obtenerALLPointPOS()
            
            # Verificar si contiene dispositivos
            if "devices" in dispositivos_data:
                dispositivos = dispositivos_data["devices"]
                
                # Buscar si existe un dispositivo con el external_pos_id especificado
                encontrado = False
                for dispositivo in dispositivos:
                    if dispositivo["external_pos_id"] == self.DICT_DATOS_ORDEN["external_id_pos"]:
                        self.datos_dispositivo = dispositivo
                        print(f"Dispositivo encontrado: {dispositivo['external_pos_id']}")
                        encontrado = True
                        break  # Detener la búsqueda al encontrar el dispositivo
                
                # Si no se encuentra ningún dispositivo
                if not encontrado:
                    self.NRO_ERROR = 24
                    self.cierre_ERROR(True)
                else:
                    self.DICT_PROGRESO["text_label_aviso"] = f"Dispositivo {self.datos_dispositivo["id"]} encontrado"
                    self.DICT_PROGRESO["carga"] = 30
                    self.DICT_PROGRESO["command"] = None
                    self.progreso(**self.DICT_PROGRESO)
                    
                    if self.datos_dispositivo["operating_mode"] == "STANDALONE":
                        self.NRO_ERROR = 25
                        self.cierre_ERROR(True)
                    else:
                        self.DICT_PROGRESO["text_label_aviso"] = f"Generando orden para {self.DICT_DATOS_ORDEN["nro_factura"]}"
                        self.DICT_PROGRESO["carga"] = 40
                        self.DICT_PROGRESO["command"] = self.generar_orden_POINT
                        self.progreso(**self.DICT_PROGRESO)
            else:
                self.NRO_ERROR = 24
                self.cierre_ERROR(True)
                #print("No se encontraron dispositivos en los datos proporcionados por la API.")
        
        except Exception as e:
            print(f"Error al buscar el dispositivo: {e}")
            error_traceback = traceback.format_exc()
            print(f"Error al recargar dispositivos: {e}\nTraceback:\n{error_traceback}")
            
            
    def generar_orden_POINT(self):
        try:
            IMPRIME_TICKET = self.pregunta_imprime()
            print(IMPRIME_TICKET)
            self.respuesta_orden = self.DICT_CONEXION["conexionAPIPOINT"].crearIntencionPAGOPoint(self.datos_dispositivo["id"], self.DICT_DATOS_ORDEN["nro_factura"], self.eliminar_decimal(self.DICT_DATOS_ORDEN["monto_pagar"]), IMPRIME_TICKET)
            print(self.respuesta_orden.json())
            
            if self.respuesta_orden.status_code >= 200 and self.respuesta_orden.status_code < 300:
                self.DICT_PROGRESO["text_label_aviso"] = f"Enviando Orden al POINT {self.datos_dispositivo["id"]}"
                self.DICT_PROGRESO["carga"] = 48
                self.DICT_PROGRESO["command"] = None
                self.progreso(**self.DICT_PROGRESO)
                self.DICT_PROGRESO["text_label_aviso"] = f"Orden enviada"
                self.DICT_PROGRESO["carga"] = 49
                self.DICT_PROGRESO["command"] = self.orden_enviada
                self.progreso(**self.DICT_PROGRESO)
            else:
                self.NRO_ERROR = 26
                self.cierre_ERROR(True)
            
        except Exception as e:
            print(e)
            
    def orden_enviada(self):
        try:
            time.sleep(2)
            self.DICT_PROGRESO["text_label_aviso"] = "Esperando Pago."
            self.DICT_PROGRESO["carga"] = 50
            self.DICT_PROGRESO["command"] = None
            self.progreso(**self.DICT_PROGRESO)
            self.nro_punto = 2
            if self.condicion_teclado == "true":
                keyboard.hook(self.on_a_and_6)
                keyboard.hook(self.on_a_and_b)
            else:
                # Asociar la combinación de teclas con la función cancelar_orden
                keyboard.add_hotkey('ctrl+alt+s', self.buscar_pago_manual)
            threading.Thread(target=self.buscar_intencion_pago).start()
            while self.esperando_pago and self.pago_manual:
                print(1)
                if self.nro_punto == 1:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Esperando Respuesta del POINT.")
                elif self.nro_punto == 2:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Esperando Respuesta del POINT..")
                elif self.nro_punto == 3:
                    self.nro_punto = 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Esperando Respuesta del POINT...")
                time.sleep(1.50)
            try:    
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["cerrar_ventana_buscar_pago_manual"]()
            except:
                pass
            if not self.NRO_ERROR == None:
                print(self.NRO_ERROR)
                self.cierre_ERROR(True, "Orden Cancelada")
            else:
                if self.pago_manual:
                    self.DICT_PROGRESO["text_label_aviso"] = "Respuesta recibida"
                    self.DICT_PROGRESO["carga"] = 60
                    self.DICT_PROGRESO["command"] = None
                else:
                    self.DICT_PROGRESO["text_label_aviso"] = "El pago manual ha sido encontrado con éxito"
                    self.DICT_PROGRESO["carga"] = 60
                    self.DICT_PROGRESO["command"] = None
                self.progreso(**self.DICT_PROGRESO)
                self.DICT_PROGRESO["text_label_aviso"] = " Procesando el pago."
                self.DICT_PROGRESO["carga"] = 70
                self.DICT_PROGRESO["command"] = self.proceso_pago_mp
                self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            print(e)
            
    
            
    def buscar_intencion_pago(self):
        intencion_encontrada = True
        while intencion_encontrada and self.pago_manual:
            print(3)
            intencion = self.DICT_CONEXION["conexionDBAServer"].obtener_datos_por_id("MPQRCODE_INTENCIONES_POINT", "id", self.respuesta_orden.json()["id"])
            if intencion == None:
                pass
            else:
                intencion_encontrada = False
            time.sleep(1)
        pprint(intencion)
        if self.pago_manual:
            if intencion["state"] == "CANCELED":
                print(self.NRO_ERROR)
                self.NRO_ERROR = 1
            elif intencion["state"] == "FINISHED" and not intencion["payment"]["id"] == 0:
                print("hola2")
                self.id_pago = intencion["payment"]["id"]
        
        self.esperando_pago = False
                

    def buscar_pago_mp(self):
        try:
            pago_encontrado = True
            while pago_encontrado:
                print(4)
                self.datos_pagos = self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOPOINTServer", "datos_pago", "external_reference", f'{self.DICT_DATOS_ORDEN['nro_factura']}', False)
                if self.datos_pagos == None:
                    pass
                else:
                    pago_encontrado = False
                time.sleep(1)
                
            
            self.datos_pagos = self.convertir_a_json(self.datos_pagos)
            pprint(self.datos_pagos)
            self.esperando_pago = False                

        except KeyError as key_error:
            print(f"Error clave faltante: {key_error}")
        except Exception as e:
            error_detallado = traceback.format_exc()
            print(f"Error inesperado: {error_detallado}")
            self.NRO_ERROR = 1  # Incrementar el número de errores
        finally:
            # Limpiar cualquier recurso o conexión si es necesario
            print("Finalizando el método 'buscar_pago_mp'.")
            
    
            
            
    def buscar_pago_manual(self):
        if self.ventana_buscarpagomanual_abierta  == False:
            self.ventana_buscarpagomanual_abierta  = True
            ventana_buscarpagomanual = Ventana_BuscarPagoManual(self.DICT_WIDGETS, self.DICT_DATOS_ORDEN, self.DICT_CONEXION)
            threading.Thread(target=self.esperar_respuesta_mp, args=(ventana_buscarpagomanual, )).start()
        else:
            print("TATATA")
        
    def esperar_respuesta_mp(self, ventana_buscarpagomanual):
        while ventana_buscarpagomanual.return_respuesta_mp() == None:
            print(ventana_buscarpagomanual.return_respuesta_mp())
            time.sleep(1)
        print(ventana_buscarpagomanual.return_respuesta_mp())
        if not ventana_buscarpagomanual.return_respuesta_mp() == False:
            if ventana_buscarpagomanual.return_respuesta_mp() == "CERRANDO":
                self.ventana_buscarpagomanual_abierta = False
                return
            else:
                self.datos_pagos = ventana_buscarpagomanual.return_respuesta_mp()
                self.datos_pagos = self.datos_pagos.json()
        else:
            self.NRO_ERROR = 101
        self.esperando_pago = False
        self.pago_manual = False

    

    def convertir_a_json(self, cadena_json):
        """
        Convierte un string JSON almacenado en un formato de texto a un diccionario de Python.
        
        Parámetros:
            cadena_json (str): El string que contiene el JSON.
        
        Retorno:
            dict: El contenido del string como un diccionario.
        """
        try:
            # Intentar cargar el string como JSON
            resultado = json.loads(cadena_json)
            return resultado
        except json.JSONDecodeError as e:
            print(f"Error al convertir el string a JSON: {e}")
            return None
        
    def proceso_pago_mp(self):
        self.esperando_pago = True
        self.nro_punto = 2
        if self.pago_manual:
            threading.Thread(target=self.buscar_pago_mp).start()
            while self.esperando_pago:
                print(2)
                if self.nro_punto == 1:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Procesando el pago.")
                elif self.nro_punto == 2:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Procesando el pago..")
                elif self.nro_punto == 3:
                    self.nro_punto = 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Procesando el pago...")
                time.sleep(1.50)
            self.resultado_estado_pago()
        else:
            threading.Thread(target=self.resultado_estado_pago).start()
            while self.esperando_pago:
                print(2)
                if self.nro_punto == 1:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Procesando el pago.")
                elif self.nro_punto == 2:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Procesando el pago..")
                elif self.nro_punto == 3:
                    self.nro_punto = 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Procesando el pago...")
                time.sleep(1.50)
        self.progreso(**self.DICT_PROGRESO)
        
        
    def resultado_estado_pago(self):
        if self.datos_pagos["external_reference"] != self.DICT_DATOS_ORDEN["nro_factura"]:
            self.NRO_ERROR = 13
        elif self.datos_pagos["transaction_amount"] != self.DICT_DATOS_ORDEN["monto_pagar"]:
            self.NRO_ERROR = 10
        elif self.datos_pagos["status"] == "refunded":
            self.NRO_ERROR = 12
        if self.NRO_ERROR == None:
            if self.datos_pagos["status"] == "approved":
                if self.datos_pagos["status_detail"] == "accredited":
                    self.DICT_PROGRESO["text_label_aviso"] = "¡¡¡Pago Exitoso!!!"
                    self.DICT_PROGRESO["carga"] = 99
                    self.DICT_PROGRESO["command"] = self.finalizar_pago                    
            elif self.datos_pagos["status"] == "rejected":
                self.NRO_ERROR = "ERROR_TARJETA"
                self.DICT_PROGRESO["text_label_aviso"] = "Error en el pago"
                self.DICT_PROGRESO["carga"] = 99
                self.DICT_PROGRESO["command"] = self.error_pago
                return
            else:
                print(self.datos_pagos["status"], self.datos_pagos["status"])
        else:
            self.DICT_PROGRESO["text_label_aviso"] = "Error en el pago"
            self.DICT_PROGRESO["carga"] = 99
            self.DICT_PROGRESO["command"] = self.error_pago
        if not self.pago_manual:
            self.esperando_pago = False
            
            
    def error_pago(self):
        self.cierre_ERROR(True, "Error en el pago")

    def ERROR_API(self, label_error):
        try:
            ERRORES_API =  {
                    'cc_rejected_insufficient_amount': {
                        'nro_error': 20.1,
                        'description': 'Saldo Insuficiente',
                    },
                    'cc_rejected_call_for_authorize': {
                        'nro_error': 20.2,
                        'description': 'Pago no autorizado',
                    },
                    'cc_rejected_bad_filled_security_code': {
                        'nro_error': 20.3,
                        'description': 'Código de seguridad inválido',
                    },
                    'cc_rejected_bad_filled_date': {
                        'nro_error': 20.4,
                        'description': 'Fecha de Vencimiento de la Tarjeta Invalida',
                    },
                    'cc_rejected_bad_filled_other': {
                        'nro_error': 20.5,
                        'description': 'Error en algún dato de la Tarjeta',
                    },
                    'cc_rejected_other_reason': {
                        'nro_error': 20.6,
                        'description': 'Pago Rechazado por la Tarjeta',
                    },
                    'cc_rejected_card_disabled': {
                        'nro_error': 20.7,
                        'description': 'Rechazado por tarjeta deshabilitada',
                    },
                    'cc_rejected_bad_filled_card_number': {
                        'nro_error': 20.8,
                        'description': 'Tu pago fue rechazado porque el número de la tarjeta es incorrecto',
                    },
                    'cc_rejected_invalid_installments': {
                        'nro_error': 20.9,
                        'description': 'Tu pago fue rechazado porque la tarjeta no acepta el número de cuotas elegido',
                    },
                    'cc_rejected_duplicated_payment': {
                        'nro_error': 21.0,
                        'description': 'Rechazamos el pago porque se realizó 2 veces',
                    },
                    'cc_rejected_card_type_not_allowed': {
                        'nro_error': 21.1,
                        'description': 'Rechazado por tipo de tarjeta no permitida',
                    },
                    'cc_rejected_max_attempts': {
                        'nro_error': 21.2,
                        'description': 'Rechazado debido a intentos excedidos del pin de la tarjeta	',
                    },
                    'cc_rejected_blacklist': {
                        'nro_error': 21.3,
                        'description': 'Tarjeta bloqueada',
                    },
                    'cc_rejected_high_risk': {
                        'nro_error': 21.4,
                        'description': 'Transacción rechazada: alto riesgo detectado',
                    }
                    
                    
                }
            error_lista = []
            # Obtener la descripción del error específico en ERRORES_API
            if label_error in ERRORES_API:
                errorEsp = ERRORES_API[label_error]
                error_lista = [errorEsp[key] for key in ('nro_error', 'description') if key in errorEsp]
                self.detalle_error = label_error
                return error_lista
            else:
                # En caso de que el error no esté en el diccionario
                return [100, "Error no registrado"]
        except Exception as e:
            # Captura el traceback completo y lo registra
            error_detallado = traceback.format_exc()
            print(label_error, error_detallado)
            log_error(error_detallado, "ERROR_API")  # Registro del error completo

        
    def pregunta_imprime(self):
        try: 
            print_TICKET = self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "MP_POINT_PRINT", False).lower()
            if print_TICKET == "auto":
                return messagebox.askyesno("Imprime ticket", "¿Desea imprimir comprobante de pago?")
            else:
                if print_TICKET == "false":
                    return False
                elif print_TICKET == "true":
                    return True
        except Exception as e:
            print(e)
            return messagebox.askyesno("Imprime ticket", "¿Desea imprimir comprobante de pago?")
        
    def eliminar_decimal(self, numero):
        """
        Elimina el punto decimal de un número y devuelve un entero considerando siempre dos decimales.
        
        Args:
            numero (float): Número con decimal a procesar.
        
        Returns:
            int: Número convertido a entero sin punto decimal, garantizando dos decimales.
        """
        # Asegurar que el número tiene exactamente dos decimales
        numero_str = f"{numero:.2f}"  # Formatear a 2 decimales
        partes = numero_str.split(".")  # Dividir en parte entera y decimal

        # Concatenar las partes y convertirlas a entero
        return int(partes[0] + partes[1])

    
    def aviso_cancelar_orden(self):
        self.DICT_PROGRESO["text_label_aviso"] = "Cancelando Orden"
        self.DICT_PROGRESO["carga"] = 51
        self.DICT_PROGRESO["command"] = self.cancelar_orden
        print("aviso_cancelar_orden")
        self.progreso(**self.DICT_PROGRESO) 
        
    def cancelar_orden(self):
        try:      
            self.NRO_ERROR = 1        
            print(self.DICT_CONEXION["conexionAPIPOINT"].cancelarIntencionPAGOPoint(self.respuesta_orden.json()["device_id"], self.respuesta_orden.json()["id"]).json())
            #self.cerrar_cronometro()
            self.cierre_ERROR(True, "Cancelando Orden")
        except Exception as e:
            log_error(str(e), "cancelar_orden")
            messagebox.showerror("Error", "Ha ocurrido un error al cancelar la orden.")

            
    def cierre_ERROR(self, paso_M, label_error=None ):
        print("cierre_ERROR")
        self.DICT_WIDGETS["ventana_tamano_400_550"]()
        if label_error == None:
            self.DICT_PROGRESO["text_label_aviso"] = "ERROR"
        else:
            self.DICT_PROGRESO["text_label_aviso"] = label_error
        self.DICT_PROGRESO["carga"] = 99
        self.DICT_PROGRESO["command"] = self.mostrar_error
        self.progreso(**self.DICT_PROGRESO)
        time.sleep(1)
        if paso_M:
            self.cerrar_ventana()
        self.DICT_CONEXION["conexionDBA"].desconectar()
        self.DICT_CONEXION["conexionDBAServer"].desconectar()
            
    def mostrar_error(self):
        CustomMessageBox(self.DICT_WIDGETS["root"], f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES(), "error")
        #messagebox.showerror(f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES())
        self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion(
            "MPQRCODE_CONEXIONPROGRAMAS",
            self.datos_error,
            "nro_factura",
            f"'{self.DICT_DATOS_ORDEN['nro_factura']}'"  # Cambiado a comillas simples internas
        )
        
    def finalizar_pago(self):
        try:
            pagos_disponibles = self.DICT_CONEXION["conexionAPIPOINT"].obtenerTodosMediosPagos()
            name_tarjeta_encontrada = None
            for pagos in pagos_disponibles.json():
                if pagos["id"] == self.datos_pagos["payment_method_id"]:
                    name_tarjeta_encontrada = pagos['name']
                    
            datos = {
                'status': 1,
                'response': 0,
                'description': 'accredited',
                'IDMercadoPago': self.id_pago,
                'card_first_six_digits':self.datos_pagos['card']["first_six_digits"],
                'card_last_four_digits':self.datos_pagos['card']["last_four_digits"],
                'payment_method_id':self.datos_pagos['payment_method_id'],
                'payment_method_name':name_tarjeta_encontrada,
                'payment_type_id':self.datos_pagos['payment_type_id'],
            }
            

            
            #messagebox.showinfo("Pago recibido", f"Pago recibido\nNro Factura: {self.DICT_DATOS_ORDEN["nro_factura"]}\nNro Operación: {self.datos_pagos["id"]}\nMonto recibido: {float(self.datos_pagos["transaction_amount"])}")
            self.DICT_WIDGETS["my_label_aviso"].config(text="Pago recibido") 
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOPOINT", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_CONEXION["conexionDBAServer"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOPOINTServer", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_CONEXIONPROGRAMAS", datos, "nro_factura", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            #guardar_json_respuesta(self.datos_pagos)
            self.cerrar_ventana()
                
        except Exception as e:
            log_error(str(e), "finalizar_pago")
            
    """def aviso_intencion_no_cerrada(self):
        CustomMessageBox(self.DICT_WIDGETS["root"], "Venta Abierta", "La Intencion de Pago sigue abierta en el Point, ¡¡¡POR FAVOR CANCELAR PARA CERRAR LA VENTA!!!", "warning")
        #messagebox.showwarning("Venta Abierta", "La Intencion de Pago sigue abierta en el Point, ¡¡¡POR FAVOR CANCELAR PARA CERRAR LA VENTA!!!")
        respuesta = CustomMessageBox(self.DICT_WIDGETS["root"], "¿Consulta Cancelación?", "¿Has cancelado la orden en el POINT?", "yesno") #messagebox.askyesno("¿Consulta Cancelación?", "¿Has cancelado la orden en el POINT?")
        if respuesta and self.estado_de_la_intencion_API():
            pass
        else:
            self.aviso_intencion_no_cerrada()"""
            
    def estado_de_la_intencion_API(self):
        respuesta = self.DICT_CONEXION["conexionAPIPOINT"].buscarIntencionPAGOPoint(self.respuesta_orden["id"]).json()
        print(respuesta)
        
        if respuesta["state"] == "CANCELED" or respuesta["state"] == "FINISHED":
            return True
        else:
            return False
        
        
        
        
    def LISTADO_ERRORES(self):
        try:
            Monto_recibido = None  # Inicializar la variable antes del if

            if self.NRO_ERROR != "ERROR_TARJETA":
                if self.NRO_ERROR != 1:
                    if self.datos_pagos is not None and "transaction_amount" in self.datos_pagos:
                        Monto_recibido = self.datos_pagos["transaction_amount"]
                else:
                    Monto_recibido = 0

                if Monto_recibido is not None:
                    Monto_recibido = float(Monto_recibido)
                else:
                    Monto_recibido = 0

                # Verificaciones antes de usar self.datos_dispositivo y self.datos_obtener_pago
                dispositivo_id = self.datos_dispositivo["id"] if self.datos_dispositivo and "id" in self.datos_dispositivo else "DESCONOCIDO"
                nom_caja = self.datos_obtener_pago["NOMCAJA"] if self.datos_obtener_pago and "NOMCAJA" in self.datos_obtener_pago else "DESCONOCIDO"

                DICT_ERRORES = {
                    1: "Orden Cancelada desde el POINT",
                    10: (
                        "El monto ingresado no es el mismo recibido en MercadoPago\n"
                        f"Monto ingresado: ${self.DICT_DATOS_ORDEN['monto_pagar'] if self.DICT_DATOS_ORDEN and 'monto_pagar' in self.DICT_DATOS_ORDEN else 'SIN MONTO'}\n"
                        f"Monto recibido: ${Monto_recibido}"
                    ),
                    11: f"El ID {self.id_pago} no coincide",
                    12: f"El ID {self.id_pago} ya tiene una devolución hecha",
                    13: "El Número de factura no coincide con el ID Obtenido",
                    21: "El pago no está aprobado",
                    23: "No hemos recibido respuesta de MercadoPago",
                    24: f"No hay dispositivos vinculados con la caja {nom_caja}.",
                    25: f"El dispositivo {dispositivo_id} no está habilitado como PDV",
                    26: f"El dispositivo {dispositivo_id} ya se encuentra con una orden. Cancelar y volver a enviar orden.",
                    100: "Error a la hora de buscar pago manual",
                    101: "Error en la búsqueda en MercadoPago",
                    1001: "Error no registrado"
                }

                self.datos_error = {
                    'status': 0,
                    'response': self.NRO_ERROR,
                    'description': DICT_ERRORES[self.NRO_ERROR]
                }
                print(DICT_ERRORES[self.NRO_ERROR])
                return DICT_ERRORES[self.NRO_ERROR]

            else:
                error_tarjeta_traducido = self.ERROR_API(self.datos_pagos["status_detail"]) if self.datos_pagos and "status_detail" in self.datos_pagos else ("ERROR", "Error desconocido")
                self.datos_error = {
                    'status': 0,
                    'response': error_tarjeta_traducido[0],
                    'description': error_tarjeta_traducido[1]
                }
                return error_tarjeta_traducido[1]

        except Exception as e:
            # Captura el traceback completo y lo registra
            error_detallado = traceback.format_exc()
            print(self.NRO_ERROR, error_detallado)
            log_error(error_detallado, "LISTADO_ERRORES")  # Registro del error completo
            self.datos_error = {
                'status': 0,
                'response': 1000,
                'description': "¡¡¡CRITICO!!!"
            }
            
    def cerrar_ventana(self): #RECUERDA QUE EN BUSCARORDENPAGO TAMBIEN HAY QUE CAMBIAR
        if not self.pago_manual:
            CustomMessageBox(self.DICT_WIDGETS["root"], "IMPORTANTE", "¡¡¡RECORDATORIO!!!\nRECUERDA CANCELAR LA ORDEN EN EL POINT YA QUE HAS USADO EL METODO PARA ID MANUAL", "warning")
            #messagebox.showwarning("IMPORTANTE", "¡¡¡RECORDATORIO!!!\nRECUERDA CANCELAR LA ORDEN EN EL POINT YA QUE HAS USADO EL METODO PARA ID MANUAL")
        self.DICT_WIDGETS["cerrar_ventana"]()
        """if self.pago_manual:
            print("61")
            self.DICT_WIDGETS["cerrar_ventana"]()
        else: 
            print("60")
            self.DICT_WIDGETS["cerrar_ventana"]()  # Solo cerrar si estado es True
            estado = self.estado_de_la_intencion_API()
            print(estado)
            if estado:
                print("59")
                self.DICT_WIDGETS["cerrar_ventana"]()  # Solo cerrar si estado es True
            else:
                print("58")
                self.aviso_intencion_no_cerrada()  # Mostrar aviso y NO cerrar"""


#------------------------------------ Teclado Hasar ------------------------------------


    def entry_info_buscar_pago_on_focus_in(self, event):
        try:
            entry = self.DICT_WIDGETS.get("def_ventana_buscar_pago_manual", {}).get("entry_info_buscar_pago")
            if entry and entry.winfo_exists():
                if entry.get() == self.placeholder_text:
                    entry.delete(0, "end")
                    entry.config(foreground='black')
        except Exception as e:
            if not self.error_flags["focus_in"]:  # Mostrar el error solo si no se ha mostrado antes
                self.error_flags["focus_in"] = True
                log_error(str(e), "entry_info_buscar_pago_on_focus_in")
                messagebox.showerror("Error", "Error al enfocar la entrada de ID de operación.")
        else:
            self.error_flags["focus_in"] = False  # Resetear el flag si no hay error


    def entry_info_buscar_pago_on_focus_out(self, event):
        try:
            entry = self.DICT_WIDGETS.get("def_ventana_buscar_pago_manual", {}).get("entry_info_buscar_pago")
            if entry and entry.winfo_exists():
                if entry.get() == "":
                    entry.insert(0, self.placeholder_text)
                    entry.config(foreground='gray')
        except Exception as e:
            if not self.error_flags["focus_out"]:  # Mostrar el error solo si no se ha mostrado antes
                self.error_flags["focus_out"] = True
                log_error(str(e), "entry_info_buscar_pago_on_focus_out")
                messagebox.showerror("Error", "Error al desenfocar la entrada de ID de operación.")
        else:
            self.error_flags["focus_out"] = False  # Resetear el flag si no hay error


    def handle_click_outside(self, event):
        try:
            ventana = self.DICT_WIDGETS.get("def_ventana_buscar_pago_manual", {}).get("ventana_buscar_pago_manual")
            entry = self.DICT_WIDGETS.get("def_ventana_buscar_pago_manual", {}).get("entry_info_buscar_pago")

            if ventana and ventana.winfo_exists() and entry and entry.winfo_exists():
                widget_under_cursor = ventana.winfo_containing(event.x_root, event.y_root)
                if widget_under_cursor != entry:
                    ventana.focus_set()
        except Exception as e:
            if not self.error_flags["click_outside"]:  # Mostrar el error solo si no se ha mostrado antes
                self.error_flags["click_outside"] = True
                log_error(str(e), "handle_click_outside")
                messagebox.showerror("Error", "Error al procesar el clic fuera del campo de entrada.")
        else:
            self.error_flags["click_outside"] = False  # Resetear el flag si no hay error



            
    def validate_number(self, entry_value):
        try:
            # Validar si la entrada es un número
            if entry_value == "" or entry_value.isdigit() or entry_value == self.placeholder_text:
                return True
            else:
                # Mostrar el mensaje de error
                messagebox.showerror("Error", "Solo puedes ingresar valores numéricos.")
                return False
        except Exception as e:
            log_error(str(e), "validate_number")
            messagebox.showerror("Error", "Error al validar el número.")
            return False

    def detectar_secuencia(self, event):
        try:
            # Agregar la tecla presionada a la secuencia solo si es relevante
            if event.keysym.isdigit() or event.keysym == "Return" or event.keysym == "a":
                self.tecla_secuencia.append(event.keysym)

            # Diccionario con las combinaciones de teclas
            combinaciones = {
                ('4', '6', 'Return'): '0',
                ('4', '7', 'Return'): '00',
                ('4', '8', 'Return'): '.',
                ('5', '6', 'Return'): '1',
                ('5', '7', 'Return'): '2',
                ('5', '8', 'Return'): '3',
                ('6', '6', 'Return'): '4',
                ('6', '7', 'Return'): '5',
                ('6', '8', 'Return'): '6',
                ('7', '6', 'Return'): '7',
                ('7', '7', 'Return'): '8',
                ('7', '8', 'Return'): '9',
            }

            # Patrones de reemplazo
            patrones_reemplazo = {
                ('4', '6', 'Return'): '46',
                ('4', '7', 'Return'): '47',
                ('4', '8', 'Return'): '48',
                ('5', '6', 'Return'): '56',
                ('5', '7', 'Return'): '57',
                ('5', '8', 'Return'): '58',
                ('6', '6', 'Return'): '66',
                ('6', '7', 'Return'): '67',
                ('6', '8', 'Return'): '68',
                ('7', '6', 'Return'): '76',
                ('7', '7', 'Return'): '77',
                ('7', '8', 'Return'): '78'
            }

            # Verificar la longitud de la secuencia y procesar si es necesario
            if len(self.tecla_secuencia) >= 3:
                # Solo consideramos las últimas 3 teclas
                secuencia_tupla = tuple(self.tecla_secuencia[-3:])

                # Acción específica para '6', '4'
                if secuencia_tupla[:2] == ('6', '4'):  # Verificar solo las dos primeras teclas
                    print("Acción específica para 6 + 4")
                    self.tecla_secuencia = []  # Limpiar la secuencia
                    return  # Salir de la función

                # Ejecutar botón si detecta '6', 'a'
                if secuencia_tupla[:2] == ('6', 'a'):  # Verificar solo las dos primeras teclas
                    # Obtener el contenido actual del Entry
                    current_text = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get()

                    # Eliminar los últimos dos caracteres del texto del Entry
                    new_text = current_text[:-2]

                    # Actualizar el Entry con el texto modificado
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, tk.END)
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(tk.END, new_text)

                    # Invocar el botón después de eliminar los caracteres
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["button_info_buscar_pago"].invoke()

                    # Limpiar la secuencia
                    self.tecla_secuencia = []  # Limpiar la secuencia
                    return  # Salir de la función


                # Acciones estándar en el diccionario de combinaciones
                if secuencia_tupla in combinaciones:
                    valor_reemplazo = combinaciones[secuencia_tupla]

                    # Si el valor es un método (callable), lo ejecutamos
                    if callable(valor_reemplazo):
                        valor_reemplazo()  # Llamar al método asociado
                    else:
                        # Obtener el contenido actual del Entry
                        current_text = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get()

                        # Reemplazar patrones en el texto actual del Entry
                        patron = patrones_reemplazo.get(secuencia_tupla, '')
                        if patron:
                            # Si el patrón está en el texto actual, realizar el reemplazo
                            if patron in current_text:
                                start_idx = current_text.rfind(patron)  # Encontrar la última aparición del patrón
                                new_text = current_text[:start_idx] + valor_reemplazo + current_text[start_idx + len(patron):]
                            else:
                                new_text = current_text + valor_reemplazo
                        else:
                            new_text = current_text + valor_reemplazo

                        # Establecer el nuevo texto en el Entry
                        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, tk.END)
                        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(tk.END, new_text)
                    self.tecla_secuencia = []  # Limpiar la secuencia

                elif secuencia_tupla == ('8', '6', 'Return'):
                    # Limpiar el Entry si la secuencia es '8', '6', 'Return'
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, tk.END)
                    self.tecla_secuencia = []  # Limpiar la secuencia

                else:
                    # Si la secuencia no coincide con las combinaciones o patrones, eliminar las últimas teclas del Entry
                    current_text = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get()
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, tk.END)

                    # Eliminar los últimos caracteres (simulando el "retroceso" de las teclas)
                    new_text = current_text[:-len(secuencia_tupla)]  # Eliminar los caracteres correspondientes a la secuencia

                    # Establecer el nuevo texto en el Entry después de eliminar
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(tk.END, new_text)

                    # Limpiar la secuencia
                    self.tecla_secuencia = []

            else:
                # Si la secuencia tiene menos de 3 teclas, no hacer nada
                pass

        except Exception as e:
            log_error(str(e), "detectar_secuencia")
            messagebox.showerror("Error", "Error al procesar la secuencia de teclas.")




    def on_a_and_6(self, event):
        try:
            if keyboard.is_pressed('a') and keyboard.is_pressed('6'):
                self.buscar_pago_manual()
        except Exception as e:
            log_error(str(e), "on_a_and_6")
            messagebox.showerror("Error", "Ha ocurrido un error al detectar las teclas 'a' y '6'.")

            
    """ def on_6_and_a(self, event):
        try:
            if not self.ventana_manual_activa:
                return  # Evitar procesar si la ventana está cerrada

            if keyboard.is_pressed('6') and keyboard.is_pressed('a'):
                self.buscar_id_pago_manual()
        except Exception as e:
            log_error(str(e), "on_6_and_a")
            messagebox.showerror("Error", "Ha ocurrido un error al detectar las teclas '6' y 'a'.")"""


    def on_a_and_b(self, event):
        try:
            if keyboard.is_pressed('a') and keyboard.is_pressed('b'):
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["cerrar_ventana_buscar_pago_manual"]()
        except Exception as e:
            log_error(str(e), "on_4_and_a")
            messagebox.showerror("Error", "Ha ocurrido un error al detectar las teclas '4' y 'a'.")