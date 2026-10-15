# Renzoverse organ inventory

This is an inventory of implementation files present in this checkout, including the current CaveSharp submodule worktree. It excludes generated `obj/` and `bin/` artifacts. File presence does not imply that a component is complete, wired into the runtime, or conformant to the Spine contracts.

Status labels:

- **Present** — source exists in the checkout.
- **Placeholder** — file exists but has no implementation.
- **Reserved** — configuration/docs name a path or capability, but no implementation is present.
- **Local-only** — source is modified or untracked in the submodule worktree and is not part of the pinned commit.
- **Unverified** — repository/source is not available in this checkout.

## Pillar 1 — Renzoverse: world, lore, registry, reusable organs

### World catalog and integration hub

| Component | Location | Status / notes |
|---|---|---|
| Module/runtime configuration | [renzoverse.json](./renzoverse.json) | Present. Registers CaveSharp and reserves telemetry/event/agent directories. It does not list all local modules or declare Spine contract versions. |
| Organ request/response types | [orchestrator/organ_contract.py](./orchestrator/organ_contract.py) | Present. Python in-process `OrganRequest` and `OrganResponse`; not a wire protocol. |
| Python organ discovery and execution | [orchestrator/registry.py](./orchestrator/registry.py) | Present. Discovers `engine.py` modules and validates callable/response shape. |
| Shared telemetry/event/agent pipes | [shared/README.md](./shared/README.md) | Reserved. The telemetry JSON file, event feed, and agent pipe are documented as not implemented. |
| Static world/region/entity definitions | `shared/worlds/cavesharp.json` | Authored initial CaveSharp `world_contract` entry with stable world, region, and entity-type IDs; additional world definitions and geometry semantics remain pending. |
| War-engine stress subsystem | `modules/war-engine/global-stress/stress_router.py`, `stress_sources.py`, `stress_state.py`, `stress_update.py` | Present source. Not registered in `renzoverse.json` or connected to the CaveSharp telemetry stream in this checkout. |
| VerseSharp engine entry point | `master_core/VerseSharpEngine/Program.cs` | Present; starts a BotWars `MatchManager` loop. Relationship to the CaveSharp world and Spine is not declared here. |

### Registered Python organs

All six organ directories have `__init__.py`, a `contract.py` re-exporting the shared Python request/response types, an empty `model.py`, and an empty `engine.py`. The registry therefore correctly treats them as placeholders, not executable organs.

| Organ | Files | Status |
|---|---|---|
| ASCANNER_DARKLY | `master_core/UTL/organs/ASCANNER_DARKLY/{__init__.py,contract.py,engine.py,model.py}` | Placeholder |
| EquilibriumSolver | `master_core/UTL/organs/EquilibriumSolver/{__init__.py,contract.py,engine.py,model.py}` | Placeholder |
| EraEngine | `master_core/UTL/organs/EraEngine/{__init__.py,contract.py,engine.py,model.py}` | Placeholder |
| IngestionPipeline | `master_core/UTL/organs/IngestionPipeline/{__init__.py,contract.py,engine.py,model.py}` | Placeholder |
| SnapshotEvolutionEngine | `master_core/UTL/organs/SnapshotEvolutionEngine/{__init__.py,contract.py,engine.py,model.py}` | Placeholder |
| TemporalHarmonizer | `master_core/UTL/organs/TemporalHarmonizer/{__init__.py,contract.py,engine.py,model.py}` | Placeholder |

### Renzoverse-side verification

- Registry/contract tests: [tests/test_organ_registry.py](./tests/test_organ_registry.py).
- No separate static-world fixture, region catalogue, glyph catalogue, or world-event registry was identified.

## Pillar 2 — Renzos-Cave: browser viewer and HUD

Source present in the vault prototype [renzoverse_vault/renzo-verse/](./renzoverse_vault/renzo-verse/):

