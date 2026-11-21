# Renzoverse unification map

Renzoverse should unify the four pillars through shared contracts and stable interfaces, not by merging their codebases into one application. Each repository remains responsible for its own domain; this repository acts as the catalog, integration point, and place to verify end-to-end compatibility.

## Target architecture

```text
                        Renzoverse (catalog + integration)
                  worlds, regions, entities, module registry
                   canonical schemas, versions, health checks
                    /                |                 \
                   /                 |                  \
       World definition       Runtime state/events      Commands
                 /                   |                     \
                v                    v                      v
       CaveSharp-OS  --------> Integration API <------- Renzo-Hacker-Lab
       simulation engine      snapshot + event stream    operator cockpit
                                      |
                                      v
                                  Renzos-Cave
                              browser viewer / HUD
```

### Responsibilities and boundaries

| Pillar | Owns | Integrates through |
|---|---|---|
| **Renzoverse** | Canonical world, region, and entity identities; module catalog; shared schemas and compatibility policy | Versioned manifests and contracts |
| **CaveSharp-OS** | Simulation ticks, creature behavior, corruption, CTA, and authoritative runtime state | Published snapshots/events; validated commands |
| **Renzos-Cave** | 3D exploration, player-facing HUD, and presentation | Read-only world catalog and live state stream |
| **Renzo-Hacker-Lab** | Operator workflows, dashboards, agent coordination, and analysis | Authenticated observability and command interfaces |

The engine owns simulation truth. The viewer and cockpit are clients; neither should independently mutate simulation state or become the source of world definitions. Renzoverse owns stable IDs and definitions, while CaveSharp owns changing runtime values. The operator cockpit may request actions, but the engine validates and applies them.

## Organ inventory and concrete Spine schemas

- [Organ inventory](./organ_inventory.md) lists the source components present in this checkout, their current status, and the initial attachment of each relevant subsystem to a contract. External repositories and unavailable history are explicitly marked unverified.
- [Organ status dashboard](./organ_status.md) tracks existence, verification, implementation, and integration status. Its conversation-sourced recovery candidates are explicitly limited to concepts named in the current request.
- [Spine contracts](./renzoverse_spine/README.md) define the first language-neutral JSON Schema v1 contracts for world definitions, telemetry snapshots, events, commands/results, and module manifests.
- [Contract conformance matrix](./contract_conformance.md), [adapter specifications](./organ_adapters.md), and [activation plan](./contract_activation_plan.md) describe current evidence and safe next steps without claiming runtime activation.
- [Cross-pillar dependency graph](./cross_pillar_graph.md), [contract flow simulation](./contract_flow.md), and [integration readiness report](./integration_readiness.md) distinguish observed paths from proposed integration.
- The isolated [Spine Runtime](./spine_runtime/README.md) provides local schema loading/validation, in-process routing, fixture bus, and contract harness. It does not yet connect to the browser or CaveSharp.
- The [CaveSharp contract shadow](./cavesharp_shadow/delta_report.md) records source-level snapshot, creature, corruption, region, and Overseer deltas against the Spine, with pinned revision and local-only changes distinguished.
- These schemas define a target, not current runtime behavior. In particular, CaveSharp's current flat WebSocket message and the browser mock do not yet include the v1 world/tick/time envelope.

## Current repository baseline

Verified in this checkout:

- `renzoverse.json` registers CaveSharp-OS and reserves telemetry, event, and agent paths.
- `modules/CaveSharp-OS/` is a Git submodule. Root documentation describes a WebSocket telemetry stream at `/telemetry/`; the cave page consumes threat, corruption, CTA, and creature data from that stream.
- The viewer prototype is in `renzoverse_vault/renzo-verse/site/`.
- `orchestrator/organ_contract.py` and `orchestrator/registry.py` define a Python-only `OrganRequest`/`OrganResponse` contract and discover executable Python organs. This is not yet a cross-repository or cross-language service API.
- The configured `shared/telemetry/cavesharp.json` and event paths are documented as reserved/not yet written by the pinned engine.
- The local organ `engine.py` files are placeholders, according to the root README.

The repository's current documentation records additional CaveSharp build and runtime limitations; treat them as release blockers to re-check when validating the current submodule revision. The Renzos-Cave prototype and its direct WebSocket connection are an initial working-slice design, not yet a general integration layer.

**Not verified from this checkout:** the internals, current APIs, build status, and module inventory of the standalone Renzo-Hacker-Lab repository; any separate Renzos-Cave repository; and historical or untracked files outside the checked-out repositories. Confirm those from their source repositories before assigning migration work. Do not treat similarly named files in a vault as proof that an external repo has been consolidated.

## Shared integration contract

