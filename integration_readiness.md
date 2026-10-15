# Integration readiness report

Assessment of the checked-out sources and current Spine drafts. “Ready” is scoped to a verified capability; a working prototype or valid JSON Schema is not equivalent to a contract-conformant integration.

## Summary

| Pillar | Contract readiness | Runtime integration readiness | Main blocker |
|---|---|---|---|
| Renzos-Cave viewer | **Validated v1 world/snapshot consumption implemented** | **Partial / blocked for live engine** | UI/API/schema paths tested; full CaveSharp build errors prevent a live producer flow |
| CaveSharp-OS engine | **Opt-in v1 snapshot builder/emitter and atomic file transport implemented** | **Blocked for live runtime** | Full engine build errors; producer does not yet run canonical JSON Schema validation internally |
| Renzo-Hacker-Lab cockpit | **Snapshot/world client implemented** | **Partial / blocked for live runtime** | Two read-only dashboard consumers and deterministic shared-API test; existing full launch paths have unrelated import blockers |
| Renzoverse world/catalog | **Authored CaveSharp `world_contract` catalog exists and validates** | **Partial** | Additional world entries and module-manifest population remain pending |

## Renzos-Cave — Viewer

| Capability | Readiness | Evidence / gap |
|---|---|---|
| Telemetry parsing | **Validated v1 active by default** | Contract mode polls `/api/telemetry/v1/latest`; browser validates required fields/version/world identity before changing HUD state. Legacy WebSocket is explicitly available via `?telemetryMode=legacy`. |
| HUD | **Present for v1 and legacy data** | Displays threat, corruption, CTA, creature count, hunger aggregate, directive, world/tick/generated-time metadata, and stale/error state. |
| Creature display | **v1 identity-aware** | Validates all creature fields and keys markers by stable `entityId`; retains last valid rendered state when a later poll fails. |
| Corruption bar | **v1 scalar consumed** | Uses contract scalar; semantic units/range still require agreement. |
| Corruption heatmap | **Not ready** | The engine serializer can include a grid, but the inspected viewer handler does not render it. Grid orientation/units/region mapping are unspecified. |
| World layer / region overlays | **Catalog context active; spatial overlays pending** | HUD displays authored world/region names; no region geometry mapping is asserted, and no heatmap is rendered without grid semantics. |
| Mock validation | **Legacy mock exists** | The mock server sends sample legacy messages; it does not validate or serve canonical v1 fixtures. |
| Contract activation | **Implemented and tested** | Browser validator and Renzoverse API tests cover v1 fixtures and failure states. |
| Runtime integration | **Blocked for live engine** | Actual Phase 9 opt-in file is consumed through the validated API, but pinned CaveSharp build errors prevent proof of live output. |

## CaveSharp-OS — Engine

| Capability | Readiness | Evidence / gap |
|---|---|---|
| Snapshot builder | **Opt-in v1 builder/emitter implemented in local submodule worktree** | Phase 9 additions require authoritative world/tick/time/entity values and validate finite values/identity before publish; full-schema validation remains in the canonical API. |
| Telemetry emitter | **Dual-path opt-in** | Legacy WebSocket remains; a separate atomic `cavesharp.v1.json` transport is available only with explicit activation. |
| World logic | **Authored ID catalog available** | `shared/worlds/cavesharp.json` validates as `world_contract`; runtime region geometry is not defined. |
| Events | **Internal sources only** | Event-related classes exist, but no unified sequenced event contract output was identified. |
| Commands | **Legacy surface** | CTA command server/hooks exist; command schema, authorization, audit, and explicit correlated result are unverified. |
| Conformance level | **0–1 by boundary** | Level 1 for legacy overlapping telemetry; level 0 for unverified world/event/command boundaries. No level 2/3 evidence. |
| Adapter requirements | **High** | Need authoritative identity/tick/sequence, field semantics, schema validation, and explicit error behavior. |
| Runtime integration | **Blocked** | Full CaveSharp build still fails on pre-existing source errors; no live v1 emission was verified. |

See the [CaveSharp contract delta report](./cavesharp_shadow/delta_report.md) and the shadow JSON files alongside it for the pinned-vs-local field comparison.

