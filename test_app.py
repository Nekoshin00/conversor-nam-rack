import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tkinter as tk
import unittest
from unittest import mock

import app

sys.path.insert(0, str(Path(__file__).parent / "tools" / "sharc"))
import nam_lite


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.model = {
            "architecture": "WaveNet",
            "config": {"layers": [{"channels": 3}]},
            "weights": nam_lite.placeholder(),
            "metadata": {"input_level_dbu": 15, "name": "captura ñ"},
            "sample_rate": 48000,
        }

    def write_model(self, name, model=None):
        path = self.directory / name
        path.write_text(json.dumps(self.model if model is None else model, ensure_ascii=False), encoding="utf-8")
        return path

    def test_conversion_matches_existing_converter_and_handles_uppercase(self):
        source = self.write_model("captura ñ.nam")
        uppercase = self.write_model("captura ñ.NAM")
        output = self.directory / "result.wav"
        baseline = self.directory / "baseline.wav"
        result = subprocess.run(
            [sys.executable, str(app.CONVERTER), str(source), "-o", str(baseline)],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"}, check=True,
        )
        details = app.convert_model(uppercase, output)
        self.assertIn("input level 15", result.stdout)
        self.assertIn("input level 15", details)
        self.assertIn(str(output), details)
        self.assertNotIn(".nam-rack-", details)
        self.assertEqual(output.read_bytes(), baseline.read_bytes())

    def test_incompatible_model_preserves_existing_output(self):
        source = self.write_model("bad.NAM", {"architecture": "Other", "config": {}, "weights": []})
        output = self.directory / "result.wav"
        output.write_bytes(b"existing")
        with self.assertRaisesRegex(ValueError, "No se pudo convertir"):
            app.convert_model(source, output)
        self.assertEqual(output.read_bytes(), b"existing")
        self.assertEqual(list(self.directory.glob(".nam-rack-*")), [])

    def test_warning_is_visible_and_invalid_extension_rejected(self):
        self.model["sample_rate"] = 44100
        source = self.write_model("rate.nam")
        with self.assertRaisesRegex(ValueError, "terminar en .wav"):
            app.convert_model(source, self.directory / "wrong.nam")
        self.assertIn("warning: trained at 44100", app.convert_model(source, self.directory / "result.wav"))

    def test_gui_selection_and_conversion(self):
        source = self.write_model("model.nam")
        output = self.directory / "result.wav"
        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        gui = app.Application(root)
        with mock.patch.object(app.filedialog, "askopenfilename", return_value=str(source)):
            gui.choose_source()
        with mock.patch.object(app.filedialog, "asksaveasfilename", return_value=str(output)), \
                mock.patch.object(app.messagebox, "showinfo") as info:
            gui.convert()
        self.assertTrue(output.is_file())
        self.assertIn("Conversión terminada", gui.status.get())
        info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
