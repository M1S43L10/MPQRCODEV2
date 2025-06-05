from pprint import pprint
from tkinter import messagebox
from GUI.BarraProgreso import BarraProgreso
from GUI.MessageBox import CustomMessageBox
from Func.log_errorsV2 import log_error
from Func.tecladohasar import TecladoHasar
import keyboard
import ttkbootstrap as ttk
import json
import threading
import time
import traceback


class BuscarOrdenPago(BarraProgreso):
    def __init__(self, frame, DICT_WIDGETS, DICT_DATOS_ORDEN, DICT_CONEXION, SELECCION_TIPO_BUSQUEDA=None):
        try:
            # Inicializar correctamente la clase base tttk.Progressbar
            super().__init__(frame)
            
            
            self.error_flags = {
                "focus_in": False,
                "focus_out": False,
                "click_outside": False
            }
            
            #self.mostrar_error = None
            self.NRO_ERROR = None
            self.respuesta_mp = None
            self.datos_dispositivo = None
            self.esperando_pago = True
            self.id_pago = None
            self.pago_manual = True
            self.ventana_buscarpagomanual_abierta = False
            self.datos_pagos = None
            self.combination = []
            self.SELECCION_TIPO_BUSQUEDA = SELECCION_TIPO_BUSQUEDA
            
            self.DICT_WIDGETS = DICT_WIDGETS
            self.DICT_CONEXION = DICT_CONEXION
            self.DICT_DATOS_ORDEN = DICT_DATOS_ORDEN
            self.condicion_teclado =  self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "teclado_km84", False)
            
            self.obtener_diccionario_pbs() #AGREGADO 23/04/2025
            
            self.datos_obtener_pago = {
                'NomCaja': self.DICT_DATOS_ORDEN["NomCaja"],
                'NumCajero': self.DICT_DATOS_ORDEN["NumCajero"],
                'NombreCajero': self.DICT_DATOS_ORDEN["NombreCajero"]
            }
            self.DICT_PROGRESO = {
                "widgets": DICT_WIDGETS,
                "text_label_aviso": "Ingrese el ID de Operación",
                "carga": 30,
                "command": self.buscar_pago_manual
            }
            self.progreso(**self.DICT_PROGRESO)
            self.esperando_respuesta_pago()
        except Exception as e:
            print(e)
            
    """ def preguntar_tipo_eleccion_buscar(self):
        self.cuadro_dialogo_eleccion_buscar()
        while self.SELECCION_TIPO_BUSQUEDA == None:
            print("hola")
            pass
            time.sleep(1)
        self.DICT_PROGRESO["text_label_aviso"] = "Ingrese el ID de Operación"
        self.DICT_PROGRESO["carga"] = 50
        self.DICT_PROGRESO["command"] =  threading.Thread(target=self.buscar_pago_manual).start
        self.progreso(**self.DICT_PROGRESO)"""
        
            
            
    """def cuadro_dialogo_eleccion_buscar(self):
        try:
            style = ttk.Style()
            # Configurar la fuente para los botones
            style.configure("TButton", font=("Helvetica", 11))
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"] = ttk.Toplevel(self.DICT_WIDGETS["root"], )
            ancho_ventana = 450
            alto_ventana = 200
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"].geometry(f"{ancho_ventana}x{alto_ventana}")  # Tamaño de la ventana
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"].overrideredirect(True)  # Eliminar la barra superior
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"].grab_set()  # Bloquear interacción con otras ventanas
            
            
            
            x_ventana = self.DICT_WIDGETS["root"].winfo_x() + (self.DICT_WIDGETS["root"].winfo_width() // 2) - (ancho_ventana // 2)
            y_ventana = self.DICT_WIDGETS["root"].winfo_y() + (self.DICT_WIDGETS["root"].winfo_height() // 2) - (alto_ventana // 2)
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"].geometry(f"{ancho_ventana}x{alto_ventana}+{x_ventana}+{y_ventana}")

            # Configurar el contenido de la ventana
            mensaje = ttk.Label(self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"], text="¿De que tipo de operacion deseas realizar al buscado del ID?", anchor="center", font=("Helvetica", 16),  wraplength=400)
            mensaje.pack(expand=True, pady=10)
            
            frame_botones = ttk.Frame(self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"])
            frame_botones.pack(pady=5, expand=True, fill="x")
            
            if  self.condicion_teclado == "true":
                keyboard.add_hotkey('8 + 6 + enter', self.on_8_and_6)
                keyboard.add_hotkey('a + 6 + enter', self.on_a_and_6)
                text_mpqr = "MP QR (CLEAR)"
                text_mppoint = "MP Point (SUB TOTAL)"
            else:
                text_mpqr = "MercadoPago QR"
                text_mppoint = "MercadoPago Point"
            # Botón para cerrar la ventana
            boton_mpqr = ttk.Button(frame_botones, text=text_mpqr, command=self.cuadro_dialogo_eleccion_buscar_seleccion_mpqr, style="TButton")
            boton_mpqr.pack(side="left", padx=20)
            
            boton_mppoint = ttk.Button(frame_botones, text=text_mppoint, command=self.cuadro_dialogo_eleccion_buscar_seleccion_mppoint, style="TButton")
            boton_mppoint.pack(side="right", padx=20)
        except Exception as e:
            print(e)
        
    def cuadro_dialogo_eleccion_buscar_seleccion_mpqr(self):
        self.SELECCION_TIPO_BUSQUEDA = True
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"].destroy()
        
    def cuadro_dialogo_eleccion_buscar_seleccion_mppoint(self):
        self.SELECCION_TIPO_BUSQUEDA = False
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"].destroy()"""

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
        
    def buscar_pago_manual(self):
        if self.ventana_buscarpagomanual_abierta  == False:
            self.ventana_buscarpagomanual_abierta  = True
            ventana_buscarpagomanual = Ventana_BuscarPagoManual(self.DICT_WIDGETS, self.DICT_DATOS_ORDEN, self.DICT_CONEXION, True)
            self.esperar_respuesta_mp(ventana_buscarpagomanual)
        else:
            print("TATATA")
        
    def esperar_respuesta_mp(self, ventana_buscarpagomanual):
        while ventana_buscarpagomanual.return_respuesta_mp() == None:
            print(ventana_buscarpagomanual.return_respuesta_mp())
            time.sleep(1)
        print(ventana_buscarpagomanual.return_respuesta_mp())
        if not ventana_buscarpagomanual.return_respuesta_mp() == False :
            if ventana_buscarpagomanual.return_respuesta_mp() == "CERRANDO":
                self.ventana_buscarpagomanual_abierta = False
                self.NRO_ERROR = 1
                self.datos_pagos = True
            else: 
                self.datos_pagos = ventana_buscarpagomanual.return_respuesta_mp()
                self.datos_pagos = self.datos_pagos.json()
        else:
            self.NRO_ERROR = 101
        self.esperando_pago = False
        self.pago_manual = False
        
    def esperando_respuesta_pago(self):
        while self.datos_pagos == None:
            print("ESPERANDO PAGO")
            time.sleep(1)
        time.sleep(1)
        if not self.NRO_ERROR == 1:
            self.DICT_PROGRESO["text_label_aviso"] = "El pago manual ha sido encontrado con éxito"
            self.DICT_PROGRESO["carga"] = 60
            self.DICT_PROGRESO["command"] = None
            self.progreso(**self.DICT_PROGRESO)
            self.DICT_PROGRESO["text_label_aviso"] = " Procesando el pago."
            self.DICT_PROGRESO["carga"] = 70
            self.DICT_PROGRESO["command"] = self.proceso_pago_mp
            self.progreso(**self.DICT_PROGRESO)
        else:
            self.cierre_ERROR(True)
        
        
        
    def proceso_pago_mp(self):
        self.esperando_pago = True
        self.nro_punto = 2
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
        self.id_pago = self.datos_pagos["id"]
        if self.datos_pagos["external_reference"] != self.DICT_DATOS_ORDEN["nro_factura"]:
            self.NRO_ERROR = 13
        elif self.datos_pagos["transaction_amount"] != self.DICT_DATOS_ORDEN["monto_pagar"]:
            self.NRO_ERROR = 10
        elif self.datos_pagos["status"] == "refunded":
            self.NRO_ERROR = 12
        elif int(self.DICT_DATOS_ORDEN["response"]) == 98: #AGREGADO 23/04/2025
            print("INICIO COMPROBANDO PBD")
            if not self.comprobación_PBS():
                if not self.NRO_ERROR == 1001:
                    self.NRO_ERROR = 15
                    CustomMessageBox(
                        self.DICT_WIDGETS["root"],
                        f"Error {self.NRO_ERROR}",
                        self.LISTADO_ERRORES(),
                        "error"
                    )
                    self.DICT_PROGRESO["text_label_aviso"] = "Realizando reembolso"
                    self.progreso(**self.DICT_PROGRESO)
                    respuesta_reembolso = self.DICT_CONEXION['conexionAPI'].crear_orden_reembolso(self.id_pago, self.datos_pagos["transaction_amount"]).status_code == 200
                    if respuesta_reembolso:
                        self.DICT_PROGRESO["text_label_aviso"] = "Reembolso realizado"
                        self.progreso(**self.DICT_PROGRESO)
                    else:
                        self.NRO_ERROR = 16
                        CustomMessageBox(
                            self.DICT_WIDGETS["root"],
                            f"Error {self.NRO_ERROR}",
                            self.LISTADO_ERRORES(),
                            "error"
                        )
                        log_error(respuesta_reembolso.json(), "realizar_comparacion_comprobación_PBS")
            print("FIN COMPROBANDO PBD")
            
            
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
            self.DICT_WIDGETS["cerrar_ventana"]()
        self.DICT_CONEXION["conexionDBA"].desconectar()
        self.DICT_CONEXION["conexionDBAServer"].desconectar()
            
    def mostrar_error(self):
        try:
            CustomMessageBox(self.DICT_WIDGETS["root"], self.LISTADO_ERRORES(), f"Error {self.NRO_ERROR}", "error")
            #Messagebox.show_error(self.LISTADO_ERRORES(), f"Error {self.NRO_ERROR}", parent=self.DICT_WIDGETS["root"])
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion(
                "MPQRCODE_CONEXIONPROGRAMAS",
                self.datos_error,
                "nro_factura",
                f"'{self.DICT_DATOS_ORDEN['nro_factura']}'"  # Cambiado a comillas simples internas
            )
        except Exception as e:
            error_detallado = traceback.format_exc()
            print(error_detallado)
        
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
            
    def obtener_diccionario_pbs(self): #AGREGADO 23/04/2025
        sentencia_traer_PBS_disponibles = """
            SELECT CDESPAGO, cMetodo_id, cMetodo_name, ctype_id
            FROM FPAGO
            WHERE NAPL1 = '2'
        """
        self.pbs_disponibles = self.DICT_CONEXION["conexionDBA"].ejecutar_consulta(sentencia_traer_PBS_disponibles)

        self.dict_pbs_disponibles = {}
        for item in self.pbs_disponibles:
            cdenspago, metodo_id, metodo_name, tipo_id = item
            self.dict_pbs_disponibles[cdenspago] = {
                "payment_method_id": metodo_id,
                "payment_metho_name": metodo_name,
                "payment_type_id": tipo_id
            }
        pprint(self.dict_pbs_disponibles)
        
    def comprobación_PBS(self): #AGREGADO 23/04/2025
        try:
            # Verifica si el método y tipo de pago están en alguno de los valores del diccionario
            encontrados = any(
                self.datos_pagos["payment_method_id"] == datos["payment_method_id"] and
                self.datos_pagos["payment_type_id"] == datos["payment_type_id"]
                for datos in self.dict_pbs_disponibles.values()
            )
            print(f"encontrados: {encontrados}")

            if not encontrados:
                return False
            return True

        except Exception as e:
            self.NRO_ERROR = 1001
            CustomMessageBox(
                self.DICT_WIDGETS["root"],
                f"Error inesperado",
                f"Ocurrió un error inesperado: {e}",
                "error"
            )
            return False
        
    def LISTADO_ERRORES(self):
        try: #SE SACO LOS PUNTO 25, 26 XQ ESTA CLASE NO NESECEITA EL DATOS_DISPOSITIVOS
            if not self.NRO_ERROR == "ERROR_TARJETA":
                Monto_recibido = self.DICT_CONEXION['conexionDBAServer'].specify_search_condicion('MPQRCODE_OBTENERPAGOServer', 'transaction_details_total_paid_amount', 'external_reference', self.DICT_DATOS_ORDEN['nro_factura'], False)
                if not Monto_recibido == None:
                    Monto_recibido = float(Monto_recibido)
                DICT_ERRORES = {
                    1: "Orden Cancelada",
                    10: (
                        "El monto ingresado no es el mismo recibido en MercadoPago\n"
                        f"Monto ingresado: ${self.DICT_DATOS_ORDEN['monto_pagar'] if not None else "SIN MONTO"}\n"
                        f"Monto recibido: ${Monto_recibido}"
                    ),
                    11: f"El ID {self.id_pago} no coincide",
                    12:  f"El ID {self.id_pago} ya tiene una devolución hecha",
                    13: "El Número de factura no coincide con el ID Obtenido",
                    15: (
                        "Este medio de pago no está disponible para realizar el descuento del PBS.\n"
                        f"Medios Disponibles: {list(self.dict_pbs_disponibles.keys())}"
                    ), #AGREGADO 23/04/2025
                    16: f"No se pudo realizar el reembolso del ID {self.id_pago}\n Por favor, verificar con el supervisor si se necesita más información sobre el reembolso.",  #AGREGADO 23/04/2025
                    21: "El pago no está aprobado",
                    23: "No hemos recibido respuesta de MercadoPago",
                    24: f"No hay dispositivos vinculados con la caja {self.datos_obtener_pago["NomCaja"]}.",
                    100: "Error a la hora de buscar pago manual",
                    101: "Error busqueda en MercadoPago",
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
                error_tarjeta_traducido = self.ERROR_API(self.datos_pagos["status_detail"])
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
            
    def finalizar_pago(self):
        try:
            datos = {
                'status': 1,
                'response': 0,
                'description': 'accredited',
                'IDMercadoPago': self.id_pago,
            }
            #messagebox.showinfo("Pago recibido", f"Pago recibido\nNro Factura: {self.DICT_DATOS_ORDEN["nro_factura"]}\nNro Operación: {self.datos_pagos["id"]}\nMonto recibido: {float(self.datos_pagos["transaction_amount"])}")
            self.DICT_WIDGETS["my_label_aviso"].config(text="Pago recibido") 
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_CONEXIONPROGRAMAS", datos, "nro_factura", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_CONEXION["conexionDBAServer"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOServer", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_WIDGETS["cerrar_ventana"]()
                
        except Exception as e:
            log_error(str(e), "finalizar_pago")
            
            
    def on_8_and_6(self):
        try:
            if keyboard.is_pressed('8') and keyboard.is_pressed('6'):
                if self.SELECCION_TIPO_BUSQUEDA == None:
                    self.cuadro_dialogo_eleccion_buscar_seleccion_mpqr()
        except Exception as e:
            log_error(str(e), "on_8_and_6")
            messagebox.showerror("Error", "Ha ocurrido un error al detectar las teclas '8' y '6'.")
            
    def on_a_and_6(self):
        try:
            if keyboard.is_pressed('a') and keyboard.is_pressed('6'):
                if self.SELECCION_TIPO_BUSQUEDA == None:
                    self.cuadro_dialogo_eleccion_buscar_seleccion_mppoint()
        except Exception as e:
            log_error(str(e), "on_a_and_6")
            messagebox.showerror("Error", "Ha ocurrido un error al detectar las teclas 'a' y '6'.")

    def on_a_and_b(self):
        """ Función que muestra el mensaje de confirmación y cierra la interfaz si el usuario acepta. """
        try:
            if messagebox.askyesno("CERRAR SISTEMA COBRO", "¿SEGURO QUE DESEA CERRAR EL SISTEMA DE COBRO?"):
                self.cerrar_orden_interfaz()
            print("a+b")
        except Exception as e:
            log_error(str(e), "on_a_and_b")
            messagebox.showerror("Error", "Ha ocurrido un error al detectar las teclas 'a' y 'b'.")
            
    def cerrar_orden_interfaz(self):
        self.NRO_ERROR = 1
        self.datos_pagos = False
        self.DICT_PROGRESO["text_label_aviso"] = "Error en el pago"
        self.DICT_PROGRESO["carga"] = 99
        self.DICT_PROGRESO["command"] = self.error_pago
        #self.DICT_WIDGETS["cerrar_ventana"]()
    
        
class Ventana_BuscarPagoManual:
    def __init__(self, DICT_WIDGETS, DICT_DATOS_ORDEN, DICT_CONEXION, tipo_busqueda=False): #AGREGAR EL DICT__DATOS, PARA REALIZAR LA COMPARACION DEL NRO FACTURA Y EL MONTO...
        
        self.DICT_WIDGETS = DICT_WIDGETS
        self.DICT_DATOS_ORDEN = DICT_DATOS_ORDEN
        self.DICT_CONEXION = DICT_CONEXION
        self.tipo_busqueda = tipo_busqueda
        self.condicion_teclado =  self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "teclado_km84", False)
        if self.condicion_teclado:
            self.teclado_hasar = TecladoHasar()

        self.respuesta_mp = None
        self.press_enter_id_pago_manual = False
        
        self.error_flags = {
                "focus_in": False,
                "focus_out": False,
                "click_outside": False
            }
        
        # Registrar el método de validación
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["func_ventana_buscar_pago_manual"]()
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["ventana_buscar_pago_manual"].protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["button_info_buscar_pago"].config(command=self.buscar_id_pago_manual)
        
        self.placeholder_text = "ID de Operación"
        #self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(0, self.placeholder_text)
        #self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].config(foreground='gray')

        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].bind("<FocusIn>", self.entry_info_buscar_pago_on_focus_in)
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].bind("<FocusOut>", self.entry_info_buscar_pago_on_focus_out)
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].focus_set()
        # Inicializa una lista para guardar la secuencia de teclas
        self.tecla_secuencia = []

        

        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["ventana_buscar_pago_manual"].bind("<Button-1>", self.handle_click_outside)
        
        if self.condicion_teclado == "false" or self.condicion_teclado == None:
            vcmd = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].register(self.validate_number)
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].config(validatecommand=(vcmd, '%P'))
            keyboard.add_hotkey('enter', self.press_enter_buscar_id_manual)
        else:
            # Asocia el evento de presionar tecla
            self.teclado_hasar.asignar_funcion("6a", self.press_enter_buscar_id_manual)
            self.teclado_hasar.asignar_funcion("ab", self.on_closing)
            self.teclado_hasar.asignar_funcion("86", self.teclado_hasar.borrar_ultimo_caracter)  # Si "67" es la combinación para borrar

            self.teclado_hasar.set_entry(self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"])
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].bind("<KeyPress>", self.detectar_secuencia)
            pass
            
    def press_enter_buscar_id_manual(self):
        try:
            if self.press_enter_id_pago_manual == False:
                self.press_enter_id_pago_manual = True
                self.buscar_id_pago_manual()
        except:
            self.on_closing()


    
    def buscar_id_pago_manual(self):
        try:
            datos_pagos = self.DICT_CONEXION["conexionAPI"].obtenerPAGO(self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get())
            pprint(datos_pagos.json())
            if datos_pagos.status_code >= 200 and datos_pagos.status_code < 300:
                if datos_pagos.json()["point_of_interaction"]["type"] == "POINT" :
                    self.SELECCION_TIPO_BUSQUEDA = False
                else:
                    self.SELECCION_TIPO_BUSQUEDA = True
                if self.SELECCION_TIPO_BUSQUEDA:
                    print("QR")
                    respuesta = self.DICT_CONEXION["conexionAPI"].obtenerPago_manual(self.DICT_DATOS_ORDEN["external_id_pos"], datos_pagos)
                    print("PAGO ENCONTRADO")
                elif self.SELECCION_TIPO_BUSQUEDA == False:
                    print("POINT")
                    respuesta = self.DICT_CONEXION["conexionAPIPOINT"].obtenerPago_manualPOINT(datos_pagos)
            else:
                respuesta = "No se ha encontrado el número de operación"

            if isinstance(respuesta, str):
                CustomMessageBox(self.DICT_WIDGETS["root"], "Error", respuesta, "error")
                #messagebox.showerror("Error", respuesta)
                if not respuesta == "No se ha encontrado el número de operación":
                    self.respuesta_mp = False
            else:
                CustomMessageBox(self.DICT_WIDGETS["root"], "Operación Exitosa", "Se ha encontrado el número de operación", "info")
                #messagebox.showinfo("Operación Exitosa", "Se ha encontrado el número de operación")
                self.respuesta_mp = respuesta
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["cerrar_ventana_buscar_pago_manual"]()
                time.sleep(1)
                return
            self.on_closing()
        except Exception as e:
            error_detallado = traceback.format_exc()
            print(error_detallado)
            log_error(str(e), "buscar_id_pago_manual")
            messagebox.showerror("Error", "Ha ocurrido un error al buscar el ID de pago manual.")
            
    def return_respuesta_mp(self):
        return self.respuesta_mp
    
    def on_closing(self):
        if self.tipo_busqueda:
            if messagebox.askyesno("CERRAR SISTEMA COBRO", "¿SEGURO QUE DESEA CERRAR EL SISTEMA DE COBRO?"):
                self.respuesta_mp = "CERRANDO"
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["cerrar_ventana_buscar_pago_manual"]()
        else:
            self.respuesta_mp = "CERRANDO"
            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["cerrar_ventana_buscar_pago_manual"]()
    
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
                CustomMessageBox(self.DICT_WIDGETS["root"], "Error", "Solo puedes ingresar valores numéricos." "error")
                self.respuesta_mp = "CERRANDO"
                #messagebox.showerror("Error", "Solo puedes ingresar valores numéricos.")
                return False
        except Exception as e:
            log_error(str(e), "validate_number")
            messagebox.showerror("Error", "Error al validar el número.")
            return False

    def detectar_secuencia(self, event):
        try:
            return "break"
            """ # Agregar la tecla presionada a la secuencia solo si es relevante
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
                
                if secuencia_tupla[:2] == ('a', 'b'):
                    # Obtener el Entry y eliminar los últimos dos caracteres
                    entry_widget = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"]
                    current_text = entry_widget.get()
                    
                    if len(current_text) >= 2:
                        entry_widget.delete(len(current_text) - 2, ttk.END)

                    # Llamar a la función de cierre
                    self.on_closing()

                    # Limpiar la secuencia
                    self.tecla_secuencia = []
                    return  # Salir de la función

                # Ejecutar botón si detecta '6', 'a'
                if secuencia_tupla[:2] == ('6', 'a'):  # Verificar solo las dos primeras teclas
                    # Obtener el contenido actual del Entry
                    current_text = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get()

                    # Eliminar los últimos dos caracteres del texto del Entry
                    new_text = current_text[:-2]

                    # Actualizar el Entry con el texto modificado
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, ttk.END)
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(ttk.END, new_text)

                    # Invocar el botón después de eliminar los caracteres
                    self.press_enter_buscar_id_manual()

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
                        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, ttk.END)
                        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(ttk.END, new_text)
                    self.tecla_secuencia = []  # Limpiar la secuencia

                elif secuencia_tupla == ('8', '6', 'Return'):
                    # Limpiar el Entry si la secuencia es '8', '6', 'Return'
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, ttk.END)
                    self.tecla_secuencia = []  # Limpiar la secuencia

                else:
                    # Si la secuencia no coincide con las combinaciones o patrones, eliminar las últimas teclas del Entry
                    current_text = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get()
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, ttk.END)

                    # Eliminar los últimos caracteres (simulando el "retroceso" de las teclas)
                    new_text = current_text[:-len(secuencia_tupla)]  # Eliminar los caracteres correspondientes a la secuencia

                    # Establecer el nuevo texto en el Entry después de eliminar
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(ttk.END, new_text)

                    # Limpiar la secuencia
                    self.tecla_secuencia = []

            else:
                # Si la secuencia tiene menos de 3 teclas, no hacer nada
                pass"""

        except Exception as e:
            log_error(str(e), "detectar_secuencia")
            messagebox.showerror("Error", "Error al procesar la secuencia de teclas.")
            