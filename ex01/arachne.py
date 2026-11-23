import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Extractor e inspector de recursos web")
    parser.add_argument("url", type=str, help="Dir web")
    parser.add_argument("-r", "--recursive", action="store_true", help="Enables recursive image download")
    parser.add_argument("-l", "--level", type=int, default=5, help="Max recursive level")
    parser.add_argument("-p", "--path", type=str, default="./data/", help="Path where the downloaded images will be stored")
    args = parser.parse_args()

    directory = Path(args.path);
    directory.mkdir(parents=True, exist_ok=True)

    print("--- Configuración recibida ---")
    print(f"URL Objetivo: {args.url}")
    print(f"Modo Recursivo: {args.recursive}")
    print(f"Profundidad (-l): {args.level}")
    print(f"Ruta de destino (-p): {args.path}")
    print(f"Directorio de destio: {directory.resolve()}")

if __name__ == "__main__":
    main()