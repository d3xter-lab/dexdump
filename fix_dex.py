import zlib
import hashlib
import argparse
from pathlib import Path

def fix_dex(file_path: Path, keep_original: bool = False):
    with open(file_path, 'rb') as f:
        dex = bytearray(f.read())

    if dex[:4] != b'dex\n':
        print(f"[-] Skipping invalid DEX: {file_path}")
        return

    # SHA-1: file[32:]
    sha1_hash = hashlib.sha1(dex[32:]).digest()
    dex[12:32] = sha1_hash
    print(f"[+] {file_path.name} - SHA-1 updated: {sha1_hash.hex()}")

    # Adler32: file[12:]
    checksum = zlib.adler32(dex[12:]) & 0xffffffff
    dex[8:12] = checksum.to_bytes(4, 'little')
    print(f"[+] {file_path.name} - Adler32 checksum updated: {hex(checksum)}")

    fixed_path = file_path.with_suffix('.fixed.dex')
    with open(fixed_path, 'wb') as f:
        f.write(dex)

    print(f"[+] Fixed DEX saved to: {fixed_path}")

    if not keep_original:
        file_path.unlink()
        fixed_path.rename(file_path)
        print(f"[+] Original deleted, fixed file renamed to: {file_path}")

def process_path(target_path: Path, keep_original: bool):
    if target_path.is_file():
        if target_path.suffix == '.dex':
            fix_dex(target_path, keep_original)
        else:
            print(f"[-] Skipping non-DEX file: {target_path}")
    elif target_path.is_dir():
        dex_files = list(target_path.rglob("*.dex"))
        if not dex_files:
            print("[-] No .dex files found in directory.")
            return
        for dex_file in dex_files:
            fix_dex(dex_file, keep_original)
    else:
        print("[-] Invalid path.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fix checksum and SHA-1 of DEX files.")
    parser.add_argument('-f', '--file', required=True, help="Path to .dex file or directory")
    parser.add_argument('-k', '--keep', action='store_true', help="Keep original .dex file")

    args = parser.parse_args()
    target = Path(args.file)

    if not target.exists():
        print(f"[-] File or directory not found: {target}")
        exit(1)

    process_path(target, args.keep)
