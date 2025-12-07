import azure.functions as func
import json
import logging
import os
from datetime import datetime
import base64

app = func.FunctionApp()

# Przechowywanie listy przesłanych plików (mock - w pamięci)
uploaded_files = []

def add_cors_headers(response):
    """Dodaj nagłówki CORS do odpowiedzi"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route(route="UploadFile", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def UploadFile(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint do przesyłania pliku.
    Przyjmuje JSON z base64-encoded plikiem
    """
    # Obsługa CORS preflight
    if req.method == "OPTIONS":
        response = func.HttpResponse("", status_code=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    logging.info('UploadFile endpoint called')
    logging.info(f'Content-Type: {req.headers.get("Content-Type")}')
    logging.info(f'Body length: {len(req.get_body())}')

    try:
        # Spróbuj parsować JSON
        body = req.get_json()
        logging.info(f'Body: {body}')
        
        filename = body.get('filename', 'unknown')
        content_b64 = body.get('content', '')
        
        if not content_b64:
            response = func.HttpResponse(
                json.dumps({"error": "Brak zawartości pliku (content field)"}),
                mimetype="application/json",
                status_code=400
            )
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Dekoduj base64
        file_content = base64.b64decode(content_b64)
        file_size = len(file_content)
        
        # Dodaj do listy
        file_info = {
            "filename": filename,
            "size": file_size,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        uploaded_files.append(file_info)
        
        logging.info(f'File uploaded: {filename}, size: {file_size} bytes, total files: {len(uploaded_files)}')
        
        response_obj = {
            "success": True,
            "message": f"Plik {filename} przesłano",
            "filename": filename,
            "size": file_size,
            "uploaded_at": file_info["uploaded_at"]
        }
        
        response = func.HttpResponse(
            json.dumps(response_obj),
            mimetype="application/json",
            status_code=200
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except ValueError as e:
        logging.error(f'JSON parsing error: {str(e)}')
        response = func.HttpResponse(
            json.dumps({"error": f"Błąd JSON: {str(e)}"}),
            mimetype="application/json",
            status_code=400
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        logging.error(f'Error uploading file: {str(e)}')
        logging.error(f'Exception type: {type(e).__name__}')
        import traceback
        logging.error(traceback.format_exc())
        response = func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route(route="GetFiles", methods=["GET", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def GetFiles(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint zwracający listę przesłanych plików
    """
    # Obsługa CORS preflight
    if req.method == "OPTIONS":
        response = func.HttpResponse("", status_code=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    logging.info('GetFiles endpoint called')
    
    try:
        response_obj = {
            "success": True,
            "total": len(uploaded_files),
            "files": [
                {
                    "filename": f["filename"],
                    "size": f["size"],
                    "uploaded_at": f["uploaded_at"]
                }
                for f in uploaded_files
            ]
        }
        
        response = func.HttpResponse(
            json.dumps(response_obj),
            mimetype="application/json",
            status_code=200
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        logging.error(f'Error getting files: {str(e)}')
        response = func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response