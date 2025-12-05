# Deployment Guide - PDP MCP Server

## Prerequisites

1. **Server Requirements**
   - Ubuntu 20.04+ atau Debian 11+
   - Python 3.11+
   - Minimal 1GB RAM
   - Akses SSH

2. **API Keys**
   - Pinecone API Key
   - Gemini API Key

3. **SSH Connection Info**
   - Host: `103.164.191.212`
   - Port: `22193`
   - Username: `devjc`
   - Auth: PPK file `devops01.ppk`

4. **GitHub Secrets** (untuk CI/CD)
   - `SSH_HOST` - `103.164.191.212`
   - `SSH_USERNAME` - `devjc`
   - `SSH_PRIVATE_KEY` - Convert dari `devops01.ppk` ke OpenSSH format
   - `SSH_PORT` - `22193`
   - `DEPLOY_PATH` - Path deployment (e.g., `/opt/pdp-mcp-server`)
   - `PINECONE_API_KEY` - API key Pinecone
   - `GEMINI_API_KEY` - API key Gemini

---

## Initial Server Setup

### Option 1: Menggunakan Setup Script

```bash
# Download dan jalankan setup script
curl -O https://raw.githubusercontent.com/your-repo/pdp-mcp-server/main/deploy/setup-server.sh
sudo bash setup-server.sh https://github.com/your-username/pdp-mcp-server.git
```

### Option 2: Manual Setup

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# 2. Create deployment directory
sudo mkdir -p /opt/pdp-mcp-server
sudo chown $USER:$USER /opt/pdp-mcp-server
cd /opt/pdp-mcp-server

# 3. Clone repository
git clone https://github.com/your-username/pdp-mcp-server.git .

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create .env file
cp .env.example .env
nano .env  # Edit dengan API keys Anda

# 7. Install systemd service
sudo cp deploy/pdp-mcp-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pdp-mcp-server
```

---

## Data Ingestion

Sebelum menjalankan server, ingest data ke Pinecone:

```bash
cd /opt/pdp-mcp-server
source venv/bin/activate

# Ekstrak PDF (jika belum)
python scripts/extract_pdf.py

# Ingest ke Pinecone
python scripts/ingest_data.py
```

---

## Service Management

```bash
# Start service
sudo systemctl start pdp-mcp-server

# Stop service
sudo systemctl stop pdp-mcp-server

# Restart service
sudo systemctl restart pdp-mcp-server

# Check status
sudo systemctl status pdp-mcp-server

# View logs
sudo journalctl -u pdp-mcp-server -f

# View recent logs
sudo journalctl -u pdp-mcp-server --since "1 hour ago"
```

---

## GitHub Actions Setup

### 1. Generate SSH Key

```bash
# Di local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions

# Copy public key ke server
ssh-copy-id -i ~/.ssh/github_actions.pub user@server-ip
```

### 2. Setup GitHub Secrets

Di repository GitHub, buka **Settings → Secrets and variables → Actions**, tambahkan:

| Secret Name | Value |
|-------------|-------|
| `SSH_HOST` | IP address server |
| `SSH_USERNAME` | Username SSH |
| `SSH_PRIVATE_KEY` | Isi dari `~/.ssh/github_actions` (private key) |
| `SSH_PORT` | `22` |
| `DEPLOY_PATH` | `/opt/pdp-mcp-server` |
| `PINECONE_API_KEY` | API key Pinecone |
| `OPENAI_API_KEY` | API key OpenAI |

### 3. Test Deployment

Push ke branch `main` untuk trigger deployment:

```bash
git push origin main
```

---

## Using with Claude Desktop

Tambahkan ke `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pdp-assistant": {
      "command": "ssh",
      "args": [
        "-o", "StrictHostKeyChecking=no",
        "user@server-ip",
        "cd /opt/pdp-mcp-server && source venv/bin/activate && python -m src.server"
      ]
    }
  }
}
```

Atau jika server berjalan lokal:

```json
{
  "mcpServers": {
    "pdp-assistant": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/pdp-mcp-server",
      "env": {
        "PINECONE_API_KEY": "your-key",
        "OPENAI_API_KEY": "your-key"
      }
    }
  }
}
```

---

## Troubleshooting

### Service tidak bisa start

```bash
# Check logs
sudo journalctl -u pdp-mcp-server -n 50

# Verify .env file exists
cat /opt/pdp-mcp-server/.env

# Test manually
cd /opt/pdp-mcp-server
source venv/bin/activate
python -m src.server
```

### Permission denied

```bash
sudo chown -R www-data:www-data /opt/pdp-mcp-server
sudo chmod -R 755 /opt/pdp-mcp-server
sudo chmod 600 /opt/pdp-mcp-server/.env
```

### Python module not found

```bash
cd /opt/pdp-mcp-server
source venv/bin/activate
pip install -r requirements.txt
```

---

## Updating

Deployment otomatis dilakukan oleh GitHub Actions saat push ke `main`.

Untuk update manual:

```bash
cd /opt/pdp-mcp-server
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart pdp-mcp-server
```
