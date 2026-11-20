"""Contracts for the reproducible news-image copier."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "story-data.json").read_text(encoding="utf-8"))


class EditorialDataTests(unittest.TestCase):
    def test_exactly_forty_distinct_stories_span_six_continents(self):
        stories = DATA["stories"]
        self.assertEqual(len(stories), 40)
        self.assertEqual([story["id"] for story in stories], list(range(1, 41)))
        self.assertEqual(
            {story["continent"] for story in stories},
            {"North America", "South America", "Europe", "Africa", "Asia", "Oceania"},
        )
        self.assertTrue(all(len(story["headline"]) <= 72 and story.get("headline") and story.get("source") and story.get("url", "").startswith("https://") for story in stories))


class ProgramContractTests(unittest.TestCase):
    def test_entry_copies_the_png_byte_for_byte_on_two_clean_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "entry.png"
            shutil.copyfile(ROOT / "entry.png", source)
            hashes = []
            for run in range(2):
                output = root / f"output{run}"
                output.mkdir()
                result = subprocess.run(
                    [sys.executable, str(ROOT / "main.py")],
                    env={**__import__("os").environ, "MAKEFUN_BOT_DIR": str(root), "MAKEFUN_OUTPUT_DIR": str(output)},
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                target = output / "entry.png"
                self.assertTrue(target.is_file())
                hashes.append(hashlib.sha256(target.read_bytes()).hexdigest())
            self.assertEqual(hashes[0], hashes[1])

    def test_artwork_is_a_whole_png_under_competition_limits(self):
        data = (ROOT / "entry.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertGreaterEqual(len(data), 45)
        self.assertLessEqual(len(data), 1_048_576)
        self.assertTrue(data.endswith(b"IEND\xaeB`\x82"))
        width, height = struct.unpack(">II", data[16:24])
        self.assertLessEqual(width, 1024)
        self.assertLessEqual(height, 1024)
        self.assertGreater(width, 900)
        self.assertEqual(width, height)


if __name__ == "__main__":
    unittest.main()
