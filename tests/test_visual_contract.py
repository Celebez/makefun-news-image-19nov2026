"""Regression coverage for the evidence-driven visual-storytelling revision."""
import hashlib
import io
import json
from pathlib import Path
import unittest

from PIL import Image, ImageDraw
import renderer

ROOT = Path(__file__).resolve().parents[1]
STORIES = json.loads((ROOT / "story-data.json").read_text())["stories"]


class VisualStorytellingTests(unittest.TestCase):
    def test_each_featured_event_has_distinct_original_art(self):
        hashes = set()
        for story in STORIES[:15]:
            image = Image.new("RGB", (300, 100), renderer.P)
            renderer.event_art(ImageDraw.Draw(image), (0, 0, 299, 99), story)
            hashes.add(hashlib.sha256(image.tobytes()).hexdigest())
            small = Image.new("RGB", (150, 45), renderer.P)
            renderer.event_art(ImageDraw.Draw(small), (0, 0, 149, 44), story)
            self.assertTrue(story["display_headline"])
            self.assertLessEqual(len(story["display_headline"]), 60)
        self.assertEqual(len(hashes), 15)

    def test_render_matches_committed_artwork_without_silent_overflow(self):
        # build raises if a featured headline, summary or art label does not fit.
        output = io.BytesIO()
        renderer.build().save(output, format="PNG", optimize=True, compress_level=9)
        self.assertEqual(output.getvalue(), (ROOT / "entry.png").read_bytes())

    def test_climate_illustration_remains_a_draft_and_court_names_rohingya(self):
        climate, court = STORIES[2], STORIES[1]
        self.assertIn("draft", climate["display_headline"].lower())
        self.assertIn("continue", climate["display_dek"].lower())
        self.assertIn("Rohingya", court["display_dek"])


if __name__ == "__main__":
    unittest.main()
