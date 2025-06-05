import keyboard

class TecladoHasar:
    instancia_unica = None  # Variable estática para almacenar la instancia única

    def __new__(cls, *args, **kwargs):
        """Patrón Singleton: Solo permite una instancia activa a la vez"""
        if cls.instancia_unica is None:
            cls.instancia_unica = super(TecladoHasar, cls).__new__(cls)
        return cls.instancia_unica

    def __init__(self):
        """Inicializa el teclado HASAR sin necesidad de Entry al inicio."""
        if hasattr(self, "inicializado"):  # Evita reinicializar múltiples veces
            return
        self.inicializado = True

        self.key_mapping = {
            "46": "0",  "47": "00", "48": ".",  
            "56": "1",  "57": "2",  "58": "3",
            "66": "4",  "67": "5",  "68": "6",
            "76": "7",  "77": "8",  "78": "9"
        }
        self.funciones = {}  # Diccionario para funciones personalizadas
        self.current_keys = []  # Almacena las teclas presionadas
        self.entry_widget = None  # Inicialmente no hay un Entry asignado
        
        if not hasattr(self, "hook_id"):
            self.hook_id = keyboard.hook(self.on_key_event)  # Registrar hook solo una vez

    def set_entry(self, entry_widget):
        """Asigna el Entry donde se insertarán los números."""
        self.entry_widget = entry_widget

    def asignar_funcion(self, combinacion, funcion):
        """Asigna una función personalizada a una combinación de teclas."""
        self.funciones[combinacion] = funcion

    def on_key_event(self, event):
        """Captura teclas presionadas y ejecuta la acción correspondiente."""
        if event.event_type == "down":  
            tecla = event.name.lower()

            if tecla == "enter":  
                self.current_keys.clear()  # Limpia buffer si se presiona ENTER
                return  

            if tecla.isalnum():  
                self.current_keys.append(tecla)

            if len(self.current_keys) == 2:  
                combinacion = "".join(self.current_keys)

                if combinacion in self.key_mapping:
                    numero = self.key_mapping[combinacion]
                    self.insertar_en_entry(numero)  # Inserta el número en el Entry
                elif combinacion in self.funciones:
                    self.funciones[combinacion]()  # Ejecuta la función personalizada
                else:
                    print(f"Teclas desconocidas: {combinacion}")

                self.current_keys.clear()  # Reinicia el buffer

    def insertar_en_entry(self, numero):
        """Agrega el número detectado al Entry de Tkinter sin eliminar otros valores."""
        if self.entry_widget:
            self.entry_widget.insert("end", numero)  # Inserta al final del Entry
            
            
    def borrar_ultimo_caracter(self):
        """Elimina el último carácter del Entry."""
        if self.entry_widget:
            texto_actual = self.entry_widget.get()  # Obtiene el contenido actual
            if texto_actual:  # Verifica si hay algo para borrar
                self.entry_widget.delete(len(texto_actual) - 1, "end")  # Borra el último carácter



"""# Ejemplo de uso
if __name__ == "__main__":
    teclado = TecladoHasar()

    # Ejemplo de funciones que se pueden asignar
    def buscar_pago():
        print("Buscando pago...")

    def cerrar_orden():
        print("Cerrando orden...")

    teclado.asignar_funcion("a6", buscar_pago)
    teclado.asignar_funcion("a7", cerrar_orden)

    print("Escuchando teclado... (Presiona ESC para salir)")
    keyboard.wait("esc")  # Espera hasta que se presione ESC"""
