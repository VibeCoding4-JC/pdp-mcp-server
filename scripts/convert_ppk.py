"""
Script untuk convert PPK (PuTTY Private Key) ke OpenSSH format.
"""
import re
import base64
import struct
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519
from cryptography.hazmat.backends import default_backend


def parse_ppk_file(ppk_path: str) -> dict:
    """Parse PPK file dan ekstrak komponennya."""
    with open(ppk_path, 'r') as f:
        content = f.read()
    
    ppk_data = {}
    
    # Parse header
    header_match = re.search(r'PuTTY-User-Key-File-(\d+):\s*(\S+)', content)
    if header_match:
        ppk_data['version'] = int(header_match.group(1))
        ppk_data['key_type'] = header_match.group(2)
    
    # Parse encryption
    encryption_match = re.search(r'Encryption:\s*(\S+)', content)
    if encryption_match:
        ppk_data['encryption'] = encryption_match.group(1)
    
    # Parse comment
    comment_match = re.search(r'Comment:\s*(.*)', content)
    if comment_match:
        ppk_data['comment'] = comment_match.group(1).strip()
    
    # Parse public lines count and data
    public_lines_match = re.search(r'Public-Lines:\s*(\d+)', content)
    if public_lines_match:
        num_lines = int(public_lines_match.group(1))
        # Find the lines after Public-Lines
        public_start = content.find('Public-Lines:')
        public_data_start = content.find('\n', public_start) + 1
        public_lines = []
        pos = public_data_start
        for _ in range(num_lines):
            end = content.find('\n', pos)
            public_lines.append(content[pos:end])
            pos = end + 1
        ppk_data['public_blob'] = base64.b64decode(''.join(public_lines))
    
    # Parse private lines count and data
    private_lines_match = re.search(r'Private-Lines:\s*(\d+)', content)
    if private_lines_match:
        num_lines = int(private_lines_match.group(1))
        private_start = content.find('Private-Lines:')
        private_data_start = content.find('\n', private_start) + 1
        private_lines = []
        pos = private_data_start
        for _ in range(num_lines):
            end = content.find('\n', pos)
            if end == -1:
                end = len(content)
            private_lines.append(content[pos:end])
            pos = end + 1
        ppk_data['private_blob'] = base64.b64decode(''.join(private_lines))
    
    return ppk_data


def read_ssh_string(data: bytes, offset: int) -> tuple:
    """Read SSH string format (4-byte length + data)."""
    length = struct.unpack('>I', data[offset:offset+4])[0]
    value = data[offset+4:offset+4+length]
    return value, offset + 4 + length


def convert_ppk_to_openssh(ppk_path: str, output_path: str = None) -> str:
    """
    Convert PPK file ke OpenSSH format.
    
    Args:
        ppk_path: Path ke file PPK
        output_path: Path output (optional, default: sama dengan input tapi .pem)
    
    Returns:
        OpenSSH private key string
    """
    ppk_data = parse_ppk_file(ppk_path)
    
    if ppk_data.get('encryption', 'none') != 'none':
        raise ValueError("Encrypted PPK files not supported. Please decrypt first using PuTTYgen.")
    
    key_type = ppk_data['key_type']
    public_blob = ppk_data['public_blob']
    private_blob = ppk_data['private_blob']
    
    if key_type == 'ssh-rsa':
        # Parse public blob
        offset = 0
        key_type_bytes, offset = read_ssh_string(public_blob, offset)
        e_bytes, offset = read_ssh_string(public_blob, offset)
        n_bytes, offset = read_ssh_string(public_blob, offset)
        
        # Parse private blob
        offset = 0
        d_bytes, offset = read_ssh_string(private_blob, offset)
        p_bytes, offset = read_ssh_string(private_blob, offset)
        q_bytes, offset = read_ssh_string(private_blob, offset)
        iqmp_bytes, offset = read_ssh_string(private_blob, offset)
        
        # Convert to integers
        e = int.from_bytes(e_bytes, 'big')
        n = int.from_bytes(n_bytes, 'big')
        d = int.from_bytes(d_bytes, 'big')
        p = int.from_bytes(p_bytes, 'big')
        q = int.from_bytes(q_bytes, 'big')
        
        # Calculate missing values
        dmp1 = d % (p - 1)
        dmq1 = d % (q - 1)
        iqmp = int.from_bytes(iqmp_bytes, 'big')
        
        # Create RSA key
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers
        
        public_numbers = RSAPublicNumbers(e, n)
        private_numbers = RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, public_numbers)
        
        private_key = private_numbers.private_key(default_backend())
        
    else:
        raise ValueError(f"Key type '{key_type}' not supported. Only ssh-rsa is currently supported.")
    
    # Serialize to OpenSSH format
    openssh_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Save to file
    if output_path is None:
        output_path = str(Path(ppk_path).with_suffix('.pem'))
    
    with open(output_path, 'w') as f:
        f.write(openssh_key)
    
    print(f"✅ Converted successfully!")
    print(f"   Input:  {ppk_path}")
    print(f"   Output: {output_path}")
    print(f"\n📋 OpenSSH Private Key (copy untuk GitHub Secret):\n")
    print(openssh_key)
    
    return openssh_key


if __name__ == "__main__":
    import sys
    
    # Default path
    ppk_file = r"c:\Users\fiedelia.zahra\Desktop\MCP\devops01.ppk"
    output_file = r"c:\Users\fiedelia.zahra\Desktop\MCP\devops01_openssh.pem"
    
    if len(sys.argv) > 1:
        ppk_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    try:
        convert_ppk_to_openssh(ppk_file, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nJika PPK terenkripsi, gunakan PuTTYgen untuk decrypt terlebih dahulu:")
        print("1. Buka PuTTYgen")
        print("2. Load file PPK")
        print("3. Masukkan password")
        print("4. Conversions → Export OpenSSH key")
