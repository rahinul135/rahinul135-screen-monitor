#!/usr/bin/env python3
"""Backend server for Employee Screen Monitor system.

This module provides the REST API that communicates with the client agents and the admin dashboard.
All endpoints are protected with JWT authentication except registration.
"""

import os
import secrets
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import base64

# ─────────────────────────────────────────────────────────────────────────────
# Configuration & Constants
# ─────────────────────────────────────────────────────────────────────────────

# Load environment variables from .env file if available
if os.getenv('PYTHONDEVMODE'):
    from dotenv import load_dotenv
    load_dotenv()

# Server configuration
HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
PORT = int(os.getenv('BACKEND_PORT', '8000'))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

# Database configuration
DB_PATH = os.getenv('DB_PATH', 'backend.db')

# Admin credentials (initial setup)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

if not ADMIN_PASSWORD_HASH:
    # Generate a bcrypt-style hash using PBKDF2 (works on Python 3.14)
    ADMIN_PASSWORD_HASH = _hash_password('admin123')  # Change this password in production!

# Allowed origins for CORS
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')

# ─────────────────────────────────────────────────────────────────────────────
# Password hashing helpers (cross-platform, no passlib needed)
# ─────────────────────────────────────────────────────────────────────────────

def _hash_password(password: str, salt: bytes = None, rounds: int = 29) -> str:
    """Create a bcrypt-compatible hash using PBKDF2-SHA256."""
    if salt is None:
        salt = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=rounds,
    )
    key = kdf.derive(password.encode('utf-8'))
    # Format as bcrypt-style: $2b$29$<22-char-salt-base64><31-char-hash-base64>
    b64_salt = base64.b64encode(salt).decode()[:22]
    b64_key = base64.b64encode(key).decode()[:31]
    return f'$2b${rounds:02d}${b64_salt}{b64_key}'

def _verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    stored = _hash_password(plain, base64.b64decode(hashed.split('$')[2][:22].encode()))
    return stored == hashed

class AuthHandler:
    def __init__(self, secret: str, algorithm: str):
        self.secret = secret
        self.algorithm = algorithm

    def encode_token(self, payload: dict) -> str:
        payload['exp'] = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

auth_handler = AuthHandler(JWT_SECRET, JWT_ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _verify_password(plain_password, hashed_password)

# ─────────────────────────────────────────────────────────────────────────────
# Database Initialization
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            pc_name TEXT NOT NULL,
            ip_address TEXT,
            os_version TEXT,
            agent_version TEXT,
            interval_minutes REAL NOT NULL DEFAULT 3.0,
            bot_id INTEGER,
            is_active INTEGER NOT NULL DEFAULT 1,
            last_seen TEXT,
            registered_at TEXT NOT NULL
        )
    ''')

    # Bots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            token TEXT NOT NULL,
            chat_id TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    # Create default settings if they don't exist
    default_settings = [
        ('default_interval', '3'),
        ('agent_version', '1.0.0'),
        ('agent_url', ''),
        ('agent_sha256', ''),
    ]

    for key, value in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value)
            VALUES (?, ?)
        ''', (key, value))

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_client(client_id: str, pc_name: str, ip_address: str, os_version: str, agent_version: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO clients (id, pc_name, ip_address, os_version, agent_version, interval_minutes, bot_id, is_active, last_seen, registered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        client_id,
        pc_name,
        ip_address,
        os_version,
        agent_version,
        3.0,  # Default interval
        None,  # No bot assigned initially
        1,  # Active
        datetime.utcnow().isoformat(),
        datetime.utcnow().isoformat(),
    ))

    conn.commit()
    conn.close()

