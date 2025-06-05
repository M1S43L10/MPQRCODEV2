import keyboard

class TecladoHasar:
    def __init__(self):
        """Inicializa el teclado con los valores y funciones asignadas."""
        self.key_mapping = {
            "46": "0",  "47": "00", "48": ".",  
            "56": "1",  "57": "2",  "58": "3",
            "66": "4",  "67": "5",  "68": "6",
            "76": "7",  "77": "8",  "78": "9"
        }
        self.funciones = {}  # Diccionario para almacenar funciones personalizadas
        self.current_keys = []  # Buffer para capturar las dos teclas
        keyboard.hook(self.on_key_event)  # Inicia la escucha del teclado

    def asignar_funcion(self, combinacion, funcion):
        """Asigna una función a una combinación de teclas (Ej: 'a6' → buscar_pago)."""
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
                    print(f"Detectado: {self.key_mapping[combinacion]}")
                elif combinacion in self.funciones:
                    print(f"Ejecutando función asignada para: {combinacion}")
                    self.funciones[combinacion]()  # Llama a la función asignada
                else:
                    print(f"Teclas desconocidas: {combinacion}")

                self.current_keys.clear()  # Reinicia buffer para la siguiente entrada

# Ejemplo de uso
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
    keyboard.wait("esc")  # Espera hasta que se presione ESC
