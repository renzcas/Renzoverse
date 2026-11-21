# Organ adapter specification

Adapters preserve stable internal APIs while translating at explicit boundaries. They must not invent identity, timestamps, ticks, units, or successful results to make legacy payloads appear valid. The specifications below are designs only; no adapter is implemented by this document.

## Adapter inventory

| Adapter | Legacy producer/consumer | Canonical contract | Direction |
|---|---|---|---|
| CaveSharp telemetry publisher adapter | Overseer, creature/corruption snapshot DTOs, legacy `/telemetry/` JSON | `telemetry_contract` | Engine DTO/state → validated snapshot JSON |
| Viewer telemetry decoder | WebSocket message parser in `site/game.html` | `telemetry_contract` | Received JSON → validated typed viewer state |
| World catalog adapter | Existing runtime region/map/world types and future authored catalog | `world_contract` | Authored definitions → canonical world document; runtime instance remains separate |
| Event publisher adapter | CTA/time/interaction event sources | `event_contract` | Actual domain event → sequenced event envelope |
| CTA command bridge | Existing `CTACommandServer` request/Overseer hooks | `command_contract` | Canonical request → validated legacy handler call → canonical result |
| Python module-manifest adapter | Python organ directories/registry and project metadata | `module_contract` | Local module metadata → validated manifest/catalog entry |

## Shared adapter rules

1. Validate inputs and outputs against the published JSON Schema Draft 2020-12 schema for the exact `schemaVersion`.
2. Keep transport separate from contract. WebSocket is currently used for telemetry, but adapters must not depend on transport-specific framing.
3. Preserve the legacy endpoint/API during migration where needed; expose version negotiation or an explicitly selected legacy route rather than guessing message versions.
4. Never silently coerce missing required fields to `0`, `false`, empty IDs, current time, or a fabricated success.
5. Report contract errors with contract ID/version, component, and field path. Avoid logging full sensitive command payloads or credentials.
6. Unknown optional properties may be retained/ignored according to client policy; unsupported major versions and invalid required fields must be surfaced and rejected.
7. Add positive and negative fixtures, including boundary values and malformed data. Record test and source revision in the conformance matrix.

## CaveSharp telemetry publisher adapter

**Input shape:** current internal values/legacy flat payload: `threat`, `cta`, `corruption`, `ctaBoss`, `directive`, `creatures[]`, and `corruptionGrid`. The legacy serializer or publisher may not exist at the pinned submodule revision; confirm the runtime source before implementation.

**Output shape:** one `telemetry_contract` v1 snapshot, including `schemaVersion`, stable `worldId`, authoritative `tick`, UTC `generatedAt`, and every required state field.

**Transformation rules:**

- Map known source values field-for-field only after documenting units/ranges; do not convert CTA or corruption to percentages based only on UI labels.
- Add `worldId` from configured/catalog identity, never from display name.
- Add `tick` from the authoritative simulation loop; do not generate it in the serializer or use wall-clock time as a substitute.
- Generate `generatedAt` in UTC at snapshot creation.
- Require stable `entityId` for each creature. Prefer IDs owned by the simulation/catalog. A persisted mapping is an interim option only if identity lifecycle and collision behavior are specified; do not use array position or creature name as identity.
- Preserve `corruptionGrid` row/column order and document axis/origin/units before consumers interpret geometry.
- Do not drop known fields or restructure them differently per client.

**Validation rules:** validate every required envelope and creature field; reject non-finite numbers; enforce any agreed ranges and grid constraints once domain owners define them. At present the schema leaves numeric domains/units open, so the adapter must not invent limits.

**Error handling:** invalid source data is reported and the snapshot is not published as successful v1. Keep last-good state only if the client explicitly labels it stale and retains its original tick/time. Report connection and serialization errors; do not send a fabricated empty snapshot.

**Versioning:** serialize the explicit schema version. Legacy clients may continue receiving a legacy-compatible shape through a migration mode/adapter. Switch the default only after viewer and cockpit conformance and a deprecation window.

## Viewer telemetry decoder

**Input shape:** JSON WebSocket message; currently the client calls `JSON.parse` and reads legacy flat fields.

**Output shape:** validated viewer state sourced from `telemetry_contract` v1. The decoder is a client-side projection, not a second contract definition.

**Transformation rules:**

- Validate the message before updating HUD state.
- Read `threat`, `cta`, and `corruption` only from a valid snapshot; do not substitute zero for absent or invalid values.
- Render creature count/list from validated `creatures[]`; use `entityId` for stable client identity.
- Derive aggregate hunger only from validated finite `hunger` values and show unavailable when none exist.
- Derive fear styling from validated boolean `isAfraid`.
- Render the corruption grid only after axis/origin/unit semantics are documented. Resolve region overlays from `world_contract`, not from guessed grid-cell names.
- Keep transport disconnect/retry separate from schema-invalid-message state.