def get_client(client_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_client_config(client_id: str, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = []
    update_values = []
    for key, value in kwargs.items():
        update_fields.append(f"{key} = ?")
        update_values.append(value)

    update_values.append(client_id)

    cursor.execute(f'''
        UPDATE clients
        SET {', '.join(update_fields)}
        WHERE id = ?
    ''', update_values)

    conn.commit()
    conn.close()

def get_all_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    results = cursor.fetchall()
    conn.close()
    return results

def update_client_bot(client_id: str, bot_id: Optional[int]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE clients SET bot_id = ? WHERE id = ?', (bot_id, client_id))
    conn.commit()
    conn.close()

def get_bot(bot_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bots WHERE id = ?', (bot_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_all_bots():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bots')
    results = cursor.fetchall()
    conn.close()
    return results

def create_bot(name: str, token: str, chat_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bots (name, token, chat_id, is_active) VALUES (?, ?, ?, 1)', (name, token, chat_id))
    bot_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return bot_id

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Application
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title='Employee Screen Monitor API',
    description='API for managing Employee Screen Monitor clients and configuration',
    version='1.0.0',
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ─────────────────────────────────────────────────────────────────────────────
# Authentication Middleware
# ─────────────────────────────────────────────────────────────────────────────

@app.middleware('http')
async def authentication_middleware(request: Request, call_next):
    # Skip authentication for public endpoints
    if request.url.path in ['/docs', '/redoc', '/openapi.json'] or request.url.path.startswith('/register'):
        response = await call_next(request)
        return response

    # Check for authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': 'Missing or invalid authorization header'},
        )

    token = auth_header.split(' ')[1]
    try:
        payload = auth_handler.decode_token(token)
        request.state.user = payload
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={'detail': e.detail},
        )

    response = await call_next(request)
    return response

# ─────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────────────────────

# Public endpoint - Client registration
@app.post('/register')
async def register_client(request: Request):
    data = await request.json()

    # Validate required fields
    required_fields = ['pc_name', 'ip_address', 'os_version', 'agent_version']
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Missing required field: {field}',
            )

    # Generate a unique client ID
    client_id = secrets.token_urlsafe(32)

    # Create client in database
    create_client(
        client_id=client_id,
        pc_name=data['pc_name'],
        ip_address=data['ip_address'],
        os_version=data['os_version'],
        agent_version=data['agent_version'],
    )

    # Return the client ID to the client
    return {
        'client_id': client_id,
        'message': 'Client registered successfully',
    }

# Public endpoint - Client configuration (used by agents)
@app.get('/config/{client_id}')
async def get_client_config(client_id: str):
    # Get client from database
    client = get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found',
        )

    # Get bot assignment
    bot_id = client['bot_id']
    bot_token = None
    bot_chat_id = None

    if bot_id:
        bot = get_bot(bot_id)
        if bot:
            bot_token = bot['token']
            bot_chat_id = bot['chat_id']

    # Return client configuration
    return {
        'interval_minutes': client['interval_minutes'],
        'bot_token': bot_token,
        'chat_id': bot_chat_id,
        'send_enabled': bool(bot_token and bot_chat_id),
        'is_active': bool(client['is_active']),
    }

# Authenticated endpoints - Admin operations

# Admin login
@app.post('/admin/login')
async def admin_login(request: Request):
    data = await request.json()

    # Validate username and password
    if data.get('username') != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )

    if not verify_password(data.get('password', ''), ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )

    # Generate JWT token
    token = auth_handler.encode_token({
        'sub': ADMIN_USERNAME,
        'role': 'admin',
    })

    return {
        'access_token': token,
        'token_type': 'bearer',
    }

# Get all clients (admin only)
@app.get('/admin/clients')
async def get_all_clients_endpoint(user: dict = Depends(lambda r: r.state.user)):
    clients = get_all_clients()

    # Convert to list of dictionaries
    client_list = []
    for client in clients:
        bot = None
        if client['bot_id']:
            bot = get_bot(client['bot_id'])

        client_list.append({
            'id': client['id'],
            'pc_name': client['pc_name'],
            'ip_address': client['ip_address'],
            'os_version': client['os_version'],
            'agent_version': client['agent_version'],
            'interval_minutes': client['interval_minutes'],
            'bot_id': client['bot_id'],
            'bot_name': bot['name'] if bot else None,
            'is_active': bool(client['is_active']),
            'last_seen': client['last_seen'],
            'registered_at': client['registered_at'],
        })

    return {'clients': client_list}

