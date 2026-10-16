using CaveSharp.Creatures;

var territory = new TerritoryBoundary(0f, 0f, 10f);
Require(territory.Contains(10f, 0f), "territory includes its perimeter");
Require(!territory.Contains(10.01f, 0f), "territory excludes points beyond its perimeter");

var encounter = new TerritorialEncounter(territory, strikeRadius: 2f);
Require(encounter.State == TerritorialAggroState.Ambush, "encounter starts in ambush");
Require(
    encounter.Update(targetPresent: true, targetX: 8f, targetY: 0f)
        == TerritorialAggroState.TerritorialTracking,
    "territory entry starts tracking");
Require(
    encounter.Update(targetPresent: true, targetX: 1f, targetY: 0f)
        == TerritorialAggroState.StrikeEngagement,
    "close approach advances tracking to strike engagement");
Require(
    encounter.Update(targetPresent: true, targetX: 5f, targetY: 0f)
        == TerritorialAggroState.TerritorialTracking,
    "retreat from strike range returns to tracking");
Require(
    encounter.Update(targetPresent: true, targetX: 10.01f, targetY: 0f)
        == TerritorialAggroState.Ambush,
    "leaving territory resets the encounter");
Require(
    encounter.Update(targetPresent: true, targetX: 1f, targetY: 0f)
        == TerritorialAggroState.TerritorialTracking,
    "entering directly at close range still begins with tracking");
Require(
    encounter.Update(targetPresent: false, targetX: 1f, targetY: 0f)
        == TerritorialAggroState.Ambush,
    "lost target returns the guardian to ambush");

Console.WriteLine("CaveSharp territorial encounter tests passed.");

static void Require(bool condition, string description)
{
    if (!condition)
        throw new InvalidOperationException($"Territorial encounter test failed: {description}.");
}