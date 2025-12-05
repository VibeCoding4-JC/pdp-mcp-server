# PDP MCP Server

MCP Server untuk menjawab pertanyaan seputar **UU Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP)** menggunakan RAG (Retrieval-Augmented Generation) dengan Pinecone sebagai vector database.

## 🚀 Features

- **RAG-powered Q&A**: Menjawab pertanyaan berdasarkan isi UU PDP
- **6 MCP Tools**:
  - `tanya_pdp` - Pertanyaan umum tentang UU PDP
  - `cari_pasal` - Cari pasal berdasarkan nomor/keyword
  - `definisi_istilah` - Cari definisi istilah hukum
  - `hak_subjek_data` - Hak-hak pemilik data pribadi
  - `kewajiban_pengendali` - Kewajiban pengendali/prosesor data
  - `sanksi_pelanggaran` - Sanksi administratif dan pidana

## 📋 Requirements

- Python 3.11+
- Pinecone Account (Free tier available)
- OpenAI API Key

## 🛠️ Installation

1. Clone repository:
```bash
git clone <repository-url>
cd pdp-mcp-server
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env dengan API keys Anda
```

## 📚 Data Ingestion

1. Ekstrak PDF UU PDP:
```bash
python scripts/extract_pdf.py
```

2. Ingest data ke Pinecone:
```bash
python scripts/ingest_data.py
```

## 🖥️ Running the Server

```bash
python -m src.server
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📖 Usage with Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "pdp-assistant": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/pdp-mcp-server"
    }
  }
}
```

## 📄 License

MIT License

## 📚 References

- [UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi](https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Pinecone Documentation](https://docs.pinecone.io/)
