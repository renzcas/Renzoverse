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

creatureManager.Tick(1f / 60f, Observe(8f, 0f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "territory entry starts tracking");
creatureManager.Tick(1f / 60f, Observe(1f, 0f));
Require(encounter.State == TerritorialAggroState.StrikeEngagement, "close approach advances tracking to strike engagement");
creatureManager.Tick(1f / 60f, Observe(5f, 0f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "retreat from strike range returns to tracking");
creatureManager.Tick(1f / 60f, Observe(10.01f, 0f));
Require(encounter.State == TerritorialAggroState.Ambush, "leaving territory resets the encounter");
creatureManager.Tick(1f / 60f, Observe(1f, 0f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "close entry still begins with tracking");
creatureManager.Tick(1f / 60f);
Require(encounter.State == TerritorialAggroState.Ambush, "missing target returns the guardian to ambush");

creatureManager.Tick(1f / 60f, Observe(1f, 0f, visibility: 0.1f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "darkness delays a strike");
creatureManager.Tick(1f / 60f, Observe(1f, 0f, perceivedThreat: 0.9f));
Require(encounter.State == TerritorialAggroState.Withdrawal, "high immediate threat triggers withdrawal");
creatureManager.Tick(1f / 60f, Observe(1f, 0f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "reduced threat returns to tracking before re-engaging");
creatureManager.Tick(1f / 60f, Observe(1f, 0f));
Require(encounter.State == TerritorialAggroState.StrikeEngagement, "clear, low-risk approach permits a strike");
creatureManager.Tick(1f / 60f, Observe(1f, 0f, visibility: 0.1f));
Require(encounter.State == TerritorialAggroState.TerritorialTracking, "darkness interrupts strike confidence");

    var now = new DateTimeOffset(2026, 10, 16, 5, 0, 0, TimeSpan.Zero);
    var targetProvider = new PlayerEncounterTargetProvider(
        TimeSpan.FromSeconds(1), () => now);
    Require(targetProvider.GetCurrentObservation() is null, "target starts disconnected");
    var playerObservation = new EncounterObservation(
        new EncounterTarget(-1.5f, -40.57f), 0.9f, 0.2f);
    targetProvider.Publish(playerObservation);
    Require(
        targetProvider.GetCurrentObservation() == playerObservation,
        "provider exposes the latest validated player position");
    now += TimeSpan.FromSeconds(1.1);
    Require(targetProvider.GetCurrentObservation() is null, "stale player position expires");

    var invalidObservationRejected = false;
    try
    {
        targetProvider.Publish(new EncounterObservation(
            new EncounterTarget(0f, 0f), 1.1f, 0f));
    }
    catch (ArgumentOutOfRangeException)
    {
        invalidObservationRejected = true;
    }
    Require(invalidObservationRejected, "provider rejects invalid visibility input");

Console.WriteLine("CaveSharp territorial encounter tests passed.");

static EncounterObservation Observe(
    float x,
    float y,
    float visibility = 1f,
    float perceivedThreat = 0f)
{
    return new EncounterObservation(new EncounterTarget(x, y), visibility, perceivedThreat);
}

static void Require(bool condition, string description)
{
    if (!condition)
        throw new InvalidOperationException($"Territorial encounter test failed: {description}.");
}