Make a small, versioned contract the seam between the pillars. Define it once in Renzoverse and publish language-neutral schemas with examples and compatibility tests.

1. **World catalog:** stable IDs and versioned definitions for worlds, regions, entities, and simulation configuration. Keep lore and authored definitions separate from live state.
2. **Snapshot:** a complete, timestamped view of the current world, including world ID, schema version, simulation tick, and the state fields needed by viewers and dashboards.
3. **Event:** an ordered state-change envelope with event ID, world ID, per-world sequence, tick, timestamp, type, schema version, and an event-specific payload. Consumers detect sequence gaps and recover from a fresh snapshot. Event-type payload schemas still need to be cataloged.
4. **Command:** a validated, auditable request with command ID, world ID, actor, type, payload, and result. Commands are not embedded in telemetry.
5. **Module manifest:** stable module ID, owner/repository, version or pinned revision, supported contract versions, capabilities, health endpoint, and startup/configuration requirements.

The existing WebSocket feed can remain the first live transport while these contracts are established. Add a snapshot/recovery interface before making event consumers depend on continuous delivery. Prefer explicit service interfaces over shared mutable files; keep the configured JSON file paths as local development/export options unless file exchange is deliberately adopted as a contract. Keep the existing Python organ contract for in-process organs, and define a separate service boundary for cross-process or cross-language calls.

## Implementation sequence

### 1. Inventory and establish ownership

- Inventory repositories, branches, deployable entry points, organs, viewers, dashboards, schemas, and known prototypes.
- Record each component's owner, source repository, dependency direction, status, and current data format in the Renzoverse module catalog.
- Classify files as active, duplicate, archival, or unrecovered. Preserve originals and history; do not bulk-move files based on names alone.
- Obtain and inspect the standalone Renzos-Cave and Renzo-Hacker-Lab sources before claiming their APIs or gaps.

**Exit:** every in-scope component has a source of truth, an owner, and a known status; unknowns are listed rather than guessed.

### 2. Freeze the first shared schema

- Specify world IDs, snapshot, event, and command envelopes, including required fields, units, ranges, ordering, and compatibility rules.
- Add representative fixtures and contract tests consumable from the .NET engine, Python registry/tools, and browser clients.
- Choose and document schema versioning and additive/breaking-change policy before adding more telemetry fields.

**Exit:** all four pillars can validate the same versioned fixtures without hand-maintained field translations.

### 3. Stabilize the simulation-to-viewer slice

- Bring the pinned CaveSharp revision to a reproducible build and run.
- Make its telemetry conform to the shared snapshot schema and expose tick/version metadata.
- Add snapshot recovery and explicit connection/error states to the viewer; preserve the existing WebSocket route through a thin adapter if compatibility requires it.
- Verify from a browser-facing test or harness that serialized engine output has the exact fields and types the viewer reads.

**Exit:** one documented local command sequence starts the engine and viewer, and the viewer renders live engine state with detectable disconnect/recovery behavior.

### 4. Connect the operator cockpit

- Add read-only catalog, health, snapshot, and event access first; keep the cockpit out of the simulation's internal storage.
- Add commands only behind engine-side validation, explicit authorization, audit records, and command results.
- Reuse the same schemas and fixtures as the viewer; do not create a second telemetry vocabulary for the dashboard.

**Exit:** the cockpit can inspect the same world and stream as the viewer, and any permitted action is validated and traceable end to end.

### 5. Make the system operable and recoverable

- Add module health/readiness, structured logs, correlation IDs, schema compatibility checks, and startup/shutdown guidance.
- Test engine restart, stale clients, duplicate/out-of-order events, unsupported schema versions, and command rejection.
- Add CI checks for schema compatibility, builds, contract tests, and the end-to-end slice; publish a module compatibility matrix.

**Exit:** a failed or incompatible module is visible and isolated rather than silently producing partial or misleading state.

## Immediate next actions

1. Get authenticated access to the standalone repositories and extend the [inventory](./organ_inventory.md) with source paths and revision provenance, without moving their contents.
2. Review the initial Spine schemas with the owners; settle event/command payload catalogs, units, and compatibility before declaring v1 stable.
3. Add durable contract fixtures/conformance tests for the engine, viewer, and any available cockpit.
4. Use the current CaveSharp-to-Renzos-Cave path as the first contract-tested vertical slice; then add the operator cockpit as a second consumer.

## Repository links

- [Module configuration](./renzoverse.json)
- [Root README and current telemetry notes](./README.md)
- [Organ request/response contract](./orchestrator/organ_contract.py)
- [Python organ registry](./orchestrator/registry.py)
- [CaveSharp submodule](./modules/CaveSharp-OS/)
- [Renzos-Cave prototype](./renzoverse_vault/renzo-verse/)
