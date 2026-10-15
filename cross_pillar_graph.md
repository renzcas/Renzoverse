# Cross-pillar dependency graph

This graph distinguishes **current, observed dependencies** from the **target contract dependencies**. A contract can be the intended seam without an implementation currently consuming it.

## Pillar graph

```text
                         ┌──────────────────────────┐
                         │ Renzoverse               │
                         │ world catalog + Spine    │
                         │ world / module contracts │
                         └────────────┬─────────────┘
                                      │
                     world definitions│module manifests
                                      v
┌──────────────────────────┐  snapshots/events  ┌──────────────────────────┐
│ CaveSharp-OS             │ ─────────────────> │ Renzos-Cave              │
│ simulation authority     │                    │ browser viewer / HUD     │
│ telemetry + events       │                    │ read-only presentation  │
└─────────────┬────────────┘                    └────────────┬─────────────┘
              ^                                              │
              │ validated commands (future; state-changing) │
              └──────────────────────────────────────────────┘
              ^
              │ validated, authorized commands (future)
              │ telemetry/events/modules (read-only clients)
┌─────────────┴────────────┐
│ Renzo-Hacker-Lab         │
│ BIG ANIMAL UI + AgentDash│
│ read-only Spine clients  │
│ module/events not wired  │
└──────────────────────────┘
```

The local Python registry is a Renzoverse in-process organ loader. The sibling Hacker-Lab checkout has separate BIG ANIMAL and AgentDash surfaces, now wired as read-only telemetry/world consumers; this does not make its local event bus a Spine event stream or establish module manifests.

## Contract-to-pillar dependency matrix

| Contract | Owner / source of truth | Producers | Consumers | Current status |
|---|---|---|---|---|
| `world_contract` | Renzoverse catalog | Renzoverse world authoring/catalog | CaveSharp-OS for authored world inputs; Renzos-Cave and Hacker-Lab dashboards for world context | Authored CaveSharp catalog and validated read-only viewer endpoint exist; consumers reject world ID mismatches. |
| `telemetry_contract` | Simulation owns runtime truth; Spine owns the schema | CaveSharp-OS snapshot boundary | Renzos-Cave HUD/viewer; Hacker-Lab BIG ANIMAL and AgentDash read-only clients | Viewer and Hacker-Lab clients validate the v1 latest-snapshot API; live CaveSharp flow remains blocked by engine build errors. |
| `event_contract` | Event-producing runtime module, with Spine-defined envelope | CaveSharp-OS only when real events are emitted; other registered modules if explicitly designed | Future cockpit, analysis consumers, and event-aware tools | Schema draft exists; no unified serialized event stream was found. |
| `command_contract` | Command receiver/runtime (CaveSharp for world-changing actions) | Authenticated viewer/cockpit/operator client when a real action is needed | CaveSharp command boundary | Schema draft and legacy CTA command surface exist; conformance, auth, audit, and explicit results are unverified. |
| `module_contract` | Renzoverse module catalog | Each module/organ publishes its manifest | Renzoverse discovery/registry, cockpit module panels, compatibility tooling | Schema draft exists; `renzoverse.json` is partial config, and Python registry does not read manifests. |

## Pillar dependencies

### Renzoverse

- Owns stable world/region/entity identities and module catalog policy.
- Publishes `world_contract` documents and indexes `module_contract` manifests once implementations exist.
- Defines schemas and compatibility rules; it does not own CaveSharp runtime values.
- Local Python `OrganRegistry` remains an in-process mechanism until a separate service boundary is deliberately implemented.

### CaveSharp-OS

- Consumes authored world definitions where they are adopted.
- Owns authoritative simulation state and should produce complete `telemetry_contract` snapshots.
- Should publish `event_contract` messages only for defined domain events, with ordered per-world sequences.
- Consumes validated `command_contract` requests for explicitly supported world-changing operations.
- Publishes its identity/capabilities through `module_contract`.

### Renzos-Cave

- Consumes `telemetry_contract` for runtime HUD and creature/corruption state.
- Consumes `world_contract` for stable world, region, and entity definitions if the scene/overlays use catalog data.
- Does not need `event_contract` for local keyboard, pointer-lock, selection, or camera movement.
- Would use `command_contract` only if a UI action changes simulation state; local creature focus or region selection can stay presentation-only.
- Publishes a `module_contract` manifest if it is registered as a deployable module.

### Renzo-Hacker-Lab

- BIG ANIMAL WorldUI and ClaudeCode AgentDash consume validated latest telemetry and world context through the read-only viewer API.
- Existing local agent/world event buses remain local; no Spine event feed or module manifest catalog is activated.
- May publish commands only through an authenticated, authorized, audited command boundary.
- Full runtime launch paths and live CaveSharp interoperability require follow-up verification; see the [Phase 10 report](./phase10_viewer_activation.md).

## Key architectural constraints

1. There is no separate `snapshot_contract`: a snapshot is `telemetry_contract`.
2. Creature, hunger, fear, CTA, and corruption values are fields in telemetry, not standalone contracts in v1.
3. `world_contract` carries authored/stable definitions; changing simulation state belongs in telemetry/events.
4. Do not infer event production from a class name such as `EventEngine`; verify the event shape and lifecycle.
5. Do not infer command semantics from viewer controls or Python `registry.execute`; commands represent explicit authorized operations at a runtime boundary.
6. Keep transport separate from contract. Current WebSocket transport is not proof of schema conformance.

## Source links

- [Spine schema index](./renzoverse_spine/README.md)
- [Organ inventory and file-level alignment](./organ_inventory.md)
- [Conformance evidence](./contract_conformance.md)
- [Local module configuration](./renzoverse.json)
- [Python registry](./orchestrator/registry.py)
- [Renzos-Cave prototype](./renzoverse_vault/renzo-verse/site/)
- [CaveSharp submodule](./modules/CaveSharp-OS/)
