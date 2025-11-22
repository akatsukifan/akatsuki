#!/usr/bin/env python3
"""Frame interpolation helper around ffmpeg.

This script upsamples a video's frame rate using ffmpeg's ``minterpolate``
filter. It is intended to be a lightweight wrapper that validates inputs and
constructs a sensible command for converting low-FPS footage to smoother
output.
"""

import argparse
import shutil
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upsample a video's frame rate using ffmpeg's minterpolate filter.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the source video.",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=60.0,
        help="Target frame rate for the output video (default: 60).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Destination file path. If omitted, a new file is created next to "
            "the input with an appended target FPS suffix."
        ),
    )
    parser.add_argument(
        "--preset",
        choices=["fast", "balanced", "quality"],
        default="balanced",
        help=(
            "Interpolation tuning: 'fast' favors speed, 'quality' favors smoothness, "
            "and 'balanced' offers a middle ground."
        ),
    )
    return parser.parse_args()


def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required but was not found in PATH.")


def build_filter(fps: float, preset: str) -> str:
    common = [f"fps={fps}", "mi_mode=mci"]
    if preset == "fast":
        common.extend(["mc_mode=aobmc", "me_mode=bidir"])
    elif preset == "quality":
        common.extend(["mc_mode=aobmc", "me_mode=bidir", "vsbmc=1"])
    else:
        common.extend(["mc_mode=aobmc", "me_mode=bidir", "vsbmc=1"])
    return "minterpolate=" + ":".join(common)


def determine_output_path(input_path: Path, fps: float, explicit_output: Path | None) -> Path:
    if explicit_output:
        return explicit_output

    stem = input_path.stem
    suffix = input_path.suffix or ".mp4"
    return input_path.with_name(f"{stem}_{int(fps)}fps{suffix}")


def interpolate_video(input_path: Path, output_path: Path, fps: float, preset: str) -> None:
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    filter_chain = build_filter(fps, preset)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        filter_chain,
        "-c:a",
        "copy",
        str(output_path),
    ]

    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    args = parse_args()
    ensure_ffmpeg_available()
    output_path = determine_output_path(args.input, args.fps, args.output)
    interpolate_video(args.input, output_path, args.fps, args.preset)


if __name__ == "__main__":
    main()
