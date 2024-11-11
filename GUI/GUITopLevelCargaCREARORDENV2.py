import threading
import customtkinter as CTk
import time
from PIL import ImageTk, Image

import assets.image_pathV2 as RutaDeImagenes

class TopLevelCargaCREARORDEN():
    def __init__(self):
        self.aviso = False
        self.aviso_actual = 0
        self.avisos = ['Conectando']
        self.numero_deseado = 1
        self.aviso_creado = threading.Event()  # Evento de sincronización
        self.hilo_activo = True  # Bandera para controlar la ejecución del hilo
        
        path_img_mp = RutaDeImagenes.LOGO_MP()
        self.top_level = CTk.CTk(fg_color="white")  
        self.logo_mp_img_CTK = CTk.CTkImage(Image.open(path_img_mp), size=(100, 70))
        self.frame_top_level_ventana = CTk.CTkFrame(self.top_level, fg_color='transparent')
        self.frame_top_level_ventana.pack()
        # Crear un widget CTkLabel para mostrar la imagen
        self.logo_mp_img_label = CTk.CTkLabel(self.frame_top_level_ventana, image=self.logo_mp_img_CTK, text="")
        self.logo_mp_img_label.grid(row=0, column=0, sticky="nsew")
        
        
        self.top_level.title('Ventana Principal')
        self.frame_ventana_toplevel = CTk.CTkFrame(self.frame_top_level_ventana, fg_color="transparent")
        self.iniciar_interfaz()
        self.cargar_imagen()
        self.progress_bar()
        self.centrar_ventana()
        self.top_level.mainloop()
        
    def iniciar_interfaz(self):
        self.frame_top_level_ventana.grid_rowconfigure(0, weight=1)
        self.frame_top_level_ventana.grid_columnconfigure(0, weight=1)
        self.top_level.geometry("150x120")
        self.top_level.overrideredirect(True)
        self.frame_ventana_toplevel.grid(row=1, column=0, sticky="nsew")
        #self.cargar_imagen()
        self.hilo_envio_MP = threading.Thread(target=self.envio_a_MercadoPago)
        self.hilo_envio_MP.start()  # Ejecutar en un hilo secundario

        # Llamar al método que crea el widget CTkLabel dentro del hilo principal
        self.top_level.after(0, self.label_aviso)
        # Esperar 5 segundos antes de cerrar la ventana
        self.top_level.after(3000, self.cerrar_ventana_y_hilo)

    def centrar_ventana(self):
        self.top_level.update_idletasks()
        ancho = self.top_level.winfo_width()
        alto = self.top_level.winfo_height()
        x = (self.top_level.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.top_level.winfo_screenheight() // 2) - (alto // 2)
        self.top_level.geometry('+{}+{}'.format(x, y)) 

    def cerrar_ventana(self):
        self.top_level.destroy()

    def progress_bar(self):
        self.frame_progress_bar_MP = CTk.CTkFrame(self.frame_ventana_toplevel, fg_color="transparent", width=150, height=100)
        self.progress_bar_envio_MP = CTk.CTkProgressBar(self.frame_progress_bar_MP, orientation='horizontal', mode='indeterminate', progress_color='#00b1ea')
        self.frame_progress_bar_MP.pack()
        self.progress_bar_envio_MP.pack()
        self.progress_bar_envio_MP.start()

    def actualizar_numero_deseado(self, nuevo_numero):
        if 1 <= nuevo_numero <= len(self.avisos):
            self.numero_deseado = nuevo_numero
            self.cambio_de_aviso()

    def label_aviso(self):
        # Esta función crea un widget CTkLabel para mostrar un aviso
        # Se programa para ejecutarse en el hilo principal usando self.top_level.after
        self.top_level.after(0, self.crear_label_aviso)

    def crear_label_aviso(self):
        # Esta función realmente crea el widget CTkLabel
        self.label_aviso_carga_menu = CTk.CTkLabel(self.frame_ventana_toplevel, text='', text_color='#000000')
        self.label_aviso_carga_menu.pack(pady=15, side='bottom')
        self.aviso_creado.set()  # Indica que el aviso ha sido creado y está listo
        self.cambio_de_aviso()

    def cambio_de_aviso(self):
        if 1 <= self.numero_deseado <= len(self.avisos):
            numero_actual = self.numero_deseado
            aviso_actual = self.avisos[self.numero_deseado - 1]
            self.actualizar_aviso(aviso_actual)
            self.mostrar_puntos()
            self.top_level.after(10000, self.cambio_de_aviso)
        else:
            print("El número deseado está fuera de rango")

    def mostrar_puntos(self, contador_puntos=0):
        if contador_puntos < 3:
            aviso_actual = self.avisos[self.numero_deseado - 1]
            self.actualizar_aviso(f'{aviso_actual}{"." * (contador_puntos + 1)}')
            self.top_level.after(1000, self.mostrar_puntos, contador_puntos + 1)
        else:
            self.top_level.after(1000, self.cambio_de_aviso)

    def actualizar_aviso(self, aviso):
        self.label_aviso_carga_menu.configure(text=aviso)

    def cargar_imagen(self):
        # Obtener la ruta de la imagen
        path_img_mp = RutaDeImagenes.LOGO_MP()
        # Crear un objeto CTkImage con la imagen y almacenar una referencia a ella
        self.logo_mp_img_CTK = CTk.CTkImage(Image.open(path_img_mp), size=(100, 70))
        # Crear un widget CTkLabel para mostrar la imagen
        self.logo_mp_img_label = CTk.CTkLabel(self.frame_ventana_toplevel, image=self.logo_mp_img_CTK, text="")
        # Empaquetar el widget en el frame
        self.logo_mp_img_label.pack() 
            
    def envio_a_MercadoPago(self):
        self.label_aviso()
        resultado_envio = True
        tiempo_espera = 3  # Duración en segundos
        tiempo_transcurrido = 0
        while resultado_envio:
            if self.numero_deseado == 1:
                if tiempo_transcurrido >= tiempo_espera:
                    resultado_envio = False
                else:
                    tiempo_transcurrido += 1
            time.sleep(1)  # Esperar un segundo antes de revisar de nuevo
    
    def cerrar_ventana_y_hilo(self):
        # Cerrar la ventana principal
        self.top_level.destroy()
        # Detener el hilo de envío a MercadoPago
        self.hilo_envio_MP.join()



#TopLevelCargaCREARORDEN(None,None,None)

# Crear instancia de la clase TopLevelCargaMenu
