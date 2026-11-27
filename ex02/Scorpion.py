import argparse
from datetime import datetime
from pathlib import Path


VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

def print_error(error_msg: str):
    print(f"[❌] {error_msg}")

def print_success(success_msg: str):
    print(f"[✅] {success_msg}")

def show_file_info(img_path: Path):
    img_stat = img_path.stat()
    print(f"====== {img_path.name} ======")
    print(f"Size:           {img_stat.st_size / 1024**2:.2f} MB") # / 1024**2:.2f transform in MegaBytes and get twto decimals
    print_error("Verificar creacion archivo")
    print(f"Created:        {datetime.fromtimestamp(img_stat.st_ctime).strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Modified:       {datetime.fromtimestamp(img_stat.st_mtime).strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Accessed:       {datetime.fromtimestamp(img_stat.st_atime).strftime('%d/%m/%Y %H:%M:%S')}")

def is_valid_image(path: Path) -> bool:
    if not path.is_file():
        print_error(f"file doesn't exist or is not a file {path}")
        return False
    if path.suffix.lower() not in VALID_EXTENSIONS:
        print_error(f"Invalid suffix {path}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="EXIF and metadata extractor")
    parser.add_argument("files", nargs="+", help="Images for analizing")
    # nargs="+" expect one or more arguments, 1 es obligatory, "*" expects none or more and "?" expect 0 or 1
    args = parser.parse_args()

    for f in args.files:
        img_path = Path(f)
        if not is_valid_image(img_path):
            continue
        print_success(f"OK: {img_path.name}")
        show_file_info(img_path)

if __name__ == "__main__":
    main()