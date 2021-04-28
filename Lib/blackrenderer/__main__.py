import argparse
import os
import pathlib
from .render import renderText


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font", metavar="FONT", type=existingFilePath, help="a font")
    parser.add_argument("text", metavar="TEXT", help="a string")
    parser.add_argument(
        "output",
        metavar="OUTPUT",
        type=outputFilePath,
        help="an output file name, with .png or .svg extension, "
        "or '-', to print SVG to stdout",
    )
    parser.add_argument("--font-size", type=float, default=250)
    parser.add_argument("--margin", type=float, default=20)
    args = parser.parse_args()
    renderText(
        args.font, args.text, args.output, fontSize=args.font_size, margin=args.margin
    )


def existingFilePath(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"file does not exist: '{path}'")
    elif not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"path is not a file: '{path}'")
    return pathlib.Path(path).resolve()


def outputFilePath(path):
    if path == "-":
        return None
    path = pathlib.Path(path).resolve()
    if path.suffix not in {".png", ".svg"}:
        raise argparse.ArgumentTypeError(
            f"path does not have the right extension; should be .png or .svg: "
            f"'{path}'"
        )
    return path


if __name__ == "__main__":
    main()