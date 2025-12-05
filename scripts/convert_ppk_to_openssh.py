"""
Script untuk convert PPK (PuTTY) ke OpenSSH format.
Jalankan: python scripts/convert_ppk_to_openssh.py <path_to_ppk_file>
"""

import subprocess
import sys
import os
from pathlib import Path


def check_puttygen():
    """Check apakah puttygen tersedia."""
    try:
        result = subprocess.run(
            ["puttygen", "--version"],
            capture_output=True,
            text=True
        )
        return True
    except FileNotFoundError:
        return False


def install_puttygen_windows():
    """Instruksi install puttygen di Windows."""
    print("""
❌ puttygen tidak ditemukan!

Untuk Windows, install PuTTY:
1. Download dari: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
2. Atau menggunakan winget:
   winget install PuTTY.PuTTY

Setelah install, tambahkan ke PATH atau gunakan full path:
   "C:\\Program Files\\PuTTY\\puttygen.exe"
""")


def convert_ppk_to_openssh_manual(ppk_path: str) -> str:
    """
    Convert PPK ke OpenSSH secara manual (parsing PPK file).
    Ini adalah alternatif jika puttygen tidak tersedia.
    """
    try:
        # Try using paramiko untuk convert
        import paramiko
        from paramiko import RSAKey, Ed25519Key, ECDSAKey
        
        # Load PPK file
        key = None
        for key_class in [RSAKey, Ed25519Key, ECDSAKey]:
            try:
                key = key_class.from_private_key_file(ppk_path)
                break
            except:
                continue
        
        if key:
            # Export ke OpenSSH format
            output_path = ppk_path.replace('.ppk', '_openssh.pem')
            key.write_private_key_file(output_path)
            return output_path
        else:
            return None
    except ImportError:
        return None
    except Exception as e:
        print(f"Error with paramiko: {e}")
        return None


def convert_with_puttygen(ppk_path: str) -> str:
    """Convert menggunakan puttygen command line."""
    output_path = ppk_path.replace('.ppk', '_openssh.pem')
    
    # Windows path untuk puttygen
    puttygen_paths = [
        "puttygen",
        "C:\\Program Files\\PuTTY\\puttygen.exe",
        "C:\\Program Files (x86)\\PuTTY\\puttygen.exe",
        os.path.expanduser("~\\AppData\\Local\\Programs\\PuTTY\\puttygen.exe")
    ]
    
    puttygen_cmd = None
    for path in puttygen_paths:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True
            )
            puttygen_cmd = path
            break
        except FileNotFoundError:
            continue
    
    if not puttygen_cmd:
        return None
    
    # Convert PPK ke OpenSSH
    try:
        result = subprocess.run(
            [puttygen_cmd, ppk_path, "-O", "private-openssh", "-o", output_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error running puttygen: {e}")
        return None


def convert_ppk_pure_python(ppk_path: str) -> str:
    """
    Convert PPK ke OpenSSH menggunakan pure Python.
    Mendukung PPK version 2 dan 3.
    """
    import base64
    import struct
    import hashlib
    
    output_path = ppk_path.replace('.ppk', '_openssh.pem')
    
    with open(ppk_path, 'r') as f:
        lines = f.readlines()
    
    # Parse PPK file
    ppk_data = {}
    current_key = None
    current_lines = []
    
    for line in lines:
        line = line.strip()
        if ': ' in line and not current_key:
            key, value = line.split(': ', 1)
            ppk_data[key] = value
        elif line.startswith('Public-Lines:') or line.startswith('Private-Lines:'):
            if current_key:
                ppk_data[current_key] = ''.join(current_lines)
            key, count = line.split(': ')
            current_key = key.replace('-Lines', '-Key')
            current_lines = []
        elif current_key and line:
            current_lines.append(line)
    
    if current_key:
        ppk_data[current_key] = ''.join(current_lines)
    
    # Get key type
    key_type = ppk_data.get('PuTTY-User-Key-File-2', ppk_data.get('PuTTY-User-Key-File-3', ''))
    
    if 'ssh-rsa' not in key_type and 'ssh-ed25519' not in key_type:
        print(f"⚠️  Key type '{key_type}' mungkin tidak didukung.")
        print("Gunakan puttygen untuk convert manual.")
        return None
    
    # Untuk konversi yang akurat, kita butuh library khusus
    # Karena PPK format kompleks, rekomendasikan puttygen
    print("""
⚠️  Pure Python conversion tidak mendukung semua format PPK.
    
Rekomendasi: Gunakan PuTTYgen GUI:
1. Buka PuTTYgen
2. Load file: {}
3. Menu Conversions → Export OpenSSH key
4. Simpan file
""".format(ppk_path))
    
    return None


def main():
    print("=" * 50)
    print("PPK to OpenSSH Converter")
    print("=" * 50)
    
    # Get PPK file path
    if len(sys.argv) > 1:
        ppk_path = sys.argv[1]
    else:
        ppk_path = input("Masukkan path ke file PPK: ").strip().strip('"')
    
    # Validate file
    if not os.path.exists(ppk_path):
        print(f"❌ File tidak ditemukan: {ppk_path}")
        sys.exit(1)
    
    if not ppk_path.lower().endswith('.ppk'):
        print("⚠️  Warning: File tidak berekstensi .ppk")
    
    print(f"\n📂 Input: {ppk_path}")
    
    # Try conversion methods
    output_path = None
    
    # Method 1: puttygen
    print("\n🔄 Mencoba konversi dengan puttygen...")
    output_path = convert_with_puttygen(ppk_path)
    
    if output_path:
        print(f"\n✅ Berhasil! Output: {output_path}")
        
        # Show content untuk copy ke GitHub
        print("\n" + "=" * 50)
        print("📋 Copy isi file berikut ke GitHub Secret SSH_PRIVATE_KEY:")
        print("=" * 50 + "\n")
        
        with open(output_path, 'r') as f:
            content = f.read()
            print(content)
        
        print("\n" + "=" * 50)
        print("✅ Selesai!")
    else:
        print("\n❌ puttygen tidak tersedia.")
        install_puttygen_windows()
        
        # Try pure python
        print("\n🔄 Mencoba metode alternatif...")
        output_path = convert_ppk_pure_python(ppk_path)
        
        if not output_path:
            print("""
📝 Cara Manual dengan PuTTYgen GUI:

1. Buka PuTTYgen (Start Menu → PuTTY → PuTTYgen)
2. Klik 'Load' dan pilih file: {}
3. Klik menu 'Conversions' → 'Export OpenSSH key'
4. Simpan sebagai: {}
5. Buka file tersebut dengan Notepad
6. Copy seluruh isi ke GitHub Secret 'SSH_PRIVATE_KEY'
""".format(ppk_path, ppk_path.replace('.ppk', '_openssh.pem')))


if __name__ == "__main__":
    main()
