"""Bridge CaveSharp's legacy WebSocket telemetry to the Spine v1 snapshot file."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import tempfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_URL = "ws://localhost:8181/telemetry/"
DEFAULT_WORLD_CATALOG = ROOT / "shared" / "worlds" / "cavesharp.json"
DEFAULT_OUTPUT = ROOT / "shared" / "telemetry" / "cavesharp.v1.json"
LOGGER = logging.getLogger("spine_runtime.telemetry_bridge")


def _field(source: Mapping[str, Any], name: str) -> Any:
    for key, value in source.items():
        if isinstance(key, str) and key.casefold() == name.casefold():
            return value
    raise ValueError(f"Legacy telemetry is missing '{name}'.")


def build_snapshot(
    legacy: Mapping[str, Any],
    world_id: str,
    tick: int,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Map a legacy CaveSharp packet into the complete Spine v1 snapshot shape."""
    if not isinstance(legacy, Mapping):
        raise ValueError("Legacy telemetry must be a JSON object.")
    if not world_id.strip():
        raise ValueError("world_id must not be empty.")
    if isinstance(tick, bool) or tick < 0:
        raise ValueError("tick must be a non-negative integer.")

    generated_at = generated_at or datetime.now(timezone.utc)
    if generated_at.tzinfo is None:
        raise ValueError("generated_at must include a timezone.")

    creatures = _field(legacy, "creatures")
    if not isinstance(creatures, list):
        raise ValueError("Legacy telemetry 'creatures' must be an array.")

    normalized_creatures = []
    for index, creature in enumerate(creatures):
        if not isinstance(creature, Mapping):
            raise ValueError(f"Creature at index {index} must be an object.")
        normalized_creatures.append(
            {
                "entityId": _field(creature, "entityId"),
                "name": _field(creature, "name"),
                "health": _field(creature, "health"),
                "aggression": _field(creature, "aggression"),
                "hunger": _field(creature, "hunger"),
                "x": _field(creature, "x"),
                "y": _field(creature, "y"),
                "corruptionExposure": _field(creature, "corruptionExposure"),
                "isAfraid": _field(creature, "isAfraid"),
            }
        )

    snapshot = {
        "schemaVersion": "1.0.0",
        "worldId": world_id,
        "tick": tick,
        "generatedAt": generated_at.astimezone(timezone.utc).isoformat(),
        "threat": _field(legacy, "threat"),
        "cta": _field(legacy, "cta"),
        "corruption": _field(legacy, "corruption"),
        "ctaBoss": _field(legacy, "ctaBoss"),
        "directive": _field(legacy, "directive"),
        "creatures": normalized_creatures,
        "corruptionGrid": _field(legacy, "corruptionGrid"),
    }
    try:
        snapshot["weather"] = _field(legacy, "weather")
    except ValueError:
        pass
    return snapshot


def write_snapshot(path: Path, snapshot: Mapping[str, Any]) -> None:
    """Atomically replace the latest snapshot so readers never see partial JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name
            json.dump(snapshot, temporary_file, allow_nan=False, separators=(",", ":"))
            temporary_file.write("\n")
        os.replace(temporary_path, path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)


def _verify_world_id(world_id: str, catalog_path: Path) -> None:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog.get("worldId") != world_id:
        raise ValueError(
            f"World ID {world_id!r} does not match catalog {catalog_path}: "
            f"{catalog.get('worldId')!r}."
        )


async def run_bridge(
    url: str,
    world_id: str,
    output_path: Path,
    reconnect_seconds: float = 1.0,
) -> None:
    import websockets

    validator = ContractValidator()
    tick = 0
    while True:
        try:
            async with websockets.connect(url, max_size=4 * 1024 * 1024) as socket:
                LOGGER.info("Connected to CaveSharp telemetry at %s", url)
                async for message in socket:
                    try:
                        legacy = json.loads(message)
                        candidate_tick = tick + 1
                        snapshot = build_snapshot(legacy, world_id, candidate_tick)
                        validator.validate("telemetry_contract", snapshot)
                        write_snapshot(output_path, snapshot)
                        tick = candidate_tick
                        LOGGER.debug("Published Spine v1 snapshot tick %d", tick)
                    except (
                        json.JSONDecodeError,
                        ContractValidationError,
                        TypeError,
                        ValueError,
                    ) as exc:
                        LOGGER.warning("Skipped invalid CaveSharp packet: %s", exc)
        except (OSError, websockets.exceptions.WebSocketException) as exc:
            LOGGER.warning("Telemetry connection unavailable: %s", exc)
        await asyncio.sleep(reconnect_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--world-id", default=os.environ.get("RENZOVERSE_CONTRACT_WORLD_ID")
    )
    parser.add_argument("--world-catalog", type=Path, default=DEFAULT_WORLD_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reconnect-seconds", type=float, default=1.0)
    args = parser.parse_args()
    if not args.world_id:
        parser.error("set --world-id or RENZOVERSE_CONTRACT_WORLD_ID")
    if args.reconnect_seconds <= 0:
        parser.error("--reconnect-seconds must be greater than zero")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _verify_world_id(args.world_id, args.world_catalog)
    try:
        asyncio.run(
            run_bridge(args.url, args.world_id, args.output, args.reconnect_seconds)
        )
    except KeyboardInterrupt:
        LOGGER.info("Stopping telemetry bridge.")


if __name__ == "__main__":
    main()