| Component | Location | Current behavior / status |
|---|---|---|
| Landing page | `site/index.html` | Present; links into the cave viewer. |
| Cave scene, HUD, and client logic | `site/game.html` | Present. Three.js scene, movement/look controls, creature markers, threat/corruption/CTA/creature/hunger/directive displays, WebSocket URL selection, and reconnect handling are in this page. |
| Telemetry parsing | `site/game.html` | Reads a legacy flat JSON payload. It currently defaults missing or non-numeric threat/corruption/CTA to zero and missing creatures to an empty list; it does not validate a schema version. |
| Region overlays and corruption heatmap | `site/game.html` | No region overlays or rendered corruption grid identified. The engine sends a grid, but this viewer does not consume it in the inspected telemetry handler. |
| Standalone mock telemetry server | [tests/mock_cavesharp_telemetry.py](./tests/mock_cavesharp_telemetry.py) | Present; sends two sample legacy payloads over a minimal WebSocket implementation. It is test support, not a production server or a contract validator. |
| Telemetry serialization harness | `tests/CaveSharpTelemetryHarness/` | Present in the root worktree as untracked local test code. It exercises the submodule's local serializer and creature snapshot files; not committed/pinned with this repository state. |

The standalone Renzos-Cave repository (if separate from the vault prototype) is **unverified** here.

## Pillar 3 — CaveSharp-OS: simulation runtime and telemetry

The source below is in the `modules/CaveSharp-OS/` submodule. Most paths are present at the pinned submodule revision; the three rows marked **Local-only** are worktree edits not included in that pin.

