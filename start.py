from __future__ import annotations

import argparse
from pathlib import Path

from app.gui import launch_gui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch the local Lecture Reconstruction Studio GUI."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the local GUI server.")
    parser.add_argument("--port", default=8181, type=int, help="Port to bind the local GUI server.")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional path to a config YAML file.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the browser automatically after launch.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    print(f"Starting Lecture Reconstruction Studio at http://{args.host}:{args.port}")
    launch_gui(
        config_path=args.config,
        host=args.host,
        port=args.port,
        auto_open_browser=not args.no_browser,
    )


if __name__ == "__main__":
    main()