# Update client configuration (admin only)
@app.patch('/admin/clients/{client_id}')
async def update_client_endpoint(
    client_id: str,
    request: Request,
    user: dict = Depends(lambda r: r.state.user),
):
    data = await request.json()

    # Update client configuration
    update_fields = {}
    if 'interval_minutes' in data:
        update_fields['interval_minutes'] = data['interval_minutes']
    if 'is_active' in data:
        update_fields['is_active'] = 1 if data['is_active'] else 0

    if update_fields:
        update_client_config(client_id, **update_fields)

    return {'message': 'Client updated successfully'}

# Assign bot to client (admin only)
@app.post('/admin/clients/{client_id}/assign/{bot_id}')
async def assign_bot_to_client_endpoint(
    client_id: str,
    bot_id: int,
    user: dict = Depends(lambda r: r.state.user),
):
    # Check if bot exists
    bot = get_bot(bot_id)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Bot not found',
        )

    # Assign bot to client
    update_client_bot(client_id, bot_id)

    return {'message': 'Bot assigned to client successfully'}

# Unassign bot from client (admin only)
@app.delete('/admin/clients/{client_id}/assign/{bot_id}')
async def unassign_bot_from_client_endpoint(
    client_id: str,
    bot_id: int,
    user: dict = Depends(lambda r: r.state.user),
):
    # Check if bot exists
    bot = get_bot(bot_id)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Bot not found',
        )

    # Unassign bot from client
    update_client_bot(client_id, None)

    return {'message': 'Bot unassigned from client successfully'}

# Get all bots (admin only)
@app.get('/admin/bots')
async def get_all_bots_endpoint(user: dict = Depends(lambda r: r.state.user)):
    bots = get_all_bots()

    # Convert to list of dictionaries
    bot_list = []
    for bot in bots:
        bot_list.append({
            'id': bot['id'],
            'name': bot['name'],
            'token': bot['token'],
            'chat_id': bot['chat_id'],
            'is_active': bool(bot['is_active']),
        })

    return {'bots': bot_list}

# Create bot (admin only)
@app.post('/admin/bots')
async def create_bot_endpoint(
    request: Request,
    user: dict = Depends(lambda r: r.state.user),
):
    data = await request.json()

    # Validate required fields
    required_fields = ['name', 'token', 'chat_id']
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Missing required field: {field}',
            )

    # Create bot
    bot_id = create_bot(
        name=data['name'],
        token=data['token'],
        chat_id=data['chat_id'],
    )

    return {
        'bot_id': bot_id,
        'message': 'Bot created successfully',
    }

# Update bot (admin only)
@app.put('/admin/bots/{bot_id}')
async def update_bot_endpoint(
    bot_id: int,
    request: Request,
    user: dict = Depends(lambda r: r.state.user),
):
    data = await request.json()

    # Check if bot exists
    bot = get_bot(bot_id)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Bot not found',
        )

    # Update bot
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = []
    update_values = []

    if 'name' in data:
        update_fields.append('name = ?')
        update_values.append(data['name'])

    if 'token' in data:
        update_fields.append('token = ?')
        update_values.append(data['token'])

    if 'chat_id' in data:
        update_fields.append('chat_id = ?')
        update_values.append(data['chat_id'])

    if 'is_active' in data:
        update_fields.append('is_active = ?')
        update_values.append(1 if data['is_active'] else 0)

    if update_fields:
        cursor.execute(f'''
            UPDATE bots
            SET {', '.join(update_fields)}
            WHERE id = ?
        ''', update_values + [bot_id])
        conn.commit()

    conn.close()

    return {'message': 'Bot updated successfully'}

# Delete bot (admin only)
@app.delete('/admin/bots/{bot_id}')
async def delete_bot_endpoint(
    bot_id: int,
    user: dict = Depends(lambda r: r.state.user),
):
    # Check if bot exists
    bot = get_bot(bot_id)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Bot not found',
        )

    # Delete bot (and unassign from all clients)
    conn = get_db_connection()
    cursor = conn.cursor()

    # First, unassign bot from all clients
    cursor.execute('UPDATE clients SET bot_id = NULL WHERE bot_id = ?', (bot_id,))

    # Then delete the bot
    cursor.execute('DELETE FROM bots WHERE id = ?', (bot_id,))

    conn.commit()
    conn.close()

    return {'message': 'Bot deleted successfully'}

