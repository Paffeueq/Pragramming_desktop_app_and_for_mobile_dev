import logging
import azure.functions as func
import json
import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.data.tables import TableServiceClient, TableEntity
from datetime import datetime, timedelta
import io
from threading import Timer
import sqlite3
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

@app.route(route="UploadFile", methods=["POST"])
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


@app.route(route="ListFiles", methods=["GET"])
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


@app.route(route="GetStatus", methods=["GET"])
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


@app.route(route="TimerLogs", methods=["GET"])
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
# DATABASE - ZADANIE 4
# ============================================

DB_PATH = "data.db"

def init_database():
    """
    Inicjalizacja bazy danych SQLite.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Utwórz tabelę jeśli nie istnieje
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                quantity INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info('[DATABASE] Initialized SQLite database')
    except Exception as e:
        logging.error(f'[DATABASE] Error initializing database: {str(e)}')


@app.route(route="SaveProduct", methods=["POST"])
def save_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do zapisywania produktu do bazy danych.
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
        
        # Zapisz do bazy
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (id, name, description, price, quantity, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, name, description, price, quantity, now, now))
        
        conn.commit()
        conn.close()
        
        logging.info(f'[DATABASE] Saved product: {product_id}')
        
        response = {
            "success": True,
            "message": "Product saved successfully",
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


@app.route(route="GetProducts", methods=["GET"])
def get_products(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do pobierania wszystkich produktów z bazy danych.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        products = [dict(row) for row in rows]
        
        logging.info(f'[DATABASE] Retrieved {len(products)} products')
        
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


@app.route(route="GetProduct", methods=["GET"])
def get_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do pobierania konkretnego produktu po ID.
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
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return func.HttpResponse(
                json.dumps({"error": "Product not found"}),
                mimetype="application/json",
                status_code=404
            )
        
        product = dict(row)
        
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


@app.route(route="UpdateProduct", methods=["PUT"])
def update_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do aktualizacji produktu.
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
        name = req_body.get('name')
        description = req_body.get('description')
        price = req_body.get('price')
        quantity = req_body.get('quantity')
        now = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buduj SQL UPDATE dynamicznie
        updates = []
        params = []
        
        if name:
            updates.append('name = ?')
            params.append(name)
        if description is not None:
            updates.append('description = ?')
            params.append(description)
        if price:
            updates.append('price = ?')
            params.append(price)
        if quantity is not None:
            updates.append('quantity = ?')
            params.append(quantity)
        
        updates.append('updated_at = ?')
        params.append(now)
        params.append(product_id)
        
        if len(updates) <= 1:
            conn.close()
            return func.HttpResponse(
                json.dumps({"error": "No fields to update"}),
                mimetype="application/json",
                status_code=400
            )
        
        sql = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(sql, params)
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse(
                json.dumps({"error": "Product not found"}),
                mimetype="application/json",
                status_code=404
            )
        
        conn.close()
        
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


@app.route(route="DeleteProduct", methods=["DELETE"])
def delete_product(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do usuwania produktu.
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
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse(
                json.dumps({"error": "Product not found"}),
                mimetype="application/json",
                status_code=404
            )
        
        conn.close()
        
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


# Inicjalizuj bazę na starcie
init_database()
