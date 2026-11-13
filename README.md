# Conversor NAM para Helix Rack

Aplicacion local y experimental para el firmware NAM adaptado al Helix Rack.
Solo convierte modelos **WaveNet A2 Lite de 3 canales**; tambien acepta un
SlimmableContainer que incluya ese modelo. Los modelos NAM de otras
arquitecturas no son compatibles. No se suben archivos a internet.

## Usar en Windows

1. Abre `Iniciar.bat` con doble clic.
2. Selecciona el `.nam`, pulsa **Convertir y guardar** y elige donde guardar
   el `.wav`. Confirma antes de reemplazar un archivo existente.
3. En HX Edit, importa el WAV en un espacio User IR libre; respalda los IR
   existentes antes de reemplazarlos. En el Rack agrega **Amp > NAM > NAM A2
   Lite** y ajusta **Model** al numero de ese espacio.

El WAV contiene datos del modelo, no es audio ni una respuesta a impulso
convencional. Para probarlo, usa volumen bajo y un preset sencillo. Edita el
preset NAM en el Rack: HX Edit podria eliminar el bloque al reescribirlo.
La reproduccion NAM y la estabilidad del port en Rack todavia requieren
validacion en hardware.

El conversor conserva el ajuste automatico de nivel del proyecto original
cuando el archivo tiene `input_level_dbu`; esta calibracion se basa en una
estimacion para HX Stomp y no se ha verificado en Rack. Tambien avisa si la
captura no fue entrenada a 48 kHz.

## Entorno virtual

El entorno `.venv` se creo en este equipo. Tkinter y las demas dependencias
son parte de Python: no se necesitan paquetes externos ni instalar librerias
con pip. Si mueves el proyecto a otro equipo, instala Python con Tkinter y
recrea el entorno en la carpeta del proyecto:

```powershell
python -m venv .venv
```

Tambien se puede abrir con `.venv\Scripts\python.exe app.py`.

## Creditos

El conversor y sus modulos en `tools` proceden de `helix-rack-nam-lite`;
se incluyen para que este proyecto sea independiente. Se modifico la lectura
para aceptar archivos `.NAM` y JSON UTF-8. Consulta `LICENSE` y `NOTICE`.
