import tkinter as tk
import ttkbootstrap as ttk
import winsound
import threading
import time
from Func.tecladohasar import TecladoHasar

class CustomMessageBox:
    def __init__(self, parent=None, title="Mensaje", message="Texto del mensaje", msg_type="info",
                 width=700, height=400, font_size=24, teclado_hasar=None):
        """Crea una MessageBox personalizada con ttkbootstrap y Toplevel."""

        self.running = True
        self.result = None

        if parent is None:
            self.parent = tk.Tk()
            self.parent.withdraw()
            self.window = tk.Toplevel(self.parent)
        else:
            self.parent = parent
            self.window = tk.Toplevel(parent)

        self.window.title(title)
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.window.transient(self.parent)
        self.window.grab_set()
        # Contenedor principal
        container = ttk.Frame(self.window, padding=20)
        container.pack(fill="both", expand=True)

        # Frame que contiene el label y los botones
        content_frame = ttk.Frame(container)
        content_frame.pack(pady=20, expand=True)  # Centrar y expandir el contenido

        # Iconos y colores
        icon_colors = {"info": "primary", "warning": "warning", "error": "danger"}
        icon_text = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
        ttk.Label(content_frame, text=icon_text.get(msg_type, "ℹ️"), font=("Arial", font_size + 10),
                  bootstyle=icon_colors.get(msg_type, "primary")).pack(pady=(10, 5))

        # Mensaje dinámico con ajuste de línea (wraplength)
        self.message_label = ttk.Label(content_frame, text=message, font=("Arial", font_size), wraplength=width - 50)
        self.message_label.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.teclado = TecladoHasar()

        # Botones
        self.create_buttons(content_frame, msg_type, font_size)

        # Ajustar la ventana automáticamente según el contenido
        self.window.update_idletasks()  # Actualizar geometría
        content_width = content_frame.winfo_reqwidth() + 50
        content_height = content_frame.winfo_reqheight() + 150
        new_width = max(width, content_width)
        new_height = max(height, content_height)

        self.window.geometry(f"{new_width}x{new_height}")
        self.center_window(new_width, new_height)

        # Sonido de alerta en un hilo
        threading.Thread(target=self.play_alert_sound, args=(msg_type,), daemon=True).start()

        # Esperar acción del usuario
        threading.Thread(target=self.teclado.asignar_funcion, args=("4a", self.close)).start()
        self.wait_for_user_action()
        #
        

    def play_alert_sound(self, msg_type):
        """Reproduce un sonido de alerta sin bloquear la interfaz"""
        if msg_type == "warning":
            winsound.Beep(1000, 1000)
        elif msg_type == "error":
            winsound.Beep(500, 1000)
        elif msg_type == "info":
            winsound.Beep(2000, 500)

    def create_buttons(self, content_frame, msg_type, font_size):
        """Crea botones según el tipo de mensaje"""
        frame = ttk.Frame(content_frame)
        frame.pack(pady=15, fill="x")  # Ajusta el frame para que los botones no se tapen

        button_style = ttk.Style()
        button_style.configure("Custom.TButton", font=("Arial", font_size))

        if msg_type in ["info", "warning", "error"]:
            buton = ttk.Button(frame, text="OK", command=self.close, style="Custom.TButton", bootstyle="success")
            buton.pack()
        elif msg_type == "yesno":
            ttk.Button(frame, text="Sí", command=lambda: self.set_result(True), style="Custom.TButton",
                       bootstyle="primary").pack(side="left", padx=10)
            ttk.Button(frame, text="No", command=lambda: self.set_result(False), style="Custom.TButton",
                       bootstyle="danger").pack(side="left", padx=10)
            

    def set_result(self, value):
        """Guarda el resultado y cierra la ventana"""
        self.result = value
        self.running = False
        self.window.destroy()

    def close(self):
        """Cierra la ventana"""
        self.running = False
        self.window.destroy()

    def center_window(self, width, height):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def wait_for_user_action(self):
        """Mantiene la ejecución en espera hasta que el usuario cierre la ventana"""
        while self.running:
            self.window.update()
            time.sleep(0.1)

    def show(self):
        """Muestra la ventana y espera la respuesta en cuadros de confirmación"""
        self.wait_for_user_action()
        return self.result

"""# ======= EJEMPLO DE USO ======= #
if __name__ == "__main__":
    root = ttk.Window(themename="superhero")  # Ventana principal

    def test_message():
        msg = CustomMessageBox(root, "Aviso", "Este es un mensaje informativo", "info", width=500, height=250, font_size=16)
        msg.show()

    def test_warning():
        msg = CustomMessageBox(root, "Atención", "Este es un mensaje de advertencia", "warning", width=450, height=220, font_size=18)
        msg.show()

    def test_error():
        msg = CustomMessageBox(root, "Error", "Ocurrió un error inesperado", "error", width=400, height=200, font_size=14)
        msg.show()

    def test_yesno():
        msg = CustomMessageBox(root, "Confirmación", "¿Estás seguro de continuar?", "yesno", width=500, height=250, font_size=16)
        respuesta = msg.show()
        print("Respuesta:", respuesta)  # True si 'Sí', False si 'No'

    # Botones de prueba
    ttk.Button(root, text="Mensaje Info", command=test_message, bootstyle="primary").pack(pady=10)
    ttk.Button(root, text="Advertencia", command=test_warning, bootstyle="warning").pack(pady=10)
    ttk.Button(root, text="Error", command=test_error, bootstyle="danger").pack(pady=10)
    ttk.Button(root, text="Confirmación", command=test_yesno, bootstyle="success").pack(pady=10)

    root.mainloop()"""
