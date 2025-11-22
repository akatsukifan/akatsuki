#!/usr/bin/env python3
"""Command-line helper to interpolate video frame rates via ffmpeg."""

from __future__ import annotations

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
    parser.add_argument(
        "--video-codec",
        default="libx264",
        help="Video codec to use for the encoded output (default: libx264).",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=18,
        help=(
            "CRF quality level for the video encoder; lower is higher quality. "
            "Common range is 18-28 (default: 18)."
        ),
    )
    parser.add_argument(
        "--encode-preset",
        choices=[
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ],
        default="medium",
        help="Encoder speed/efficiency trade-off passed to the video codec (default: medium).",
    )
    return parser.parse_args()


def ensure_ffmpeg_available() -> None:
    """Exit with a helpful message if ffmpeg is missing."""
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required but was not found in PATH.")


def build_filter(fps: float, preset: str) -> str:
    """Construct the minterpolate filter chain for the chosen preset."""
    base = [f"fps={fps}", "mi_mode=mci"]
    tuning = {
        "fast": ["mc_mode=aobmc"],
        # Balanced favors smoothness without the more expensive vsbmc pass.
        "balanced": ["mc_mode=aobmc", "me_mode=bidir"],
        "quality": ["mc_mode=aobmc", "me_mode=bidir", "vsbmc=1"],
    }
    return "minterpolate=" + ":".join(base + tuning[preset])


def determine_output_path(input_path: Path, fps: float, explicit_output: Path | None) -> Path:
    """Return an output path, adding a `<fps>fps` suffix if none was provided."""
    if explicit_output:
        return explicit_output

    stem = input_path.stem
    suffix = input_path.suffix or ".mp4"
    return input_path.with_name(f"{stem}_{int(fps)}fps{suffix}")


def interpolate_video(
    input_path: Path,
    output_path: Path,
    fps: float,
    preset: str,
    video_codec: str,
    crf: int,
    encode_preset: str,
) -> None:
    """Run ffmpeg with the configured minterpolate filter to create the output video."""
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    if input_path.resolve() == output_path.resolve():
        raise SystemExit("Output path must be different from the input path.")

    filter_chain = build_filter(fps, preset)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        filter_chain,
        "-c:v",
        video_codec,
        "-preset",
        encode_preset,
        "-crf",
        str(crf),
        "-c:a",
        "copy",
        str(output_path),
    ]

    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    args = parse_args()
    ensure_ffmpeg_available()
    if args.fps <= 0:
        raise SystemExit("--fps must be a positive number.")
    if args.crf < 0:
        raise SystemExit("--crf must be zero or a positive integer.")
    output_path = determine_output_path(args.input, args.fps, args.output)
    interpolate_video(
        args.input,
        output_path,
        args.fps,
        args.preset,
        args.video_codec,
        args.crf,
        args.encode_preset,
    )


if __name__ == "__main__":
    main()