## Renzo-Hacker-Lab — Cockpit

| Capability | Readiness | Evidence / gap |
|---|---|---|
| Source provenance | **Inspected** | Sibling checkout `renzcas/Renzo-Hacker-Lab`, starting revision `80d0ad1f9804f23816a3501a2ada9a7cbe4a272e`. |
| Python registry | **Separate local system** | Hacker-Lab's source is now available; do not conflate it with Renzoverse's `orchestrator/registry.py`. |
| Cockpit panels / dashboards | **Snapshot/world consumer implemented** | BIG ANIMAL `WorldUI` and ClaudeCode AgentDash display validated contract feed state. |
| Module manifests | **Pending** | No checked-in `module_contract` manifest or Renzoverse manifest endpoint was found. |
| Command patterns | **Not activated** | No cross-pillar authorized command client/result/audit flow verified. |
| Telemetry consumers | **Implemented and fixture-tested** | Client reads both world and latest telemetry endpoints, validates canonical schemas, checks matching world ID and valid tick progression (accepting process reset only with a newer timestamp), and preserves last valid snapshot on failure. |
| Event consumers | **Not activated** | Existing Hacker-Lab event buses carry local agent/world signals without Spine envelope, sequencing, or shared event transport. |
| Runtime integration | **Partial / blocked** | Cross-pillar API test passes; the BigAnimal and ClaudeCode top-level runtime launch paths have unrelated import blockers. Live CaveSharp flow is also blocked by its build errors. |

## Renzoverse — World and module catalog

| Capability | Readiness | Evidence / gap |
|---|---|---|
| World definitions | **Authored catalog present for CaveSharp** | `shared/worlds/cavesharp.json` validates against the canonical `world_contract`; this is the first authored entry, not a full world registry. |
| Region definitions | **Stable authored IDs; runtime geometry pending** | The catalog contains stable region/entity-type IDs and viewer displays names; no geometry, overlay coordinates, or region-to-entity mapping is established. |
| Corruption rules | **Partial runtime subsystem** | `CorruptionMap` and healing logic exist. Their authored rule source and semantics are not represented in a canonical world definition. Runtime corruption state belongs to telemetry/events, not world catalog by default. |
| Module registry/config | **Partial** | `renzoverse.json` registers CaveSharp and reserves paths; it does not describe all local modules or schema compatibility. Python organ discovery is a separate in-process loader. |
| Contract conformance | **Draft schemas validated; producers/catalog not conformant** | JSON Schemas pass schema checks; this validates schema syntax, not world/catalog data or runtime implementations. |
| Runtime integration | **Partial** | Validated read-only world/snapshot endpoints are served with the viewer; module manifest catalog and authenticated remote service are not implemented. |

## Cross-cutting blockers and gates

1. **Contract semantics:** settle units/ranges for CTA, threat, corruption, creature fields, grid dimensions/orientation, event payload types, and command payload types.
2. **Identity/time:** source stable world/entity IDs, authoritative simulation ticks, generated timestamps, and event sequence semantics from their owners.
3. **Conformance fixtures:** add positive and negative shared fixtures and run them against the viewer, mock, registry manifest reader, and engine adapter as each becomes available.
4. **External ownership:** Hacker-Lab source is now inspected at the recorded revision; recheck that revision before making later conformance claims.
5. **Build/runtime:** verify the selected CaveSharp commit builds and can run; keep local uncommitted submodule changes separate from a reproducible pinned integration.
6. **Security/operations:** before remote commands, define authenticated identity, authorization, audit, idempotency, timeout, and error behavior.

## Phase 5 entry criteria

Begin runtime integration only when:

- the contract owners approve v1 field semantics and event/command type catalogs;
- a minimal `world_contract` fixture and module manifests validate and have stable IDs;
- the viewer rejects invalid telemetry without displaying success-shaped defaults;
- the Python registry's module-manifest behavior is tested without changing its local invocation contract;
- CaveSharp's chosen revision has a reproducible build and an adapter testable against the same telemetry fixtures; and
- the command boundary is explicitly scoped and secured, or remains disabled.

No pillar is currently reported as fully v1-integrated.
