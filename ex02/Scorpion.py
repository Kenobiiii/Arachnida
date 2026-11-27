import argparse
from pathlib import Path

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')



def main():
    parser = argparse.ArgumentParser(description="EXIF and metadata extractor")
    parser.add_argument("files", nargs="+", help="Images for analizing")
    # nargs="+" expect one or more arguments, 1 es obligatory, "*" expects none or more and "?" expect 0 or 1
    args = parser.parse_args()

    for f in args.files:
        print(f)

if __name__ == "__main__":
    main()