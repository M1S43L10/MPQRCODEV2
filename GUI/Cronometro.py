from Func.log_errorsV2 import log_error
from tkinter import messagebox

class Cronometro:
    def __init__(self, DIC_WIDGETS, tiempo, funcion):
        try:
            self.DIC_WIDGETS = DIC_WIDGETS
            self.tiempo = tiempo
            self.funcion = funcion
            self.tiempo_espera = 0
            self.timer_id = None  # Identificador para el temporizador
        except Exception as e:
            log_error(str(e), "orden_cronometro")
            messagebox.showerror("Error", "Ha ocurrido un error en el cronómetro de la orden.")

    def actualizar_label(self):
        try:
            self.DIC_WIDGETS["label_cronometro"].config(text=f"Tiempo de respuesta: {self.tiempo_espera} de {self.tiempo}")
            self.DIC_WIDGETS["root"].update_idletasks()
        except Exception as e:
            log_error(str(e), "actualizar_label")
            messagebox.showerror("Error", "Ha ocurrido un error al actualizar el label de tiempo.")

    def temporizador(self):
        try:
            if self.tiempo_espera < self.tiempo:
                self.tiempo_espera += 1
                self.actualizar_label()  # Actualiza el label con el nuevo tiempo
                self.timer_id = self.DIC_WIDGETS["root"].after(1000, self.temporizador)
            else:
                self.funcion()  # Ejecuta la función cuando el tiempo se completa
        except Exception as e:
            log_error(str(e), "temporizador")
            messagebox.showerror("Error", "Ha ocurrido un error en el temporizador.")

    def start_cronometro(self):
        try:
            self.detener_temporizador()  # Detiene cualquier temporizador activo antes de iniciar
            self.tiempo_espera = 0  # Reinicia el tiempo de espera
            self.actualizar_label()  # Actualiza el label al reiniciar
            self.temporizador()  # Inicia el cronómetro
        except Exception as e:
            log_error(str(e), "start_cronometro")
            messagebox.showerror("Error", "Ha ocurrido un error al iniciar el cronómetro.")

    def detener_temporizador(self):
        try:
            if self.timer_id is not None:
                self.DIC_WIDGETS["root"].after_cancel(self.timer_id)
                self.timer_id = None
            self.tiempo_espera = 0  # Reinicia el tiempo de espera a cero
            self.actualizar_label()  # Actualiza el label al reiniciar
        except Exception as e:
            log_error(str(e), "detener_temporizador")
            messagebox.showerror("Error", "Ha ocurrido un error al detener el temporizador.")