| Organ / subsystem | Source files | Contract attachment / status |
|---|---|---|
| Process entry and update/tick loop | `Program.cs`; `Core/Program.cs`; `Core/UpdateLoop.cs`; `Core/KernelPulseLoop.cs`; `Kernel/KernelPulseLoop.cs`; `Core/SystemBinder.cs`; `Systems/SystemBinder.cs`; `Core/Kernel/Kernel.cs` | Tick loop present. Multiple kernel/binder paths exist; their relationship and ownership need confirmation before consolidation. |
| Creatures, lifecycle, behavior, movement, senses | `Creatures/BehaiviorEngine.cs`; `Creature.cs`; `CreatureManager.cs`; `CreatureSnapshot.cs`; `CreatureSpawner.cs`; `ICreature.cs`; `MindWavesCreatureBehaviors.cs`; `MindWavesCreatureIntegration.cs`; `MovementEngine.cs`; `SensesEngine.cs`; `Vector2.cs` | Creature snapshot is the nearest existing telemetry DTO. **Local-only:** `Creatures/CreatureSnapshot.cs` has worktree edits. The manager populates common creature values; `CorruptionExposure` exists on the DTO but is not populated by the inspected `GetSnapshot()` implementation. |
| Combat | `Systems/Combat/CombatEngine.cs` | Present; currently wired through `CreatureManager`. |
| CTA / boss / directives / events / commands | `CTA/CTABoss.cs`; `CTA/CTACommandServer.cs`; `CTA/CTADirective.cs`; `CTA/CTAEntity.cs`; `CTA/CTAEventEngine.cs`; `CTA/CTAEvolutionEngine.cs`; `CTA/CTAManager.cs` | CTA values contribute to Overseer telemetry. A command server exists, but no Spine command envelope/result contract is wired. |
| Realm, corruption, healing, junctions, rifts, weather | `Realm/CorruptionMap.cs`; `HealingMap.cs`; `MindWavesRealmHarmonics.cs`; `NonLinearJunctionDetector.cs`; `RealmRegion.cs`; `SpatialRiftEngine.cs`; `WeatherSystem.cs` | Runtime/world subsystems present. `RealmRegion` is a runtime type, not a canonical world/region manifest. Corruption grid is included in engine telemetry but not currently displayed by the viewer. |
| World, map, ecology, weather, economy, factions | `Environment/MindWavesWorldFlux.cs`; `Environment/MindWavesWorldSensors.cs`; `Environment/WeatherEngine.cs`; `Environment/World.cs`; `Ecology/EcologyEngine.cs`; `Economy/EconomyEngine.cs`; `Factions/FactionEngine.cs`; `Factions/Factions.cs`; `Factions/IFaction.cs`; `Factions/MindWavesFactionMind.cs`; `Map/MapEngine.cs`; `Systems/World/EcologyEngine.cs`; `Systems/World/MapEngine.cs`; `Systems/World/PortalEngine.cs`; `Systems/World/WeatherEngine.cs`; `Systems/Interaction/FactionEngine.cs` | Present source. Multiple similarly named engines live in separate namespaces/paths; treat as potentially overlapping, not proven duplicates. |
| Overseer / threat aggregation / defense | `MetaAI/CyberDefenseAgent.cs`; `MetaAI/MindWavesMetaAI.cs`; `MetaAI/Overseer.cs` | Overseer aggregates threat and publishes the current telemetry payload. **Local-only:** `MetaAI/Overseer.cs` has worktree edits. No stable world ID or tick is included in the payload currently serialized by the local snapshot serializer. |
| Telemetry model, serializer, WebSocket publisher | `Telemetry/WebSocketServer.cs`; `Telemetry/TelemetrySnapshot.cs` | WebSocket publisher is present at the pinned revision. **Local-only:** `Telemetry/TelemetrySnapshot.cs` is untracked in the submodule worktree. The legacy payload has threat, CTA, corruption, boss, directive, creatures, and corruption grid; it lacks the proposed Spine envelope fields. |
| MindWaves cognition, agents, telemetry, integration | `Core/MindWaves/MindWavesAgent.cs`; `MindWavesCore.cs`; `MindWavesDebugger.cs`; `MindWavesKernelIntegration.cs`; `MindWavesPersonaBinding.cs`; `MindWavesTelemetry.cs`; `Oracle/MindWavesOracle.cs`; `Oracle/OracleEngine.cs` | Present source; no cross-pillar event/agent contract connection identified. |
| Myth, narrative, symbolic systems, personas, interaction events | `Narrative/NarrativeEngine.cs`; `Personas/DialogueEngine.cs`; `Personas/IPersona.cs`; `Personas/PersonaEngine.cs`; `Systems/Interaction/DialogueEngine.cs`; `Systems/Interaction/EventEngine.cs`; `Systems/Interaction/FactionEngine.cs`; `Systems/Interaction/PersonaEngine.cs`; `Systems/Mythic/ArchetypeEngine.cs`; `Systems/Mythic/CycleEngine.cs`; `Systems/Mythic/MythEngine.cs`; `Systems/Mythic/MythicLawEngine.cs`; `Systems/Mythic/MythicMemoryEngine.cs`; `Systems/Mythic/MythicNarrativeEngine.cs`; `Systems/Mythic/SymbolEngine.cs`; `Systems/Mythic/SymbolicDynamicsEngine.cs` | Present source; potential event/symbol producers, but no serialized Spine event stream identified. |
| Portals, physics, divine math, forge, gothic, grimoire, sacred text, sound, input, UI | `DivineMath/DivineMathEngine.cs`; `Forge/ForgeEngine.cs`; `Gothic/GothicEngine.cs`; `Grimoire/GrimoireEngine.cs`; `Input/InputEngine.cs`; `Physics/MythicPhysicsEngine.cs`; `Portals/MindWavesPortalActivation.cs`; `Portals/MindWavesPortalScene.cs`; `Portals/PortalEngine.cs`; `SacredTexts/SacredTextsEngine.cs`; `Sound/SoundEngine.cs`; `UI/UIEngine.cs`; `webui/HeartbeatPanel.cs` | Present source; no contract attachment established for these internal/runtime capabilities. |
| Time, cycles, and event scheduling | `Time/EventEngine.cs`; `Time/TimeEngine.cs`; `Time/YugaCycle.cs` | Present source; event types are not yet emitted using the Spine event envelope. |
| Build and project boundary | `CaveSharpEngine.csproj` | Targets .NET 8. Root README records current compile/runtime limitations; re-check against the current submodule worktree before treating those as fixed or unchanged. |

The parent-repository source comparison is recorded in the [CaveSharp contract shadow](./cavesharp_shadow/delta_report.md). It distinguishes the pinned submodule source from local-only edits and does not claim successful pinned telemetry emission.

### Complete CaveSharp source-path index

Paths below are relative to `modules/CaveSharp-OS/`. This exhaustive index includes every tracked C# source/project file plus the untracked local telemetry serializer:

