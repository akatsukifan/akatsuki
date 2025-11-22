# akatsuki

Frame interpolation helper to turn low-FPS videos into smoother, higher-FPS output.

## Installation

The project can be installed as a package with a console command:

```bash
pip install .
```

This installs an `akatsuki-interpolate` command you can run anywhere (requires
Python 3.9+ and a system `ffmpeg` binary).

> Tip: in offline or firewalled environments, use `pip install --no-build-isolation .`
> to avoid fetching build dependencies from the internet.

## Usage

### Quickstart (from the project root)

```bash
# view all options
python -m akatsuki_interpolate.cli --help

# interpolate a video to 60 fps in-place next to the source file
python -m akatsuki_interpolate.cli input.mp4 --fps 60
```

### CLI command

```bash
akatsuki-interpolate input.mp4 --fps 60
```

### Direct script invocation

If you prefer to keep it uninstalled, run it directly from the repo:

```bash
python -m akatsuki_interpolate.cli input.mp4 --fps 60
# or the compatibility wrapper
python scripts/interpolate.py input.mp4 --fps 60
```

### Options

- `--fps` sets the target frame rate (default: 60).
- `--output` lets you choose a destination file; otherwise a `_<fps>fps` suffix is used next to the input.
- `--preset` can be `fast`, `balanced`, or `quality` depending on your speed/quality needs.

Ensure `ffmpeg` is available on your system before running the script.

## Packaging

To build a distributable wheel (e.g., to share or upload), run:

```bash
python -m build
```

The wheel will appear under `dist/`; install it with `pip install dist/<wheel>.whl`.
