import pypyodbc
import json


def dsn_configurados():
    try:
        # Obtener una lista de DSNs
        dsn_list = pypyodbc.dataSources()
        return dsn_list
    except pypyodbc.Error as ex:
        print("Error al obtener la lista de DSNs:", ex)

class ConexionSybase:
    def __init__(self, **kwargs):
        self.conexion = None
        self.cursor = None
        self.usuario = kwargs["user"]
        self.contrasena = kwargs["password"]
        self.dsn_name = kwargs["dsn"]

    #CONEXION DE LA BASE DE DATOS
    def conectar(self):
        try:
            self.conexion = pypyodbc.connect(
                DSN=self.dsn_name,
                user=self.usuario,
                password=self.contrasena,
                Driver="{Adaptive Server Anywhere 9.0}",                
            )
            self.cursor = self.conexion.cursor()  # Crea el cursor
            return True
        except pypyodbc.Error as err:
            print(f"Error al conectar a Sybase: {err}")
            return False
        
    def conectarServer(self):
        try:
            self.conexion = pypyodbc.connect(
                DSN=self.dsn_name,  # Nombre del DSN configurado en tu sistema
                user=self.usuario,
                password=self.contrasena,
                Driver="{Adaptive Server Anywhere 9.0}"                
            )
            self.cursor = self.conexion.cursor()  # Crea el cursor
            return True
        except pypyodbc.Error as err:
            print(f"Error al conectar a Sybase: {err}")
            return False
        
        
    #MANEJO A LA BASE DE DATOS
    def eliminar_base_de_datos(self, nombre_bd):
        try:
            with self.conexion.cursor() as cursor:
                consulta = f"DROP DATABASE {nombre_bd}"
                cursor.execute(consulta)
                print(f"Base de datos '{nombre_bd}' eliminada exitosamente.")
        except pypyodbc.Error as err:
            print(f"Error al eliminar la base de datos: {err}")
            
        
    #MANEJOS DE TABLAS 
    
    def crear_tabla_MPQRCODE_CONEXIONSERVIDORAPI(self):
        try:
            self.conectar()
            query = f"""
                CREATE TABLE MPQRCODE_CONEXIONSERVIDORAPI (
                    id INT PRIMARY KEY NOT NULL,
                    status VARCHAR(15),
                    ultima_actualizacion VARCHAR(30)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print(f'Tabla MPQRCODE_CONEXIONSERVIDORAPI creada con éxito.')
        except Exception as e:
            print(f'Error al crear la tabla: {e}')
        finally:
            self.desconectar()   
    
    def crear_tabla_MPQRCODE_CONEXIONPROGRAMAS(self):
        try:
            self.conectar()
            query = f"""
                CREATE TABLE MPQRCODE_CONEXIONPROGRAMAS (
                    nro_factura VARCHAR(16),
                    tipo_factura INT,
                    monto_pagar MONEY,
                    status BIT,
                    response FLOAT,
                    description VARCHAR(255),
                    tipo_point INT,
                    IDMercadoPago VARCHAR(255),
                    NOMCAJA VARCHAR(255),
                    NUMCAJERO VARCHAR(255),
                    NOMBRECAJERO VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print(f'Tabla MPQRCODE_CONEXIONPROGRAMAS creada con éxito.')
        except Exception as e:
            print(f'Error al crear la tabla: {e}')
        finally:
            self.desconectar()
    
    def crear_tabla_MPQRCODE_CLIENTE(self):
        try:
            self.conectar()
            query = f"""
                CREATE TABLE MPQRCODE_CLIENTE (
                    idINCREMENT INT IDENTITY PRIMARY KEY,
                    idUSER VARCHAR(255),
                    AUTH_TOKEN VARCHAR(255),
                    AUTH_TOKENPOINT VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print(f'Tabla MPQRCODE_CLIENTE creada con éxito.')
        except Exception as e:
            print(f'Error al crear la tabla: {e}')
        finally:
            self.desconectar()

    def crear_tabla_MPQRCODE_SUCURSAL(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_SUCURSAL (
                    idINCREMENT INT IDENTITY PRIMARY KEY, 
                    id VARCHAR(255), 
                    name VARCHAR(255), 
                    date_creation VARCHAR(255),
                    external_id VARCHAR(255),
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_SUCURSAL creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_SUCURSAL_business_hours(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_SUCURSAL_business_hours (
                    idSUC VARCHAR(255),
                    DIA VARCHAR(255),
                    open_business_hours VARCHAR(255),
                    close_business_hours VARCHAR(255)                    
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_SUCURSAL creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_SUCURSAL_location(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_SUCURSAL_location (
                    idSUC VARCHAR(255),
                    address_line VARCHAR(255),
                    reference_location VARCHAR(255),
                    latitude FLOAT,
                    longitude FLOAT,
                    id VARCHAR(255),
                    type VARCHAR(255),
                    city VARCHAR(255),
                    state_id VARCHAR(255)                    
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_SUCURSAL creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
        
    
    def crear_tabla_MPQRCODE_CAJAS(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_CAJAS (
                    idINCREMENT INT IDENTITY PRIMARY KEY, 
                    id BIGINT, 
                    status VARCHAR(255), 
                    date_created VARCHAR(255), 
                    date_last_updated VARCHAR(255), 
                    uuid VARCHAR(255), 
                    user_id BIGINT, 
                    name VARCHAR(255), 
                    fixed_amount VARCHAR(255), 
                    category BIGINT, 
                    store_id VARCHAR(255), 
                    external_store_id VARCHAR(255), 
                    external_id VARCHAR(255), 
                    site VARCHAR(255), 
                    qr_code VARCHAR(255),
                    picture_url VARCHAR(255),
                    IPN_url VARCHAR(255)
                ) 
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_CAJAS creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_CAJAS_qr(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_CAJAS_qr (
                    id_POS BIGINT,
                    external_id VARCHAR(255),
                    image VARCHAR(255),
                    template_document VARCHAR(255),
                    template_image VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_CAJAS_qr creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_CAJA(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_CAJA (
                    idINCREMENT INT IDENTITY PRIMARY KEY,
                    sucNAME VARCHAR(255),
                    posNAME VARCHAR(255),
                    external_id_pos VARCHAR(255),
                    IPN_url VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_CAJA creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def obtener_nombres_columnas(self, tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Obtener información sobre las columnas de la tabla
                cursor.execute(f"SELECT * FROM {tabla} WHERE 1=0")
                column_info = cursor.description

                # Extraer nombres de las columnas
                nombres_columnas = [column[0] for column in column_info]

                return nombres_columnas
        except pypyodbc.Error as err:
            print(f"Error al obtener nombres de columnas: {err}")
            return None
        finally:
            self.desconectar()

            
    #----------------------------------------------------TABLAS QUE TRABAJAN JUNTOSA PARA LA OBTENCIÓN DEL PAGO----------------------------------------------------

    def crear_tabla_MPQRCODE_CREARORDEN(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_CREARORDEN (
                    idINCREMENT INT IDENTITY, 
                    date_creation DATETIME,
                    external_reference VARCHAR(255) PRIMARY KEY,
                    external_idPOS VARCHAR(255),
                    id VARCHAR(255),
                    collector_id BIGINT, 
                    collector VARCHAR(255), 
                    total_amount FLOAT, 
                    amount FLOAT, 
                    operation_type VARCHAR(255),
                    marketplace VARCHAR(255), 
                    marketplace_fee VARCHAR(255), 
                    sponsor_id BIGINT, 
                    notification_url VARCHAR(255), 
                    expiration_date_to VARCHAR(255),                    
                    expires VARCHAR(255), 
                    additional_info VARCHAR(255), 
                    site_id VARCHAR(255), 
                    client_id BIGINT, 
                    processing_modes VARCHAR(255),
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_CREARORDEN creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_CREARORDEN_items(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_CREARORDEN_items (
                    external_reference VARCHAR(255),
                    idMERCADERIA VARCHAR(255),
                    category_id VARCHAR(255),
                    title VARCHAR(255),
                    quantity BIGINT,
                    currency_id VARCHAR(255),
                    unit_price FLOAT,
                    description VARCHAR(255),
                    picture_url VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_CREARORDEN_items creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_RESPUESTAPOST(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_RESPUESTAPOST (
                    action VARCHAR(255), 
                    api_version VARCHAR(255), 
                    data VARCHAR(255) PRIMARY KEY, 
                    date_created VARCHAR(255), 
                    id BIGINT, 
                    live_mode VARCHAR(255), 
                    type VARCHAR(255), 
                    user_id VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_RESPUESTAPOST creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_RESPUESTAPOSTPOINT(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_RESPUESTAPOSTPOINT (
                    action VARCHAR(255), 
                    api_version VARCHAR(255), 
                    data VARCHAR(255) PRIMARY KEY, 
                    date_created VARCHAR(255), 
                    id BIGINT, 
                    live_mode VARCHAR(255), 
                    type VARCHAR(255), 
                    user_id VARCHAR(255)                    
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_RESPUESTAPOSTPOINT creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def crear_tabla_MPQRCODE_OBTENERPAGO(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_OBTENERPAGO (
                    external_reference VARCHAR(255),
                    external_idPOS VARCHAR(255),
                    collector_id BIGINT, 
                    coupon_amount BIGINT, 
                    currency_id VARCHAR(255), 
                    date_approved VARCHAR(255), 
                    date_created VARCHAR(255), 
                    date_last_updated VARCHAR(255), 
                    date_of_expiration VARCHAR(255), 
                    deduction_schema VARCHAR(255), 
                    description VARCHAR(255),
                    id BIGINT, 
                    installments INT, 
                    integrator_id VARCHAR(255), 
                    issuer_id VARCHAR(255), 
                    live_mode VARCHAR(255), 
                    marketplace_owner VARCHAR(255), 
                    merchant_account_id VARCHAR(255), 
                    merchant_number VARCHAR(255),
                    order_id VARCHAR(255),
                    order_type VARCHAR(255),
                    payer_id VARCHAR(255),
                    payment_metodo_id VARCHAR(255),
                    payment_metodo_issuer_id VARCHAR(255),
                    payment_metodo_type VARCHAR(255),
                    pos_id  VARCHAR(255), 
                    processing_mode  VARCHAR(255),
                    shipping_amount BIGINT, 
                    sponsor_id  VARCHAR(255), 
                    status  VARCHAR(255), 
                    status_detail  VARCHAR(255), 
                    store_id  VARCHAR(255),
                    taxes_amount BIGINT, 
                    transaction_amount FLOAT, 
                    transaction_amount_refunded FLOAT,
                    net_received_amount FLOAT, 
                    transaction_details_total_paid_amount VARCHAR(255),
                    NomCaja VARCHAR(255),
                    NumCajero VARCHAR(255),
                    NombreCajero VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_OBTENERPAGO creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def recrear_tabla_MPQRCODE_OBTENERPAGO(self): #05-11-24
        try:
            self.conectar()

            # Paso 1: Renombrar la tabla actual a _old
            self.cursor.execute("ALTER TABLE MPQRCODE_OBTENERPAGO RENAME MPQRCODE_OBTENERPAGO_old;")
            self.conexion.commit()

            # Paso 2: Crear la nueva tabla
            self.crear_tabla_MPQRCODE_OBTENERPAGO()

            # Paso 3: Copiar los datos de la tabla antigua a la nueva
            query_copy = """
                INSERT INTO MPQRCODE_OBTENERPAGO (external_reference, external_idPOS, collector_id, coupon_amount, 
                                                currency_id, date_approved, date_created, date_last_updated, 
                                                date_of_expiration, deduction_schema, description, id, installments, 
                                                integrator_id, issuer_id, live_mode, marketplace_owner, 
                                                merchant_account_id, merchant_number, order_id, order_type, payer_id, 
                                                payment_metodo_id, payment_metodo_issuer_id, payment_metodo_type, pos_id, 
                                                processing_mode, shipping_amount, sponsor_id, status, status_detail, 
                                                store_id, taxes_amount, transaction_amount, transaction_amount_refunded,
                                                transaction_details_total_paid_amount, NomCaja, 
                                                NumCajero, NombreCajero)
                SELECT external_reference, external_idPOS, collector_id, coupon_amount, currency_id, date_approved, 
                    date_created, date_last_updated, date_of_expiration, deduction_schema, description, id, 
                    installments, integrator_id, issuer_id, live_mode, marketplace_owner, merchant_account_id, 
                    merchant_number, order_id, order_type, payer_id, payment_metodo_id, payment_metodo_issuer_id, 
                    payment_metodo_type, pos_id, processing_mode, shipping_amount, sponsor_id, status, status_detail, 
                    store_id, taxes_amount, transaction_amount, transaction_amount_refunded, transaction_details_total_paid_amount, NomCaja, NumCajero, NombreCajero 
                FROM MPQRCODE_OBTENERPAGO_old;
            """
            self.cursor.execute(query_copy)
            self.conexion.commit()

            # Paso 4: Eliminar la tabla antigua
            self.cursor.execute("DROP TABLE MPQRCODE_OBTENERPAGO_old;")
            self.conexion.commit()

            print("Tabla MPQRCODE_OBTENERPAGO recreada con éxito.")
        except Exception as e:
            print(f"Error al recrear la tabla: {e}")
        finally:
            self.desconectar()

    
    def crear_tabla_MPQRCODE_OBTENERPAGOPOINT(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_OBTENERPAGOPOINT (
                    external_reference VARCHAR(255),
                    external_idPOS VARCHAR(255),
                    collector_id BIGINT, 
                    coupon_amount BIGINT, 
                    currency_id VARCHAR(255), 
                    date_approved VARCHAR(255), 
                    date_created VARCHAR(255), 
                    date_last_updated VARCHAR(255), 
                    date_of_expiration VARCHAR(255), 
                    deduction_schema VARCHAR(255), 
                    description VARCHAR(255),
                    id BIGINT, 
                    installments INT, 
                    integrator_id VARCHAR(255), 
                    issuer_id VARCHAR(255), 
                    live_mode VARCHAR(255), 
                    marketplace_owner VARCHAR(255), 
                    merchant_account_id VARCHAR(255), 
                    merchant_number VARCHAR(255),
                    order_id VARCHAR(255),
                    order_type VARCHAR(255),
                    payer_id VARCHAR(255),
                    payment_metodo_id VARCHAR(255),
                    payment_metodo_issuer_id VARCHAR(255),
                    payment_metodo_type VARCHAR(255),
                    pos_id  VARCHAR(255), 
                    processing_mode  VARCHAR(255),
                    shipping_amount BIGINT, 
                    sponsor_id  VARCHAR(255), 
                    status  VARCHAR(255), 
                    status_detail  VARCHAR(255), 
                    store_id  VARCHAR(255),
                    taxes_amount BIGINT, 
                    transaction_amount FLOAT, 
                    transaction_amount_refunded FLOAT,
                    net_received_amount FLOAT, 
                    transaction_details_total_paid_amount VARCHAR(255),
                    NomCaja VARCHAR(255),
                    NumCajero VARCHAR(255),
                    NombreCajero VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_OBTENERPAGOPOINT creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
            
    def crear_tabla_MPQRCODE_OBTENERPAGOServer(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_OBTENERPAGOServer (
                    external_reference VARCHAR(255),
                    data VARCHAR(255),
                    collector_id BIGINT, 
                    coupon_amount BIGINT, 
                    currency_id VARCHAR(255), 
                    date_approved VARCHAR(255), 
                    date_created VARCHAR(255), 
                    date_last_updated VARCHAR(255), 
                    date_of_expiration VARCHAR(255), 
                    deduction_schema VARCHAR(255), 
                    description VARCHAR(255),
                    id BIGINT, 
                    installments INT, 
                    integrator_id VARCHAR(255), 
                    issuer_id VARCHAR(255), 
                    live_mode VARCHAR(255), 
                    marketplace_owner VARCHAR(255), 
                    merchant_account_id VARCHAR(255), 
                    merchant_number VARCHAR(255),
                    order_id VARCHAR(255),
                    order_type VARCHAR(255),
                    payer_id VARCHAR(255),
                    payment_metodo_id VARCHAR(255),
                    payment_metodo_issuer_id VARCHAR(255),
                    payment_metodo_type VARCHAR(255),
                    pos_id  VARCHAR(255), 
                    processing_mode  VARCHAR(255),
                    shipping_amount BIGINT, 
                    sponsor_id  VARCHAR(255), 
                    status  VARCHAR(255), 
                    status_detail  VARCHAR(255), 
                    store_id  VARCHAR(255),
                    taxes_amount BIGINT, 
                    transaction_amount FLOAT, 
                    transaction_amount_refunded FLOAT,
                    net_received_amount FLOAT,  
                    transaction_details_total_paid_amount VARCHAR(255),
                    NomCaja VARCHAR(255),
                    NumCajero VARCHAR(255),
                    NombreCajero VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_OBTENERPAGOServer creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    def recrear_tabla_MPQRCODE_OBTENERPAGOServer(self):
        try:
            self.conectar()

            # Paso 1: Renombrar la tabla actual a _old
            self.cursor.execute("ALTER TABLE MPQRCODE_OBTENERPAGOServer RENAME MPQRCODE_OBTENERPAGOServer_old;")
            self.conexion.commit()

            # Paso 2: Crear la nueva tabla
            self.crear_tabla_MPQRCODE_OBTENERPAGOServer()

            # Paso 3: Copiar los datos de la tabla antigua a la nueva
            query_copy = """
                INSERT INTO MPQRCODE_OBTENERPAGOServer (external_reference, data, collector_id, coupon_amount, 
                                                        currency_id, date_approved, date_created, date_last_updated, 
                                                        date_of_expiration, deduction_schema, description, id, 
                                                        installments, integrator_id, issuer_id, live_mode, 
                                                        marketplace_owner, merchant_account_id, merchant_number, 
                                                        order_id, order_type, payer_id, payment_metodo_id, 
                                                        payment_metodo_issuer_id, payment_metodo_type, pos_id, 
                                                        processing_mode, shipping_amount, sponsor_id, status, 
                                                        status_detail, store_id, taxes_amount, transaction_amount, 
                                                        transaction_amount_refunded,
                                                        transaction_details_total_paid_amount, NomCaja, NumCajero, 
                                                        NombreCajero)
                SELECT external_reference, data, collector_id, coupon_amount, currency_id, date_approved, 
                    date_created, date_last_updated, date_of_expiration, deduction_schema, description, id, 
                    installments, integrator_id, issuer_id, live_mode, marketplace_owner, merchant_account_id, 
                    merchant_number, order_id, order_type, payer_id, payment_metodo_id, payment_metodo_issuer_id, 
                    payment_metodo_type, pos_id, processing_mode, shipping_amount, sponsor_id, status, status_detail, 
                    store_id, taxes_amount, transaction_amount, transaction_amount_refunded,
                    transaction_details_total_paid_amount, NomCaja, NumCajero, NombreCajero 
                FROM MPQRCODE_OBTENERPAGOServer_old;
            """
            self.cursor.execute(query_copy)
            self.conexion.commit()

            # Paso 4: Eliminar la tabla antigua
            self.cursor.execute("DROP TABLE MPQRCODE_OBTENERPAGOServer_old;")
            self.conexion.commit()

            print("Tabla MPQRCODE_OBTENERPAGOServer recreada con éxito.")
        except Exception as e:
            print(f"Error al recrear la tabla: {e}")
        finally:
            self.desconectar()

            
    def crear_tabla_MPQRCODE_OBTENERPAGOPOINTServer(self):
        try:
            self.conectar()
            query = """
                CREATE TABLE MPQRCODE_OBTENERPAGOPOINTServer (
                    external_reference VARCHAR(255),
                    data VARCHAR(255),
                    collector_id BIGINT, 
                    coupon_amount BIGINT, 
                    currency_id VARCHAR(255), 
                    date_approved VARCHAR(255), 
                    date_created VARCHAR(255), 
                    date_last_updated VARCHAR(255), 
                    date_of_expiration VARCHAR(255), 
                    deduction_schema VARCHAR(255), 
                    description VARCHAR(255),
                    id BIGINT, 
                    installments INT, 
                    integrator_id VARCHAR(255), 
                    issuer_id VARCHAR(255), 
                    live_mode VARCHAR(255), 
                    marketplace_owner VARCHAR(255), 
                    merchant_account_id VARCHAR(255), 
                    merchant_number VARCHAR(255),
                    order_id VARCHAR(255),
                    order_type VARCHAR(255),
                    payer_id VARCHAR(255),
                    payment_metodo_id VARCHAR(255),
                    payment_metodo_issuer_id VARCHAR(255),
                    payment_metodo_type VARCHAR(255),
                    pos_id  VARCHAR(255), 
                    processing_mode  VARCHAR(255),
                    shipping_amount BIGINT, 
                    sponsor_id  VARCHAR(255), 
                    status  VARCHAR(255), 
                    status_detail  VARCHAR(255), 
                    store_id  VARCHAR(255),
                    taxes_amount BIGINT, 
                    transaction_amount FLOAT, 
                    transaction_amount_refunded FLOAT, 
                    net_received_amount FLOAT,
                    transaction_details_total_paid_amount VARCHAR(255),
                    NomCaja VARCHAR(255),
                    NumCajero VARCHAR(255),
                    NombreCajero VARCHAR(255)
                )
            """
            self.cursor.execute(query)
            self.conexion.commit()
            print("Tabla MPQRCODE_OBTENERPAGOPOINTServer creada con éxito.")
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.desconectar()
            
    #CREAR EXEPCION PARA INSERTAR order del POST ya que en SyBase DICHA PALABRA ESTA RESERVA, EL valor de orden va a ir en ordermp

                
    def mostrar_tablas(self, nombre_bda):
        try:
            with self.conexion.cursor() as cursor:
                consulta = f"""
                    SELECT table_name
                    FROM {nombre_bda}..SYSTABLE
                """
                cursor.execute(consulta)
                filas = cursor.fetchall()

                print("Lista de tablas en la base de datos:")
                for fila in filas:
                    print(fila[0])
        except pypyodbc.Error as err:
            print(f"Error al mostrar las tablas: {err}")
    
    def actualizar_tabla(self, nombre_tabla, columnas_actualizadas):
        try:
            with self.conexion.cursor() as cursor:
                consulta = f"ALTER TABLE {nombre_tabla} {columnas_actualizadas}"
                cursor.execute(consulta)
                print(f"Tabla '{nombre_tabla}' actualizada exitosamente.")
        except pypyodbc.Error as err:
            print(f"Error al actualizar la tabla: {err}")
            
    def verificar_existencia_tabla(self, nombre_tabla):
        try:
            with self.conexion.cursor() as cursor:
                consulta = f"SELECT COUNT(*) FROM SYSTABLE WHERE TABLE_NAME = '{nombre_tabla}'"
                cursor.execute(consulta)
                cantidad = cursor.fetchone()[0]
                return cantidad > 0
        except pypyodbc.Error as err:
            print(f"Error al verificar la existencia de la tabla: {err}")
            return False


    def eliminar_tabla(self, nombre_tabla):
        try:
            if self.conectar():  # Llama a conectar antes de continuar
                if self.verificar_existencia_tabla(nombre_tabla):
                    with self.conexion.cursor() as cursor:
                        consulta = f"DROP TABLE {nombre_tabla}"
                        cursor.execute(consulta)
                        print(f"Tabla '{nombre_tabla}' eliminada exitosamente.")
                else:
                    print(f"La tabla '{nombre_tabla}' no existe en la base de datos.")
            else:
                print("Error al conectar a la base de datos.")
        except pypyodbc.Error as err:
            print(f"Error al eliminar la tabla: {err}")


            
    def limpiar_tabla(self, tabla):
        try:
            self.conectar()

            # Eliminar los datos de la tabla
            with self.conexion.cursor() as cursor:
                consulta_eliminar = f"DELETE FROM {tabla}"
                cursor.execute(consulta_eliminar)
                self.conexion.commit()

            print(f"Tabla '{tabla}' limpiada exitosamente.")
        except pypyodbc.Error as err:
            print(f"Error al limpiar la tabla: {err}")
        finally:
            self.desconectar()
            
    def seleccionar_tabla(self, nombre_tabla):
        try:
            with self.conexion.cursor() as cursor:
                consulta = f"SELECT * FROM {nombre_tabla}"
                cursor.execute(consulta)
                return cursor.fetchall()
                
        except pypyodbc.Error as err:
            print(f"Error al seleccionar la tabla '{nombre_tabla}': {err}")       
            
    def agregar_columna(self, tabla, columna, tipo_dato):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL para agregar la nueva columna
                query = f"ALTER TABLE {tabla} ADD {columna} {tipo_dato}"
                cursor.execute(query)
                self.conexion.commit()
                print(f"Columna '{columna}' agregada exitosamente a la tabla '{tabla}'.")
        except pypyodbc.Error as e:
            print(f"Error al agregar la columna: {e}")
        finally:
            self.desconectar()

    # MANEJO DE DATOS DE UNA TABLA
    
    def insertar_dato_en_tabla(self, nombre_tabla, nombre_columna, id_increment, dato):
        try:
            self.conectar()

            # Verificar si la tabla existe en la base de datos
            if self.verificar_existencia_tabla(nombre_tabla):
                with self.conexion.cursor() as cursor:
                    # Verificar si la columna existe en la tabla
                    consulta_columna = f"SELECT COUNT(*) FROM SYS.SYSCOLUMNS WHERE tname = '{nombre_tabla}' AND cname = '{nombre_columna}'"
                    cursor.execute(consulta_columna)
                    existe_columna = cursor.fetchone()[0] > 0

                    if existe_columna:
                        # Verificar si existe una fila con el idINCREMENT proporcionado
                        consulta_fila = f"SELECT COUNT(*) FROM {nombre_tabla} WHERE idINCREMENT = {id_increment}"
                        cursor.execute(consulta_fila)
                        existe_fila = cursor.fetchone()[0] > 0

                        if existe_fila:
                            # Insertar el dato en la fila correspondiente
                            consulta_insertar = f"UPDATE {nombre_tabla} SET {nombre_columna} = '{dato}' WHERE idINCREMENT = {id_increment}"
                            cursor.execute(consulta_insertar)
                            self.conexion.commit()

                            print(f"Dato '{dato}' insertado en la fila con idINCREMENT={id_increment} en la tabla '{nombre_tabla}'.")
                        else:
                            # Insertar el dato en la fila correspondiente y establecer el idINCREMENT
                            consulta_insertar = f"INSERT INTO {nombre_tabla} ({nombre_columna}) VALUES ('{dato}')"
                            cursor.execute(consulta_insertar)
                            self.conexion.commit()

                            # Obtener el idINCREMENT recién asignado
                            consulta_id = f"SELECT @@IDENTITY"
                            cursor.execute(consulta_id)
                            id_increment_nuevo = cursor.fetchone()[0]

                            print(f"Dato '{dato}' insertado en la fila con idINCREMENT={id_increment_nuevo} en la tabla '{nombre_tabla}'.")
                    else:
                        print(f"No existe la columna '{nombre_columna}' en la tabla '{nombre_tabla}'.")
            else:
                print(f"No existe la tabla '{nombre_tabla}' en la base de datos.")
        except pypyodbc.Error as err:
            print(f"Error al insertar dato en la tabla: {err}")
        finally:
            self.desconectar()



    
    
    def insertar_datos_obtener_idINCREMENT(self, tabla, datos):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL de inserción
                columnas = ", ".join([f'"{col}"' for col in datos.keys()])
                valores = ", ".join([f"'{v}'" if not isinstance(v, dict) else f"'{json.dumps(v)}'" for v in datos.values()])
                consulta_insert = f'INSERT INTO {tabla} ({columnas}) VALUES ({valores})'
                cursor.execute(consulta_insert)
                self.conexion.commit()

                # Obtener el valor autoincremental de la fila recién insertada
                consulta_id = f'SELECT @@IDENTITY'
                cursor.execute(consulta_id)
                id_increment_insertado = cursor.fetchone()[0]

                print(f"Datos insertados en la tabla '{tabla}' exitosamente. idINCREMENT: {id_increment_insertado}")

                return id_increment_insertado
        except pypyodbc.Error as err:
            print(f"Error al insertar datos: {err}")
            return None
        finally:
            self.desconectar()
            
    def insertar_datos_o_actualizar(self, tabla, datos):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Reemplazar cualquier valor de 'None' como cadena por None en el diccionario
                #datos = {k: (None if v == 'None' else v) for k, v in datos.items()}

                # Comprobar si el external_reference ya existe
                external_reference = datos.get('external_reference')
                consulta_existente = f"SELECT COUNT(*) FROM {tabla} WHERE external_reference = '{external_reference}'"
                cursor.execute(consulta_existente)
                existe = cursor.fetchone()[0] > 0

                if existe:
                    # Si existe, realizar un UPDATE con los valores formateados
                    set_clause = ", ".join([f"{col} = '{v}'" if v is not None else f"{col} = NULL" for col, v in datos.items()])
                    consulta_update = f"UPDATE {tabla} SET {set_clause} WHERE external_reference = '{external_reference}'"
                    print("Consulta UPDATE:", consulta_update)
                    cursor.execute(consulta_update)
                    print("Datos actualizados con éxito.")
                else:
                    # Si no existe, construir el INSERT con los valores formateados
                    columnas = ", ".join([f"{col}" for col in datos.keys()])
                    valores = ", ".join([f"'{v}'" if v is not None else "NULL" for v in datos.values()])
                    consulta_insert = f'INSERT INTO {tabla} ({columnas}) VALUES ({valores})'
                    print("Consulta INSERT:", consulta_insert)
                    cursor.execute(consulta_insert)
                    print("Datos insertados con éxito.")
                
                self.conexion.commit()
            return True
        except pypyodbc.Error as err:
            print(f"Error al insertar o actualizar datos: {err}")
            return False
        finally:
            self.desconectar()


            
    """def insertar_datos_o_actualizar(self, tabla, datos):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Comprobar si el external_reference ya existe
                external_reference = datos.get('external_reference')
                consulta_existente = f"SELECT COUNT(*) FROM {tabla} WHERE external_reference = '{external_reference}'"
                cursor.execute(consulta_existente)
                existe = cursor.fetchone()[0] > 0
                print(existe)
                
                if existe:
                    # Si existe, realizar un UPDATE
                    set_clause = ", ".join([f'"{col}" = ?' for col in datos.keys()])
                    consulta_update = f"UPDATE {tabla} SET {set_clause} WHERE external_reference = '{external_reference}'"
                    print(consulta_update)
                    valores_update = list(datos.values())
                    cursor.execute(consulta_update, valores_update)
                    print("Datos actualizados con éxito.")
                else:
                    # Si no existe, realizar un INSERT
                    columnas = ", ".join([f"{col}" for col in datos.keys()])
                    valores = ", ".join(['?' for _ in datos.values()])
                    print("Columnas:", columnas)
                    print("Valores:", list(datos.values()))
                    consulta_insert = f'INSERT INTO {tabla} ({columnas}) VALUES ({valores})'
                    print(consulta_insert)
                    cursor.execute(consulta_insert, list(datos.values()))
                    print("Datos insertados con éxito.")

                
                self.conexion.commit()
            return True
        except pypyodbc.Error as err:
            print(f"Error al insertar o actualizar datos: {err}")
            return False
        finally:
            self.desconectar()"""

            
    """def insertar_datos_o_actualizar(self, tabla, datos):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Comprobar si el external_reference ya existe
                external_reference = datos.get('external_reference')
                consulta_existente = f"SELECT COUNT(*) FROM {tabla} WHERE external_reference = '{external_reference}'"
                cursor.execute(consulta_existente, (external_reference,))
                existe = cursor.fetchone()[0] > 0
                print(existe)
                
                if existe:
                    # Si existe, realizar un UPDATE
                    set_clause = ", ".join([f'"{col}" = ?' for col in datos.keys()])
                    consulta_update = f"UPDATE {tabla} SET {set_clause} WHERE external_reference = '{external_reference}'"
                    valores_update = list(datos.values()) + [external_reference]
                    cursor.execute(consulta_update, valores_update)
                    print("Datos actualizados con éxito.")
                else:
                    # Si no existe, realizar un INSERT
                    columnas = ", ".join([f'"{col}"' for col in datos.keys()])
                    valores = ", ".join(['?' for _ in datos.values()])
                    consulta_insert = f'INSERT INTO {tabla} ({columnas}) VALUES ({valores})'
                    cursor.execute(consulta_insert, list(datos.values()))
                    print("Datos insertados con éxito.")
                
                self.conexion.commit()
            return True
        except pypyodbc.Error as err:
            print(f"Error al insertar o actualizar datos: {err}")
            return False
        finally:
            self.desconectar()"""


    def insertar_datos_sin_obtener_id(self, tabla, datos):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL de inserción
                columnas = ", ".join([f'"{col}"' for col in datos.keys()])
                valores = ", ".join([f"'{v}'" if not isinstance(v, dict) else f"'{json.dumps(v)}'" for v in datos.values()])
                consulta_insert = f'INSERT INTO {tabla} ({columnas}) VALUES ({valores})'
                cursor.execute(consulta_insert)
                self.conexion.commit()
            return True
        except pypyodbc.Error as err:
            print(f"Error al insertar datos: {err}")
            return False
        finally:
            self.desconectar()
            
    def borrar_datos_tabla(self, tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL para borrar todos los datos de la tabla
                consulta_delete = f'DELETE FROM {tabla}'
                cursor.execute(consulta_delete)
                self.conexion.commit()

                print(f"Todos los datos de la tabla '{tabla}' han sido eliminados exitosamente.")

        except pypyodbc.Error as err:
            print(f"Error al borrar los datos de la tabla '{tabla}': {err}")
        finally:
            self.desconectar()
            
    def eliminar_filas_por_condicion(self, nombre_tabla, nombre_columna, valor_condicion):
        try:
            self.conectar()
            if not self.conexion:
                print("No se pudo establecer la conexión con la base de datos.")
                return

            with self.conexion.cursor() as cursor:
                # Construir la consulta DELETE
                query = f"DELETE FROM {nombre_tabla} WHERE {nombre_columna} = {valor_condicion}"
                cursor.execute(query)
                self.conexion.commit()
                print(f"Filas eliminadas donde {nombre_columna} = {valor_condicion}")
        
        except pypyodbc.Error as e:
            print(f"Error al ejecutar la consulta DELETE: {e}")
        
        finally:
            self.desconectar()
            
            
    def eliminar_filas_repetidas_por_condicion(self, nombre_tabla, nombre_columna, valor_condicion):
        try:
            self.conectar()
            if not self.conexion:
                print("No se pudo establecer la conexión con la base de datos.")
                return

            with self.conexion.cursor() as cursor:
                # Obtener el ID de una fila que coincida con la condición
                select_query = f"SELECT id FROM {nombre_tabla} WHERE {nombre_columna} = {valor_condicion} ORDER BY id LIMIT 1"
                cursor.execute(select_query)
                fila_mantener = cursor.fetchone()
                
                if fila_mantener:
                    id_mantener = fila_mantener[0]
                    # Construir la consulta DELETE para eliminar todas las filas excepto la seleccionada
                    delete_query = f"DELETE FROM {nombre_tabla} WHERE id != ? AND {nombre_columna} = ?"
                    cursor.execute(delete_query, (id_mantener, valor_condicion))
                    self.conexion.commit()
                    print(f"Filas eliminadas donde {nombre_columna} = {valor_condicion}, excepto la fila con id = {id_mantener}")
                else:
                    print(f"No se encontraron filas donde {nombre_columna} = {valor_condicion}")

        except pypyodbc.Error as e:
            print(f"Error al ejecutar la consulta DELETE: {e}")
        
        finally:
            self.desconectar()

            
    def tabla_vacia(self, tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL para verificar si la tabla está vacía
                consulta_select = f'SELECT COUNT(*) FROM {tabla}'
                cursor.execute(consulta_select)
                resultado = cursor.fetchone()

                # Si la tabla está vacía (no hay filas), retorna True, de lo contrario, retorna False
                return resultado[0] == 0

        except pypyodbc.Error as err:
            print(f"Error al verificar si la tabla '{tabla}' está vacía: {err}")
            return False  # Retorna False en caso de error
        finally:
            self.desconectar()

            
    def actualizar_datos(self, tabla, datos, condicion):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL de actualización
                asignaciones = ", ".join([f'"{col}" = \'{v}\'' if not isinstance(v, dict) else f'"{col}" = \'{json.dumps(v)}\'' for col, v in datos.items()])
                consulta_update = f'UPDATE {tabla} SET {asignaciones} WHERE idINCREMENT = {condicion}'
                cursor.execute(consulta_update)
                self.conexion.commit()

                print(f"Datos actualizados en la tabla '{tabla}' exitosamente.")

        except pypyodbc.Error as err:
            print(f"Error al actualizar datos: {err}")
        finally:
            self.desconectar()
            
    def actualizar_datos_condicion(self, tabla, datos, condicion, valor_condicion):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL de actualización
                asignaciones = ", ".join([f'"{col}" = \'{v}\'' if not isinstance(v, dict) else f'"{col}" = \'{json.dumps(v)}\'' for col, v in datos.items()])
                consulta_update = f'UPDATE {tabla} SET {asignaciones} WHERE {condicion} = {valor_condicion}'
                cursor.execute(consulta_update)
                self.conexion.commit()

                print(f"Datos actualizados en la tabla '{tabla}' exitosamente.")

        except pypyodbc.Error as err:
            print(f"Error al actualizar datos: {err}")
        finally:
            self.desconectar()
            
    def actualizar_datos_condicionID(self, tabla, datos, condicion1, valor_condicion1, condicion2, valor_condicion2):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Construir la consulta SQL de actualización
                asignaciones = ", ".join([f'"{col}" = \'{v}\'' if not isinstance(v, dict) else f'"{col}" = \'{json.dumps(v)}\'' for col, v in datos.items()])
                consulta_update = f'UPDATE {tabla} SET {asignaciones} WHERE {condicion1} = \'{valor_condicion1}\' AND {condicion2} = \'{valor_condicion2}\''
                cursor.execute(consulta_update)
                self.conexion.commit()

                print(f"Datos actualizados en la tabla '{tabla}' exitosamente.")

        except pypyodbc.Error as err:
            print(f"Error al actualizar datos: {err}")
        finally:
            self.desconectar()


    def actualizar_todos_valores_columna(self, tabla, columna, nuevo_valor):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Obtener todos los valores actuales de la columna
                cursor.execute(f'SELECT {columna} FROM {tabla}')
                valores_actuales = cursor.fetchall()

                # Construir la consulta UPDATE para establecer todos los valores de la columna a un nuevo valor
                if isinstance(nuevo_valor, str):
                    # Si el nuevo valor es una cadena, envolverlo entre comillas simples
                    nuevo_valor = f"'{nuevo_valor}'"

                consulta_update = f'UPDATE {tabla} SET {columna} = {nuevo_valor}'

                # Ejecutar la consulta con pypyodbc
                cursor.execute(consulta_update)

                # Hacer commit para aplicar los cambios
                self.conexion.commit()

                print(f'Todos los valores de la columna "{columna}" en la tabla "{tabla}" actualizados exitosamente.')

        except pypyodbc.Error as err:
            print(f"Error al actualizar todos los valores de la columna: {err}")
        finally:
            self.desconectar()




#/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/ INSERTAR DATOS DE SUCURSAL #/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/
    def inicializar_tabla_MPQRCODE_SUCURSAL(self, id):
        datos = {
            'id': id
        }
        id_incrementado = self.insertar_datos_obtener_idINCREMENT("MPQRCODE_SUCURSAL", datos)
        return id_incrementado

    def inicializar_tablas_OBTIENEidINCREMENT(self, tabla, columna_inicial ,datos_inicializar):
        datos = {
            columna_inicial: datos_inicializar
        }
        id_incrementado = self.insertar_datos_obtener_idINCREMENT(tabla, datos)
        return id_incrementado
    
    def insertar_datos_MPQRCODE_SUCURSAL_business_hours(self, idSUC, dia, open, close):
        datos = {
            'idSUC' : idSUC,
            'DIA' : dia,
            'open_business_hours' : open,
            'close_business_hours' : close
        }        
        self.insertar_datos_sin_obtener_id("MPQRCODE_SUCURSAL_business_hours", datos)
        
    def insertar_datos_MPQRCODE_SUCURSAL_location(self, idSUC, address_line, reference, latitude, longitude, id_location, type_location, city, state_id):
        datos = {
            "idSUC" : idSUC,
            'address_line': address_line,
            'reference_location': reference,
            'latitude': latitude,
            'longitude': longitude,
            'id': id_location,
            'type': type_location,
            'city': city,
            'state_id': state_id
        }
        self.insertar_datos_sin_obtener_id("MPQRCODE_SUCURSAL_location", datos)
        
        
        
#/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/ INSERTAR DATOS DE CAJAS #/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/
    def inicializar_tabla_MPQRCODE_CAJAS(self, id):
        datos = {
            'id': id
        }
        id_incrementado = self.insertar_datos_obtener_idINCREMENT("MPQRCODE_CAJAS", datos)
        return id_incrementado
    
    """
    def insertar_datos_MPQRCODE_CAJAS(self, id_POS, status, date_created, date_last_updated, uuid, user_id, name, fixed_amount, category, store_id, external_store_id, external_id, site, qr_code):
        datos = {
            'id' : id_POS,
            'status' : status,
            'date_created' : date_created,
            'date_last_updated': date_last_updated,
            'uuid' : uuid,
            'user_id': user_id,
            'name': name,
            'fixed_amount': fixed_amount,
            'category': category,
            'store_id': store_id,
            'external_store_id': external_store_id,
            'external_id': external_id,
            'site': site,
            'qr_code': qr_code            
        }
        self.insertar_datos_sin_obtener_id("MPQRCODE_CAJAS", datos)
        """
        
    def insertar_datos_MPQRCODE_CAJAS_qr(self, id_pos, image, template_document, template_image):
        datos = {
            'id_POS' : id_pos,
            'image': image,
            'template_document': template_document,
            'template_image': template_image
        }
        
        self.insertar_datos_sin_obtener_id("MPQRCODE_CAJAS_qr", datos)
        
    def insertar_datos_MPQRCODE_CAJAS_qrFALTANTE(self, external_id, id_POS):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                query = f"UPDATE MPQRCODE_CAJAS_qr SET external_id = '{external_id}' WHERE id_POS = '{id_POS}'"
                cursor.execute(query)
                self.conexion.commit()
                print("external_ID ACTUALIZADO")
        except pypyodbc.Error as err:
            print(f"Error al actualizar external_id: {err}")
        finally:
            self.desconectar()
            

    """
    #PRUEBAS QUE YA NO SE USAN
    def insertar_datos_MERCHANT(self, FECHA_CREACION, NRO_FACTURA, PUNTO_VENTA):
        datos = {
            'FECHA_CREACION': FECHA_CREACION,
            'NRO_FACTURA': NRO_FACTURA,
            'PUNTO_VENTA': PUNTO_VENTA
        }
        self.insertar_datos('MERCHANTORDEN', datos)
        
    def insertar_datos_MERCHANTPAGO(self, FECHA_CREACION, ID_PAGO):
        datos = {
            'FECHA_CREACION': FECHA_CREACION,
            'ID_PAGO': ID_PAGO,
        }
        self.insertar_datos('MERCHANTPAGO', datos)
    """            
    def actualizar_id_pago_MERCHANTORDEN(self, factura, POS, fecha_pago, ID_PAGO):
        try:
            self.conectar()

            # Verificar si existe una fila con la combinación de NRO_FACTURA y PUNTO_VENTA
            if self.existe_fila(factura, POS):
                with self.conexion.cursor() as cursor:
                    # Ejecutar la consulta para actualizar el ID_PAGO
                    query = f"UPDATE MERCHANTORDEN SET FECHA_PAGO = '{fecha_pago}', ID_PAGO = '{ID_PAGO}' WHERE NRO_FACTURA = '{factura}' AND PUNTO_VENTA = '{POS}'"
                    cursor.execute(query)
                    self.conexion.commit()

                    print(f"ID_PAGO actualizado exitosamente para la factura {POS}.")
            else:
                print(f"No se encontró una fila con NRO_FACTURA='{factura}' y PUNTO_VENTA='{POS}' en la base de datos.")
        except pypyodbc.Error as err:
            print(f"Error al actualizar ID_PAGO: {err}")
        finally:
            self.desconectar()
            
    def actualizar_hs_pago(self, factura, POS, fecha_creacion):
        try:
            self.conectar()

            # Verificar si existe una fila con la combinación de NRO_FACTURA y PUNTO_VENTA
            if self.existe_fila(factura, POS):
                with self.conexion.cursor() as cursor:
                    # Ejecutar la consulta para actualizar el ID_PAGO
                    query = f"UPDATE MERCHANTORDEN SET FECHA_CREACION = '{fecha_creacion}' WHERE NRO_FACTURA = '{factura}' AND PUNTO_VENTA = '{POS}'"
                    cursor.execute(query)
                    self.conexion.commit()

                    print(f"FECHA_CREACION actualizado exitosamente para la factura {POS}.")
            else:
                print(f"No se encontró una fila con NRO_FACTURA='{factura}' y PUNTO_VENTA='{POS}' en la base de datos.")
        except pypyodbc.Error as err:
            print(f"Error al actualizar FECHA_CREACION: {err}")
        finally:
            self.desconectar()

    def existe_fila(self, numero_factura, punto_venta):
        try:
            with self.conexion.cursor() as cursor:
                # Ejecutar la consulta para verificar la existencia de la fila
                query = f"SELECT 1 FROM MERCHANTORDEN WHERE NRO_FACTURA = '{numero_factura}' AND PUNTO_VENTA = '{punto_venta}'"
                cursor.execute(query)

                # Obtener el resultado de la consulta
                resultado = cursor.fetchone()

                # Si se encontró un resultado, la fila existe
                return resultado is not None
        except pypyodbc.Error as err:
            print(f"Error al verificar la existencia de la fila: {err}")
            return False

    
    # MANEJO DE OBTENCIOS DE DATOS DE UNA TABLA
    def obtener_id_compra(self, resultado_id_orden):
        try:
            self.conectar()  # Asegúrate de conectar antes de ejecutar la consulta

            with self.conexion.cursor() as cursor:
                # Obtener el resultado de la consulta

                query = f"SELECT data FROM MPQRCODE_OBTENERPAGOServer WHERE external_reference = '{resultado_id_orden}'"
                cursor.execute(query)

                # Obtener el resultado de la consulta
                resultado = cursor.fetchone()
                
                if resultado is not None:
                    # Si se encontró un resultado, devolver el ID de compra y ID_PAGO
                    id_pago = resultado
                    print(f"ID_PAGO: {id_pago}")
                    return id_pago
                else:
                    # Si no se encontró ninguna coincidencia, devolver None
                    print(f"TODAVIA NO SE HA RECIBIDO ID DE PAGO...")
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener el ID de compra: {err}")
            return None
        finally:
            self.desconectar()  # Asegúrate de desconectar incluso si hay un error
            
    def obtener_todos_los_name(self, tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                query = f"SELECT name FROM {tabla}"
                cursor.execute(query)
                resultados = cursor.fetchall()
                return [resultado[0] for resultado in resultados]
        except Exception as e:
            print(f"Error al obtener los names: {e}")
        finally:
            self.desconectar()
            
            
    def obtener_todos_los_external_id(self, tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                query = f"SELECT external_id FROM {tabla}"
                cursor.execute(query)
                resultados = cursor.fetchall()
                return [resultado[0] for resultado in resultados]
        except Exception as e:
            print(f"Error al obtener los external_ids: {e}")
        finally:
            self.desconectar()
            

    def obtener_valor_id_por_idINCREMENT(self, idINCREMENT, nombre_tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'idINCREMENT'
                query = f"SELECT id FROM {nombre_tabla} WHERE idINCREMENT = {idINCREMENT}"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None:
                    id_valor = resultado[0]
                    print(f"Valor de 'id' para idINCREMENT={idINCREMENT}: {id_valor}")
                    return id_valor
                else:
                    print(f"No se encontró una fila con idINCREMENT={idINCREMENT}.")
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'id': {err}")
            return None
        finally:
            self.desconectar()
            
    def obtener_valor_external_idPOS_por_idINCREMENT(self, idINCREMENT, nombre_tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'idINCREMENT'
                query = f"SELECT external_id FROM {nombre_tabla} WHERE idINCREMENT = {idINCREMENT}"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None:
                    id_valor = resultado[0]
                    print(f"Valor de 'external_id' para external_id={idINCREMENT}: {id_valor}")
                    return id_valor
                else:
                    print(f"No se encontró una fila con external_id={idINCREMENT}.")
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'external_id': {err}")
            return None
        finally:
            self.desconectar()
            
    def obtener_valor_id_por_external_id(self, external_id, nombre_tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'external_id'
                query = f"SELECT id FROM {nombre_tabla} WHERE external_id = '{external_id}'"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None:
                    id_valor = resultado[0]
                    print(f"Valor de 'id' para external_id={external_id}: {id_valor}")
                    return id_valor
                else:
                    print(f"No se encontró una fila con external_id={external_id}.")
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'id': {err}")
            return None
        
    def specify_search(self, nombre_tabla, nombre_columna, condicion):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'condicion'
                query = f"SELECT {nombre_columna} FROM {nombre_tabla} WHERE idINCREMENT = '{condicion}'"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None:
                    id_valor = resultado[0]
                    return id_valor
                else:
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'id': {err}")
            return None
        
    def specify_search_condicion(self, nombre_tabla, nombre_columna, condicion, valor_condicion, valor_unico):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'condicion'
                query = f"SELECT {nombre_columna} FROM {nombre_tabla} WHERE {condicion} = '{valor_condicion}'"
                cursor.execute(query)
                if valor_unico:
                    resultado = cursor.fetchall()
                else:
                    resultado = cursor.fetchone()

                if resultado is not None and valor_unico == False:
                    id_valor = resultado
                    return id_valor[0]
                elif resultado is not None and valor_unico == True:
                    id_valor = resultado
                    return id_valor
                else:
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'id': {err}")
            return None
        
    def specify_search_columna(self, nombre_tabla, nombre_columna):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'condicion'
                query = f"SELECT {nombre_columna} FROM {nombre_tabla}"
                cursor.execute(query)
                resultado = cursor.fetchall()
                return resultado
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'id': {err}")
            return None
        
    def specify_search_fila(self, nombre_tabla, condicion_columna, condicion_valor):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener todas las filas que cumplan con la condición
                query = f"SELECT * FROM {nombre_tabla} WHERE {condicion_columna} = {condicion_valor}"
                cursor.execute(query)
                resultado = cursor.fetchall()
                return resultado
        except pypyodbc.Error as err:
            print(f"Error al obtener las filas: {err}")
            return None
        
    def specify_search_columna(self, nombre_tabla, nombre_columna):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'condicion'
                consulta = f"SELECT {nombre_columna} FROM {nombre_tabla}"
                cursor.execute(consulta)
                resultado = cursor.fetchall()
                if resultado:
                    lista_nueva = []
                    for i in resultado:
                        lista_nueva.append(i[0])
                    return lista_nueva
                else:
                    return resultado
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'id': {err}")
            return None
        
    def specify_search_condicionID(self, nombre_tabla, nombre_columna, condicion1, valor_condicion1, condicion2, valor_condicion2, valor_unico):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener el valor de la columna 'id' por 'condicion'
                query = f"SELECT {nombre_columna} FROM {nombre_tabla} WHERE {condicion1} = '{valor_condicion1}' AND {condicion2} = '{valor_condicion2}'"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None and valor_unico == False:
                    id_valor = resultado
                    return id_valor[0]
                elif resultado is not None and valor_unico == True:
                    id_valor = resultado
                    return id_valor
                else:
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener el valor de 'id': {err}")
            return None

    def modificar_columna_y_dato_variable(self, nuevo_dato, long):
        print(long)
        try:
            columnas = self.obtener_nombres_columnas('SPDIR')
            print(columnas)
            self.conectar()     
            with self.conexion.cursor() as cursor:
                # Modificar el tamaño de la columna ID a VARCHAR(50)
                cursor.execute(f"ALTER TABLE SPDIR MODIFY id VARCHAR({long})")

                # Actualizar el dato en la columna ID donde GRID == 'mp_programa'
                print(f"UPDATE SPDIR SET ID = '{nuevo_dato}' WHERE GRID = 'mp_programa'")
                
                cursor.execute(f"UPDATE SPDIR SET ID = '{nuevo_dato}' WHERE GRID = 'mp_programa'")
                
                # Confirmar cambios y cerrar la conexión
                self.conexion.commit()
                print("Columna modificada y dato actualizado exitosamente.")
        except pypyodbc.Error as e:
            print("Error:", e)
            self.conexion.rollback()
            self.conexion.close()


        
    def specify_search_all_columns(self, nombre_tabla, condicion, valor_condicion):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener todos los valores de las columnas por 'condicion'
                query = f"SELECT * FROM {nombre_tabla} WHERE {condicion} = '{valor_condicion}'"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None:
                    # Convertir la fila de resultado a una lista
                    valores = list(resultado)
                    return valores
                else:
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener los valores de las columnas: {err}")
            return None
        
    def specify_search_all_columns_nocondicion(self, nombre_tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para obtener todos los valores de las columnas por 'condicion'
                query = f"SELECT * FROM {nombre_tabla}"
                cursor.execute(query)
                resultado = cursor.fetchall()

                if resultado is not None:
                    # Convertir la fila de resultado a una lista
                    return resultado
                else:
                    return None
        except pypyodbc.Error as err:
            print(f"Error al obtener los valores de las columnas: {err}")
            return None
        
    def check_existence(self, nombre_tabla, condicion, valor_condicion):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para verificar la existencia de filas que cumplen con la condición
                query = f"SELECT 1 FROM {nombre_tabla} WHERE {condicion} = '{valor_condicion}'"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None:
                    return True  # Existe al menos una fila que cumple con la condición
                else:
                    return False  # No hay filas que cumplan con la condición
        except pypyodbc.Error as err:
            print(f"Error al verificar la existencia de filas: {err}")
            return False
        
    def check_existence2(self, nombre_tabla, condicion, valor_condicion, condicion2, valor_condicion2):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para verificar la existencia de filas que cumplen con la condición
                query = f"SELECT 1 FROM {nombre_tabla} WHERE {condicion} = '{valor_condicion}' AND {condicion2} = '{valor_condicion2}'"
                cursor.execute(query)
                resultado = cursor.fetchone()

                if resultado is not None:
                    return True  # Existe al menos una fila que cumple con la condición
                else:
                    return False  # No hay filas que cumplan con la condición
        except pypyodbc.Error as err:
            print(f"Error al verificar la existencia de filas: {err}")
            return False

    def check_table_existence(self, nombre_tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                # Consulta para verificar la existencia de la tabla en el catálogo de información de la base de datos
                query = f"IF EXISTS (SELECT 1 FROM sysobjects WHERE name = '{nombre_tabla}' AND type = 'U') SELECT 1 ELSE SELECT 0"
                cursor.execute(query)
                resultado = cursor.fetchone()

                return resultado[0] == 1  # True si la tabla existe, False si no existe

        except pypyodbc.Error as err:
            print(f"Error al verificar la existencia de la tabla: {err}")
            return False

        finally:
            self.desconectar()
        
        
    def contar_registros(self, tabla):
        try:
            self.conectar()
            with self.conexion.cursor() as cursor:
                consulta = f'SELECT COUNT(*) FROM {tabla}'
                cursor.execute(consulta)
                resultado = cursor.fetchone()
                return resultado[0] if resultado else 0
        except pypyodbc.Error as err:
            print(f"Error al contar registros en la tabla '{tabla}': {err}")
            return 0
        finally:
            self.desconectar()

#/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/ ELIMINAR DATOS DE CAJAS #/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/
    def eliminar_filas(self, tabla, columna, external_id):
        try:
            # Verifica si la conexión está establecida
            if not self.conexion:
                self.conectar()

            # Utiliza 'with' statement para asegurar el cierre adecuado del cursor
            with self.conexion.cursor() as cursor:
                # Construye y ejecuta la instrucción DELETE con parámetros de consulta
                sql_query = f"DELETE FROM {tabla} WHERE {columna} = '{external_id}'"
                print(f"Ejecutando SQL: {sql_query}")
                cursor.execute(sql_query)
                self.conexion.commit()

                print(f"Filas con external_id {external_id} eliminadas correctamente.")
        except pypyodbc.Error as err:
            print(f"Error: {err}")
        except Exception as e:
            print(f"Error: {e}")
            
    def eliminarOrdenesPostDBA(self):
        try:
            self.eliminar_tabla("MPQRCODE_CREARORDEN")
            self.eliminar_tabla("MPQRCODE_CREARORDEN_items")
            self.eliminar_tabla("MPQRCODE_RESPUESTAPOST")
            self.eliminar_tabla("MPQRCODE_OBTENERPAGO")
            self.crear_tabla_MPQRCODE_CREARORDEN()
            self.crear_tabla_MPQRCODE_CREARORDEN_items()
            self.crear_tabla_MPQRCODE_RESPUESTAPOST()
            self.crear_tabla_MPQRCODE_OBTENERPAGO()
        except Exception as e:
            print(f"Eror: {e}")
            
            
#/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/ FUNCIONES COMPLETAS #/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/

    def crearTablasSERVER(self):
        self.crear_tabla_MPQRCODE_CLIENTE()
        self.crear_tabla_MPQRCODE_SUCURSAL()
        self.crear_tabla_MPQRCODE_SUCURSAL_business_hours()
        self.crear_tabla_MPQRCODE_SUCURSAL_location()
        self.crear_tabla_MPQRCODE_CAJAS()
        self.crear_tabla_MPQRCODE_CAJAS_qr()
        self.crear_tabla_MPQRCODE_OBTENERPAGOServer()
        self.crear_tabla_MPQRCODE_RESPUESTAPOST()
        self.crear_tabla_MPQRCODE_RESPUESTAPOSTPOINT()
        self.crear_tabla_MPQRCODE_OBTENERPAGOPOINTServer()
        
    def eliminarTablasSERVER(self):
        self.eliminar_tabla("MPQRCODE_CLIENTE")
        self.eliminar_tabla("MPQRCODE_CONEXIONSERVIDORAPI")
        self.eliminar_tabla("MPQRCODE_SUCURSAL")
        self.eliminar_tabla("MPQRCODE_SUCURSAL_business_hours")
        self.eliminar_tabla("MPQRCODE_SUCURSAL_location")
        self.eliminar_tabla("MPQRCODE_CAJAS")
        self.eliminar_tabla("MPQRCODE_CAJAS_qr")
        self.eliminar_tabla("MPQRCODE_RESPUESTAPOST")
        self.eliminar_tabla("MPQRCODE_OBTENERPAGOServer")
        self.eliminar_tabla("MPQRCODE_RESPUESTAPOSTPOINT")
        self.eliminar_tabla("MPQRCODE_OBTENERPAGOPOINTServer")
        
        
    def crearTablasPOS(self):
        self.crear_tabla_MPQRCODE_CAJA()
        self.crear_tabla_MPQRCODE_OBTENERPAGO()
        self.crear_tabla_MPQRCODE_OBTENERPAGOPOINT()
        
    def eliminarTablasPOS(self):
        self.eliminar_tabla("MPQRCODE_CAJA")
        self.eliminar_tabla("MPQRCODE_OBTENERPAGO")
        self.eliminar_tabla("MPQRCODE_OBTENERPAGOPOINT")

    # DESCONECTAR DE LA BASE DE DATOS
    def desconectar(self):
        try:
            if self.conexion and self.conexion.connected:
                self.conexion.close()
            else:
                print("La conexión ya estaba cerrada.")
        except pypyodbc.Error as err:
            print(f"Error al cerrar la conexión: {err}")