```text
CTA/CTABoss.cs
CTA/CTACommandServer.cs
CTA/CTADirective.cs
CTA/CTAEntity.cs
CTA/CTAEventEngine.cs
CTA/CTAEvolutionEngine.cs
CTA/CTAManager.cs
CaveSharpEngine.csproj
Core/Kernel/Kernel.cs
Core/KernelPulseLoop.cs
Core/MindWaves/MindWavesAgent.cs
Core/MindWaves/MindWavesCore.cs
Core/MindWaves/MindWavesDebugger.cs
Core/MindWaves/MindWavesKernelIntegration.cs
Core/MindWaves/MindWavesPersonaBinding.cs
Core/MindWaves/MindWavesTelemetry.cs
Core/Program.cs
Core/SystemBinder.cs
Core/UpdateLoop.cs
Creatures/BehaiviorEngine.cs
Creatures/Creature.cs
Creatures/CreatureManager.cs
Creatures/CreatureSnapshot.cs [modified in local submodule worktree]
Creatures/CreatureSpawner.cs
Creatures/ICreature.cs
Creatures/MindWavesCreatureBehaviors.cs
Creatures/MindWavesCreatureIntegration.cs
Creatures/MovementEngine.cs
Creatures/SensesEngine.cs
Creatures/Vector2.cs
DivineMath/DivineMathEngine.cs
Ecology/EcologyEngine.cs
Economy/EconomyEngine.cs
Environment/MindWavesWorldFlux.cs
Environment/MindWavesWorldSensors.cs
Environment/WeatherEngine.cs
Environment/World.cs
Factions/FactionEngine.cs
Factions/Factions.cs
Factions/IFaction.cs
Factions/MindWavesFactionMind.cs
Forge/ForgeEngine.cs
Gothic/GothicEngine.cs
Grimoire/GrimoireEngine.cs
Input/InputEngine.cs
Kernel/KernelPulseLoop.cs
Map/MapEngine.cs
MetaAI/CyberDefenseAgent.cs
MetaAI/MindWavesMetaAI.cs
MetaAI/Overseer.cs [modified in local submodule worktree]
Narrative/NarrativeEngine.cs
Oracle/MindWavesOracle.cs
Oracle/OracleEngine.cs
Personas/DialogueEngine.cs
Personas/IPersona.cs
Personas/PersonaEngine.cs
Physics/MythicPhysicsEngine.cs
Portals/MindWavesPortalActivation.cs
Portals/MindWavesPortalScene.cs
Portals/PortalEngine.cs
Program.cs
Realm/CorruptionMap.cs
Realm/HealingMap.cs
Realm/MindWavesRealmHarmonics.cs
Realm/NonLinearJunctionDetector.cs
Realm/RealmRegion.cs
Realm/SpatialRiftEngine.cs
Realm/WeatherSystem.cs
SacredTexts/SacredTextsEngine.cs
Sound/SoundEngine.cs
Systems/Combat/CombatEngine.cs
Systems/Interaction/DialogueEngine.cs
Systems/Interaction/EventEngine.cs
Systems/Interaction/FactionEngine.cs
Systems/Interaction/PersonaEngine.cs
Systems/Mythic/ArchetypeEngine.cs
Systems/Mythic/CycleEngine.cs
Systems/Mythic/MythEngine.cs
Systems/Mythic/MythicLawEngine.cs
Systems/Mythic/MythicMemoryEngine.cs
Systems/Mythic/MythicNarrativeEngine.cs
Systems/Mythic/SymbolEngine.cs
Systems/Mythic/SymbolicDynamicsEngine.cs
Systems/SystemBinder.cs
Systems/World/EcologyEngine.cs
Systems/World/MapEngine.cs
Systems/World/PortalEngine.cs
Systems/World/WeatherEngine.cs
Telemetry/TelemetrySnapshot.cs [untracked in local submodule worktree]
Telemetry/WebSocketServer.cs
Time/EventEngine.cs
Time/TimeEngine.cs
Time/YugaCycle.cs
UI/UIEngine.cs
webui/HeartbeatPanel.cs
```

