#!/usr/bin/env python3
"""News in one image — Tuesday 17 November 2026.

Standard-library-only entry: copies the pre-rendered front page
(entry.png, committed in this repository) to the output directory.
The sandbox installs nothing before running, so this program uses
only os / shutil / sys. No network access. Fully deterministic:
two runs write byte-identical copies of entry.png to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

The image is a 1024x1024 newspaper front page summarising the real
world news of Tuesday 17 November 2026 (six stories: Kerch Bridge,
Trump in Manila, Hormuz tankers, JPMorgan outage, Vulcan rocket,
Nvidia earnings), drawn by code in an earlier session and committed
as entry.png.

SPDX-License-Identifier: MIT
"""

import os
import shutil
import struct
import sys

SOURCE_NAME = "entry.png"
MAX_BYTES = 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path):
    """Read width/height from the PNG IHDR chunk (stdlib only).

    Returns (width, height), or None if the file is not a valid PNG.
    """
    try:
        with open(path, "rb") as fh:
            header = fh.read(33)
    except OSError:
        return None
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        return None
    # IHDR chunk: length (4) + type "IHDR" (4) + width (4) + height (4).
    if header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not out_dir.strip():
        print("error: MAKEFUN_OUTPUT_DIR is set but empty", file=sys.stderr)
        return 1
    out_dir = os.path.abspath(os.path.expanduser(out_dir))
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create output dir {out_dir}: {exc}",
              file=sys.stderr)
        return 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(script_dir, SOURCE_NAME)
    if not os.path.isfile(src):
        print(f"error: source image not found: {src}", file=sys.stderr)
        return 1

    path = os.path.join(out_dir, "entry.png")
    try:
        shutil.copyfile(src, path)
    except OSError as exc:
        print(f"error: cannot write {path}: {exc}", file=sys.stderr)
        return 1

    size = os.path.getsize(path)
    if size > MAX_BYTES:
        print(f"error: {path} is {size} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    dims = png_dimensions(path)
    if dims is None:
        print(f"error: {path} is not a valid PNG", file=sys.stderr)
        return 1
    print(f"wrote {path} ({dims[0]}x{dims[1]}, {size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
