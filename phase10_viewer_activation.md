# Phase 10 — Viewer and Hacker-Lab contract activation

**Status:** the available viewer and Hacker-Lab snapshot/world consumers are implemented and read-only. Module/event activation and live-engine cross-pillar verification remain blocked by absent producer surfaces and the existing CaveSharp build failure.

## Viewer contract activation

Contract mode is the default for [game.html](./renzoverse_vault/renzo-verse/site/game.html). The viewer polls a read-only local API at `/api/world/v1/current` and `/api/telemetry/v1/latest`. Run `python3 -m spine_runtime.viewer_server` from the repository root to serve the static site and expose those endpoints. The API reads the Phase 9 authored catalog and latest snapshot file, validates each against the canonical checked-in Spine schemas, disables response caching, and distinguishes unavailable/malformed source data (503) from invalid contract data (502).

The browser independently checks required v1 fields before changing displayed state. Invalid data leaves the last valid values untouched; the connection indicator reports an error before the first valid snapshot and stale thereafter. World ID mismatch, unsupported schema versions, invalid timestamps, duplicate entity IDs, missing creature values, and non-finite numbers are rejected. Creature markers are keyed by stable `entityId`, not array position.

The HUD consumes world name/ID and authored region names from `world_contract`, and world ID, tick, generation time, and telemetry values from `telemetry_contract`. It does not invent region coordinates, claim entities belong to regions, or render a corruption heatmap without documented grid geometry. Camera movement and keyboard controls remain local presentation behavior. Legacy WebSocket mode remains available only with `?telemetryMode=legacy`; that path does not claim contract validation.

For a live local flow, start CaveSharp with the explicit opt-in and Phase 9 environment paths, then run the viewer server. In Codespaces, bind the viewer server with `python3 -m spine_runtime.viewer_server --host 0.0.0.0` and forward port 8000. This local server is read-only and has no authentication; do not expose it to an untrusted network.

## Hacker-Lab snapshot/world activation

The Hacker-Lab checkout is available alongside Renzoverse at `/workspaces/Renzo-Hacker-Lab`. Its actual consumer surfaces are BIG ANIMAL's `WorldUI` and ClaudeCode's AgentDash cockpit. Both now use the `renzoverse_contracts.SpineContractFeed` read-only client to poll the viewer API's world and latest-snapshot endpoints, validate responses against the canonical schemas, check world identity and tick validity, and report disabled/connecting/live/stale/invalid/unavailable states. The feed permits a tick reset only when `generatedAt` proves a newer simulation run, matching the Phase 9 process-restart semantics. See the [Hacker-Lab integration guide](../Renzo-Hacker-Lab/docs/renzoverse-contract-integration.md).

The AgentDash event panel remains connected only to its existing local event bus. Those stimulus/spike/anomaly/fuzz/defense messages are not `event_contract` world events. No actual module manifests or event endpoint were found, so module/event subscription is deliberately not claimed or fabricated. Commands remain outside scope without a cross-pillar authorization and audit design. Hacker-Lab also has unrelated runtime import blockers in the full ClaudeCode and BIG ANIMAL launch paths; its contract feed and dashboard rendering surfaces are tested independently.

Both repos now have a deterministic cross-pillar integration test that serves the shared world and telemetry contracts through the actual Renzoverse API and reads them through the actual Hacker-Lab client. It verifies matching world ID and tick. The test is not a live CaveSharp end-to-end run.

## Verification

```sh
python3 -m unittest tests.test_viewer_server
node --test tests/contract_viewer_validation.test.mjs
python3 -m unittest discover -s spine_runtime/harness -p '*.py' -v
cd ../Renzo-Hacker-Lab
python3 -m unittest discover -s tests -v
```

The server/API, browser validator, Hacker-Lab consumer, dashboard status surfaces, and deterministic shared-transport flow are tested. No automated browser/DOM run or live full-engine-to-viewer-and-Hacker-Lab session is claimed. The full CaveSharp build remains independently blocked by existing compile errors documented in the Phase 9 report. Therefore **Phase 10 is not complete** until module/event producers and consumer requirements are resolved where needed and a live CaveSharp cross-pillar flow is verified.
