import logging
import azure.functions as func
import json
import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.data.tables import TableServiceClient, TableEntity
from azure.storage.queue import QueueServiceClient
from datetime import datetime, timedelta
import io
from threading import Timer
import uuid
from dotenv import load_dotenv

# Załaduj zmienne z .env
load_dotenv()

app = func.FunctionApp()

# Konfiguracja Azure Storage
STORAGE_CONNECTION_STRING = os.getenv("AzureWebJobsStorage", "")
CONTAINER_NAME = "uploads"
TABLE_NAME = "FileUploadLogs"

# Zmienne do trackowania schedulowanych zadań
scheduled_logs = []
max_logs = 100

@app.route(route="UploadFile", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    """
    Funkcja do przesyłania pliku do Blob Storage.
    """
    try:
        logging.info('File upload function started.')
        
        # Pobranie pliku z base64 w JSON body
        req_body = req.get_json()
        
        if 'filename' not in req_body or 'content' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing filename or content. Send JSON: {filename, content}"}),
                mimetype="application/json",
                status_code=400
            )
        
        filename = req_body['filename']
        import base64
        file_content = base64.b64decode(req_body['content'])
        
        logging.info(f'Received file: {filename}, size: {len(file_content)} bytes')
        
        # Mock: bez faktycznego upload do Azure (credentials są fake)
        blob_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        response = {
            "success": True,
            "message": "File received and processed",
            "filename": filename,
            "blob_name": blob_name,
            "file_size": len(file_content),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "File upload to Blob Storage requires valid Azure credentials"
        }
        
        logging.info(f'File processed: {blob_name}')
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e), "type": type(e).__name__}),
            mimetype="application/json",
            status_code=500
        )


@app.blob_trigger(arg_name="myblob", path=f"{CONTAINER_NAME}/{{name}}", connection="AzureWebJobsStorage")
def blob_trigger(myblob: func.InputStream):
    """
    Blob Trigger: loguje do Table Storage, gdy plik się pojawi w kontenerze.
    WYŁĄCZONE NA POTRZEBY LOKALNEGO TESTOWANIA - wymaga Azurite
    """
    pass
    # try:
    #     logging.info(f'Blob trigger activated for: {myblob.name}')
    #     logging.info(f'Blob size: {myblob.length} bytes')
    #     
    #     # Inicjalizacja Table Storage
    #     table_service_client = TableServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    #     table_client = table_service_client.get_table_client(table_name=TABLE_NAME)
    #     
    #     # Przygotowanie wpisu do logu
    #     file_log = TableEntity()
    #     file_log.PartitionKey = datetime.utcnow().strftime('%Y%m%d')  # Dzień jako partition key
    #     file_log.RowKey = f"{datetime.utcnow().strftime('%H%M%S')}_{myblob.name}"
    #     file_log.BlobName = myblob.name
    #     file_log.FileSize = myblob.length
    #     file_log.UploadedAt = datetime.utcnow()
    #     file_log.Status = "Uploaded"
    #     
    #     # Zapis do tabeli
    #     table_client.upsert_entity(file_log)
    #     
    #     logging.info(f'Logged file upload: {myblob.name}')
    #     
    # except Exception as e:
    #     logging.error(f'Error in blob trigger: {str(e)}')


