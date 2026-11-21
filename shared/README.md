# Shared pipes

This directory is the file-based handoff area between Renzoverse modules. Runtime output is generated locally and is not committed.

- `telemetry/cavesharp.json` is the intended file-based CaveSharp snapshot path in `renzoverse.json`, but the pinned engine source does not currently write it.
- `events/cavesharp_events.json` is reserved in configuration; CaveSharp does not publish an event feed yet.
- `agent/` is reserved for future agent messages.

For real-time cave rendering, the frontend uses CaveSharp's WebSocket stream at `ws://localhost:8181/telemetry/`. A file-based snapshot feed for other tools and processes is not implemented yet.
