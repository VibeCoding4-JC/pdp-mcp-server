"""
MCP Tools untuk UU Perlindungan Data Pribadi (UU PDP).
"""

from typing import Optional
from fastmcp import FastMCP

from ..rag.retriever import PDPRetriever, get_retriever


def register_tools(mcp: FastMCP, retriever: Optional[PDPRetriever] = None):
    """
    Register semua MCP tools untuk UU PDP.
    
    Args:
        mcp: FastMCP instance
        retriever: PDPRetriever instance (optional, will create if not provided)
    """
    _retriever = retriever or get_retriever()
    
    @mcp.tool()
    def tanya_pdp(pertanyaan: str) -> str:
        """
        Menjawab pertanyaan umum tentang UU Perlindungan Data Pribadi (UU No. 27 Tahun 2022).
        
        Gunakan tool ini untuk bertanya tentang:
        - Ketentuan umum dan definisi
        - Hak-hak subjek data pribadi
        - Kewajiban pengendali dan prosesor data
        - Sanksi pelanggaran
        - Transfer data pribadi
        - Dan topik lainnya terkait UU PDP
        
        Args:
            pertanyaan: Pertanyaan tentang UU PDP dalam Bahasa Indonesia
            
        Returns:
            Jawaban berdasarkan isi UU PDP
        """
        context, results = _retriever.get_context_for_query(
            pertanyaan,
            top_k=5,
            max_tokens=4000
        )
        
        if not results:
            return "Maaf, saya tidak menemukan informasi yang relevan dalam UU PDP untuk pertanyaan Anda."
        
        # Build response with references
        response = f"""Berdasarkan UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi:

{context}

---
Referensi yang digunakan:
"""
        for i, result in enumerate(results, 1):
            ref = result.metadata.get("full_reference", f"Pasal {result.metadata.get('pasal', 'N/A')}")
            response += f"\n{i}. {ref} (relevansi: {result.score:.2%})"
        
        return response
    
    @mcp.tool()
    def cari_pasal(
        keyword: str,
        bab: Optional[str] = None,
        jumlah_hasil: int = 5
    ) -> str:
        """
        Mencari pasal dalam UU PDP berdasarkan keyword atau topik tertentu.
        
        Args:
            keyword: Kata kunci atau topik yang dicari
            bab: Filter berdasarkan BAB (opsional, contoh: "I", "II", "III", dst.)
            jumlah_hasil: Jumlah pasal yang dikembalikan (default: 5, max: 10)
            
        Returns:
            Daftar pasal yang relevan dengan keyword
        """
        jumlah_hasil = min(max(1, jumlah_hasil), 10)
        
        results = _retriever.search_pasal(
            query=keyword,
            top_k=jumlah_hasil,
            bab=bab
        )
        
        if not results:
            msg = f"Tidak ditemukan pasal yang relevan dengan '{keyword}'"
            if bab:
                msg += f" pada BAB {bab}"
            return msg
        
        response = f"Hasil pencarian pasal untuk '{keyword}'"
        if bab:
            response += f" (BAB {bab})"
        response += f":\n\n"
        
        for i, result in enumerate(results, 1):
            ref = result.metadata.get("full_reference", f"Pasal {result.metadata.get('pasal', 'N/A')}")
            content = result.content
            score = result.score
            
            response += f"**{i}. {ref}** (relevansi: {score:.2%})\n"
            response += f"{content}\n\n"
        
        return response
    
    @mcp.tool()
    def definisi_istilah(istilah: str) -> str:
        """
        Mencari definisi istilah hukum dalam UU PDP.
        
        Gunakan tool ini untuk mencari arti/definisi dari istilah seperti:
        - Data Pribadi
        - Subjek Data Pribadi
        - Pengendali Data Pribadi
        - Prosesor Data Pribadi
        - Persetujuan
        - Dan istilah hukum lainnya
        
        Args:
            istilah: Istilah yang ingin dicari definisinya
            
        Returns:
            Definisi istilah berdasarkan UU PDP
        """
        # Search di definisi dulu
        def_results = _retriever.search_definisi(istilah, top_k=2)
        
        # Search juga di pasal (karena definisi mungkin ada di Pasal 1)
        pasal_results = _retriever.search_pasal(
            f"definisi {istilah} adalah",
            top_k=3,
            bab="I"  # BAB I biasanya berisi ketentuan umum
        )
        
        all_results = def_results + pasal_results
        
        if not all_results:
            return f"Tidak ditemukan definisi untuk istilah '{istilah}' dalam UU PDP."
        
        response = f"Definisi '{istilah}' dalam UU PDP:\n\n"
        
        for i, result in enumerate(all_results[:3], 1):
            if result.metadata.get("type") == "definisi":
                response += f"{i}. **{result.metadata.get('istilah', istilah)}**\n"
                response += f"   {result.metadata.get('definisi', result.content)}\n"
                response += f"   _(Sumber: {result.metadata.get('sumber', 'UU PDP')})_\n\n"
            else:
                ref = result.metadata.get("full_reference", "UU PDP")
                response += f"{i}. Berdasarkan **{ref}**:\n"
                response += f"   {result.content[:500]}...\n\n"
        
        return response
    
    @mcp.tool()
    def hak_subjek_data() -> str:
        """
        Menjelaskan hak-hak subjek data pribadi menurut UU PDP.
        
        Tool ini mengembalikan daftar lengkap hak-hak yang dimiliki
        oleh subjek data pribadi (pemilik data) berdasarkan UU No. 27 Tahun 2022.
        
        Returns:
            Daftar hak-hak subjek data pribadi
        """
        query = "hak subjek data pribadi mendapatkan informasi akses menolak meminta hapus"
        
        results = _retriever.search_pasal(
            query=query,
            top_k=8,
            bab="IV"  # BAB IV tentang Hak Subjek Data Pribadi
        )
        
        if not results:
            # Fallback to general search
            results = _retriever.search_pasal(query=query, top_k=8)
        
        response = """# Hak-Hak Subjek Data Pribadi (UU No. 27 Tahun 2022)

Berdasarkan UU Perlindungan Data Pribadi, subjek data memiliki hak-hak berikut:

"""
        
        for i, result in enumerate(results, 1):
            ref = result.metadata.get("full_reference", f"Pasal {result.metadata.get('pasal', 'N/A')}")
            response += f"## {i}. {ref}\n"
            response += f"{result.content}\n\n"
        
        response += """
---
_Catatan: Hak-hak ini diatur dalam BAB IV UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi._
"""
        
        return response
    
    @mcp.tool()
    def kewajiban_pengendali() -> str:
        """
        Menjelaskan kewajiban pengendali dan prosesor data pribadi menurut UU PDP.
        
        Tool ini mengembalikan daftar kewajiban yang harus dipenuhi oleh:
        - Pengendali Data Pribadi
        - Prosesor Data Pribadi
        
        Returns:
            Daftar kewajiban pengendali dan prosesor data
        """
        query = "kewajiban pengendali prosesor data pribadi wajib harus menjaga keamanan"
        
        results = _retriever.search_pasal(
            query=query,
            top_k=8,
            bab="VIII"  # BAB tentang Kewajiban
        )
        
        if not results:
            results = _retriever.search_pasal(query=query, top_k=8)
        
        response = """# Kewajiban Pengendali dan Prosesor Data Pribadi

Berdasarkan UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi:

"""
        
        for i, result in enumerate(results, 1):
            ref = result.metadata.get("full_reference", f"Pasal {result.metadata.get('pasal', 'N/A')}")
            response += f"## {i}. {ref}\n"
            response += f"{result.content}\n\n"
        
        return response
    
    @mcp.tool()
    def sanksi_pelanggaran(jenis_sanksi: Optional[str] = None) -> str:
        """
        Menjelaskan sanksi pelanggaran UU Perlindungan Data Pribadi.
        
        Args:
            jenis_sanksi: Jenis sanksi yang dicari (opsional):
                         - "administratif" untuk sanksi administratif
                         - "pidana" untuk sanksi pidana
                         - None untuk semua jenis sanksi
                         
        Returns:
            Daftar sanksi pelanggaran UU PDP
        """
        if jenis_sanksi == "administratif":
            query = "sanksi administratif peringatan tertulis penghentian denda"
            bab = "X"  # BAB tentang Sanksi Administratif
        elif jenis_sanksi == "pidana":
            query = "sanksi pidana penjara denda tahun"
            bab = "XIV"  # BAB tentang Ketentuan Pidana
        else:
            query = "sanksi pelanggaran pidana administratif denda penjara"
            bab = None
        
        results = _retriever.search_pasal(
            query=query,
            top_k=8,
            bab=bab
        )
        
        title = "Sanksi Pelanggaran UU Perlindungan Data Pribadi"
        if jenis_sanksi:
            title += f" ({jenis_sanksi.title()})"
        
        response = f"""# {title}

Berdasarkan UU No. 27 Tahun 2022:

"""
        
        for i, result in enumerate(results, 1):
            ref = result.metadata.get("full_reference", f"Pasal {result.metadata.get('pasal', 'N/A')}")
            response += f"## {i}. {ref}\n"
            response += f"{result.content}\n\n"
        
        if jenis_sanksi == "administratif":
            response += """
---
_Sanksi administratif dapat berupa: peringatan tertulis, penghentian sementara kegiatan pemrosesan, 
penghapusan data pribadi, dan/atau denda administratif._
"""
        elif jenis_sanksi == "pidana":
            response += """
---
_Sanksi pidana dapat berupa pidana penjara dan/atau denda sesuai dengan tingkat pelanggaran._
"""
        
        return response
    
    return mcp