@app.route(route="ListFiles", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def list_files(req: func.HttpRequest) -> func.HttpResponse:
    """
    Funkcja do wylistowania wszystkich przesłanych plików.
    """
    try:
        logging.info('List files function started.')
        
        blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        blobs = []
        for blob in container_client.list_blobs():
            blobs.append({
                "name": blob.name,
                "size": blob.size,
                "created": blob.creation_time.isoformat() if blob.creation_time else None
            })
        
        response = {
            "success": True,
            "count": len(blobs),
            "files": blobs
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'Error listing files: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="GetStatus", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do sprawdzenia statusu aplikacji i logów czasowych.
    """
    try:
        status = {
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "upload": "POST /api/UploadFile",
                "list": "GET /api/ListFiles",
                "status": "GET /api/GetStatus",
                "timer_logs": "GET /api/TimerLogs"
            },
            "timer_trigger": "scheduled_task (uruchamiana co minutę lokalnie)"
        }
        return func.HttpResponse(
            json.dumps(status),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="TimerLogs", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_timer_logs(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do przeglądu logów z Timer Trigger.
    """
    try:
        response = {
            "total_executions": len(scheduled_logs),
            "logs": scheduled_logs[-20:] if scheduled_logs else [],  # Ostatnie 20
            "message": "Timer Trigger uruchamia się co minutę"
        }
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


def log_scheduled_execution():
    """
    Funkcja do logowania wykonań - uruchamiana periodycznie.
    """
    global scheduled_logs
    
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "executed_at": timestamp,
        "task_name": "scheduled_task",
        "status": "success"
    }
    
    logging.info(f'[TIMER TRIGGER] Executed at: {timestamp}')
    
    # Dodaj do listy (ogranicz do max_logs)
    scheduled_logs.append(log_entry)
    if len(scheduled_logs) > max_logs:
        scheduled_logs.pop(0)
    
    # Zaplanuj następne wykonanie za 60 sekund
    timer = Timer(60.0, log_scheduled_execution)
    timer.daemon = True
    timer.start()


# Uruchom Timer na starcie aplikacji
log_scheduled_execution()


# ============================================
# DATABASE - ZADANIE 4 - AZURE TABLES
# ============================================

STORAGE_CONNECTION_STRING = os.getenv("AzureWebJobsStorage", "")
PRODUCTS_TABLE_NAME = "products"

def get_table_client():
    """
    Pobierz klienta Azure Tables dla tabeli produktów.
    """
    try:
        table_service_client = TableServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        table_client = table_service_client.get_table_client(table_name=PRODUCTS_TABLE_NAME)
        logging.info(f'[DATABASE] Connected to Azure Table: {PRODUCTS_TABLE_NAME}')
        return table_client
    except Exception as e:
        logging.error(f'[DATABASE] Error connecting to Azure Table: {str(e)}')
        raise

def init_database():
    """
    Inicjalizacja Azure Tables - utwórz tabelę jeśli nie istnieje.
    """
    try:
        table_service_client = TableServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        
        # Utwórz tabelę jeśli nie istnieje
        try:
            table_service_client.create_table_if_not_exists(table_name=PRODUCTS_TABLE_NAME)
            logging.info('[DATABASE] Initialized Azure Table: products')
        except Exception as e:
            logging.info(f'[DATABASE] Table might already exist: {str(e)}')
    except Exception as e:
        logging.error(f'[DATABASE] Error initializing Azure Table: {str(e)}')

# Inicjalizuj bazę przy starcie
init_database()



@app.route(route="SaveProduct", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def save_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do zapisywania produktu do Azure Tables.
    Body: {"name": "...", "description": "...", "price": 99.99, "quantity": 10}
    """
    try:
        req_body = req.get_json()
        
        # Walidacja wymaganych pól
        if 'name' not in req_body or 'price' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: name, price"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Przygotuj dane
        product_id = str(uuid.uuid4())
        name = req_body['name']
        description = req_body.get('description', '')
        price = float(req_body['price'])
        quantity = int(req_body.get('quantity', 0))
        now = datetime.utcnow().isoformat()
        
        # Utwórz encję do Azure Tables (użyj słownika)
        # PartitionKey = typ produktu (default: "product")
        # RowKey = product_id (unikalny)
        product_entity = {
            "PartitionKey": "product",
            "RowKey": product_id,
            "name": name,
            "description": description,
            "price": price,
            "quantity": quantity,
            "created_at": now,
            "updated_at": now
        }
        
        # Zapisz do Azure Tables
        table_client = get_table_client()
        table_client.upsert_entity(entity=product_entity)
        
        logging.info(f'[DATABASE] Saved product to Azure Tables: {product_id}')
        
        response = {
            "success": True,
            "message": "Product saved successfully to Azure Tables",
            "product_id": product_id,
            "name": name,
            "price": price,
            "quantity": quantity,
            "created_at": now
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=201
        )
        
    except Exception as e:
        logging.error(f'[DATABASE] Error saving product: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="GetProducts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_products(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do pobierania wszystkich produktów z Azure Tables.
    """
    try:
        table_client = get_table_client()
        
        # Pobierz wszystkie encje z PartitionKey = "product"
        entities = table_client.query_entities(query_filter="PartitionKey eq 'product'")
        
        products = []
        for entity in entities:
            product = {
                "id": entity.get("RowKey"),
                "name": entity.get("name"),
                "description": entity.get("description"),
                "price": entity.get("price"),
                "quantity": entity.get("quantity"),
                "created_at": entity.get("created_at"),
                "updated_at": entity.get("updated_at")
            }
            products.append(product)
        
        # Sortuj malejąco po created_at
        products.sort(key=lambda x: x['created_at'], reverse=True)
        
        logging.info(f'[DATABASE] Retrieved {len(products)} products from Azure Tables')
        
        response = {
            "success": True,
            "total": len(products),
            "products": products
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'[DATABASE] Error retrieving products: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="GetProduct", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do pobierania konkretnego produktu po ID z Azure Tables.
    Query param: id=<product_id>
    """
    try:
        product_id = req.params.get('id')
        
        if not product_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'id' parameter"}),
                mimetype="application/json",
                status_code=400
            )
        
        table_client = get_table_client()
        
        try:
            entity = table_client.get_entity(partition_key="product", row_key=product_id)
        except Exception as e:
            if "ResourceNotFoundError" in str(type(e).__name__):
                return func.HttpResponse(
                    json.dumps({"error": "Product not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            raise
        
        product = {
            "id": entity.get("RowKey"),
            "name": entity.get("name"),
            "description": entity.get("description"),
            "price": entity.get("price"),
            "quantity": entity.get("quantity"),
            "created_at": entity.get("created_at"),
            "updated_at": entity.get("updated_at")
        }
        
        response = {
            "success": True,
            "product": product
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'[DATABASE] Error retrieving product: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="UpdateProduct", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def update_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do aktualizacji produktu w Azure Tables.
    Body: {"id": "...", "name": "...", "price": 99.99, "quantity": 10}
    """
    try:
        req_body = req.get_json()
        
        if 'id' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'id' field"}),
                mimetype="application/json",
                status_code=400
            )
        
        product_id = req_body['id']
        now = datetime.utcnow().isoformat()
        
        table_client = get_table_client()
        
        # Pobierz istniejący produkt
        try:
            entity = table_client.get_entity(partition_key="product", row_key=product_id)
            # Konwertuj do słownika dla modyfikacji
            entity_dict = dict(entity)
        except Exception as e:
            if "ResourceNotFoundError" in str(type(e).__name__):
                return func.HttpResponse(
                    json.dumps({"error": "Product not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            raise
        
        # Aktualizuj pola jeśli są dostarczone
        if 'name' in req_body:
            entity_dict['name'] = req_body['name']
        if 'description' in req_body:
            entity_dict['description'] = req_body['description']
        if 'price' in req_body:
            entity_dict['price'] = float(req_body['price'])
        if 'quantity' in req_body:
            entity_dict['quantity'] = int(req_body['quantity'])
        
        entity_dict['updated_at'] = now
        
        # Zapisz aktualizacji
        table_client.upsert_entity(entity=entity_dict)
        
        response = {
            "success": True,
            "message": "Product updated successfully",
            "product_id": product_id,
            "updated_at": now
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'[DATABASE] Error updating product: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="DeleteProduct", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do usuwania produktu z Azure Tables.
    Query param: id=<product_id>
    """
    try:
        product_id = req.params.get('id')
        
        if not product_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'id' parameter"}),
                mimetype="application/json",
                status_code=400
            )
        
        table_client = get_table_client()
        
        try:
            table_client.delete_entity(partition_key="product", row_key=product_id)
        except Exception as e:
            if "ResourceNotFoundError" in str(type(e).__name__):
                return func.HttpResponse(
                    json.dumps({"error": "Product not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            raise
        
        response = {
            "success": True,
            "message": "Product deleted successfully",
            "product_id": product_id
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'[DATABASE] Error deleting product: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


# ============================================
# STORAGE QUEUE - ZADANIE 7
# ============================================

QUEUE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=z6storage;AccountKey=66WYyu8jdvy89w1KsZjkbjGD+GpoUGpVwd38+4fVjShPoLoo1D+k2vInhkaefxYrq7DvCBnEJpyl+AStsWpL3A==;EndpointSuffix=core.windows.net"
QUEUE_NAME = "z7-tasks"

@app.route(route="SendToQueue", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def send_to_queue(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do wysyłania wiadomości do Azure Storage Queue.
    Body: {"message": "content", "task_type": "process_file", "priority": "high"}
    """
    try:
        req_body = req.get_json()
        
        if 'message' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'message' field in request body"}),
                mimetype="application/json",
                status_code=400
            )
        
        message_content = req_body['message']
        task_type = req_body.get('task_type', 'generic_task')
        priority = req_body.get('priority', 'normal')
        
        # Przygotuj wiadomość
        queue_message = {
            "id": str(uuid.uuid4()),
            "message": message_content,
            "task_type": task_type,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "status": "queued"
        }
        
        # Połącz z Queue Storage
        logging.info(f'[QUEUE SEND] Creating QueueServiceClient...')
        queue_service_client = QueueServiceClient.from_connection_string(QUEUE_CONNECTION_STRING)
        logging.info(f'[QUEUE SEND] Getting queue client for {QUEUE_NAME}...')
        queue_client = queue_service_client.get_queue_client(QUEUE_NAME)
        
        # Wyślij wiadomość
        logging.info(f'[QUEUE SEND] Sending message with ID: {queue_message["id"]}')
        queue_client.send_message(json.dumps(queue_message))
        logging.info(f'[QUEUE SEND] Message sent successfully: {queue_message["id"]} - {task_type}')
        
        response = {
            "success": True,
            "message": "Task queued successfully",
            "task_id": queue_message["id"],
            "task_type": task_type,
            "priority": priority,
            "queued_at": queue_message["created_at"]
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'[QUEUE SEND] Error sending message: {str(e)}')
        import traceback
        logging.error(f'[QUEUE SEND] Traceback: {traceback.format_exc()}')
        return func.HttpResponse(
            json.dumps({"error": str(e), "type": type(e).__name__}),
            mimetype="application/json",
            status_code=500
        )



# ============================================
# QueueTrigger - Task 7 - Automatyczne przetwarzanie
# ============================================

@app.queue_trigger(arg_name="msg", queue_name=QUEUE_NAME, connection="QueueStorageConnection")
def process_queue_message(msg: func.QueueMessage):
    """
    QueueTrigger: Automatycznie przetwarza wiadomości z Azure Storage Queue.
    Uruchamia się każdorazowo gdy pojawi się nowa wiadomość w kolejce.
    """
    try:
        # Odczytaj zawartość wiadomości
        message_json = msg.get_body()
        
        logging.info(f'[QUEUE TRIGGER] Processing message: {msg.id}')
        logging.info(f'[QUEUE TRIGGER] Content: {message_json}')
        
        # Parsuj JSON
        message_data = json.loads(message_json)
        
        task_id = message_data.get('id')
        task_type = message_data.get('task_type', 'unknown')
        message_content = message_data.get('message')
        priority = message_data.get('priority')
        
        # Logika przetwarzania - zapisz do bazy danych (SQLite dla LOCAL, SQL Database dla AZURE)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Sprawdź czy tabela istnieje
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS queue_tasks (
                    task_id TEXT PRIMARY KEY,
                    message TEXT NOT NULL,
                    task_type TEXT,
                    priority TEXT,
                    status TEXT,
                    created_at TEXT,
                    processed_at TEXT
                )
            ''')
            
            # Zapisz zadanie jako przetworzone
            processed_at = datetime.utcnow().isoformat()
            cursor.execute('''
                INSERT OR REPLACE INTO queue_tasks 
                (task_id, message, task_type, priority, status, created_at, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, message_content, task_type, priority, 'processed', 
                  message_data.get('created_at'), processed_at))
            
            conn.commit()
            conn.close()
            
            logging.info(f'[QUEUE TRIGGER] Task processed successfully: {task_id}')
            logging.info(f'[QUEUE TRIGGER] Task type: {task_type}, Priority: {priority}')
            
        except Exception as db_error:
            logging.error(f'[QUEUE TRIGGER] Database error: {str(db_error)}')
            raise
        
    except json.JSONDecodeError as json_error:
        logging.error(f'[QUEUE TRIGGER] JSON decode error: {str(json_error)}')
        logging.error(f'[QUEUE TRIGGER] Raw message: {msg.get_body()}')
    except Exception as e:
        logging.error(f'[QUEUE TRIGGER] Error processing message: {str(e)}')
        logging.error(f'[QUEUE TRIGGER] Message ID: {msg.id}')





# Nie potrzebny drugi trigger - wystarczy jeden powyżej



@app.route(route="ProcessQueueMessages", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def process_queue_messages_manual(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do ręcznego przetwarzania wiadomości z Azure Storage Queue.
    POST body: {"batch_size": 5} (opcjonalnie)
    """
    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        batch_size = req_body.get('batch_size', 5)
        
        # Połącz z Queue Storage
        queue_service_client = QueueServiceClient.from_connection_string(QUEUE_CONNECTION_STRING)
        queue_client = queue_service_client.get_queue_client(QUEUE_NAME)
        
        processed_count = 0
        errors = []
        
        logging.info(f'[QUEUE MANUAL] Starting batch processing (size: {batch_size})')
        
        # Pobierz wiadomości z kolejki
        for i in range(batch_size):
            try:
                # Pobierz wiadomości
                messages = list(queue_client.receive_messages(max_messages=1, visibility_timeout=30))
                
                if not messages:
                    logging.info(f'[QUEUE MANUAL] No more messages in queue (iteration {i})')
                    break
                
                for message in messages:
                    try:
                        # Parsuj JSON - message.content może być base64 encoded
                        message_content_str = message.content
                        
                        # Spróbuj dekodować z base64 jeśli to konieczne
                        try:
                            import base64
                            decoded = base64.b64decode(message_content_str).decode('utf-8')
                            message_data = json.loads(decoded)
                        except:
                            # Jeśli nie base64, parsuj bezpośrednio
                            message_data = json.loads(message_content_str)
                        
                        task_id = message_data.get('id')
                        task_type = message_data.get('task_type', 'unknown')
                        message_text = message_data.get('message')
                        priority = message_data.get('priority')
                        
                        logging.info(f'[QUEUE MANUAL] Processing task: {task_id} (type: {task_type})')
                        logging.info(f'[QUEUE MANUAL] Message content: {message_text}')
                        
                        # Zapisz do bazy danych
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        
                        # Utwórz tabelę jeśli nie istnieje
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS queue_tasks (
                                task_id TEXT PRIMARY KEY,
                                message TEXT NOT NULL,
                                task_type TEXT,
                                priority TEXT,
                                status TEXT,
                                created_at TEXT,
                                processed_at TEXT
                            )
                        ''')
                        
                        processed_at = datetime.utcnow().isoformat()
                        cursor.execute('''
                            INSERT OR REPLACE INTO queue_tasks 
                            (task_id, message, task_type, priority, status, created_at, processed_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (task_id, message_text, task_type, priority, 'processed',
                              message_data.get('created_at'), processed_at))
                        
                        conn.commit()
                        conn.close()
                        
                        # Usuń wiadomość z kolejki
                        queue_client.delete_message(message.id, message.pop_receipt)
                        
                        logging.info(f'[QUEUE MANUAL] Task processed and deleted from queue: {task_id}')
                        processed_count += 1
                        
                    except Exception as msg_error:
                        logging.error(f'[QUEUE MANUAL] Error processing message: {str(msg_error)}')
                        logging.error(f'[QUEUE MANUAL] Message ID: {message.id if message else "unknown"}')
                        errors.append(str(msg_error))
                        
            except Exception as batch_error:
                logging.error(f'[QUEUE MANUAL] Batch error: {str(batch_error)}')
                break
        
        response = {
            "success": True,
            "message": "Batch processing completed",
            "processed_count": processed_count,
            "requested_batch_size": batch_size,
            "errors": errors if errors else []
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'[QUEUE MANUAL] Error in batch processing: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e), "type": type(e).__name__}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="ClearPoisonQueue", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def clear_poison_queue(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do czyszczenia poison queue.
    """
    try:
        queue_service_client = QueueServiceClient.from_connection_string(QUEUE_CONNECTION_STRING)
        poison_queue_name = f"{QUEUE_NAME}-poison"
        
        try:
            poison_queue_client = queue_service_client.get_queue_client(poison_queue_name)
            
            # Pobierz i usuń wszystkie wiadomości z poison queue
            deleted_count = 0
            while True:
                messages = list(poison_queue_client.receive_messages(max_messages=32))
                if not messages:
                    break
                for message in messages:
                    poison_queue_client.delete_message(message.id, message.pop_receipt)
                    deleted_count += 1
            
            logging.info(f'[POISON QUEUE] Cleared {deleted_count} messages from poison queue')
            
            return func.HttpResponse(
                json.dumps({"success": True, "message": f"Deleted {deleted_count} messages from poison queue"}),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            # Poison queue might not exist
            logging.info(f'[POISON QUEUE] No poison queue found or already empty: {str(e)}')
            return func.HttpResponse(
                json.dumps({"success": True, "message": "Poison queue is empty or doesn't exist"}),
                mimetype="application/json",
                status_code=200
            )
            
    except Exception as e:
        logging.error(f'[POISON QUEUE] Error clearing poison queue: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="DebugQueue", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def debug_queue(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do debugowania - sprawdź co jest w kolejce.
    """
    try:
        queue_service_client = QueueServiceClient.from_connection_string(QUEUE_CONNECTION_STRING)
        queue_client = queue_service_client.get_queue_client(QUEUE_NAME)
        
        # Pobierz liczę wiadomości bez usuwania
        properties = queue_client.get_queue_properties()
        approx_count = properties['approximate_message_count']
        
        # Spróbuj pobierać wiadomości (nie usuwając) z peek
        messages_data = []
        messages = queue_client.peek_messages(max_messages=5)
        for msg in messages:
            messages_data.append({
                "id": msg.id,
                "content_preview": msg.content[:100] if msg.content else None,
                "insertion_time": str(msg.insertion_time) if hasattr(msg, 'insertion_time') else None
            })
        
        response = {
            "queue_name": QUEUE_NAME,
            "approximate_count": approx_count,
            "peek_messages": messages_data
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f'[DEBUG] Error peeking queue: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="GetQueueTasks", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_queue_tasks(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do pobierania wszystkich zadań z queue_tasks tabeli.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Najpierw utwórz tabelę jeśli nie istnieje
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queue_tasks (
                task_id TEXT PRIMARY KEY,
                message TEXT NOT NULL,
                task_type TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT,
                processed_at TEXT
            )
        ''')
        
        cursor.execute('SELECT * FROM queue_tasks ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        tasks = [dict(row) for row in rows]
        
        logging.info(f'[QUEUE] Retrieved {len(tasks)} queue tasks')
        
        response = {
            "success": True,
            "total": len(tasks),
            "tasks": tasks
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'[QUEUE] Error retrieving queue tasks: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


# Inicjalizuj bazę na starcie
init_database()
