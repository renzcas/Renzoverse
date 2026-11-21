# Renzoverse Spine contracts

This directory contains the initial language-neutral JSON Schema contracts for the Renzoverse integration boundary. Contract schemas are the target v1 shape; they do **not** mean that the current CaveSharp payload, viewer, Python organ registry, or external repositories already conform.

| Contract | Schema | Intended use |
|---|---|---|
| Telemetry snapshot | [telemetry_contract/schema.json](./telemetry_contract/schema.json) | Versioned state snapshot consumed by viewer and operator clients |
| World catalog | [world_contract/schema.json](./world_contract/schema.json) | Stable world, region, and entity-type definitions |
| Event | [event_contract/schema.json](./event_contract/schema.json) | Ordered, replayable world-state changes |
| Command | [command_contract/schema.json](./command_contract/schema.json) | Validated command requests and explicit results |
| Module | [module_contract/schema.json](./module_contract/schema.json) | Module identity, source, capabilities, and contract compatibility |

## Conventions

- Schemas use JSON Schema Draft 2020-12.
- Every message carries a `schemaVersion` string. The first contract major version is `1.0.0`.
- IDs are stable, opaque strings; clients must not derive identity from display names.
- Timestamps use RFC 3339 date-time strings in UTC.
- Telemetry is a complete snapshot, not a delta. Events carry a monotonically increasing per-world sequence and simulation tick; consumers detect sequence gaps and recover from a fresh snapshot.
- Commands are separate from telemetry and must be authorized, validated, and audited by the engine before execution.
- Event and command payload objects are envelopes only in this draft; event-type and command-type-specific payload schemas remain to be cataloged.
- Additive optional fields may be compatible within a major version. Removing/renaming fields or changing meaning/units requires a new major contract version.
- A module should advertise exact contract IDs/versions it supports. No transport, auth scheme, broker, or deployment mechanism is mandated by these schemas.

## Adoption status

These schemas are a first contract draft based on source shapes present in this checkout. The existing CaveSharp WebSocket payload and Python in-process organ API are legacy interfaces; adapters and conformance tests are still required. There is no canonical world catalog or cross-repository integration service yet.
