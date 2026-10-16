# Renzoverse

Renzoverse is the master hub and registry for Renzo's standalone engines, reusable organs, and worlds. It is a modular home base, not one monolithic application.

## How the pieces fit

- See the [unification map](./arch_map.md) for the target boundaries, verified integration baseline, and phased path for connecting the four pillars.
- See the [organ inventory](./organ_inventory.md) for source files and subsystem status in this checkout, and the [Spine schemas](./renzoverse_spine/README.md) for the initial versioned contracts.
- See the [organ status dashboard](./organ_status.md) for implementation, verification, and integration status, including explicitly sourced recovery candidates.
- Phase 3 artifacts: [contract conformance matrix](./contract_conformance.md), [organ adapter specifications](./organ_adapters.md), and [contract activation plan](./contract_activation_plan.md).
- Phase 4 artifacts: [cross-pillar dependency graph](./cross_pillar_graph.md), [contract flow simulation](./contract_flow.md), and [integration readiness report](./integration_readiness.md).
- The standalone [Spine Runtime](./spine_runtime/README.md) validates the checked-in schemas, routes deterministic local fixtures, and runs its harness without changing CaveSharp or the viewer.
- The [CaveSharp shadow and delta report](./cavesharp_shadow/delta_report.md) documents pinned-source telemetry gaps and local-only adapter additions without changing the pinned submodule commit.
- Phase 7 added C# contract snapshot builder/emitter components beside CaveSharp telemetry. Phase 9 wires them behind a disabled-by-default Overseer gate and a separate file transport; the legacy WebSocket payload remains unchanged.
- [Phase 8 activation plan](./phase8_activation_plan.md) proposes authoritative metadata owners, an opt-in Overseer boundary, a separate snapshot transport, and gates for future viewer/Hacker-Lab activation. Planning only; no runtime or consumer is activated.
- [Phase 9 transport implementation](./phase9_contract_transport.md) added an opt-in, atomic v1 snapshot file, an authored CaveSharp world definition, authoritative update tick and UTC timestamp propagation, and per-instance creature IDs. At Phase 9 completion, the legacy WebSocket payload and consumers were unchanged.
- [Phase 10 consumer activation](./phase10_viewer_activation.md) covers the validated viewer and read-only Hacker-Lab BIG ANIMAL/AgentDash snapshot consumers, plus the remaining module/event and live-engine gates. Phase 10 is not complete yet.
- **Renzoverse root** holds module configuration in [`renzoverse.json`](./renzoverse.json) and shared communication areas under [`shared/`](./shared).
- **Organs** are reusable Python and C# capabilities that engines can discover and call. Python organs share the request/response types in `orchestrator/organ_contract.py`; each organ's `contract.py` re-exports that contract, and executable organs provide `execute(request)` in `engine.py`.
- **CaveSharp-OS** is the simulation engine in `modules/CaveSharp-OS/`. It advances cave-world state and publishes a live snapshot.
- **Renzos-Cave** is the 3D gameworld where Trog-Croman explores and the CaveSharp state is visualized. Its current prototype lives in `renzoverse_vault/renzo-verse/site/`.

## Run the first connected slice

From the repository root, start the simulation:

```sh
dotnet run --project modules/CaveSharp-OS/CaveSharpEngine.csproj
```

In a second terminal, serve the cave frontend:

```sh
python3 -m http.server 8000 --directory renzoverse_vault/renzo-verse/site
```

Open `http://localhost:8000`, then enter the cave. Use WASD to move and click the world to look around. Stop the simulation with Ctrl+C.

In this Codespace, the newly installed .NET 8 SDK/runtime lives under `/usr/lib/dotnet`, while the pre-existing `dotnet` command points to another SDK root. If plain `dotnet run` reports that .NET 8 is missing, run CaveSharp with `DOTNET_ROOT=/usr/lib/dotnet /usr/lib/dotnet/dotnet run --project modules/CaveSharp-OS/CaveSharpEngine.csproj`.

## Current telemetry contract

CaveSharp targets .NET 8 and broadcasts its telemetry JSON over `ws://localhost:8181/telemetry/`. The cave page consumes that WebSocket stream directly to display threat, corruption, CTA, and creature data. Creature fields are serialized in camel case to match the browser contract.

`renzoverse.json` declares a telemetry output path and sync interval, but the pinned CaveSharp source does not currently read that configuration or write `shared/telemetry/cavesharp.json`; that file-based handoff is not implemented yet. The `events_out` path is also reserved. The Python organ contract and discovery registry are implemented; concrete organ engines, cross-language invocation, event output, and additional worlds remain future work.

The pinned CaveSharp source currently has unrelated compile errors, so the run command above will not start until those are repaired.

## Discover and call Python organs

The registry skips empty `engine.py` placeholders and loads only organs that provide a callable `execute(request)` returning an `OrganResponse`. Load errors and invalid responses are reported rather than silently accepted.

After an organ's `engine.py` implements `execute(request)`, call it through the registry:

```python
from orchestrator.organ_contract import OrganRequest
from orchestrator.registry import discover_organs

registry = discover_organs()
response = registry.execute(
    "IngestionPipeline",
    OrganRequest(payload={"source": "example"}, context_tags=["demo"]),
)
```

`IngestionPipeline` is the first executable organ. It accepts a single record in the payload or a `records` list of dictionaries, returns the ingested records and count, and reports malformed batches through `OrganResponse`. The other five organ engines remain placeholders. Run the registry tests with `python3 -m unittest discover -s tests -v`.