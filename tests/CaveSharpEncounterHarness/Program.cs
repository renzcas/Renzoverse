using CaveSharp.Creatures;
using CaveSharp.Realm;

var territory = new TerritoryBoundary(0f, 0f, 10f);
Require(territory.Contains(10f, 0f), "territory includes its perimeter");
Require(!territory.Contains(10.01f, 0f), "territory excludes points beyond its perimeter");

var encounter = new TerritorialEncounter(territory, strikeRadius: 2f);
Require(encounter.State == TerritorialAggroState.Ambush, "encounter starts in ambush");
var corruption = new CorruptionMap();
var junctions = new NonLinearJunctionDetector();
var creatureManager = new CreatureManager(
    new BehaviorEngine(corruption, junctions),
    new MovementEngine(corruption, junctions),
    new SensesEngine(corruption, junctions),
    new CombatEngine());
creatureManager.RegisterTerritorialEncounter(encounter);

creatureManager.Tick(1f / 60f, new EncounterTarget(8f, 0f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "territory entry starts tracking");
creatureManager.Tick(1f / 60f, new EncounterTarget(1f, 0f));
Require(encounter.State == TerritorialAggroState.StrikeEngagement, "close approach advances tracking to strike engagement");
creatureManager.Tick(1f / 60f, new EncounterTarget(5f, 0f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "retreat from strike range returns to tracking");
creatureManager.Tick(1f / 60f, new EncounterTarget(10.01f, 0f));
Require(encounter.State == TerritorialAggroState.Ambush, "leaving territory resets the encounter");
creatureManager.Tick(1f / 60f, new EncounterTarget(1f, 0f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "close entry still begins with tracking");
creatureManager.Tick(1f / 60f);
Require(encounter.State == TerritorialAggroState.Ambush, "missing target returns the guardian to ambush");

Console.WriteLine("CaveSharp territorial encounter tests passed.");

static void Require(bool condition, string description)
{
    if (!condition)
        throw new InvalidOperationException($"Territorial encounter test failed: {description}.");
}