import time
import keyboard
import ttkbootstrap as ttk
import json
import threading
import traceback
from tkinter import messagebox
from GUI.BarraProgreso import BarraProgreso
from GUI.MessageBox import CustomMessageBox
from Func.log_errorsV2 import log_error

class CrearOrdenReembolso(BarraProgreso):
    def __init__(self, frame, DICT_WIDGETS, DICT_DATOS_ORDEN, DICT_CONEXION):
        try:
            super().__init__(frame)
            
            #------------------------------------------- DICCIONARIOS CON DATOS -------------------------------------------
            self.DICT_WIDGETS = DICT_WIDGETS
            self.DICT_CONEXION = DICT_CONEXION
            self.DICT_DATOS_ORDEN = DICT_DATOS_ORDEN
            #---------------------------------------- VARIABLES INICIADORAS ----------------------------------------
            self.id_factura = None
            self.NRO_ERROR = None
            self.respuesta_mp = None
            self.datos_pago = None
            self.detalle_respuesta_mp = None
            self.SELECCION_TIPO_BUSQUEDA = None
            self.condicion_teclado =  self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "teclado_km84", False)
            
            
            self.datos_obtener_pago = {
                'NomCaja': self.DICT_DATOS_ORDEN["NomCaja"],
                'NumCajero': self.DICT_DATOS_ORDEN["NumCajero"],
                'NombreCajero': self.DICT_DATOS_ORDEN["NombreCajero"]
            }
            
            self.DICT_PROGRESO = {
                "widgets": DICT_WIDGETS,
                "text_label_aviso": "Buscando tipo de pago",
                "carga": 15,
                "command": self.tipo_eleccion_buscar
            }
            self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(e, "CrearOrdenReembolso")
            
            
    def buscar_id_factura(self):
        try:
            if self.SELECCION_TIPO_BUSQUEDA == True:
                self.id_factura = self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "id", "external_reference", f'{self.DICT_DATOS_ORDEN["nro_factura"]}', False)
                self.DICT_PROGRESO["text_label_aviso"] = "ID Encontrada"
                self.DICT_PROGRESO["carga"] = 30
                self.DICT_PROGRESO["command"] = None
                self.progreso(**self.DICT_PROGRESO)
                self.DICT_PROGRESO["text_label_aviso"] = f"Número de ID > {self.id_factura}"
                self.DICT_PROGRESO["carga"] = 45
                self.DICT_PROGRESO["command"] = self.iniciar_reembolso
                self.progreso(**self.DICT_PROGRESO)
            else:
                self.id_factura = self.datos_pago["id"]
                self.DICT_PROGRESO["text_label_aviso"] = "ID Encontrada"
                self.DICT_PROGRESO["carga"] = 30
                self.DICT_PROGRESO["command"] = None
                self.progreso(**self.DICT_PROGRESO)
                self.DICT_PROGRESO["text_label_aviso"] = f"Número de ID > {self.id_factura}"
                self.DICT_PROGRESO["carga"] = 45
                self.DICT_PROGRESO["command"] = self.buscar_reembolso_POINT
                self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(e, "buscar_id_factura")
            
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
            
            
    """def cuadro_dialogo_eleccion_buscar(self):
        try:
            # Crear un objeto Style
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
            mensaje = ttk.Label(self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["top_level_cuadro_dialago"], text="¿De que tipo de operacion deseas realizar el reembolso?", anchor="center", font=("Helvetica", 16),  wraplength=400)
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
    
        
        
    def tipo_eleccion_buscar(self):
        try:
            consulta_qr = f"""SELECT COUNT(*) AS existe
                FROM MPQRCODE_OBTENERPAGOServer
                WHERE external_reference = '{self.DICT_DATOS_ORDEN["nro_factura"]}';
            """

            consulta_point = f"""SELECT COUNT(*) AS existe
                FROM MPQRCODE_OBTENERPAGOPOINTServer
                WHERE external_reference = '{self.DICT_DATOS_ORDEN["nro_factura"]}';
            """

            # Ejecutar consulta
            resultado_qr = self.DICT_CONEXION["conexionDBAServer"].ejecutar_consulta(consulta_qr)
            resultado_point = self.DICT_CONEXION["conexionDBAServer"].ejecutar_consulta(consulta_point)

            # Verificar si el resultado no es None y extraer correctamente el valor
            if resultado_qr and len(resultado_qr) > 0:
                resultado_qr = resultado_qr[0][0]  # Extraer el primer valor de la primera fila
            else:
                resultado_qr = 0  # Si no hay resultados, asumimos 0

            if resultado_point and len(resultado_point) > 0:
                resultado_point = resultado_point[0][0]  # Extraer el primer valor de la primera fila
            else:
                resultado_point = 0  # Si no hay resultados, asumimos 0

            # Convertir a entero para evitar errores
            resultado_qr = int(resultado_qr)
            resultado_point = int(resultado_point)

            # Verificar existencia de registros
            if resultado_qr > 0:  
                self.SELECCION_TIPO_BUSQUEDA = True
            elif resultado_point > 0:  
                self.SELECCION_TIPO_BUSQUEDA = False
            else:
                self.NRO_ERROR = 1
                self.cierre_ERROR()
                return  

            if self.SELECCION_TIPO_BUSQUEDA == False:
                self.datos_pago = self.convertir_a_json(self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOPOINTServer", "datos_pago", "external_reference", f'{self.DICT_DATOS_ORDEN["nro_factura"]}', False))
                CustomMessageBox(self.DICT_WIDGETS["root"], "¡¡¡RECORDATORIO!!!", f"REALIZA LA DEVOLUCIÓN DEL PAGO DESDE EL POINT {self.datos_pago["point_of_interaction"]["device"]["serial_number"]}.\nUNA VEZ REALIZADO LA DEVOLUCIÓN DESDE EL POINT PRESIONE EL BOTON OK.", "info")
                #messagebox.showinfo("¡¡¡RECORDATORIO!!!", f"REALIZA LA DEVOLUCIÓN DEL PAGO DESDE EL POINT {self.datos_pago["point_of_interaction"]["device"]["serial_number"]}.\nUNA VEZ REALIZADO LA DEVOLUCIÓN DESDE EL POINT PRESIONE EL BOTON ACEPTAR.")

            self.DICT_PROGRESO["text_label_aviso"] = "Buscando ID de Operación"
            self.DICT_PROGRESO["carga"] = 25
            self.DICT_PROGRESO["command"] = threading.Thread(target=self.buscar_id_factura).start
            self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            print(e)

            
            
    def iniciar_reembolso(self):
        try:
            log_error(f"Iniciando reembolso para ID {self.id_factura}", "iniciar_reembolso")
            self.DICT_PROGRESO["text_label_aviso"] = f"Iniciando Reembolso de Op > {self.id_factura}"
            self.DICT_PROGRESO["carga"] = 55
            self.DICT_PROGRESO["command"] = None
            self.progreso(**self.DICT_PROGRESO)
            self.DICT_PROGRESO["text_label_aviso"] = f"Procesando Reembolso de Op > {self.id_factura}"
            self.DICT_PROGRESO["carga"] = 70
            self.DICT_PROGRESO["command"] = self.mandar_orden_reembolso
            self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(e, "iniciar_reembolso")
            
    def buscar_reembolso_POINT(self):
        try:
            self.DICT_PROGRESO["text_label_aviso"] = f"Consultando con MERCADOPAGO por el pago > {self.id_factura}"
            self.DICT_PROGRESO["carga"] = 55
            self.DICT_PROGRESO["command"] = None
            self.progreso(**self.DICT_PROGRESO)
            self.datos_pago = self.DICT_CONEXION["conexionAPIPOINT"].obtenerPago_manualPOINT(self.DICT_CONEXION["conexionAPIPOINT"].obtenerPAGO(self.id_factura))
            if not isinstance(self.datos_pago, str):
                self.datos_pago = self.datos_pago.json()
                if self.datos_pago["status"] == "refunded":
                    self.DICT_PROGRESO["text_label_aviso"] = f"Reembolso encontrado"
                    self.DICT_PROGRESO["carga"] = 75
                    self.DICT_PROGRESO["command"] = None
                    self.progreso(**self.DICT_PROGRESO)
                    self.DICT_PROGRESO["text_label_aviso"] = f"Avisando al Facturador"
                    self.DICT_PROGRESO["carga"] = 99
                    self.DICT_PROGRESO["command"] = self.finalizar_pago
                    self.progreso(**self.DICT_PROGRESO)
                else:
                    CustomMessageBox(self.DICT_WIDGETS["root"], "ERROR", "TODAVIA NO SEA HA HECHO LA DEVOLUCIÓN DESDE EL POINT", "error")
                    #messagebox.showerror("ERROR", "TODAVIA NO SEA HA HECHO LA DEVOLUCIÓN DESDE EL POINT")
                    self.NRO_ERROR = 21
                    self.cierre_ERROR()
            else:
                CustomMessageBox(self.DICT_WIDGETS["root"], "ERROR", self.datos_pago, "error")
                messagebox.showerror("ERROR", self.datos_pago)
                self.NRO_ERROR = 21
                self.cierre_ERROR()
        except Exception as e:
            print(e)
            self.NRO_ERROR = 21
            self.cierre_ERROR()
                
    
            
    def mandar_orden_reembolso(self):
        try:
            threading.Thread(target=self.conexion_con_mp_reembolso).start()
            while self.respuesta_mp == None:
                print("Esperando Respueta")
                time.sleep(1)
            if not self.respuesta_mp == False:
                self.DICT_PROGRESO["text_label_aviso"] = f"Actualizando Datos en el DBA"
                self.DICT_PROGRESO["carga"] = 85
                self.DICT_PROGRESO["command"] = self.actaulizar_nuevos_datos
                self.progreso(**self.DICT_PROGRESO)
                log_error("Reembolso exitoso, actualizando datos...", "mandar_orden_reembolso")
            else:
                CustomMessageBox(self.DICT_WIDGETS["root"], "Error Repuesta MP", self.detalle_respuesta_mp,"error")
                #messagebox.showerror("Error Repuesta MP", self.detalle_respuesta_mp)
                self.NRO_ERROR = 3
                self.cierre_ERROR()
                log_error(f"Fallo el reembolso: {self.detalle_respuesta_mp}", "mandar_orden_reembolso")
        except Exception as e:
            log_error(e, "mandar_orden_reembolso")
            
    def conexion_con_mp_reembolso(self):
        try:
            self.DICT_PROGRESO["text_label_aviso"] = f"Aguardando Respuesta..."
            self.DICT_PROGRESO["carga"] = 75
            self.DICT_PROGRESO["command"] = None
            self.progreso(**self.DICT_PROGRESO)
            reintentos = 3
            intento = 0
            respuesta = None

            while intento < reintentos:
                try:
                    if self.SELECCION_TIPO_BUSQUEDA:
                        respuesta = self.DICT_CONEXION["conexionAPI"].crear_orden_reembolso(
                            self.id_factura,
                            self.DICT_DATOS_ORDEN["monto_pagar"]
                        )
                    else:
                        respuesta = self.DICT_CONEXION["conexionAPIPOINT"].crear_orden_reembolso(
                            self.id_factura,
                            self.DICT_DATOS_ORDEN["monto_pagar"]
                        )

                    if not 'message' in respuesta.json():
                        log_error(f"Reembolso creado correctamente en el intento #{intento + 1}", "conexion_con_mp_reembolso")
                        self.respuesta_mp = respuesta.json()
                        break
                    else:
                        self.detalle_respuesta_mp = respuesta.json()["message"]
                        log_error(f"Intento #{intento + 1} fallido: {self.detalle_respuesta_mp}", "conexion_con_mp_reembolso")
                        self.respuesta_mp = False
                        intento += 1
                        time.sleep(1.5)

                except Exception as e:
                    log_error(f"Excepción en intento #{intento + 1}: {str(e)}", "conexion_con_mp_reembolso")
                    self.respuesta_mp = False
                    intento += 1
                    time.sleep(1.5)
        except Exception as e:
            log_error(e, "conexion_con_mp_reembolso")
            
            
    def actaulizar_nuevos_datos(self):
        try:
            self.DICT_CONEXION["conexionAPI"].obtenerPago_manual(self.DICT_DATOS_ORDEN["external_id_pos"], self.DICT_CONEXION["conexionAPI"].obtenerPAGO(self.id_factura))
        
            self.DICT_PROGRESO["text_label_aviso"] = f"Datos actualizados"
            self.DICT_PROGRESO["carga"] = 99
            self.DICT_PROGRESO["command"] = self.finalizar_pago
            self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(str(e), "actaulizar_nuevos_datos")

            
    def finalizar_pago(self):
        try:
            
            datos = {
                'status': 1,
                'response': 0,
                'description': 'refunded',
                'IDMercadoPago': self.id_factura,
            }
            
            self.DICT_WIDGETS["my_label_aviso"].config(text="Reembolso logrado") 
            if self.SELECCION_TIPO_BUSQUEDA:
                self.DICT_CONEXION["conexionDBAServer"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOServer", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
                self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGO", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
                #messagebox.showinfo("Reembolso logrado", f"Reembolso logrado a:\nNro Factura: {self.DICT_DATOS_ORDEN["nro_factura"]}\nNro Operación: {self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "id", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False)}\nMonto devuelto: {float(self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "transaction_details_total_paid_amount", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False))}")
            else:
                #messagebox.showinfo("Reembolso logrado", f"Reembolso logrado a:\nNro Factura: {self.DICT_DATOS_ORDEN["nro_factura"]}\nNro Operación: {self.datos_pago["id"]}\nMonto devuelto: {float(self.datos_pago["transaction_amount_refunded"])}")
                self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOPOINT", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
                self.DICT_CONEXION["conexionDBAServer"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOPOINTServer", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_CONEXIONPROGRAMAS", datos, "nro_factura", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            log_error("Reembolso finalizado y datos actualizados correctamente.", "finalizar_pago")
            self.DICT_WIDGETS["cerrar_ventana"]()
        except Exception as e:
            print(e)
            log_error(str(e), "finalizar_pago")
            #self.cierre_ERROR(paso_M=True)
#------------------------------------------------------------ CIERRES --------------------------------------------------------------
    def cierre_ERROR(self, paso_M=True, label_error=None ):
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
            
    def mostrar_error(self):
        try:
            CustomMessageBox(self.DICT_WIDGETS["root"], f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES(), "error")
            #messagebox.showerror(f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES())
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion(
                "MPQRCODE_CONEXIONPROGRAMAS",
                self.datos_error,
                "nro_factura",
                f"'{self.DICT_DATOS_ORDEN['nro_factura']}'"  # Cambiado a comillas simples internas
            )
        except Exception as e:
            print(e)
            
    def LISTADO_ERRORES(self):
        try:
            Monto_recibido = self.DICT_CONEXION['conexionDBAServer'].specify_search_condicion('MPQRCODE_OBTENERPAGOServer', 'transaction_details_total_paid_amount', 'external_reference', self.DICT_DATOS_ORDEN['nro_factura'], False)
            if not Monto_recibido == None:
                Monto_recibido = float(Monto_recibido)
            DICT_ERRORES = {
                1: f"No se encontro ID de Operacion para la factura {self.DICT_DATOS_ORDEN["nro_factura"]}",
                2: f"No se encontro ID de Operacion en el servidor",
                3: f"Ya existe una devolución para el ID de Operacion > {self.id_factura}",
                10: (
                    "El monto ingresado no es el mismo recibido en MercadoPago\n"
                    f"Monto ingresado: ${self.DICT_DATOS_ORDEN['monto_pagar'] if not None else "SIN MONTO"}\n"
                    f"Monto recibido: ${Monto_recibido}"
                ),
                11: f"El ID {self.id_factura} no coincide",
                12:  f"El ID {self.id_factura} ya tiene una devolución hecha",
                20: "LA DEVOLUCIÓN TODAVIA NO FUE HECHA DESDE EL POINT",
                21: "La devolución no está aprobada",
                23: "No hemos recibido respuesta de MercadoPago",
                1001: "Error no registrado"
            }
        
            self.datos_error = {
                'status': 0,
                'response': self.NRO_ERROR,
                'description': DICT_ERRORES[self.NRO_ERROR]
            }
            print(DICT_ERRORES[self.NRO_ERROR])
            return DICT_ERRORES[self.NRO_ERROR]
        except Exception as e:
            # Captura el traceback completo y lo registra
            error_detallado = traceback.format_exc()
            print(self.NRO_ERROR, error_detallado)
            log_error(error_detallado, "LISTADO_ERRORES")  # Registro del error completo
            
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
            
    def llamado_taskkill(self):
        self.DICT_WIDGETS["cerrar_con_taskill"](self.DICT_DATOS_ORDEN['nro_factura'])