## Pillar 4 — Renzo-Hacker-Lab: operator cockpit

Inspected source: sibling checkout `/workspaces/Renzo-Hacker-Lab`, branch `main`, starting revision `80d0ad1f9804f23816a3501a2ada9a7cbe4a272e`.

| Component | Location | Status |
|---|---|---|
| BIG ANIMAL world UI | `big_animal/ui/world_ui.py`; wired through `big_animal/organism/world_organism.py` and `big_animal/simulation/main_loop.py` | Text UI renders local pulse/organs/climate/events; now also displays the read-only Spine world/latest-snapshot feed when explicitly configured. Full loop currently has unrelated import blockers. |
| ClaudeCode AgentDash cockpit | `claudecode/claudecore/agentdash/cockpit.py`, `agentdash/panels/event_panel.py`, `claudecode/runtime/run_claudecode.py` | Local stimulus/spike/anomaly/fuzz/defense panel plus read-only Spine world/latest-snapshot summary. Full runtime currently has an unrelated missing UTE state import. |
| ClaudeCode event bus | `claudecode/claudecore/event_bus.py` | In-process pub/sub for AgentDash events; these payloads are not versioned world `event_contract` messages. |
| BIG ANIMAL event producer | `big_animal/events/` and `WorldOrganism.step()` | Local world events only; no stable event ID, world ID, per-world sequence, timestamp, or shared transport. Not an event-contract producer. |
| Python tools and red-team scanners | `claudecode/claudecore/`, `Renzo-Hacker-Lab/red-team/`, `labs/` | Actual source present; no checked-in Spine `module_contract` manifests or shared module catalog endpoint found. |
| Legacy telemetry mock/server | `telemetry_server.py` | WebSocket emits placeholder `CREATURES`/`CTA`/`HEATMAP` text; not a Spine telemetry producer and left unchanged. |

## Initial attachment map to the Spine

| Existing source | Intended contract | Consumer / status |
|---|---|---|
| `Realm/RealmRegion.cs`, `Map/MapEngine.cs`, `Systems/World/MapEngine.cs`, `World.cs` | `world_contract/schema.json` | Future catalog of stable world/region/entity definitions. Existing runtime classes are not yet that catalog. |
| `Creatures/CreatureSnapshot.cs`, `MetaAI/Overseer.cs`, `Telemetry/TelemetrySnapshot.cs` | `telemetry_contract/schema.json` | Renzos-Cave and Hacker-Lab read-only consumers use the v1 file/API; full live producer-to-consumer flow remains unverified while CaveSharp build errors persist. |
| `CTA/CTAEventEngine.cs`, `Time/EventEngine.cs`, `Systems/Interaction/EventEngine.cs`, MindWaves and world event sources | `event_contract/schema.json` | Future replayable event stream. Hacker-Lab's local event sources are not contract-conformant; no unified event emitter/store identified. |
| `CTA/CTACommandServer.cs`, `Overseer` command hooks | `command_contract/schema.json` | Future validated command requests/results. Existing hook is not verified as contract-conformant or appropriately exposed. |
| `renzoverse.json`, Python `OrganRegistry`, engine/project manifests | `module_contract/schema.json` | Future catalog of versioned modules and advertised capabilities. Current config is partial and has no contract compatibility declarations; Hacker-Lab source also has no module manifests. |
| `tests/mock_cavesharp_telemetry.py`, `tests/CaveSharpTelemetryHarness/` | Telemetry contract examples/tests | Mock currently emits legacy shape; harness tests local serializer shape. Both need explicit versioned v1 conformance tests before being called contract tests. |

## Conversation-sourced recovery candidates

This section records ideas explicitly named in the user's 2026-10-15 request. It is a recovery queue, not evidence that these ideas appeared in older conversations, existed as files, or had a settled design. Recover original requirements or source artifacts before implementation.

