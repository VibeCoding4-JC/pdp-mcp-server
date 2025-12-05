# Setup GitHub Secrets untuk Deployment

## Informasi SSH Server

| Parameter | Value |
|-----------|-------|
| Host | `103.164.191.212` |
| Port | `22193` |
| Username | `devjc` |
| Auth | PPK file `devops01.ppk` |

---

## Step 1: Convert PPK ke OpenSSH Format

PPK adalah format PuTTY, GitHub Actions membutuhkan format OpenSSH.

### Menggunakan PuTTYgen (Windows):
1. Buka **PuTTYgen**
2. Klik **Load** dan pilih file `devops01.ppk`
3. Klik menu **Conversions** → **Export OpenSSH key**
4. Simpan sebagai `devops01_openssh` (tanpa extension)
5. Buka file dengan Notepad, copy seluruh isi

### Menggunakan puttygen CLI (Linux/WSL):
```bash
# Install putty-tools jika belum ada
sudo apt install putty-tools

# Convert PPK ke OpenSSH
puttygen devops01.ppk -O private-openssh -o devops01_openssh.pem

# Lihat isi untuk dicopy ke GitHub
cat devops01_openssh.pem
```

---

## Step 2: Setup GitHub Repository

1. Buka browser dan login ke GitHub
2. Buat repository baru atau gunakan repository existing
3. Repository URL: `https://github.com/VibeCoding6-JC/pdp-mcp-server`

---

## Step 3: Setup GitHub Secrets

1. Buka repository di GitHub
2. Pergi ke **Settings** → **Secrets and variables** → **Actions**
3. Klik **New repository secret** dan tambahkan:

| Secret Name | Value |
|-------------|-------|
| `SSH_HOST` | `103.164.191.212` |
| `SSH_PORT` | `22193` |
| `SSH_USERNAME` | `devjc` |
| `SSH_PRIVATE_KEY` | *Paste isi file OpenSSH key* |
| `DEPLOY_PATH` | `/opt/pdp-mcp-server` |
| `PINECONE_API_KEY` | `pcsk_6Pjt8U_TkwyJQHmyiQNjqYm8GEUzgkJyrQdmWRGHEPfhvZcP85yATPGpVQ7jDuGnbQJVPp` |
| `GEMINI_API_KEY` | `AIzaSyD9tPPsEJFJaR_ZXoxO8aafrKSHtldErgM` |

---

## Step 4: Push ke GitHub

```powershell
cd c:\Users\fiedelia.zahra\Desktop\MCP\pdp-mcp-server

# Initialize git jika belum
git init

# Add remote
git remote add origin https://github.com/VibeCoding6-JC/pdp-mcp-server.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: PDP MCP Server with Gemini embedding"

# Push
git push -u origin main
```

---

## Step 5: Initial Server Setup

SSH ke server dan jalankan setup awal:

```bash
# Connect via SSH (menggunakan PuTTY atau OpenSSH)
ssh -p 22193 -i devops01_openssh.pem devjc@103.164.191.212

# Atau menggunakan PuTTY
# Host: 103.164.191.212
# Port: 22193
# Connection > SSH > Auth > Private key file: devops01.ppk
```

Di server:
```bash
# Create directory
sudo mkdir -p /opt/pdp-mcp-server
sudo chown devjc:devjc /opt/pdp-mcp-server

# Clone repository
cd /opt/pdp-mcp-server
git clone https://github.com/VibeCoding6-JC/pdp-mcp-server.git .

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy systemd service
sudo cp deploy/pdp-mcp-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pdp-mcp-server
```

---

## Step 6: Test Deployment

Setelah push ke main branch, GitHub Actions akan otomatis:
1. Menjalankan tests
2. Deploy ke server via SSH
3. Restart service

Cek status di: `https://github.com/VibeCoding6-JC/pdp-mcp-server/actions`

---

## Troubleshooting

### Error: Permission denied (publickey)
- Pastikan private key sudah di-convert ke format OpenSSH
- Pastikan key sudah ditambahkan ke server (`~/.ssh/authorized_keys`)

### Error: Connection refused
- Cek port SSH sudah benar (22193)
- Cek firewall server

### Error: Service failed to start
```bash
# Cek logs
sudo journalctl -u pdp-mcp-server -f

# Cek status
sudo systemctl status pdp-mcp-server
```