**Validation rules:** reject malformed JSON, unsupported major versions, missing required fields, wrong JSON types, non-finite numbers, and invalid date-time values. Optionally use generated validators or a small checked-in equivalent that is tested against the canonical schema; avoid maintaining independent field lists without conformance tests.

**Error handling:** keep the last valid snapshot visibly marked stale if desired; show a clear invalid-data state and log a concise field-path error. Do not replace invalid values with zero or present the connection as live-valid. Retry policy should not create an unbounded reconnect loop or hide repeated schema failure.

**Versioning:** support only explicitly tested contract versions. Legacy handling must be opt-in or clearly identified; do not guess version based on a few property names.

## World catalog adapter

**Input shape:** authored world/catalog source plus current runtime types such as `RealmRegion`, `World`, and map engine objects. These runtime classes are not currently a canonical catalog.

**Output shape:** `world_contract` v1 document with stable `worldId`, `worldVersion`, named regions and entity types, and optional metadata.

**Transformation rules:** map only authored, stable identity and descriptive/configuration fields; keep mutable runtime state in telemetry. A display name is not a stable ID. Avoid reverse-engineering generated runtime state as lore/catalog data.

**Validation rules:** enforce required IDs/names, unique IDs within the relevant catalog scope, valid parent-region references, and schema validity. Referential-integrity rules beyond the schema need catalog tests.

**Error handling:** reject duplicate/missing IDs or invalid references with source paths; do not publish partial catalogs as complete.

**Versioning:** increment `worldVersion` for authored content changes. Change the contract `schemaVersion` only for schema compatibility changes.

## Event publisher adapter

**Input shape:** actual domain transitions from CTA, time, interaction, or other selected producers. Existing event-related classes are not a unified event stream.

**Output shape:** `event_contract` v1 envelope with event ID, world ID, monotonically increasing per-world `sequence`, simulation `tick`, UTC `occurredAt`, event type, payload, and source module ID where known.

**Transformation rules:** one envelope per actual event; preserve source order; use tick from the simulation clock and sequence from a durable/appropriately scoped event sequencer. Payloads must have event-type-specific schemas before production use.

**Validation rules:** validate envelope, event type, payload schema, world ID, and sequence/tick semantics. Reject duplicate IDs and detect sequence gaps at consumers.

**Error handling:** report invalid events and backpressure/publish failures. Do not silently drop/reorder events or fabricate sequence continuity; define retry/idempotency behavior before enabling delivery.

**Versioning:** envelope and payload versions are explicit. Add a new event type or compatible optional fields without changing old event meaning; incompatible payload semantics require a versioned event type or contract-major change.

## CTA command bridge

**Input shape:** canonical command request from an authenticated operator/service. Existing command endpoint and `Overseer` hooks are legacy and are not assumed safe or conformant.

**Output shape:** canonical `commandResult` with the same `commandId` and `worldId`, status (`accepted`, `rejected`, or `completed`), response time, and result/error details.

**Transformation rules:** allow-list command types; map only explicitly specified command fields to handler calls; bind actor identity from authenticated transport context, not untrusted payload alone; preserve correlation by command ID. Distinguish acceptance from completion.

**Validation rules:** validate schema, authorization, target world, type-specific payload, rate/size limits, and idempotency policy before invoking a handler. Do not treat Python registry function execution as a world command.

**Error handling:** return explicit rejection for invalid/unauthorized commands; record audit metadata without secrets; surface handler failures with non-sensitive error details. Never return success-shaped fallback results.

**Versioning:** version request and result schemas together; unknown command types are rejected explicitly. Keep old command transports behind a compatibility adapter during migration.

## Python module-manifest adapter

**Input shape:** organ directory name, `engine.py` presence, Python package metadata, and explicit module metadata to be added. Current registry only imports a non-empty engine and checks for `execute(request)`; it does not read manifests.

**Output shape:** `module_contract` v1 manifest with stable module ID, display name, version, source/revision, capabilities, and exact contract IDs/versions supported.

**Transformation rules:** derive only immutable identity defaults that are documented; require declared version/source/capabilities/contracts rather than infer them from names. Keep the existing `OrganRequest`/`OrganResponse` as a local invocation interface.

**Validation rules:** validate manifest schema, unique module ID, contract references, and consistency between advertised capability and implemented entry point. Empty placeholder organs may be listed as placeholders in inventory but must not advertise executable capabilities.

**Error handling:** invalid manifests are reported and excluded from the executable registry; report a precise validation error. Discovery must not silently downgrade an invalid manifest to inferred metadata.

**Versioning:** module release version and contract compatibility are separate. A module can implement a new release while supporting multiple exact contract versions.
