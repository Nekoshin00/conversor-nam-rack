import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


CONVERTER = Path(__file__).resolve().parent / "tools" / "nam2ir.py"


def convert_model(source: Path, destination: Path) -> str:
    if source.suffix.lower() != ".nam" or not source.is_file():
        raise ValueError("Selecciona un archivo .nam existente.")
    if destination.suffix.lower() != ".wav":
        raise ValueError("El archivo de salida debe terminar en .wav.")
    if source.resolve() == destination.resolve():
        raise ValueError("El archivo de salida no puede ser el archivo original.")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    with tempfile.NamedTemporaryFile(
        prefix=".nam-rack-", suffix=".wav", dir=destination.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        result = subprocess.run(
            [sys.executable, str(CONVERTER), str(source), "-o", str(temporary_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode:
            details = (result.stderr + "\n" + result.stdout).strip()
            raise ValueError(
                "No se pudo convertir la captura. Verifica que sea un modelo "
                "WaveNet A2 Lite de 3 canales.\n\n" + (details or "Error sin detalles.")
            )
        os.replace(temporary_path, destination)
        return (result.stderr + "\n" + result.stdout).strip().replace(str(temporary_path), str(destination))
    finally:
        temporary_path.unlink(missing_ok=True)


class Application:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Conversor NAM para Helix Rack")
        root.minsize(580, 280)
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root, padding=20)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text="Conversor NAM para Helix Rack", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            frame,
            text="Convierte capturas WaveNet A2 Lite de 3 canales a WAV para User IR.",
            wraplength=560,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 18))
        ttk.Label(frame, text="Archivo NAM:").grid(row=2, column=0, sticky="w")
        self.source = tk.StringVar()
        ttk.Entry(frame, textvariable=self.source, state="readonly").grid(
            row=3, column=0, sticky="ew", padx=(0, 8), pady=(4, 12)
        )
        ttk.Button(frame, text="Buscar...", command=self.choose_source).grid(row=3, column=1, pady=(4, 12))
        ttk.Button(frame, text="Convertir y guardar...", command=self.convert).grid(
            row=4, column=0, sticky="w", pady=(0, 12)
        )
        self.status = tk.StringVar(value="Selecciona una captura para comenzar.")
        ttk.Label(frame, textvariable=self.status, wraplength=560).grid(
            row=5, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            frame,
            text="El WAV transporta datos NAM; impórtalo en User IR y selecciona su número en el bloque NAM del Rack.",
            wraplength=560,
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(15, 0))

    def choose_source(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self.root,
            title="Seleccionar captura NAM",
            filetypes=[("Capturas NAM", "*.nam"), ("Todos los archivos", "*.*")],
        )
        if selected:
            self.source.set(selected)
            self.status.set("Captura seleccionada. Pulsa Convertir y guardar.")

    def convert(self) -> None:
        if not self.source.get():
            messagebox.showwarning("Selecciona una captura", "Primero selecciona un archivo .nam.", parent=self.root)
            return
        source = Path(self.source.get())
        destination = filedialog.asksaveasfilename(
            parent=self.root,
            title="Guardar WAV para User IR",
            initialdir=str(source.parent),
            initialfile=source.stem + " - NAM A2 Lite.wav",
            defaultextension=".wav",
            filetypes=[("Archivo WAV", "*.wav")],
            confirmoverwrite=True,
        )
        if not destination:
            return
        self.status.set("Convirtiendo...")
        self.root.update_idletasks()
        try:
            details = convert_model(source, Path(destination))
        except (OSError, ValueError) as exc:
            self.status.set("La conversión falló.")
            messagebox.showerror("Error de conversión", str(exc), parent=self.root)
            return
        self.status.set("Conversión terminada: " + destination)
        messagebox.showinfo(
            "Conversión terminada",
            "Archivo creado:\n" + destination
            + "\n\nImporta el WAV en un espacio User IR libre y elige ese número "
            "en Model del bloque NAM del Rack."
            "\n\nEl ajuste automático de nivel usa una referencia de Stomp no verificada en Rack."
            "\n\nDetalles del conversor:\n" + details,
            parent=self.root,
        )


def main() -> None:
    root = tk.Tk()
    Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
