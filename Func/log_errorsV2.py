import logging

# Configurar el archivo donde se guardarán los errores
logging.basicConfig(
    filename='errores.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(error_message, function_name=None):
    if function_name:
        logging.error(f"{function_name}: {error_message}")
    else:
        logging.error(error_message)