"""Serve the cave viewer and validated, read-only Spine v1 endpoints."""

from __future__ import annotations

import argparse
import json
import logging
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE_DIR = ROOT / "renzoverse_vault" / "renzo-verse" / "site"
DEFAULT_WORLD_PATH = ROOT / "shared" / "worlds" / "cavesharp.json"
DEFAULT_TELEMETRY_PATH = ROOT / "shared" / "telemetry" / "cavesharp.v1.json"
LOGGER = logging.getLogger("spine_runtime.viewer_server")


class ViewerRequestHandler(SimpleHTTPRequestHandler):
    def __init__(
        self,
        *args: Any,
        directory: str,
        validator: ContractValidator,
        telemetry_path: Path,
        world_path: Path,
        **kwargs: Any,
    ) -> None:
        self.validator = validator
        self.telemetry_path = telemetry_path
        self.world_path = world_path
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/telemetry/v1/latest":
            self._serve_contract_file(self.telemetry_path, "telemetry_contract")
            return
        if path == "/api/world/v1/current":
            self._serve_contract_file(self.world_path, "world_contract")
            return
        super().do_GET()

    def _serve_contract_file(self, path: Path, contract_name: str) -> None:
        try:
            message = json.loads(path.read_text(encoding="utf-8"))
            self.validator.validate(contract_name, message)
        except ContractValidationError as exc:
            LOGGER.warning("Rejected invalid %s source %s: %s", contract_name, path, exc)
            self._send_json(
                502,
                {
                    "error": "invalid_contract",
                    "contract": contract_name,
                    "message": str(exc),
                },
            )
            return
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            LOGGER.info("Could not read %s source %s: %s", contract_name, path, exc)
            self._send_json(
                503,
                {
                    "error": "source_unavailable",
                    "contract": contract_name,
                    "message": "Contract source is unavailable or malformed.",
                },
            )
            return

        self._send_json(200, message)

    def _send_json(self, status: int, document: dict[str, Any]) -> None:
        body = json.dumps(document, allow_nan=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def create_server(
    host: str,
    port: int,
    site_dir: Path = DEFAULT_SITE_DIR,
    telemetry_path: Path = DEFAULT_TELEMETRY_PATH,
    world_path: Path = DEFAULT_WORLD_PATH,
) -> ThreadingHTTPServer:
    site_dir = site_dir.resolve()
    telemetry_path = telemetry_path.resolve()
    world_path = world_path.resolve()
    if not site_dir.is_dir():
        raise FileNotFoundError(f"Viewer site directory does not exist: {site_dir}")

    validator = ContractValidator()

    def handler(*args: Any, **kwargs: Any) -> ViewerRequestHandler:
        return ViewerRequestHandler(
            *args,
            directory=str(site_dir),
            validator=validator,
            telemetry_path=telemetry_path,
            world_path=world_path,
            **kwargs,
        )

    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve the cave viewer and validated Spine v1 read-only endpoints."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE_DIR)
    parser.add_argument("--telemetry", type=Path, default=DEFAULT_TELEMETRY_PATH)
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD_PATH)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    server = create_server(args.host, args.port, args.site, args.telemetry, args.world)
    LOGGER.info("Viewer listening at http://%s:%s", args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Stopping viewer server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
