"""Exercise the viewer's read-only contract endpoints over HTTP."""

import json
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path
from unittest import TestCase

from spine_runtime.mock_bus import MockBus
from spine_runtime.viewer_server import create_server


class ViewerServerTests(TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        root = Path(self.temp_directory.name)
        self.telemetry_path = root / "latest.json"
        self.world_path = root / "world.json"
        self.site_path = root / "site"
        self.site_path.mkdir()
        (self.site_path / "index.html").write_text("viewer", encoding="utf-8")

        bus = MockBus()
        self.snapshot = bus.read_channel("telemetry_stream")[0]
        self.world = bus.read_channel("world_state")[0]
        self.world["worldId"] = self.snapshot["worldId"]
        self.write_telemetry(self.snapshot)
        self.world_path.write_text(json.dumps(self.world), encoding="utf-8")

        self.server = create_server(
            "127.0.0.1",
            0,
            site_dir=self.site_path,
            telemetry_path=self.telemetry_path,
            world_path=self.world_path,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp_directory.cleanup()

    def write_telemetry(self, snapshot: object) -> None:
        self.telemetry_path.write_text(json.dumps(snapshot), encoding="utf-8")

    def get(self, path: str) -> tuple[int, dict[str, str], bytes]:
        try:
            response = urllib.request.urlopen(f"{self.base_url}{path}", timeout=2)
        except urllib.error.HTTPError as response:
            with response:
                return response.code, dict(response.headers), response.read()
        with response:
            return response.status, dict(response.headers), response.read()

    def test_telemetry_endpoint_returns_schema_validated_latest_snapshot(self) -> None:
        status, headers, body = self.get("/api/telemetry/v1/latest")

        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(json.loads(body), self.snapshot)

    def test_world_endpoint_returns_schema_validated_authored_catalog(self) -> None:
        status, _, body = self.get("/api/world/v1/current")

        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), self.world)

    def test_invalid_contract_is_rejected_not_returned_as_fresh_data(self) -> None:
        invalid_snapshot = dict(self.snapshot, tick=-1)
        self.write_telemetry(invalid_snapshot)

        status, _, body = self.get("/api/telemetry/v1/latest")

        self.assertEqual(status, 502)
        self.assertEqual(json.loads(body)["error"], "invalid_contract")

    def test_missing_snapshot_reports_unavailable(self) -> None:
        self.telemetry_path.unlink()

        status, _, body = self.get("/api/telemetry/v1/latest")

        self.assertEqual(status, 503)
        self.assertEqual(json.loads(body)["error"], "source_unavailable")

    def test_static_viewer_is_served_from_configured_site_only(self) -> None:
        status, _, body = self.get("/")

        self.assertEqual(status, 200)
        self.assertEqual(body, b"viewer")
