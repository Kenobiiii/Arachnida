import argparse
from pathlib import Path

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

def print_error(error_msg: str):
    print(f"[❌] {error_msg}")

def print_success(success_msg: str):
    print(f"[✅] {success_msg}")

def is_valid_image(path: Path) -> bool:
    if not path.is_file():
        print_error("file doesn't exist or is not a file")
        return False
    if path.suffix.lower() not in VALID_EXTENSIONS:
        print_error("Invalid suffix")
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

if __name__ == "__main__":
    main()