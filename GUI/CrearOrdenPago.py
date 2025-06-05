from pprint import pprint
import tkinter as tk
import time
import threading
import traceback
import keyboard
import pytz
from datetime import datetime, timedelta
from tkinter import messagebox
from GUI.BuscarOrdenPago import Ventana_BuscarPagoManual
from GUI.Cronometro import Cronometro
from GUI.BarraProgreso import BarraProgreso
from GUI.MessageBox import CustomMessageBox
from Func.qrcode_mpV2 import crear_qr_data
from Func.log_errorsV2 import log_error
from Func.tecladohasar import TecladoHasar

class CrearOrdenPago(BarraProgreso):
    def __init__(self, frame, DICT_WIDGETS, DICT_DATOS_ORDEN, DICT_CONEXION):
        try:
        
            # Inicializar correctamente la clase base ttk.Progressbar
            super().__init__(frame)
            
            #---------------------------------------- VARIABLES INICIADORAS ----------------------------------------
            self.crearorden = True
            self.orden_creada = False
            self.id_pago = None
            self.datos_error = None
            self.detalle_error = None
            self.ultima_actualizacion = None
            self.datos_pagos = None
            self.NRO_ERROR = None
            self.PAGO_MANUAL = False
            self.reintentarpago = None
            self.ventana_buscarpagomanual_abierta = False
            
            
            self.card_first_six_digits = None
            self.card_last_four_digits = None
            self.payment_method_id = None
            self.payment_method_name = None
            self.payment_type_id = None
            
            #------------------------------------------- DICCIONARIOS CON DATOS -------------------------------------------
            self.DICT_WIDGETS = DICT_WIDGETS
            self.DICT_CONEXION = DICT_CONEXION
            self.DICT_DATOS_ORDEN = DICT_DATOS_ORDEN
            
            self.condicion_teclado = self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "teclado_km84", False)
            if self.condicion_teclado:
                self.teclado_hasar = TecladoHasar()
                self.teclado_hasar.asignar_funcion("98", self.llamado_taskkill)
                
            self.obtener_diccionario_pbs() #AGREGADO 23/04/2025
            
            self.datos_obtener_pago = {
                'NomCaja': self.DICT_DATOS_ORDEN["NomCaja"],
                'NumCajero': self.DICT_DATOS_ORDEN["NumCajero"],
                'NombreCajero': self.DICT_DATOS_ORDEN["NombreCajero"]
            }
            
            self.DICT_PROGRESO = {
                "widgets": DICT_WIDGETS,
                "text_label_aviso": "Creando Orden",
                "carga": 25,
                "command": self.crear_orden
            }
            
            self.cronometro = Cronometro(self.DICT_WIDGETS, int(self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "mp_tiempo", False)), self.cancelar_orden_pasado_segundos)
            #threading.Thread(target=self.iniciar_orden).start()
            self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(e, "CrearOrdenPago")
        
    def crear_orden(self):
        try:
            reintentos = 3
            intento = 0
            error_envio = None

            while intento < reintentos:
                try:
                    if self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("SPDIR", "ID", "GRID", "MP_NUEVA_VERSION", False).lower() == "true":
                        self.qr_data = self.DICT_CONEXION["conexionAPI"].crearOrdenDinamicoV2(
                            self.DICT_DATOS_ORDEN["external_id_pos"],
                            self.DICT_DATOS_ORDEN["nro_factura"],
                            self.DICT_DATOS_ORDEN["sucNAME"],
                            self.DICT_DATOS_ORDEN["monto_pagar"],
                            self.DICT_DATOS_ORDEN["url_API"]
                        )
                    else:
                        self.qr_data = self.DICT_CONEXION["conexionAPI"].crearOrdenDinamico(
                            self.DICT_DATOS_ORDEN["external_id_pos"],
                            self.DICT_DATOS_ORDEN["nro_factura"],
                            self.DICT_DATOS_ORDEN["sucNAME"],
                            self.DICT_DATOS_ORDEN["monto_pagar"],
                            self.DICT_DATOS_ORDEN["url_API"]
                        )
                        
                    print(self.qr_data.json())

                    if self.qr_data is not None and self.qr_data.status_code == 200:
                        log_error("Orden enviada exitosamente en el intento #" + str(intento + 1), "crear_orden")
                        break  # Salir del bucle si se envió correctamente
                    else:
                        error_envio = self.qr_data.json()['message'] if self.qr_data else "No conexión"
                        intento += 1
                        log_error(f"Error al enviar orden. Intento #{intento}: {error_envio}", "crear_orden")
                        time.sleep(1.5)

                except Exception as inner_e:
                    error_envio = str(inner_e)
                    intento += 1
                    log_error(f"Excepción al enviar orden. Intento #{intento}: {error_envio}", "crear_orden")
                    time.sleep(1.5)

            if self.qr_data is not None and self.qr_data.status_code == 200:
                data_qr = self.qr_data.json()['qr_data']
                crear_qr_data(data_qr)
                self.DICT_PROGRESO["text_label_aviso"] = "Orden Creada. Escanee el QR"
                self.DICT_PROGRESO["carga"] = 40
                self.DICT_PROGRESO["command"] = self.func_orden_creada
                self.progreso(**self.DICT_PROGRESO)
            else:
                CustomMessageBox(self.DICT_WIDGETS["root"], "ERROR", f"Fallo al crear orden después de {reintentos} intentos.\n{error_envio}", "error")
                self.aviso_cancelar_orden()
        except Exception as e:
            log_error(str(e), 'crear_orden')
            CustomMessageBox(self.DICT_WIDGETS["root"], 'Error', 'Ocurrió un error al crear la orden.', "error")
            self.aviso_cancelar_orden()

        
    def func_orden_creada(self):
        try:
            if self.reintentarpago == None:
                self.DICT_PROGRESO["carga"] = 50
                self.DICT_PROGRESO["command"] = self.DICT_WIDGETS["mostrar_qr"]
                log_error("QR mostrado correctamente al usuario.", "func_orden_creada")
                self.progreso(**self.DICT_PROGRESO)
            else:
                self.DICT_WIDGETS["ventana_tamano_800_550"]()
            threading.Thread(target=self.buscar_pago_en_dba).start()
            self.nro_punto = 1
            self.cronometro.start_cronometro()
            #self.DICT_WIDGETS["label_cronometro"].pack(pady=10)
            self.DICT_WIDGETS["boton_cancelar"].config(command=self.aviso_cancelar_orden, state=tk.NORMAL)
            self.id_pago = None
            if self.condicion_teclado:
                self.teclado_hasar.asignar_funcion("a6", self.buscar_pago_manual)
                self.teclado_hasar.asignar_funcion("a7", self.cancelar_orden)
                self.teclado_hasar.asignar_funcion("ab", self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["cerrar_ventana_buscar_pago_manual"])
                """keyboard.hook(self.on_a_and_7)
                keyboard.hook(self.on_a_and_6)
                keyboard.hook(self.on_a_and_b)"""
            else:
                # Asociar la combinación de teclas con la función cancelar_orden
                keyboard.add_hotkey('ctrl+alt+s', self.buscar_pago_manual)
            while self.id_pago == None and not self.DICT_PROGRESO["text_label_aviso"] == "Cancelando Orden":
                if self.nro_punto == 1:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Esperando Pago.")
                    print("Esperando Pago.")
                elif self.nro_punto == 2:
                    self.nro_punto += 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Esperando Pago..")
                    print("Esperando Pago..")
                elif self.nro_punto == 3:
                    self.nro_punto = 1
                    self.DICT_WIDGETS["my_label_aviso"].config(text="Esperando Pago...")
                    print("Esperando Pago...")
                time.sleep(1)
            if not self.DICT_PROGRESO["text_label_aviso"] == "Cancelando Orden":
                self.cerrar_cronometro()
                self.DICT_WIDGETS["ventana_tamano_400_550"]()
                
                self.DICT_PROGRESO["text_label_aviso"] = "Notificación Recibida"
                self.DICT_PROGRESO["carga"] = 51
                self.DICT_PROGRESO["command"] = None
                self.progreso(**self.DICT_PROGRESO)
                time.sleep(1)
                self.DICT_WIDGETS["label_cronometro"].pack_forget()
                if not self.id_pago == None:
                    self.DICT_WIDGETS["id_pago"].config(text=f"Nro. OP: {self.id_pago}")
                    self.DICT_WIDGETS["id_pago"].pack(pady=10)
                self.DICT_PROGRESO["text_label_aviso"] = f"Nro. OP: {self.id_pago}"
                self.DICT_PROGRESO["carga"] = 65
                self.DICT_PROGRESO["command"] = None
                self.progreso(**self.DICT_PROGRESO)
                self.DICT_PROGRESO["carga"] = 75
                self.DICT_PROGRESO["text_label_aviso"] = "Realizando Comparación"
                self.DICT_PROGRESO["command"] = None
                self.esperando_comparacion = False
                print("antes realizar_comparacion")
                if not self.PAGO_MANUAL:
                    self.buscar_pago_en_MP()
                    pprint(self.datos_pagos)
                threading.Thread(target=self.realizar_comparacion).start()
                print("despues realizar_comparacion")
                self.progreso(**self.DICT_PROGRESO)
                
                
                while not self.esperando_comparacion:
                    time.sleep(1)
                    print("Esperando Comparación")
                    pass
                print(self.DICT_PROGRESO["text_label_aviso"])
                if self.reintentarpago == None:
                    self.DICT_PROGRESO["text_label_aviso"] = "Guardando datos..."
                    self.DICT_PROGRESO["carga"] = 80
                    self.DICT_PROGRESO["command"] = self.agrega_datos_dba_caja
                    self.progreso(**self.DICT_PROGRESO)
                elif self.reintentarpago == True:
                    self.DICT_PROGRESO["carga"] = 50
                    self.DICT_PROGRESO["command"] = self.func_orden_creada
                    self.DICT_WIDGETS["id_pago"].pack_forget()
                    self.DICT_WIDGETS["label_cronometro"].pack()
                    self.des_progreso(**self.DICT_PROGRESO)
                elif self.reintentarpago == False:
                    self.DICT_PROGRESO["command"] = self.cancelar_orden
                    self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(e, "func_orden_creada")
            self.cierre_ERROR()
            
    def buscar_pago_en_MP(self):
        self.respuesta_pago = self.DICT_CONEXION["conexionAPI"].obtenerPAGO(self.id_pago)
        self.datos_pagos = self.respuesta_pago.json()
            
    def buscar_pago_en_dba(self): #Activado por un thread que lo hace es esperar el pago en el DBA
        try:
            pos_id = self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_CAJAS", "id", "external_id", self.DICT_DATOS_ORDEN["external_id_pos"], False)
            #print(self.reintentarpago)
            if self.reintentarpago == None:
                while self.DICT_CONEXION["conexionDBAServer"].specify_search_condicionID("MPQRCODE_OBTENERPAGOServer", "data", "external_reference", self.DICT_DATOS_ORDEN["nro_factura"], "pos_id", pos_id, False) == None and not self.DICT_PROGRESO["text_label_aviso"] == "Cancelando Orden" and not self.PAGO_MANUAL == True:
                    time.sleep(1)
                    pass
            elif self.reintentarpago == True:
                self.reintentarpago = False
                self.esperando_comparacion = True
                while self.DICT_CONEXION["conexionDBAServer"].specify_search_condicionID("MPQRCODE_OBTENERPAGOServer", "date_last_updated", "external_reference", self.DICT_DATOS_ORDEN["nro_factura"], "pos_id", pos_id, False) == self.ultima_actualizacion and not self.DICT_PROGRESO["text_label_aviso"] == "Cancelando Orden" and not self.PAGO_MANUAL == True:
                    #print(self.DICT_CONEXION["conexionDBAServer"].specify_search_condicionID("MPQRCODE_OBTENERPAGOServer", "status", "external_reference", self.DICT_DATOS_ORDEN["nro_factura"], "pos_id", pos_id, False))
                    time.sleep(1)
                    pass
            if not self.DICT_CONEXION["conexionDBAServer"].specify_search_condicionID("MPQRCODE_OBTENERPAGOServer", "data", "external_reference", self.DICT_DATOS_ORDEN["nro_factura"], "pos_id", pos_id, False) == None and not self.DICT_PROGRESO["text_label_aviso"] == "Cancelando Orden" and not self.PAGO_MANUAL == True:
                self.id_pago = self.DICT_CONEXION["conexionDBAServer"].specify_search_condicionID("MPQRCODE_OBTENERPAGOServer", "data", "external_reference", self.DICT_DATOS_ORDEN["nro_factura"], "pos_id", pos_id, False)
        except Exception as e:
            log_error(e, "buscar_pago_en_dba")
            #self.cierre_ERROR()
            
            
    def buscar_pago_manual(self):
        log_error("Ventana buscar pago manual abierta.", "buscar_pago_manual")
        
        if self.ventana_buscarpagomanual_abierta  == False:
            self.ventana_buscarpagomanual_abierta  = True
            ventana_buscarpagomanual = Ventana_BuscarPagoManual(self.DICT_WIDGETS, self.DICT_DATOS_ORDEN, self.DICT_CONEXION)
            threading.Thread(target=self.esperar_respuesta_mp, args=(ventana_buscarpagomanual, )).start()
        else:
            print("TATATA")
        """ # Registrar el método de validación
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["func_ventana_buscar_pago_manual"]()
        
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["button_info_buscar_pago"].config(command=self.buscar_id_pago_manual)
        
        vcmd = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].register(self.validate_number)
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].config(validatecommand=(vcmd, '%P'))
        self.placeholder_text = "ID de Operación"
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(0, self.placeholder_text)
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].config(foreground='gray')

        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].bind("<FocusIn>", self.entry_info_buscar_pago_on_focus_in)
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].bind("<FocusOut>", self.entry_info_buscar_pago_on_focus_out)
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].focus_set()
        # Inicializa una lista para guardar la secuencia de teclas
        self.tecla_secuencia = []

        # Asocia el evento de presionar tecla
        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].bind("<KeyPress>", self.detectar_secuencia)

        self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["ventana_buscar_pago_manual"].bind("<Button-1>", self.handle_click_outside)
        
        if self.DICT_CONEXION["conexionDBA"].specify_search_condicion("SPDIR", "ID", "GRID", "teclado_km84", False) == "true":
            keyboard.hook(self.on_4_and_a)"""
            
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
                self.respuesta_pago = self.datos_pagos
                self.datos_pagos = self.respuesta_pago.json()
                self.id_pago = self.datos_pagos["id"]
        else:
            self.NRO_ERROR = 101
        self.esperando_pago = False
        self.PAGO_MANUAL = True
        
    def entry_info_buscar_pago_on_focus_in(self, event):
        try:
            if self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get() == self.placeholder_text:
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, "end")
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].config(foreground='black')
        except Exception as e:
            log_error(str(e), "entry_info_buscar_pago_on_focus_in")
            #messagebox.showerror("Error", "Error al enfocar la entrada de ID de operación.")


    def entry_info_buscar_pago_on_focus_out(self, event):
        try:
            if self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get() == "":
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(0, self.placeholder_text)
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].config(foreground='gray')
        except Exception as e:
            log_error(str(e), "entry_info_buscar_pago_on_focus_out")
            #messagebox.showerror("Error", "Error al desenfocar la entrada de ID de operación.")
            
    def validate_number(self, entry_value):
        try:
            # Validar si la entrada es un número
            if entry_value == "" or entry_value.isdigit() or entry_value == self.placeholder_text:
                return True
            else:
                # Mostrar el mensaje de error
                CustomMessageBox(self.DICT_WIDGETS["root"], "Error", "Solo puedes ingresar valores numéricos.", "error")
                self.ventana_buscarpagomanual_abierta = False
                #messagebox.showerror("Error", "Solo puedes ingresar valores numéricos.")
                return False
        except Exception as e:
            log_error(str(e), "validate_number")
            #messagebox.showerror("Error", "Error al validar el número.")
            return False
        
    def handle_click_outside(self, event):
        try:
            # Verificar si el clic fue fuera del Entry
            widget_under_cursor = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["ventana_buscar_pago_manual"].winfo_containing(event.x_root, event.y_root)
            if widget_under_cursor != self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"]:
                # Llamar al método de pérdida de foco manualmente
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].focus_set()
                self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["ventana_buscar_pago_manual"].focus_set()  # O enfocar el contenedor principal para garantizar la pérdida de foco
        except Exception as e:
            log_error(str(e), "handle_click_outside")
            #messagebox.showerror("Error", "Error al procesar el clic fuera del campo de entrada.")

            
    def detectar_secuencia(self, event):
        try:
            # Agregar la tecla presionada a la secuencia
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
                ('7', '8', 'Return'): '9'
            }

            # Verificar la longitud de la secuencia y procesar si es necesario
            if len(self.tecla_secuencia) >= 3:
                # Solo consideramos las últimas 3 teclas
                secuencia_tupla = tuple(self.tecla_secuencia[-3:])
                if secuencia_tupla == ('8', '6', 'Return'):
                    # Limpiar el Entry si la secuencia es '8', '6', 'Return'
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, tk.END)
                    # Limpiar la secuencia después de la inserción
                    self.tecla_secuencia = []
                elif secuencia_tupla in combinaciones:
                    valor_reemplazo = combinaciones[secuencia_tupla]
                    log_error(f"Secuencia detectada: {secuencia_tupla} → {valor_reemplazo}", "detectar_secuencia")
                    
                    # Obtener el contenido actual del Entry
                    current_text = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get()
                    
                    # Para reemplazos específicos, definimos patrones
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
                    
                    # Reemplazar la secuencia detectada con el valor correspondiente
                    patron = patrones_reemplazo.get(secuencia_tupla, '')
                    if patron:
                        # Eliminar el patrón en el texto y añadir el nuevo valor
                        if patron in current_text:
                            start_idx = current_text.rfind(patron)
                            new_text = current_text[:start_idx] + valor_reemplazo + current_text[start_idx + len(patron):]
                        else:
                            # Si el patrón no está, añadir al final
                            new_text = current_text + valor_reemplazo
                    else:
                        # Para otras secuencias, simplemente añadir al final
                        new_text = current_text + valor_reemplazo
                    
                    # Establecer el nuevo texto en el Entry
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].delete(0, tk.END)
                    self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].insert(tk.END, new_text)
                    
                    # Limpiar la secuencia después de la inserción
                    self.tecla_secuencia = []
                else:
                    # Mantener solo las últimas 3 teclas si la secuencia no coincide
                    self.tecla_secuencia = self.tecla_secuencia[-3:]
        except Exception as e:
            log_error(str(e), "detectar_secuencia")
            #messagebox.showerror("Error", "Error al procesar la secuencia de teclas.")
            
    """def buscar_id_pago_manual(self):
        try:
            respuesta = self.DICT_CONEXION["conexionAPI"].obtenerPago_manual(self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get(), self.DICT_DATOS_ORDEN["nro_factura"], self.DICT_DATOS_ORDEN["external_id_pos"])

            if respuesta == True:
                CustomMessageBox(self.DICT_WIDGETS["root"], "Nro Operacion exitosa", "Se ha encontrado el número de operación", "info")
                #messagebox.showinfo("Nro Operacion exitosa", "Se ha encontrado el número de operación")
                self.cerrar_cronometro()
                self.id_pago = self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"].get()
                self.PAGO_MANUAL = True

            elif respuesta == False:
                CustomMessageBox(self.DICT_WIDGETS["root"], "Error", "No se ha encontrado el número de operación", "error")
                #messagebox.showerror("Error", "No se ha encontrado el número de operación")
            else:
                CustomMessageBox(self.DICT_WIDGETS["root"], "Error", respuesta, "error")
                #messagebox.showerror("Error", respuesta)

            self.DICT_WIDGETS["def_ventana_buscar_pago_manual"]["cerrar_ventana_buscar_pago_manual"]()
        except Exception as e:
            log_error(str(e), "buscar_id_pago_manual")
            messagebox.showerror("Error", "Ha ocurrido un error al buscar el ID de pago manual.")"""
            
        
        
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
                return ["Error no registrado"]
        except Exception as e:
            # Captura el traceback completo y lo registra
            error_detallado = traceback.format_exc()
            print(label_error, error_detallado)
            log_error(error_detallado, "ERROR_API")  # Registro del error completo

    def LISTADO_ERRORES(self):
        try:
            Monto_recibido = self.DICT_CONEXION['conexionDBAServer'].specify_search_condicion(
                'MPQRCODE_OBTENERPAGOServer',
                'transaction_amount',
                'external_reference',
                self.DICT_DATOS_ORDEN['nro_factura'],
                False
            )
            if Monto_recibido is not None:
                Monto_recibido = float(Monto_recibido)

            DICT_ERRORES = {
                1: "Orden Cancelada",
                10: (
                    "El monto ingresado no es el mismo recibido en MercadoPago\n"
                    f"Monto ingresado: ${self.DICT_DATOS_ORDEN['monto_pagar'] if self.DICT_DATOS_ORDEN['monto_pagar'] is not None else 'SIN MONTO'}\n"
                    f"Monto recibido: ${Monto_recibido}"
                ),
                11: f"El ID {self.id_pago} no coincide",
                12: f"El ID {self.id_pago} ya tiene una devolución hecha",
                13: "El Número de factura no coincide con el ID Obtenido",
                15: (
                    "Este medio de pago no está disponible para realizar el descuento del PBS.\n"
                    f"Medios Disponibles: {list(self.dict_pbs_disponibles.keys())}"
                ), #AGREGADO 23/04/2025
                16: f"No se pudo realizar el reembolso del ID {self.id_pago}\n Por favor, verificar con el supervisor si se necesita más información sobre el reembolso.",  #AGREGADO 23/04/2025
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
            error_detallado = traceback.format_exc()
            print(self.NRO_ERROR, error_detallado)
            log_error(error_detallado, "LISTADO_ERRORES")

            
    def llamado_taskkill(self):
        self.DICT_WIDGETS["cerrar_con_taskill"](self.DICT_DATOS_ORDEN['nro_factura'])            

            
#------------------------------------------------------------Comparar datos--------------------------------------------------------

    def realizar_comparacion(self):
        try:
            print("realizar_comparacion")
            if self.PAGO_MANUAL:
                    #BUSCA SI COINCIDEN LOS NÚMMEROS DE FACTURAS
                    print("#BUSCA SI COINCIDEN LOS NÚMEROS DE FACTURAS")
                    if self.DICT_DATOS_ORDEN["nro_factura"] != self.datos_pagos["external_reference"]:
                        if self.es_fecha_aprovado(self.datos_pagos['date_approved']) <= 300:
                            datos_actulizar = {
                                "external_reference": self.DICT_DATOS_ORDEN["nro_factura"],
                            }
                            respuesta = self.DICT_CONEXION["conexionAPI"].actualizarPago(self.id_pago, datos_actulizar)
                            if respuesta.status_code == 200:
                                self.DICT_CONEXION["conexionDBAServer"].insertar_datos_o_actualizar("MPQRCODE_OBTENERPAGOServer", datos_actulizar)
                            else:
                                print(respuesta.json())
                                CustomMessageBox(self.DICT_WIDGETS["root"], f"Error API", respuesta.json(), "error")
                                self.DICT_PROGRESO["text_label_aviso"] = "ERROR"
                                self.esperando_comparacion = True
                                self.reintentarpago = False
                                return
                        else:
                            self.NRO_ERROR = 13
                            CustomMessageBox(self.DICT_WIDGETS["root"], f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES(), "error")
                            self.DICT_PROGRESO["text_label_aviso"] = "ERROR"
                            self.esperando_comparacion = True
                            self.reintentarpago = False
                            return
            if self.datos_pagos["status"] == 'approved':
                #BUSCA SI COINCIDEN LOS MONTOS DE FACTURAS
                print("BUSCA SI COINCIDEN LOS MONTOS DE FACTURAS")
                if self.DICT_DATOS_ORDEN["monto_pagar"] == self.datos_pagos["transaction_amount"]:
                    print(self.DICT_DATOS_ORDEN["monto_pagar"], self.datos_pagos["transaction_amount"])
                else:
                    self.NRO_ERROR = 10
                    CustomMessageBox(self.DICT_WIDGETS["root"], f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES(), "error")
                    #messagebox.showerror(f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES())
                    self.DICT_PROGRESO["text_label_aviso"] = "ERROR"
                    
                    self.esperando_comparacion = True
                    self.reintentarpago = False
                    return 
                #BUSCA SI COINCIDEN EL ID DE MP DE FACTURAS
                """print("BUSCA SI COINCIDEN EL ID DE MP DE FACTURAS")
                if self.id_pago == self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "data", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False):
                    print(self.id_pago == self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "data", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False))
                else:
                    self.NRO_ERROR = 11
                    CustomMessageBox(self.DICT_WIDGETS["root"], f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES(), "error")
                    #messagebox.showerror(f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES())
                    self.DICT_PROGRESO["text_label_aviso"] = "ERROR"
                    self.esperando_comparacion = True
                    self.reintentarpago = False
                    return """                
            elif self.datos_pagos["status"] == 'refunded':
                self.NRO_ERROR = 12
                CustomMessageBox(self.DICT_WIDGETS["root"], f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES(), "error")
                #messagebox.showerror(f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES())
                self.reintentarpago = False                    
                self.esperando_comparacion = True
                return
            elif self.datos_pagos["status"] == "rejected":
                if messagebox.askretrycancel(message=f"No sea recibido el pago.\n ERROR: \n DETALLE: {self.datos_pagos["status"]} {self.ERROR_API(self.datos_pagos["status_detail"])[1]}\n ¿Desea reintentar el pago?", title="Error de Pago"):
                    self.reintentarpago = True
                    self.esperando_comparacion = True
                    self.ultima_actualizacion = self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "date_last_updated", "external_reference", self.DICT_DATOS_ORDEN["nro_factura"], False)
                else:
                    self.DICT_CONEXION["conexionDBAServer"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOServer", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
                    self.reintentarpago = False
                    self.esperando_comparacion = True
                return
            elif self.datos_pagos["status"] == 'in_process':
                self.DICT_PROGRESO["text_label_aviso"] = "Aguardando confirmación de Pago"
                self.progreso(**self.DICT_PROGRESO)
                while self.datos_pagos["status"] == 'in_process':
                    self.buscar_pago_en_MP()
                    print(self.datos_pagos["status"], self.datos_pagos["status_detail"])
                    time.sleep(3)
                self.DICT_PROGRESO["text_label_aviso"] = "Pago Confirmado"
                self.progreso(**self.DICT_PROGRESO)
                self.DICT_PROGRESO["text_label_aviso"] = "Realizando comparación"
                self.progreso(**self.DICT_PROGRESO)
                self.realizar_comparacion()
            # Verificar si los valores PBS son válidos
            elif int(self.DICT_DATOS_ORDEN["response"]) == 98: #AGREGADO 23/04/2025
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
                    self.esperando_comparacion = True
                    self.reintentarpago = False
                    return
                else:
                    CustomMessageBox(self.DICT_WIDGETS["root"], f"Error", "ERROR DE COMPARACIÓN", "error")
                    self.DICT_PROGRESO["text_label_aviso"] = "ERROR"
                    self.esperando_comparacion = True
                    self.reintentarpago = False
                    return
            self.esperando_comparacion = True 
            self.reintentarpago = None   
        except Exception as e:
            print(e)
            log_error(e, "realizar_comparacion")
                
                
                
    def agrega_datos_dba_caja(self):
        try:
            """datos_dba = {
                "external_reference": self.datos_pago["external_reference"],
                "external_idPOS": self.DICT_DATOS_ORDEN["external_id_pos"],
                "collector_id": self.datos_pago["collector_id"],
                "coupon_amount": self.datos_pago["coupon_amount"],
                "currency_id": self.datos_pago["currency_id"],
                "date_approved": self.datos_pago["date_approved"],
                "date_created": self.datos_pago["date_created"],
                "date_last_updated": self.datos_pago["date_last_updated"],
                "date_of_expiration": self.datos_pago["date_of_expiration"],
                "deduction_schema": self.datos_pago["deduction_schema"],
                "description": self.datos_pago["description"],
                "id": self.datos_pago["id"],
                "installments": self.datos_pago["installments"],
                "integrator_id": self.datos_pago["integrator_id"],
                "issuer_id": self.datos_pago["issuer_id"],
                "live_mode": self.datos_pago["live_mode"],
                "marketplace_owner": self.datos_pago["marketplace_owner"],
                "merchant_account_id": self.datos_pago["merchant_account_id"],
                "merchant_number": self.datos_pago["merchant_number"],
                "order_id": self.datos_pago["order_id"],
                "order_type": self.datos_pago["order_type"],
                "payer_id": self.datos_pago["payer_id"],
                "payment_metodo_id": self.datos_pago["payment_method"]["payment_method_id"],
                "payment_metodo_issuer_id": self.datos_pago["payment_method"]["payment_method_issuer_id"],
                "payment_metodo_type": self.datos_pago["payment_method"]["payment_method_type"],
                "pos_id": self.datos_pago["pos_id"],
                "processing_mode": self.datos_pago["processing_mode"],
                "shipping_amount": self.datos_pago["shipping_amount"],
                "sponsor_id": self.datos_pago["sponsor_id"],
                "status": self.datos_pago["status"],
                "status_detail": self.datos_pago["status_detail"],
                "store_id": self.datos_pago["store_id"],
                "taxes_amount": self.datos_pago["32"],
                "transaction_amount": self.datos_pago["transaction_amount"],
                "transaction_amount_refunded": self.datos_pago["transaction_amount_refunded"],
                "net_received_amount": self.datos_pago["transaction_details"]["net_received_amount"],
                "transaction_details_total_paid_amount": self.datos_pago["transaction_details"]["total_paid_amount"],
                "NomCaja": self.datos_obtener_pago["NomCaja"],
                "NumCajero": self.datos_obtener_pago["NumCajero"],
                "NombreCajero":self.datos_obtener_pago["NombreCajero"]
                }"""
            
            #COMPARAR Y SEPARAR EL TIPO DE PAGO
            if self.datos_pagos["payment_method_id"] == "account_money" or self.datos_pagos["payment_method_id"] == "consumer_credits":
                pass
            elif self.datos_pagos["payment_method_id"] == "interop_transfer":
                self.payment_method_id = self.datos_pagos["payment_method_id"]
                self.payment_method_name = "Billetera Virtual"
                self.payment_type_id = self.datos_pagos["payment_type_id"]
            else:
                pagos_disponibles = self.DICT_CONEXION["conexionAPI"].obtenerTodosMediosPagos()
                name_tarjeta_encontrada = None
                for pagos in pagos_disponibles.json():
                    if pagos["id"] == self.datos_pagos["payment_method_id"]:
                        name_tarjeta_encontrada = pagos['name']
                self.card_first_six_digits = self.datos_pagos["card"]["first_six_digits"]
                self.card_last_four_digits = self.datos_pagos["card"]["last_four_digits"]
                self.payment_method_id = self.datos_pagos["payment_method_id"]
                self.payment_method_name = name_tarjeta_encontrada
                self.payment_type_id = self.datos_pagos["payment_type_id"]
                
                
                
            self.DICT_CONEXION["conexionAPI"].obtenerPago_manual(self.DICT_DATOS_ORDEN["external_id_pos"], self.respuesta_pago)
            self.DICT_PROGRESO["carga"] = 99
            self.DICT_PROGRESO["command"] = self.finalizar_pago
            self.progreso(**self.DICT_PROGRESO)
        except Exception as e:
            log_error(e, "agrega_datos_dba_caja")       
            

        
        
#------------------------------------------------------------ CIERRES --------------------------------------------------------------
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
                
    def mostrar_error(self):
        CustomMessageBox(self.DICT_WIDGETS["root"], f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES(), "error")
        #messagebox.showerror(f"Error {self.NRO_ERROR}", self.LISTADO_ERRORES())
        self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion(
            "MPQRCODE_CONEXIONPROGRAMAS",
            self.datos_error,
            "nro_factura",
            f"'{self.DICT_DATOS_ORDEN['nro_factura']}'"  # Cambiado a comillas simples internas
        )
        
    def aviso_cancelar_orden(self):
        self.DICT_PROGRESO["text_label_aviso"] = "Cancelando Orden"
        self.DICT_PROGRESO["carga"] = 51
        self.DICT_PROGRESO["command"] = self.cancelar_orden
        print("aviso_cancelar_orden")
        self.progreso(**self.DICT_PROGRESO)
        log_error("Usuario solicitó cancelar la orden manualmente.", "aviso_cancelar_orden") 
        
    def cancelar_orden(self):
        try:      
            self.NRO_ERROR = 1        
            self.DICT_CONEXION["conexionAPI"].cancelarOrden(self.DICT_DATOS_ORDEN["external_id_pos"])
            self.cerrar_cronometro()
            self.cierre_ERROR(True, "Cancelando Orden")
        except Exception as e:
            log_error(str(e), "cancelar_orden")
            messagebox.showerror("Error", "Ha ocurrido un error al cancelar la orden.")
            
    def cancelar_orden_pasado_segundos(self):
        try:
            self.DICT_CONEXION["conexionAPI"].cancelarOrden(self.DICT_DATOS_ORDEN["external_id_pos"])
            self.cerrar_cronometro()
            self.NRO_ERROR = 23
            self.cierre_ERROR(False, "Cancelando Orden")
            self.DICT_WIDGETS["cerrar_ventana"]()
        except Exception as e:
            log_error(str(e), "cancelar_orden_pasado_segundos")
            
    def cerrar_cronometro(self):
        try:
            self.cronometro.detener_temporizador()
            self.DICT_WIDGETS["label_cronometro"].pack_forget()
            self.DICT_WIDGETS["boton_cancelar"].config(state=tk.DISABLED)
        except Exception as e:
            log_error(str(e), "cerrar_cronometro")
            self.cierre_ERROR()
            
            
    def finalizar_pago(self):
        try:
            datos = {
                'status': 1,
                'response': 0,
                'description': 'accredited',
                'IDMercadoPago': self.id_pago,
                'card_first_six_digits': self.card_first_six_digits,
                'card_last_four_digits': self.card_last_four_digits,
                'payment_method_id': self.payment_method_id,
                'payment_method_name': self.payment_method_name,
                'payment_type_id': self.payment_type_id,
            }
            self.DICT_WIDGETS["my_label_aviso"].config(text="Pago recibido") 
            #messagebox.showinfo("Pago recibido", f"Pago recibido\nNro Factura: {self.DICT_DATOS_ORDEN["nro_factura"]}\nNro Operación: {self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "id", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False)}\nMonto recibido: {float(self.DICT_CONEXION["conexionDBAServer"].specify_search_condicion("MPQRCODE_OBTENERPAGOServer", "transaction_details_total_paid_amount", "external_reference", f"{self.DICT_DATOS_ORDEN["nro_factura"]}", False))}")
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_CONEXIONPROGRAMAS", datos, "nro_factura", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_CONEXION["conexionDBAServer"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGOServer", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            self.DICT_CONEXION["conexionDBA"].actualizar_datos_condicion("MPQRCODE_OBTENERPAGO", self.datos_obtener_pago, "external_reference", f"'{self.DICT_DATOS_ORDEN["nro_factura"]}'")
            log_error("Pago finalizado exitosamente, se actualiza base y se cierra ventana.", "finalizar_pago")
            self.DICT_WIDGETS["cerrar_ventana"]()
        except Exception as e:
            log_error(str(e), "finalizar_pago")
            #self.cierre_ERROR(paso_M=True)
            
    def es_fecha_aprovado(self, date_string):
        try:
            # Parsear la fecha que viene con zona horaria -04:00
            fecha_remota = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.000-04:00")

            # La fecha en la zona -04:00 (ya está en ese huso, sin necesidad de conversión)
            tz_remota = pytz.timezone("Etc/GMT+4")  # GMT+4 es UTC-04:00
            fecha_remota = tz_remota.localize(fecha_remota)

            # Hora actual en Argentina (UTC-03:00)
            tz_arg = pytz.timezone("America/Argentina/Buenos_Aires")
            ahora_arg = datetime.now(tz_arg)

            # Convertimos ambas fechas a UTC para comparar correctamente
            diferencia = abs((ahora_arg.astimezone(pytz.utc) - fecha_remota.astimezone(pytz.utc)).total_seconds())

            return diferencia
        except Exception as e:
            print(f"Error al verificar la fecha: {e}")
            return False
        
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

        
    def comprobación_PBS(self): #AGREGADO 23/04/2025
        try:
            # Verifica si el método y tipo de pago están en alguno de los valores del diccionario
            encontrados = any(
                self.datos_pagos["payment_method_id"] == datos["payment_method_id"] and
                self.datos_pagos["payment_type_id"] == datos["payment_type_id"]
                for datos in self.dict_pbs_disponibles.values()
            )

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
