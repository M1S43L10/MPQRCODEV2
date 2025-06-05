from pprint import pprint
import os
import requests
import json
import uuid
import datetime

dt_today = datetime.datetime.now()
dt_today_minutes = datetime.timedelta(minutes=1)
dt_today_plus = dt_today + dt_today_minutes

fechamodificada = dt_today_plus.strftime('%Y-%m-%dT%H:%M:%S.000-04:00')

class Conexion_Api:
    def __init__(self, id_user, acess_token):
        self.id_user = id_user
        self.access_token = acess_token

    def crear_sucursal(self, datosSUC):
        # Url con el Id_User para crear la SUCURSAL
        url = f'https://api.mercadopago.com/users/{self.id_user}/stores'

        # Los headers que necesita la APIs para dar una respuesta
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',  # Modificar los TOKENS de identificación de cada cuenta.
        }

        SUCload = datosSUC

        response = requests.post(url, headers=headers, data=json.dumps(SUCload))
        
        #GUARDAR EL JSON COMO ARCHIVO DE FORMAR LOCAL
        """
        # Crear la carpeta si no existe
        folder_path = "SUCURSALES_JSON"
        os.makedirs(folder_path, exist_ok=True)

        # Guardar la respuesta en un archivo JSON en la carpeta
        with open(os.path.join(folder_path, f"{direccion_SUC[7]}.json"), "w") as json_file:
            json.dump(response.json(), json_file, indent=2)
        """
        
        return response


    def eliminar_sucursal(self, id_sucursal):
        try:
            url = f"https://api.mercadopago.com/users/{self.id_user}/stores/{id_sucursal}"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}',  # Modificar los TOKENS de identificación de cada cuenta.
            }

            # Realizar la solicitud para eliminar la sucursal
            response = requests.delete(url, headers=headers)
            return response.status_code
        except:
            print(response)

    def crear_caja(self, datosPOS):
        url = 'https://api.mercadopago.com/pos'

        hedears = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        POSload = datosPOS
        """
        {
            "category": int(datos_CAJA[0]),  # Convertir el conjunto a lista
            "external_id": str(datos_CAJA[1]),  # Asegurarse de que los datos sean strings si es necesario
            "external_store_id": external_store_id,
            "fixed_amount": True,
            "name": str(datos_CAJA[2]),
            "store_id": int(store_id)
        }

        """
        response = requests.post(url, headers=hedears, data=json.dumps(POSload))
        print(response)
        
        #CREAR ARCHIVO .JSON CON LA RESPUESTA Y GUARDARLO DE FORMA LOCAL (nombre_SUC)
        """# Crear la carpeta si no existe
        folder_path = f"{nombre_SUC}_CAJAS_JSON"
        os.makedirs(folder_path, exist_ok=True)

        # Guardar la respuesta en un archivo JSON en la carpeta
        with open(os.path.join(folder_path, f"{datos_CAJA[3]}.json"), "w") as json_file:
            json.dump(response.json(), json_file, indent=2)      
        """
        if response.status_code >= 200 and response.status_code < 300:
            print("Creación de Caja EXITOSA")
        else:
            print(f"No se logró la Conexión. ERROR {response.status_code} \t\n {response}")
            
        return response
    
    def eliminar_caja(self, idPOS):
        url = f"https://api.mercadopago.com/pos/{idPOS}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.delete(url, headers=headers)
        
        return response
            
    #ORDEN ATENDIDA
    def crear_orden(self, external_id, factura, sucNAME, monto_pagar, picture_url):
        
        url = f"https://api.mercadopago.com/mpmobile/instore/qr/{self.id_user}/{external_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Ttl-Store-Preference': "180" ,
            'Authorization': f'Bearer {self.access_token}'
        }
        payload = {
            "external_reference": f"Factura-{factura}",
            "items": [
                {
                    'id': 000000000000,
                    'title': sucNAME,
                    'currency_id': "ARS",
                    'unit_price': monto_pagar,
                    'quantity': 1,
                    'description': "QR_ATENDIDO",
                    'picture_url': picture_url
                }
            ]
            }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        """
        # Crear la carpeta si no existe
        folder_path = "CREAR_PAGOS"
        os.makedirs(folder_path, exist_ok=True)

        # Guardar la respuesta en un archivo JSON en la carpeta
        with open(os.path.join(folder_path, f"{external_id}.json"), "w") as json_file:
            json.dump(response.json(), json_file, indent=2)
        print(response.status_code)
        """
        guardar_json(response.json(), f"crear_orden_{factura}.json")
        return response
    
    #NO FUNCIONA
    #CREAR LA ORDEN (VERSION 2.0) PODEMOS OBTENER LA ORDEN DE COMPRA
    def crear_ordenV2(self, precio, external_store_id, external_pos_id):
        
        url = f"https://api.mercadopago.com/instore/qr/seller/collectors/{self.id_user}/stores/{external_store_id}/pos/{external_pos_id}/orders"    
        
        headers = {
            "Content-Type": 'application/json',
            'Authorization': f'Bearer {self.access_token}'
            }
        
        payload = {
            "cash_out": {
                "amount": 0
            },
            "description": "Compras Mercaderias",
            "external_reference": "reference_12345678",
            "items": [
                {
                "sku_number": "A123K9191938",
                "category": "marketplace",
                "title": "Inforhard",
                "description": "QR_ATENDIDOV2",
                "picture_url": "https://i.ibb.co/s2hGyvh/366713592-763738879087401-2393967495391053232-n.jpg",
                "unit_price": precio,
                "quantity": 1,
                "unit_measure": "unit",
                "total_amount": precio
                },
            ],
            "title": "Inforhard",
            "total_amount": precio          
            }
        
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        guardar_json(response.json(), f"crear_ordenV2_reference_12345678.json")
        return response.status_code
    
        
    def obtener_ordenV2(self, external_pos_id,):
        url = f"https://api.mercadopago.com/instore/qr/seller/collectors/{self.id_user}/pos/{external_pos_id}/orders"
        
        headers = {
            "Content-Type": 'application/json',
            "Authorization": f"Bearer {self.access_token}"
            }
        
        response = requests.get(url= url, headers=headers)
        return response.status_code
    
    def reembolso_orden(self, precio, external_store_id, external_pos_id):
        
        url = f"https://api.mercadopago.com/instore/qr/seller/collectors/{self.id_user}/stores/{external_store_id}/pos/{external_pos_id}/orders"    
        
        headers = {
            "Content-Type": 'application/json',
            'Authorization': f'Bearer {self.access_token}'
            }
        
        payload = {
            "cash_out": {
                "amount": precio
            },
            "description": "Compras Mercaderias",
            "external_reference": "reference_12345678",
            "items": [
                {
                "sku_number": "A123K9191938",
                "category": "marketplace",
                "title": "Inforhard",
                "description": "QR_ATENDIDOV2",
                "picture_url": "https://i.ibb.co/s2hGyvh/366713592-763738879087401-2393967495391053232-n.jpg",
                "unit_price": 0,
                "quantity": 1,
                "unit_measure": "unit",
                "total_amount": 0
                },
            ],
            "title": "Inforhard",
            "total_amount": precio          
            }
        
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        return response.status_code
    
    def eliminar_ordenV2(self, external_id_pos):
        
        url = f"https://api.mercadopago.com/instore/qr/seller/collectors/{self.id_user}/pos/{external_id_pos}/orders"
        
        headers = {
            "Content-Type": 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.delete(url, headers=headers)
        
        return response.status_code
    
        
        
    def crear_orden_dinamico(self, external_idPOS, nro_factura, sucNAME, monto_pagar, IPN_URL):
        print(fechamodificada, "crear_orden_dinamico")
        url = f"https://api.mercadopago.com/instore/orders/qr/seller/collectors/{self.id_user}/pos/{external_idPOS}/qrs"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        pagodata_json = {
            "cash_out": {
                "amount": 0
            },
            "description": "Purchase description.",
            "expiration_date": f"{fechamodificada}",
            "external_reference": nro_factura,
            "items": [
                {
                "sku_number": "A123K9191938",
                "category": "marketplace",
                "title": sucNAME,
                "description": "QR_DINAMICO",
                "unit_price": monto_pagar,
                "quantity": 1,
                "unit_measure": "unit",
                "total_amount": monto_pagar
                },
            ],
            'notification_url': f'{IPN_URL}api/MPQRCODE', #f'{IPN_URL}'api/MPQRCODE NUEVA VERSION CON ENVIO A AWS
            "title": sucNAME,
            "total_amount": monto_pagar          
            }
        
        response = requests.put(url, headers=headers, data=json.dumps(pagodata_json))
        guardar_json(response.json(), f"crear_orden_dinamico_{nro_factura}.json")
        print(response)
        return response
    
    
    def crear_orden_dinamicoV2(self, external_idPOS, nro_factura, sucNAME, monto_pagar, IPN_URL):
        print(fechamodificada,"crear_orden_dinamicoV2")
        url = f"https://api.mercadopago.com/instore/orders/qr/seller/collectors/{self.id_user}/pos/{external_idPOS}/qrs"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        pagodata_json = {
            "cash_out": {
                "amount": 0
            },
            "description": "Purchase description.",
            "expiration_date": f"{fechamodificada}",
            "external_reference": nro_factura,
            "items": [
                {
                "sku_number": "A123K9191938",
                "category": "marketplace",
                "title": sucNAME,
                "description": "QR_DINAMICO",
                "unit_price": monto_pagar,
                "quantity": 1,
                "unit_measure": "unit",
                "total_amount": monto_pagar
                },
            ],
            'notification_url': f'{IPN_URL}', #f'{IPN_URL}'api/MPQRCODE NUEVA VERSION CON ENVIO A AWS
            "title": sucNAME,
            "total_amount": monto_pagar          
            }
        
        response = requests.put(url, headers=headers, data=json.dumps(pagodata_json))
        print(response)
        guardar_json(response.json(), f"crear_orden_dinamicoV2_{nro_factura}.json")
        return response
    
    def obtener_pago(self, nro_operacion):
        url = f"https://api.mercadopago.com/v1/payments/{nro_operacion}"
        
        headers = {
            "Content-Type": 'application/json',
            'Authorization': f'Bearer {self.access_token}'
            }
        
        response = requests.get(url=url, headers=headers)
        guardar_json(response.json(), f"obtener_pago_{nro_operacion}.json")
        """
        print(response.status_code)
        # Crear la carpeta si no existe
        folder_path = "OBTENER_PAGOS"
        os.makedirs(folder_path, exist_ok=True)

        # Guardar la respuesta en un archivo JSON en la carpeta
        with open(os.path.join(folder_path, f"{self.id_user}.json"), "w") as json_file:
            json.dump(response.json(), json_file, indent=2)
        print(response.status_code)
        """
        pprint(response.json())
        return response
    
#/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*REEMBOLSOS/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*
    def crear_reembolso(self, id_compra, pago_devolver):
        url = f"https://api.mercadopago.com/v1/payments/{id_compra}/refunds"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Idempotency-Key': f'{uuid.uuid4()}',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        returnload = {
            'amount': pago_devolver
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(returnload))
        guardar_json(response.json(), f"crear_reembolso_{id_compra}.json")
        
        return response
    
    def obtener_reembolso(self, id_pago, id_reembolso):
        url = f"https://api.mercadopago.com/v1/payments/{id_pago}/refunds/{id_reembolso}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(url, headers=headers)
        guardar_json(response.json(), f"obtener_reembolso_{id_pago}.json")
        
        return response.json()
        
    def lista_reembolsos(self, id_compra):
        url = f"https://api.mercadopago.com/v1/payments/{id_compra}/refunds"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(url=url, headers=headers)
        return response.json()
    
    def crear_cancelacion_compra(self, user_id, external_pos_id):
        url = f"https://api.mercadopago.com/instore/qr/seller/collectors/{user_id}/pos/{external_pos_id}/orders"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        returnload = {
            'status': "cancelled"
        }
        
        response = requests.put(url, headers=headers, data=json.dumps(returnload))
        return response.json()
    
    def buscar_pagos(self, id_store, id_pos):
        url = f'https://api.mercadopago.com/v1/payments/search?sort=date_approved&criteria=desc&range=date_created&begin_date=NOW-30DAYS&end_date=NOW&store_id={id_store}&pos_id={id_pos}'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(url, headers=headers)
        
        return response
    
    #*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*CONEXION MP POINT*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*
    
    def obtener_dispositivo_POINT(self, store_id, pos_id):
        url = f"https://api.mercadopago.com/point/integration-api/devices?store_id={store_id}&pos_id={pos_id}&limit=50"
        
        headers = {
            "Content-Type": 'application/json',
            #'x-test-scope': 'sandbox',
            "Authorization": f"Bearer {self.access_token}"
            }
        
        response = requests.get(url, headers=headers)
        return response
    
    def obtener_dispositivo_POINTALL(self,):
        url = f"https://api.mercadopago.com/point/integration-api/devices?&limit=50"
        
        headers = {
            "Content-Type": 'application/json',
            #'x-test-scope': 'sandbox',
            "Authorization": f"Bearer {self.access_token}"
            }
        
        response = requests.get(url, headers=headers)
        return response
    
    def crear_intencion_pago_POINT(self, deviceid, nro_factura, precio, imprime_ticket, TicketNUM):
        url = f"https://api.mercadopago.com/point/integration-api/devices/{deviceid}/payment-intents" 
        
        headers = {
            "Content-Type": 'application/json',
            #'x-test-scope': 'sandbox',
            "Authorization": f"Bearer {self.access_token}"
            }
        
        payload = {
            "additional_info": {
                "external_reference": nro_factura,
                "print_on_terminal": imprime_ticket,
                "ticket_number": TicketNUM
            },
            "amount": precio
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        guardar_json(response.json(), f"crear_intencion_pago_POINT_{nro_factura}.json")
        return response
    
    

    
    
    def cancelar_intencion_pago_POINT(self, deviceid, paymentintentid):
        url = f"https://api.mercadopago.com/point/integration-api/devices/{deviceid}/payment-intents/{paymentintentid}"
        
        headers = {
            "Content-Type": 'application/json',
            #'x-test-scope': 'sandbox',
            "Authorization": f"Bearer {self.access_token}"
            }
        
        response = requests.delete(url, headers=headers)
        return response
    
    def buscar_intencion_pago_POINT(self, paymentintentid):
        url = f"https://api.mercadopago.com/point/integration-api/payment-intents/{paymentintentid}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)  # Agregamos un timeout de 10 segundos
            response.raise_for_status()  # Lanza un error si el código de estado es 4xx o 5xx
            
            # Intentamos convertir la respuesta a JSON
            try:
                guardar_json(response.json(), f"buscar_intencion_pago_POINT_{paymentintentid}.json")
                return response.json()  
            except ValueError:
                print("❌ Error: La respuesta no es un JSON válido")
                return None  # Devolver None si la respuesta no es JSON válido

        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la solicitud: {e}")
            return None  # En caso de error, devolvemos None
    
    def cambiar_modo_operacion(self, device_id, tipo):
        url = f"https://api.mercadopago.com/point/integration-api/devices/{device_id}"
        
        headers = {
            "Content-Type": 'application/json',
            #'x-test-scope': 'sandbox',
            "Authorization": f"Bearer {self.access_token}"
            }
        
        dataload = {
            "operating_mode": tipo
        }
        
        response = requests.patch(url, headers=headers, data=json.dumps(dataload)) 
        return response
    
    def obtener_todos_medios_pagos(self):
        url = "https://api.mercadopago.com/v1/payment_methods"
        
        headers = {
            "Content-Type": 'application/json',
            "Authorization": f"Bearer {self.access_token}"
            }
        
        return requests.get(url, headers=headers)
    
    
def guardar_json(data, nombre_archivo):
    """
    Guarda un diccionario o JSON serializable en F:\Sp\Fac_Elec\Clover\nombre_archivo.
    Crea la carpeta si no existe.

    :param data: dict o JSON serializable
    :param nombre_archivo: nombre del archivo (ej: "salida.json")
    """
    ruta_base = r"F:\Sp\Fac_Elec\MPQRCODE"
    os.makedirs(ruta_base, exist_ok=True)  # Crea la carpeta si no existe

    ruta_archivo = os.path.join(ruta_base, nombre_archivo)

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)