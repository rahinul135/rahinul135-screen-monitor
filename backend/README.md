# Employee Screen Monitor — Backend API

This directory contains the backend server for the Employee Screen Monitor system.

## What It Does

The backend provides the following functionalities:

- **Client Registration** — Clients can register themselves with the backend to receive a unique client ID.
- **Configuration Management** — Clients receive their current configuration (interval, bot assignment, active status) from the backend.
- **Heartbeat Tracking** — The backend tracks the last known status of each client.
- **Update Distribution** — The backend manages and distributes agent updates to clients.
- **Admin Dashboard Integration** — The admin dashboard uses this API to manage clients, bots, and settings.

## Endpoints

### Public Endpoints (No Authentication Required)

#### `/register` (POST)
Registers a new client with the backend.

**Request Body:**
```json
{
  "pc_name": "OFFICE-PC-01",
  "ip_address": "192.168.1.100",
  "os_version": "Windows 11 Pro",
  "agent_version": "1.0.0"
}
```

**Response:**
```json
{
  "client_id": "uuid-generated-by-server",
  "message": "Client registered successfully"
}
```

#### `/config/{client_id}` (GET)
Returns the configuration for a specific client.

**Response:**
```json
{
  "interval_minutes": 3,
  "bot_token": "bot_token_here",
  "chat_id": "-100123456789",
  "send_enabled": true,
  "is_active": true
}
```

#### `/heartbeat` (POST)
Receives a heartbeat from a client to indicate that it is alive.

**Request Body:**
```json
{
  "client_id": "client_id_here",
  "timestamp": "2026-11-02T12:00:00Z"
}
```

**Response:**
```json
{
  "message": "Heartbeat received"
}
```

#### `/update/latest` (GET)
Returns the latest agent version and download information.

**Response:**
```json
{
  "version": "1.2.0",
  "url": "/update/download?version=1.2.0",
  "sha256": "abc123..."
}
```

#### `/update/download` (GET)
Downloads the agent binary for a specific version.

**Query Parameters:**
- `version`: Version of the agent to download.

**Response:**
- Binary file (`agent_{version}.exe`)

### Authenticated Endpoints (JWT Required)

All endpoints in this section require a valid JWT token in the Authorization header.

#### `/admin/login` (POST)
Logs in as an admin user and returns a JWT token.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

#### `/admin/clients` (GET)
Returns a list of all clients.

**Response:**
```json
{
  "clients": [
    {
      "id": "client_id_here",
      "pc_name": "OFFICE-PC-01",
      "ip_address": "192.168.1.100",
      "os_version": "Windows 11 Pro",
      "agent_version": "1.0.0",
      "interval_minutes": 3,
      "bot_id": 1,
      "bot_name": "Office Branch A",
      "is_active": true,
      "last_seen": "2026-11-02T12:00:00Z",
      "registered_at": "2026-11-02T11:45:00Z"
    }
  ]
}
```

#### `/admin/clients/{client_id}` (PATCH)
Updates a client's configuration.

**Request Body:**
```json
{
  "interval_minutes": 5,
  "is_active": false
}
```

**Response:**
```json
{
  "message": "Client updated successfully"
}
```

#### `/admin/clients/{client_id}/assign/{bot_id}` (POST)
Assigns a bot to a client.

**Response:**
```json
{
  "message": "Bot assigned to client successfully"
}
```

#### `/admin/clients/{client_id}/unassign/{bot_id}` (DELETE)
Unassigns a bot from a client.

**Response:**
```json
{
  "message": "Bot unassigned from client successfully"
}
```

#### `/admin/bots` (GET)
Returns a list of all bots.

**Response:**
```json
{
  "bots": [
    {
      "id": 1,
      "name": "Office Branch A",
      "token": "bot_token_here",
      "chat_id": "-100123456789",
      "is_active": true
    }
  ]
}
```

#### `/admin/bots` (POST)
Creates a new bot.

**Request Body:**
```json
{
  "name": "Office Branch A",
  "token": "bot_token_here",
  "chat_id": "-100123456789"
}
```

**Response:**
```json
{
  "bot_id": 1,
  "message": "Bot created successfully"
}
```

#### `/admin/bots/{bot_id}` (PUT)
Updates a bot.

**Request Body:**
```json
{
  "name": "Office Branch B",
  "token": "new_bot_token_here",
  "chat_id": "-100987654321",
  "is_active": true
}
```

**Response:**
```json
{
  "message": "Bot updated successfully"
}
```

#### `/admin/bots/{bot_id}` (DELETE)
Deletes a bot (and unassigns it from all clients).

**Response:**
```json
{
  "message": "Bot deleted successfully"
}
```

#### `/admin/settings` (GET)
Returns global settings.

**Response:**
```json
{
  "default_interval": "3",
  "agent_version": "1.2.0",
  "agent_url": "",
  "agent_sha256": ""
}
```

#### `/admin/settings` (PATCH)
Updates global settings.

**Request Body:**
```json
{
  "default_interval": "5",
  "agent_version": "1.2.0"
}
```

**Response:**
```json
{
  "message": "Settings updated successfully"
}
```

#### `/admin/release` (POST)
Uploads a new agent release.

**Form Data:**
- `version`: Agent version (e.g., "1.2.0")
- `agent_binary`: Agent binary file (`.exe`)

**Response:**
```json
{
  "message": "Agent release uploaded successfully",
  "version": "1.2.0",
  "download_url": "/update/download?version=1.2.0",
  "checksum": "abc123..."
}
```

## Database Schema

The backend uses SQLite to store the following tables:

### `clients`
- `id`: Client ID (primary key)
- `pc_name`: PC name
- `ip_address`: IP address
- `os_version`: Operating system version
- `agent_version`: Agent version
- `interval_minutes`: Screenshot interval in minutes
- `bot_id`: Bot ID (foreign key to bots table)
- `is_active`: Whether the client is active
- `last_seen`: Last heartbeat timestamp
- `registered_at`: Registration timestamp

### `bots`
- `id`: Bot ID (primary key)
- `name`: Bot name
- `token`: Bot token
- `chat_id`: Telegram chat ID
- `is_active`: Whether the bot is active

### `settings`
- `key`: Setting key (primary key)
- `value`: Setting value

## Installation

1. **Clone this repository:**
   ```bash
   git clone <repo_url>
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database:**
   ```bash
   python main.py
   ```
   (This will create the database file)

4. **Run the backend server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Docker Deployment

To deploy using Docker:

```bash
# Build the Docker image
docker build -t employee-screen-monitor-backend .

# Run the Docker container
docker run -p 8000:8000 employee-screen-monitor-backend
```

## License

This project is licensed under the MIT License.