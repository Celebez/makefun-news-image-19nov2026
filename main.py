"""Copy and validate the finished PNG in the offline grading sandbox."""
from pathlib import Path
import os
import shutil
import struct

bot = Path(os.environ.get("MAKEFUN_BOT_DIR", str(Path(__file__).resolve().parent)))
output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
source = bot / "entry.png"
if not source.is_file():
    raise FileNotFoundError(f"Required artwork is missing: {source.name}")

image = source.read_bytes()
if len(image) < 45 or len(image) > 1_048_576:
    raise ValueError("The PNG must be complete and no larger than 1 MiB.")
if image[:8] != b"\x89PNG\r\n\x1a\n" or image[-8:] != b"IEND\xaeB`\x82":
    raise ValueError("The entry must be one complete PNG file.")
width, height = struct.unpack(">II", image[16:24])
if width > 1024 or height > 1024 or not width or not height:
    raise ValueError("The PNG dimensions must be non-empty and at most 1024 × 1024.")

output.mkdir(parents=True, exist_ok=True)
target = output / "entry.png"
target.write_bytes(image)
