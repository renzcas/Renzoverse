# Shared pipes

This directory is the file-based handoff area between Renzoverse modules. Runtime output is generated locally and is not committed.

- `telemetry/cavesharp.json` contains CaveSharp's latest snapshot. Its path and write interval are configured in the root `renzoverse.json`.
- `events/cavesharp_events.json` is reserved in configuration; CaveSharp does not publish an event feed yet.
- `agent/` is reserved for future agent messages.

For real-time cave rendering, the frontend uses CaveSharp's WebSocket stream; the JSON snapshot is the latest-state feed for other tools and processes.
