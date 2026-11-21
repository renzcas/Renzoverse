# Renzos-Cave

Renzos-Cave is the 3D gameworld in Renzoverse. The current prototype lets you explore a cave as Trog-Croman and displays live state from CaveSharp-OS.

## Run locally

From the repository root, configure and start CaveSharp-OS with the Phase 9 v1 output enabled:

```sh
export RENZOVERSE_CONTRACT_TELEMETRY_ENABLED=true
export RENZOVERSE_CONTRACT_WORLD_ID=renzoverse.cavesharp.primary
export RENZOVERSE_WORLD_CATALOG="$PWD/shared/worlds/cavesharp.json"
export RENZOVERSE_CONTRACT_TELEMETRY_PATH="$PWD/shared/telemetry/cavesharp.v1.json"
dotnet run --project modules/CaveSharp-OS/CaveSharpEngine.csproj
```

In a second terminal, serve the frontend:

```sh
python3 -m pip install -r spine_runtime/requirements.txt
python3 -m spine_runtime.viewer_server
```

Open `http://localhost:8000` and select **Enter the cave**. The viewer reads the authored world catalog and polls the validated, read-only `/api/telemetry/v1/latest` endpoint. Without a valid `shared/telemetry/cavesharp.v1.json`, it reports telemetry unavailable rather than displaying an empty or fabricated snapshot. Use WASD to move and click the scene to look around with the mouse.

The former legacy WebSocket viewer remains available only by explicitly adding `?telemetryMode=legacy` to `game.html`. Contract mode is the default. The browser displays the authored world and region names, snapshot world/tick/time metadata, and contract-backed creature/HUD values; it does not infer region geometry or render a corruption heatmap.

The 3D renderer loads Three.js from jsDelivr. For Codespaces port forwarding, bind the viewer server to `0.0.0.0` with `python3 -m spine_runtime.viewer_server --host 0.0.0.0`; forward port 8000. This endpoint is read-only and is intended for a trusted development environment.

The pinned CaveSharp source in this checkout has unrelated compile errors, so the engine command may not start until those are repaired. The isolated contract harness and schema/API tests can still verify the Phase 9/10 boundary without the engine.