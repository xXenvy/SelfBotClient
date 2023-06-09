import argparse

from .client import Client


def version() -> None:
    print(Client.__version__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="asynccore")
    parser.add_argument(
        "-v",
        "--version",
        action="store_true"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args: argparse.Namespace = parse_args()
    if args.version:
        version()
