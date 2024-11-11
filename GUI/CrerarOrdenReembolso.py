import time
import json
import threading
import traceback
from tkinter import messagebox
from GUI.BarraProgreso import BarraProgreso
from Func.log_errorsV2 import log_error

class CrearOrdenReembolso(BarraProgreso):
    def __init__(self, frame, DICT_WIDGETS, DICT_DATOS_ORDEN, DICT_CONEXION):
        try:
            super().__init__(frame)
            
            #---------------------------------------- VARIABLES INICIADORAS ----------------------------------------
            self.id_factura = None
            self.NRO_ERROR = None
            self.respuesta_mp = None
            self.detalle_respuesta_mp = None
            
            #------------------------------------------- DICCIONARIOS CON DATOS -------------------------------------------
            self.DICT_WIDGETS = DICT_WIDGETS
            self.DICT_CONEXION = DICT_CONEXION
            self.DICT_DATOS_ORDEN = DICT_DATOS_ORDEN
            
            
            self.datos_obtener_pago = {
                'NomCaja': self.DICT_DATOS_ORDEN["NomCaja"],
                'NumCajero': self.DICT_DATOS_ORDEN["NumCajero"],
                'NombreCajero': self.DICT_DATOS_ORDEN["NombreCajero"]
            }
            
            self.DICT_PROGRESO = {
                "widgets": DICT_WIDGETS,
                "text_label_aviso": "Buscando ID de la Factura",
                "carga": 25,
                "command": self.buscar_id_factura
            }
            self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(e, "CrearOrdenReembolso")
            
            
    def buscar_id_factura(self):
        try:
            if not self.DICT_CONEXION["conexionDBA"].specify_search_condicion("MPQRCODE_OBTENERPAGO", "id", "external_reference", f'{self.DICT_DATOS_ORDEN["nro_factura"]}', False) == None:
                if not self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "id", "external_reference", f'{self.DICT_DATOS_ORDEN["nro_factura"]}', False) == None:
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
                    self.NRO_ERROR = 2
                    self.cierre_ERROR()
            else:
                self.NRO_ERROR = 1
                self.cierre_ERROR()
        except Exception as e:
            log_error(e, "buscar_id_factura")
            
            
    def iniciar_reembolso(self):
        try:
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
            else:
                messagebox.showerror("Error Repuesta MP", self.detalle_respuesta_mp)
                self.NRO_ERROR = 3
                self.cierre_ERROR()
        except Exception as e:
            log_error(e, "mandar_orden_reembolso")
            
    def conexion_con_mp_reembolso(self):
        try:
            self.DICT_PROGRESO["text_label_aviso"] = f"Aguardando Respuesta..."
            self.DICT_PROGRESO["carga"] = 75
            self.DICT_PROGRESO["command"] = None
            self.progreso(**self.DICT_PROGRESO)
            respuesta = self.DICT_CONEXION["conexionAPI"].crear_orden_reembolso(self.id_factura, self.DICT_DATOS_ORDEN["monto_pagar"])
            
            if not 'message' in respuesta.json():
                self.respuesta_mp = respuesta.json()
            else:
                self.detalle_respuesta_mp = respuesta.json()["message"]
                self.respuesta_mp = False
        except Exception as e:
            log_error(e, "conexion_con_mp_reembolso")
            
            
    def actaulizar_nuevos_datos(self):
        try:
            self.DICT_CONEXION["conexionAPI"].obtenerPago_manual(self.id_factura, self.DICT_DATOS_ORDEN["nro_factura"], self.DICT_DATOS_ORDEN["external_id_pos"])
        
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
            
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_CONEXIONPROGRAMAS", datos, "nro_factura", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_CONEXION["conexionDBAServer"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOServer", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_WIDGETS["my_label_aviso"].config(text="Reembolso logrado") 
            messagebox.showinfo("Reembolso logrado", f"Reembolso logrado a:\nNro Factura: {self.DICT_DATOS_ORDEN["nro_factura"]}\nNro Operación: {self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "id", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False)}\nMonto devuelto: {float(self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "transaction_details_total_paid_amount", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False))}")
            self.DICT_WIDGETS["cerrar_ventana"]()
        except Exception as e:
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
        messagebox.showerror(f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES())
        self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion(
            "MPQRCODE_CONEXIONPROGRAMAS",
            self.datos_error,
            "nro_factura",
            f"'{self.DICT_DATOS_ORDEN['nro_factura']}'"  # Cambiado a comillas simples internas
        )
        
        
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
                21: "El pago no está aprobado",
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