# Get global settings (admin only)
@app.get('/admin/settings')
async def get_settings_endpoint(user: dict = Depends(lambda r: r.state.user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings')
    results = cursor.fetchall()
    conn.close()

    settings = {}
    for row in results:
        settings[row['key']] = row['value']

    return settings

# Update global settings (admin only)
@app.patch('/admin/settings')
async def update_settings_endpoint(
    request: Request,
    user: dict = Depends(lambda r: r.state.user),
):
    data = await request.json()

    conn = get_db_connection()
    cursor = conn.cursor()

    for key, value in data.items():
        cursor.execute('''
            UPDATE settings
            SET value = ?
            WHERE key = ?
        ''', (value, key))

    conn.commit()
    conn.close()

    return {'message': 'Settings updated successfully'}

# Upload new agent binary (admin only)
@app.post('/admin/release')
async def upload_agent_release_endpoint(
    request: Request,
    user: dict = Depends(lambda r: r.state.user),
):
    # Parse multipart form data
    form = await request.form()

    # Get version
    version = form.get('version')
    if not version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Missing version field',
        )

    # Get agent binary
    agent_file = form.get('agent_binary')
    if not agent_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Missing agent_binary field',
        )

    # Save agent binary to file
    agent_dir = Path('releases')
    agent_dir.mkdir(exist_ok=True)

    agent_path = agent_dir / f'agent_{version}.exe'
    with open(agent_path, 'wb') as f:
        content = await agent_file.read()
        f.write(content)

    # Calculate SHA256 checksum
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(agent_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256_hash.update(chunk)
    checksum = sha256_hash.hexdigest()

    # Update settings
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (version, 'agent_version'))
    cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (str(agent_path), 'agent_url'))
    cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (checksum, 'agent_sha256'))

    conn.commit()
    conn.close()

    return {
        'message': 'Agent release uploaded successfully',
        'version': version,
        'download_url': f'/update/download?version={version}',
        'checksum': checksum,
    }

# Download agent binary (public - used by clients)
@app.get('/update/download')
async def download_agent_release_endpoint(request: Request):
    version = request.query_params.get('version')
    if not version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Missing version parameter',
        )

    # Get download URL from settings
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('agent_url',))
    result = cursor.fetchone()
    conn.close()

    if not result or not result['value']:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No agent binary found for this version',
        )

    agent_path = Path(result['value'])
    if not agent_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Agent binary not found on server',
        )

    # Read and stream the file
    with open(agent_path, 'rb') as f:
        content = f.read()

    return JSONResponse(content=content, media_type='application/octet-stream', headers={
        'Content-Disposition': f'attachment; filename=agent_{version}.exe',
    })

# Get update information (public - used by clients)
@app.get('/update/latest')
async def get_latest_version_endpoint(request: Request):
    # Get update information from settings
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT value FROM settings WHERE key IN (?, ?, ?)',
                   ('agent_version', 'agent_url', 'agent_sha256'))
    results = cursor.fetchall()
    conn.close()

    settings = {}
    for row in results:
        settings[row['key']] = row['value']

    if not settings.get('agent_version'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No update information available',
        )

    return {
        'version': settings['agent_version'],
        'url': settings.get('agent_url', ''),
        'sha256': settings.get('agent_sha256', ''),
    }

# Heartbeat endpoint (public - used by clients)
@app.post('/heartbeat')
async def heartbeat_endpoint(request: Request):
    data = await request.json()

    # Validate required fields
    required_fields = ['client_id', 'timestamp']
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Missing required field: {field}',
            )

    # Update client last seen time
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE clients SET last_seen = ? WHERE id = ?',
                   (data['timestamp'], data['client_id']))
    conn.commit()
    conn.close()

    return {'message': 'Heartbeat received'}

# ─────────────────────────────────────────────────────────────────────────────
# Application Startup
# ─────────────────────────────────────────────────────────────────────────────

# Initialize database
init_db()

if __name__ == '__main__':
    import uvicorn

    print(f"Starting backend server...")
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Debug: {DEBUG}")
    print(f"Database: {DB_PATH}")

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level='debug' if DEBUG else 'info',
    )