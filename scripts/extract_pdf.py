"""
Script untuk ekstraksi teks dari PDF UU PDP dan parsing ke struktur JSON.
"""

import json
import re
import os
from pathlib import Path
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Ekstrak semua teks dari PDF.
    
    Args:
        pdf_path: Path ke file PDF
        
    Returns:
        Teks lengkap dari PDF
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page_num, page in enumerate(doc):
        text = page.get_text()
        full_text += f"\n--- Halaman {page_num + 1} ---\n"
        full_text += text
    
    doc.close()
    return full_text


def parse_uu_structure(text: str) -> list[dict]:
    """
    Parse struktur UU dari teks menjadi chunks.
    
    Args:
        text: Teks lengkap UU
        
    Returns:
        List of chunks dengan metadata
    """
    chunks = []
    
    # Pattern untuk mendeteksi BAB
    bab_pattern = r'BAB\s+([IVXLCDM]+)\s*\n\s*([A-Z\s]+?)(?=\n)'
    
    # Pattern untuk mendeteksi Pasal
    pasal_pattern = r'Pasal\s+(\d+)\s*\n(.*?)(?=Pasal\s+\d+|BAB\s+[IVXLCDM]+|$)'
    
    # Cari semua BAB
    bab_matches = list(re.finditer(bab_pattern, text, re.MULTILINE))
    
    current_bab = None
    current_bab_title = None
    
    # Parse setiap Pasal dengan konteks BAB-nya
    for i, bab_match in enumerate(bab_matches):
        current_bab = bab_match.group(1).strip()
        current_bab_title = bab_match.group(2).strip()
        
        # Tentukan range teks untuk BAB ini
        start_pos = bab_match.end()
        end_pos = bab_matches[i + 1].start() if i + 1 < len(bab_matches) else len(text)
        bab_text = text[start_pos:end_pos]
        
        # Cari semua Pasal dalam BAB ini
        pasal_matches = list(re.finditer(pasal_pattern, bab_text, re.DOTALL))
        
        for pasal_match in pasal_matches:
            pasal_num = pasal_match.group(1).strip()
            pasal_content = pasal_match.group(2).strip()
            
            # Bersihkan teks
            pasal_content = clean_text(pasal_content)
            
            if pasal_content and len(pasal_content) > 50:  # Filter chunk terlalu pendek
                chunk = {
                    "id": f"pasal_{pasal_num}",
                    "bab": current_bab,
                    "bab_title": current_bab_title,
                    "pasal": pasal_num,
                    "content": pasal_content,
                    "full_reference": f"BAB {current_bab} - {current_bab_title}, Pasal {pasal_num}"
                }
                chunks.append(chunk)
    
    return chunks


def clean_text(text: str) -> str:
    """
    Bersihkan teks dari karakter yang tidak diinginkan.
    
    Args:
        text: Teks mentah
        
    Returns:
        Teks yang sudah dibersihkan
    """
    # Hapus multiple whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Hapus nomor halaman
    text = re.sub(r'--- Halaman \d+ ---', '', text)
    
    # Hapus karakter aneh
    text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\"\'\!\?\/\%]', '', text)
    
    return text.strip()


def create_overlapping_chunks(chunks: list[dict], overlap_size: int = 1) -> list[dict]:
    """
    Buat chunks dengan overlap untuk konteks yang lebih baik.
    
    Args:
        chunks: List of chunks asli
        overlap_size: Jumlah pasal sebelum/sesudah yang disertakan
        
    Returns:
        List of chunks dengan overlap
    """
    enhanced_chunks = []
    
    for i, chunk in enumerate(chunks):
        # Ambil konteks dari chunk sebelum dan sesudah
        context_before = ""
        context_after = ""
        
        if i > 0:
            context_before = f"[Konteks Pasal {chunks[i-1]['pasal']}]: {chunks[i-1]['content'][:200]}..."
        
        if i < len(chunks) - 1:
            context_after = f"[Konteks Pasal {chunks[i+1]['pasal']}]: {chunks[i+1]['content'][:200]}..."
        
        enhanced_content = chunk['content']
        if context_before:
            enhanced_content = context_before + "\n\n" + enhanced_content
        if context_after:
            enhanced_content = enhanced_content + "\n\n" + context_after
        
        enhanced_chunk = {
            **chunk,
            "content_with_context": enhanced_content
        }
        enhanced_chunks.append(enhanced_chunk)
    
    return enhanced_chunks


def extract_definitions(text: str) -> list[dict]:
    """
    Ekstrak definisi istilah dari BAB I (Ketentuan Umum).
    
    Args:
        text: Teks lengkap UU
        
    Returns:
        List of definisi
    """
    definitions = []
    
    # Pattern untuk definisi dalam Pasal 1
    # Format biasanya: "1. Istilah adalah definisi."
    definition_pattern = r'(\d+)\.\s+([A-Za-z\s]+)\s+adalah\s+(.+?)(?=\d+\.\s+[A-Za-z]|$)'
    
    # Cari teks Pasal 1
    pasal1_pattern = r'Pasal\s+1\s*\n(.*?)(?=Pasal\s+2)'
    pasal1_match = re.search(pasal1_pattern, text, re.DOTALL)
    
    if pasal1_match:
        pasal1_text = pasal1_match.group(1)
        definition_matches = re.finditer(definition_pattern, pasal1_text, re.DOTALL)
        
        for match in definition_matches:
            num = match.group(1).strip()
            term = match.group(2).strip()
            definition = clean_text(match.group(3))
            
            definitions.append({
                "id": f"definisi_{num}",
                "nomor": num,
                "istilah": term,
                "definisi": definition,
                "sumber": "Pasal 1 UU No. 27 Tahun 2022"
            })
    
    return definitions


def main():
    """Main function untuk ekstraksi PDF."""
    # Path ke PDF
    script_dir = Path(__file__).parent.parent
    pdf_path = script_dir / "docs" / "UU Nomor 27 Tahun 2022.pdf"
    output_path = script_dir / "src" / "data" / "pdp_knowledge.json"
    
    print(f"Extracting PDF from: {pdf_path}")
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    # Ekstrak teks
    print("Step 1: Extracting text from PDF...")
    full_text = extract_text_from_pdf(str(pdf_path))
    
    # Parse struktur
    print("Step 2: Parsing UU structure...")
    chunks = parse_uu_structure(full_text)
    print(f"  Found {len(chunks)} pasal chunks")
    
    # Tambah overlap
    print("Step 3: Adding context overlap...")
    enhanced_chunks = create_overlapping_chunks(chunks)
    
    # Ekstrak definisi
    print("Step 4: Extracting definitions...")
    definitions = extract_definitions(full_text)
    print(f"  Found {len(definitions)} definitions")
    
    # Gabungkan semua data
    knowledge_base = {
        "metadata": {
            "source": "UU Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi",
            "total_pasal": len(chunks),
            "total_definisi": len(definitions)
        },
        "pasal": enhanced_chunks,
        "definisi": definitions,
        "raw_text": full_text[:5000] + "..."  # Simpan sample raw text
    }
    
    # Simpan ke JSON
    print(f"Step 5: Saving to {output_path}...")
    os.makedirs(output_path.parent, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Extraction complete!")
    print(f"   - Total pasal: {len(chunks)}")
    print(f"   - Total definisi: {len(definitions)}")
    print(f"   - Output: {output_path}")
    
    # Preview beberapa chunk
    print("\n📋 Preview chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n  [{i+1}] {chunk['full_reference']}")
        print(f"      Content: {chunk['content'][:100]}...")


if __name__ == "__main__":
    main()