| Candidate organ | Description from current request | Pillar attachment | Intended Spine contract | Code evidence in this checkout | Status / next step |
|---|---|---|---|---|---|
| Corruption physics | Corruption physics and system sketches | CaveSharp-OS | Telemetry, event; world if authored rules are needed | `Realm/CorruptionMap.cs`, `Realm/HealingMap.cs` exist; no source evidence establishes the proposed physics model | Pending specification; inspect older source/history |
| CTA triggers | Conditions that cause CTA actions or state changes | CaveSharp-OS | Event, command; telemetry for resulting state | CTA engines and command hooks exist; trigger semantics are not established by the inventory | Pending specification; identify trigger vocabulary and authority |
| Glyph system | Glyph definitions, interpretation, or transformations | Renzoverse + CaveSharp-OS | World for authored definitions; event for runtime interpretation | `Systems/Mythic/SymbolEngine.cs` and `SymbolicDynamicsEngine.cs` are related code; glyph behavior is unverified | Pending; determine whether glyphs are distinct from current symbol systems |
| Region overlays | Viewer overlays driven by region/world data | Renzos-Cave | World + telemetry | Viewer prototype has no region overlays identified; CaveSharp has `RealmRegion` and map sources | Pending integration; define region IDs, geometry, and overlay state |
| Symbolic agents | Agents operating on symbols or symbolic state | CaveSharp-OS + Renzo-Hacker-Lab | Event, module; command only if they request actions | CaveSharp MindWaves and Hacker-Lab agent sources exist; no cross-pillar symbolic-agent flow is verified | Pending recovery; identify agent ownership and allowed effects |
| Multi-layer spiking neurons | A multi-layer spiking-neuron model | Renzo-Hacker-Lab or Renzoverse cognition; exact owner unknown | Module; event only for published runtime observations | No implementation confirmed in this checkout | Unverified concept; recover design/source before assigning implementation |
| Attention tensors | Tensor-based attention representation or transform | Renzo-Hacker-Lab or Renzoverse cognition; exact owner unknown | Module; telemetry only if it is an observable runtime output | No implementation confirmed in this checkout | Unverified concept; recover design/source before assigning implementation |
| Runtime loops | Simulation/runtime scheduling and update loops | CaveSharp-OS | Telemetry snapshot tick; event sequence | `Core/UpdateLoop.cs` and kernel pulse loop sources are present | Partially present; reconcile loop ownership and add contract metadata |
| World-generation rules | Rules for generating worlds, regions, or entities | Renzoverse + CaveSharp-OS | World | No canonical worldgen rules/configuration identified | Pending specification and implementation |
| Cockpit panels | Operator-facing dashboards and controls | Renzo-Hacker-Lab | Telemetry + world read-only; module when manifests exist; command only for authorized controls | BIG ANIMAL WorldUI and ClaudeCode AgentDash exist and consume validated snapshot/world data; no module manifest catalog or command flow | Snapshot/world consumer implemented; verify against live CaveSharp and define further contracts only when producers exist |
| Telemetry shapes | Payload layouts exchanged between engine and clients | All pillars | Telemetry | Legacy CaveSharp WebSocket payload, viewer parser, Python mock, and local serializer harness are present | Legacy implementation exists; v1 Spine conformance is pending |
| Module manifests | Descriptions of module identity, version, capabilities, and compatibility | Renzoverse; all modules publish | Module | `renzoverse.json` is a partial configuration, not the new manifest contract | Draft schema exists; populate and validate manifests after contract review |
| Python tools | Python utilities or tool modules | Renzoverse + Renzo-Hacker-Lab; ownership depends on source | Module; event/command only where tool behavior requires them | Local Python registry, Hacker-Lab BigAnimal/ClaudeCode, and red-team tools exist; no Hacker-Lab Spine module manifests are present | Inventory source; create manifests only with module owner/version/capability metadata |
| Region maps | Authored or runtime maps of regions | Renzoverse + CaveSharp-OS + Renzos-Cave | World + telemetry | `RealmRegion`, `MapEngine`, and `World` sources exist; no canonical map artifact identified | Pending; distinguish authored catalog from simulation map state |

## Out-of-checkout recovery

The Hacker-Lab checkout was added to the inspection scope after the initial inventory and is recorded above with its starting revision. A separate Renzos-Cave repository and untracked files on other machines were not inspected. Add further sources with repository and revision provenance when they become available.
