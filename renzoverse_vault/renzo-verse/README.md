# Renzos-Cave

Renzos-Cave is the 3D gameworld in Renzoverse. The current prototype lets you explore a cave as Trog-Croman and displays live state from CaveSharp-OS.

## Run locally

From the repository root, start CaveSharp-OS:

```sh
dotnet run --project modules/CaveSharp-OS/CaveSharpEngine.csproj
```

In a second terminal, serve the frontend:

```sh
python3 -m http.server 8000 --directory renzoverse_vault/renzo-verse/site
```

Open `http://localhost:8000` and select **Enter the cave**. CaveSharp writes its latest JSON snapshot to the configured `shared/telemetry/cavesharp.json` path and broadcasts the same state at `ws://localhost:8181/telemetry/`. Use WASD to move and click the scene to look around with the mouse. Press Ctrl+C in the CaveSharp terminal to stop the simulation.

The 3D renderer loads Three.js from jsDelivr. If the page is served through a forwarded Codespaces port and the telemetry connection does not resolve automatically, pass the forwarded WebSocket address in the URL, for example `game.html?telemetry=wss://<forwarded-8181-host>/telemetry/`.