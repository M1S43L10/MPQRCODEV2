import tkinter as tk
import ttkbootstrap as ttk
import Func.window_position
import threading
from decimal import Decimal
from GUI.CrearOrdenPago import CrearOrdenPago
from GUI.CrerarOrdenReembolso import CrearOrdenReembolso
from ttkbootstrap.constants import *
from tkinter import messagebox
from assets.image_pathV2 import *
from PIL import Image, ImageTk
from Func.log_errorsV2 import log_error


class GUIMAIN:
    def __init__(self, version, DICT_CONEXION):
        
        self.conexionAPI = DICT_CONEXION["conexionAPI"]
        self.conexionAPIPOINT = DICT_CONEXION["conexionAPIPOINT"]
        self.conexionDBA = DICT_CONEXION["conexionDBA"]
        self.conexionDBAServer = DICT_CONEXION["conexionDBAServer"]
        
        try:
            self.datos_para_orden = self.conexionDBA.specify_search_all_columns_nocondicion("MPQRCODE_CONEXIONPROGRAMAS")[0]
            #self.datos_para_orden[0] = nro_factura
            #self.datos_para_orden[1] = tipo_factura
            #self.datos_para_orden[2] = monto_pagar
            #self.datos_para_orden[3] = status
            #self.datos_para_orden[4] = response
            #self.datos_para_orden[5] = description
            #self.datos_para_orden[6] = tipo_point
            #self.datos_para_orden[7] = IDMercadoPago
            #self.datos_para_orden[8] = NOMCAJA
            #self.datos_para_orden[9] = NUMCAJERO
            #self.datos_para_orden[10] = NOMBRECAJERO
            
            self.datos_caja = self.conexionDBA.specify_search_all_columns("MPQRCODE_CAJA", "idINCREMENT", 1)
            #self.datos_caja[0] = idINCREMENT
            #self.datos_caja[1] = sucNAME
            #self.datos_caja[2] = posNAME
            #self.datos_caja[3] = external_id_pos
            #self.datos_caja[4] = IPN_url
        except Exception as e:
            log_error(f"Error al obtener datos para la orden: {e}", function_name='__init__')
            messagebox.showerror("Error", "No se pudo obtener los datos necesarios para la orden.")
        
        self.ventana_creacion_caja = ttk.Window(themename="lumen")
        self.ventana_creacion_caja.title(f"Creación de OrdenV2, V.{version}")
        self.ventana_creacion_caja.resizable(False, False)
        self.ventana_creacion_caja.iconbitmap(Icono_MercadoPago_Blue())
        
        
        self.frame_left = tk.Frame(
            self.ventana_creacion_caja, 
            width=400, 
            height=550, 
            borderwidth=5, 
            relief=tk.GROOVE  # Cambia 'tk.GROOVE' a otro estilo si prefieres un borde diferente
        )

        self.frame_left.pack(side='left')
        self.frame_left.pack_propagate(False)  # Evitar que el tamaño del frame cambie

        
        self.frame_right = tk.Frame(
            self.ventana_creacion_caja, 
            width=400, 
            height=550, 
            borderwidth=5, 
            relief=tk.GROOVE  # Cambia 'tk.GROOVE' a otro estilo si prefieres un borde diferente
        )

        

        self.frame_conjunto = tk.Frame(self.frame_left)
        self.frame_conjunto.pack()
        
        self.logo_mp()
        self.label_img()
        
        self.func_barra_progreso(DICT_CONEXION)
        
        
        Func.window_position.center_window(self.ventana_creacion_caja, 400, 550)
        self.ventana_creacion_caja.protocol("WM_DELETE_WINDOW", self.mostrar_error)
        self.ventana_creacion_caja.mainloop()
        
    def mostrar_error(self):
        # Mostrar un mensaje de error
        messagebox.showerror("Error", "No se puede cerrar la ventana porque una orden está en proceso.")
        #self.ventana_creacion_caja.destroy()
        
    def logo_mp(self):
        try:
            path_img_dir = LOGO_MP()

            # Cargar y redimensionar la imagen
            self.logo_mp_img = Image.open(path_img_dir)
            self.logo_mp_img = self.logo_mp_img.resize((240, 190), Image.LANCZOS)
            self.logo_mp_img_tk = ImageTk.PhotoImage(self.logo_mp_img)

            # Crear y empacar el Label con la imagen
            self.logo_mp_img_label = ttk.Label(self.frame_conjunto, image=self.logo_mp_img_tk)
            self.logo_mp_img_label.pack()

        except Exception as e:
            log_error(str(e), "logo_mp")
            messagebox.showerror("Error", "Ha ocurrido un error al cargar el logo de MercadoPago.")
            
            
    def func_barra_progreso(self, DICT_CONEXION):
        self.frame_contenedor_barra_progreso = tk.Frame(self.frame_conjunto)
        self.frame_contenedor_barra_progreso.pack(pady=15)
        
        
        self.my_label_aviso = tk.Label(self.frame_contenedor_barra_progreso, text="", font=("Helvetica", 18),  wraplength=250)
        self.my_label_aviso.pack(pady=10)
        
        self.frame_progress_bar = tk.Frame(self.frame_contenedor_barra_progreso)
        self.frame_progress_bar.pack(pady=10)
        
        self.my_label_estado = tk.Label(self.frame_contenedor_barra_progreso, text="", font=("Helvetica", 18))
        self.my_label_estado.pack(pady=10)
        
        self.label_id_pago = tk.Label(self.frame_left, text="", font=("Helvetica", 14))
        
        self.my_label_time = tk.Label(self.frame_left, text="", font=("Helvetica", 16))
        self.my_label_time.pack(pady=10)
        
        self.my_buttonDLT = tk.Button(self.frame_conjunto, text="Cancelar Orden", state=tk.DISABLED, width=15, height=2)
        self.my_buttonDLT.pack(pady=10)
        self.my_buttonDLT.pack_propagate(False)
        
        self.DIC_WIDGET = {
            "root": self.ventana_creacion_caja,
            "label_estado": self.my_label_estado,
            "my_label_aviso": self.my_label_aviso,
            "label_cronometro": self.my_label_time, 
            "id_pago": self.label_id_pago,
            "boton_cancelar":  self.my_buttonDLT,
            "mostrar_qr": self.mostrar_qr,
            "window_position": Func.window_position.center_window, 
            "ventana_tamano_400_550": self.ventana_tamano_400_550,
            "ventana_tamano_800_550": self.ventana_tamano_800_550,
            "def_ventana_buscar_pago_manual": {
                "func_ventana_buscar_pago_manual": self.def_ventana_buscar_pago_manual,
                "cerrar_ventana_buscar_pago_manual": self.cerrar_ventana_buscar_pago_manual
                },
            "cerrar_ventana": self.after_cerrar_ventana
        }
        
        
        
        if self.datos_para_orden[1] == 1:
            if self.conexionDBAServer.specify_search_condicion("SPDIR", "ID", "GRID", "MP_NUEVA_VERSION", False).lower() == "true":
                DICT_DATOS_ORDEN = {
                    "external_id_pos": self.datos_caja[3], 
                    "nro_factura": self.datos_para_orden[0], 
                    "sucNAME": self.datos_caja[1], 
                    "monto_pagar": float(self.datos_para_orden[2].quantize(Decimal('1.00'))),
                    "url_API": self.conexionDBAServer.specify_search_condicion("SPDIR", "ID", "GRID", "url_api_AWS", False),
                    'NomCaja': self.datos_para_orden[8],
                    'NumCajero': self.datos_para_orden[9],
                    'NombreCajero': self.datos_para_orden[10]
                }
            else:
                DICT_DATOS_ORDEN = {
                    "external_id_pos": self.datos_caja[3], 
                    "nro_factura": self.datos_para_orden[0], 
                    "sucNAME": self.datos_caja[1], 
                    "monto_pagar": float(self.datos_para_orden[2].quantize(Decimal('1.00'))),
                    "url_API": self.conexionDBAServer.specify_search_condicion("SPDIR", "ID", "GRID", "url_api_NGROK", False),
                    'NomCaja': self.datos_para_orden[8],
                    'NumCajero': self.datos_para_orden[9],
                    'NombreCajero': self.datos_para_orden[10]
                }
            threading.Thread(target=CrearOrdenPago, args=(self.frame_progress_bar, self.DIC_WIDGET, DICT_DATOS_ORDEN, DICT_CONEXION)).start()
            """threading.Thread(target=self.cerrar_ventana).start()
            print(threading.enumerate())"""
        elif self.datos_para_orden[1] == 2:
            if self.conexionDBAServer.specify_search_condicion("SPDIR", "ID", "GRID", "MP_NUEVA_VERSION", False).lower() == "true":
                DICT_DATOS_ORDEN = {
                    "external_id_pos": self.datos_caja[3], 
                    "nro_factura": self.datos_para_orden[0], 
                    "sucNAME": self.datos_caja[1], 
                    "monto_pagar": float(self.datos_para_orden[2].quantize(Decimal('1.00'))),
                    "url_API": self.conexionDBAServer.specify_search_condicion("SPDIR", "ID", "GRID", "url_api_AWS", False),
                    'NomCaja': self.datos_para_orden[8],
                    'NumCajero': self.datos_para_orden[9],
                    'NombreCajero': self.datos_para_orden[10]
                }
            else:
                DICT_DATOS_ORDEN = {
                    "external_id_pos": self.datos_caja[3], 
                    "nro_factura": self.datos_para_orden[0], 
                    "sucNAME": self.datos_caja[1], 
                    "monto_pagar": float(self.datos_para_orden[2].quantize(Decimal('1.00'))),
                    "url_API": self.conexionDBAServer.specify_search_condicion("SPDIR", "ID", "GRID", "url_api_NGROK", False),
                    'NomCaja': self.datos_para_orden[8],
                    'NumCajero': self.datos_para_orden[9],
                    'NombreCajero': self.datos_para_orden[10]
                }
            threading.Thread(target=CrearOrdenReembolso, args=(self.frame_progress_bar, self.DIC_WIDGET, DICT_DATOS_ORDEN, DICT_CONEXION)).start()
            
            
    def label_img(self):
        try:
            self.ventana_tamano_800_550()
            self.frame_right.pack(side='right')
            self.frame_right.pack_propagate(False)  # Evitar que el tamaño del frame cambie
            
            self.frame_right_contenedor = ttk.Frame(self.frame_right)
            self.frame_right_contenedor.place(relx=0.5, rely=0.5, anchor=ttk.CENTER)
            
            self.frame_aviso_qr = ttk.Frame(self.frame_right_contenedor)
            self.frame_aviso_qr.pack(pady=10)

            self.label_aviso_QR_left = ttk.Label(self.frame_aviso_qr, text="Escanee el ", font=("Helvetica", 18))
            self.label_aviso_QR_left.pack(side="left")
            
            self.label_aviso_QR_right = ttk.Label(self.frame_aviso_qr, text="CÓDIGO QR", font=("Arial Black", 18), foreground="#13a5d5")
            self.label_aviso_QR_right.pack(side="right")
            
            """self.qr_img = Image.open(path_img_dir)
            self.qr_img = self.qr_img.resize((300, 300), Image.LANCZOS)
            self.qr_img_tk = ImageTk.PhotoImage(self.qr_img)"""

            self.qr_img_label = tk.Label(self.frame_right_contenedor)
            self.qr_img_label.pack()
        except Exception as e:
            log_error(str(e), "label_img")
            messagebox.showerror("Error", "Ha ocurrido un error al cargar la imagen QR.")
            
    def mostrar_qr(self):
        path_script = os.path.dirname(os.path.abspath(__file__))
        path_img_dir = os.path.join(path_script, "..", 'QRIMGDATA', 'Scan.png')
        self.qr_img = Image.open(path_img_dir)
        self.qr_img = self.qr_img.resize((300, 300), Image.LANCZOS)
        self.qr_img_tk = ImageTk.PhotoImage(self.qr_img)
        self.qr_img_label.config(image=self.qr_img_tk)
        self.qr_img_label.update_idletasks()
        self.ventana_tamano_800_550()
            
    def def_ventana_buscar_pago_manual(self): 
        try:
            self.ventana_buscar_pago_manual = ttk.Toplevel(self.ventana_creacion_caja)
            self.ventana_buscar_pago_manual.title("Buscar pago manual")
            self.ventana_buscar_pago_manual.iconbitmap(Icono_MercadoPago_Blue())
            self.ventana_buscar_pago_manual.grab_set()

            self.frame_buscar_pago_manual = ttk.Frame(self.ventana_buscar_pago_manual)
            self.frame_buscar_pago_manual.pack(pady=50, padx=100)

            self.label_info_buscar_pago = ttk.Label(self.frame_buscar_pago_manual, text="Ingrese el ID de Operación a verificar:")
            self.entry_info_buscar_pago = ttk.Entry(self.frame_buscar_pago_manual, width=30, validate="key")
            self.button_info_buscar_pago = ttk.Button(self.frame_buscar_pago_manual, text="Buscar")

            self.label_info_buscar_pago.pack(pady=5)
            self.entry_info_buscar_pago.pack(pady=5)
            self.button_info_buscar_pago.pack(pady=5)
            
            self.DIC_WIDGET["def_ventana_buscar_pago_manual"]["ventana_buscar_pago_manual"] = self.ventana_buscar_pago_manual
            self.DIC_WIDGET["def_ventana_buscar_pago_manual"]["frame_buscar_pago_manual"] = self.frame_buscar_pago_manual
            self.DIC_WIDGET["def_ventana_buscar_pago_manual"]["label_info_buscar_pago"] = self.label_info_buscar_pago
            self.DIC_WIDGET["def_ventana_buscar_pago_manual"]["entry_info_buscar_pago"] = self.entry_info_buscar_pago
            self.DIC_WIDGET["def_ventana_buscar_pago_manual"]["button_info_buscar_pago"] = self.button_info_buscar_pago

            Func.window_position.center_window(self.ventana_buscar_pago_manual, 400, 225)

        except Exception as e:
            log_error(str(e), "fun_ventana_buscar_pago_manual")
            messagebox.showerror("Error", "Ha ocurrido un error en la ventana de búsqueda de pago manual.")
            
    def cerrar_ventana_buscar_pago_manual(self):
        self.ventana_creacion_caja.after(25, self.ventana_buscar_pago_manual.destroy)
            
            
    def ventana_tamano_400_550(self):
        Func.window_position.center_window(self.ventana_creacion_caja, 400, 550)
        self.ventana_creacion_caja.update_idletasks()
        
    def ventana_tamano_800_550(self):
        Func.window_position.center_window(self.ventana_creacion_caja, 800, 550)
        self.ventana_creacion_caja.update_idletasks()
            
            
    def after_cerrar_ventana(self):
        self.ventana_creacion_caja.after(25, self.cerrar_ventana)
            
    def cerrar_ventana(self):
        self.ventana_creacion_caja.quit()
        self.ventana_creacion_caja.destroy()