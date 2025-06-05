import json
import os

def guardar_json_respuesta(respuesta_json, carpeta="tickets"):
    """
    Guarda la respuesta JSON en un archivo cuyo nombre es el valor de 'external_reference'.
    
    :param respuesta_json: Diccionario con la respuesta JSON.
    :param carpeta: Carpeta donde se guardará el archivo (por defecto 'tickets').
    :return: Ruta del archivo guardado o mensaje de error.
    """
    try:
        # Verificar que la clave "external_reference" existe
        if "external_reference" not in respuesta_json:
            return "Error: La respuesta no contiene 'external_reference'."

        # Obtener el nombre del archivo
        nombre_archivo = f"{respuesta_json['external_reference']}.json"

        # Crear la carpeta si no existe
        os.makedirs(carpeta, exist_ok=True)

        # Guardar el archivo JSON
        ruta_archivo = os.path.join(carpeta, nombre_archivo)
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(respuesta_json, archivo, indent=2, ensure_ascii=False)

        return f"Archivo guardado: {ruta_archivo}"

    except Exception as e:
        return f"Error al guardar el archivo: {str(e)}"