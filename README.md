# akatsuki

Frame interpolation helper to turn low-FPS videos into smoother, higher-FPS output.

## Usage

The `scripts/interpolate.py` wrapper relies on `ffmpeg`'s `minterpolate` filter.

```bash
python scripts/interpolate.py input.mp4 --fps 60
```

- `--fps` sets the target frame rate (default: 60).
- `--output` lets you choose a destination file; otherwise a `_<fps>fps` suffix is used next to the input.
- `--preset` can be `fast`, `balanced`, or `quality` depending on your speed/quality needs.

Ensure `ffmpeg` is available on your system before running the script.
