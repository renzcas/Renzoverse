using System.Text.Json;
using CaveSharp.Creatures;
using CaveSharp.Telemetry;

var creatures = new[]
{
    new CreatureSnapshot
    {
        EntityId = "creature.tunnel-rat.legacy-hidden",
        Name = "TunnelRat",
        Health = 85,
        Aggression = 20,
        Hunger = 35,
        X = -8,
        Y = 4,
        CorruptionExposure = 3,
        IsAfraid = false
    },
    new CreatureSnapshot
    {
        Name = "StoneCrawler",
        Health = 42,
        Aggression = 75,
        Hunger = 80,
        X = 7,
        Y = -5,
        CorruptionExposure = 18,
        IsAfraid = true
    }
};
var corruptionGrid = new float[2, 2];
corruptionGrid[1, 0] = 0.5f;

var json = TelemetrySnapshotSerializer.Serialize(
    threat: 24,
    cta: 18,
    corruption: 12.5f,
    creatures,
    ctaBoss: "Telemetry Harness",
    directive: "Verify browser telemetry contract",
    corruptionGrid);

using var document = JsonDocument.Parse(json);
var root = document.RootElement;
Require(root.GetProperty("threat").GetInt32() == 24, "threat");
Require(root.GetProperty("cta").GetSingle() == 18, "cta");
Require(root.GetProperty("corruption").GetSingle() == 12.5f, "corruption");
Require(root.GetProperty("ctaBoss").GetString() == "Telemetry Harness", "ctaBoss");
Require(root.GetProperty("directive").GetString() == "Verify browser telemetry contract", "directive");

var serializedCreatures = root.GetProperty("creatures");
Require(serializedCreatures.GetArrayLength() == 2, "creatures");
var tunnelRat = serializedCreatures[0];
Require(tunnelRat.GetProperty("name").GetString() == "TunnelRat", "creature.name");
Require(tunnelRat.GetProperty("health").GetSingle() == 85, "creature.health");
Require(tunnelRat.GetProperty("aggression").GetSingle() == 20, "creature.aggression");
Require(tunnelRat.GetProperty("hunger").GetSingle() == 35, "creature.hunger");
Require(tunnelRat.GetProperty("x").GetSingle() == -8, "creature.x");
Require(tunnelRat.GetProperty("y").GetSingle() == 4, "creature.y");
Require(tunnelRat.GetProperty("corruptionExposure").GetSingle() == 3, "creature.corruptionExposure");
Require(!tunnelRat.GetProperty("isAfraid").GetBoolean(), "creature.isAfraid");
Require(!tunnelRat.TryGetProperty("entityId", out _), "legacy creature identity remains private");
Require(
    root.GetProperty("corruptionGrid")[1][0].GetSingle() == 0.5f,
    "corruptionGrid");

var legacy = new TelemetrySnapshot(
    24,
    18,
    12.5f,
    creatures,
    "Telemetry Harness",
    "Verify browser telemetry contract",
    [[0.0f, 0.0f], [0.5f, 0.0f]]);
var sourceCorruptionGrid = new float[2, 2];
sourceCorruptionGrid[1, 0] = 0.5f;
var generatedAt = new DateTimeOffset(2026, 10, 15, 17, 0, 0, TimeSpan.FromHours(-4));
var contractSnapshot = SnapshotContractBuilder.Build(
    legacy,
    sourceCorruptionGrid,
    "renzoverse.mock.cave",
    42,
    generatedAt,
    creature => creature.Name switch
    {
        "TunnelRat" => "creature.tunnel-rat.001",
        "StoneCrawler" => "creature.stone-crawler.001",
        _ => throw new InvalidOperationException($"No stable ID for '{creature.Name}'.")
    });
var contractJson = JsonSerializer.Serialize(
    contractSnapshot,
    new JsonSerializerOptions(JsonSerializerDefaults.Web));
using var contractDocument = JsonDocument.Parse(contractJson);
var contractRoot = contractDocument.RootElement;
Require(contractRoot.GetProperty("schemaVersion").GetString() == "1.0.0", "schemaVersion");
Require(contractRoot.GetProperty("worldId").GetString() == "renzoverse.mock.cave", "worldId");
Require(contractRoot.GetProperty("tick").GetInt64() == 42, "tick");
Require(
    contractRoot.GetProperty("generatedAt").GetDateTimeOffset() ==
    generatedAt.ToUniversalTime(),
    "generatedAt");
Require(
    contractRoot.GetProperty("creatures")[0].GetProperty("entityId").GetString() ==
    "creature.tunnel-rat.001",
    "creature.entityId");
Require(
    contractRoot.GetProperty("corruptionGrid")[1][0].GetSingle() == 0.5f,
    "contract.corruptionGrid");
Require(
    contractRoot.GetProperty("creatures")[0].TryGetProperty("Name", out _) is false,
    "contract.creature.camelCase");

var duplicateIdentityRejected = false;
try
{
    SnapshotContractBuilder.Build(
        legacy,
        sourceCorruptionGrid,
        "renzoverse.mock.cave",
        42,
        generatedAt,
        _ => "creature.duplicate");
}
catch (ArgumentException)
{
    duplicateIdentityRejected = true;
}
Require(duplicateIdentityRejected, "duplicate stable IDs rejected");

var outputDirectory = Path.Combine(
    Path.GetTempPath(),
    $"renzoverse-phase9-{Guid.NewGuid():N}");
var outputPath = Path.Combine(outputDirectory, "cavesharp.v1.json");
var disabledActivation = new ContractTelemetryOptions(
    false,
    outputPath: outputPath).Activate();
Require(disabledActivation is null, "contract telemetry disabled by default");
Require(!Directory.Exists(outputDirectory), "disabled activation creates no output directory");

var catalogPath = Path.GetFullPath("shared/worlds/cavesharp.json");
var activation = new ContractTelemetryOptions(
    true,
    "renzoverse.cavesharp.primary",
    catalogPath,
    outputPath).Activate()
    ?? throw new InvalidOperationException("Enabled contract telemetry did not activate.");
Require(
    activation.WorldId == "renzoverse.cavesharp.primary",
    "world catalog resolves configured identity");
await activation.Emitter.EmitAsync(
    legacy,
    sourceCorruptionGrid,
    activation.WorldId,
    43,
    generatedAt,
    creature => creature.Name switch
    {
        "TunnelRat" => "creature.tunnel-rat.001",
        "StoneCrawler" => "creature.stone-crawler.001",
        _ => throw new InvalidOperationException($"No stable ID for '{creature.Name}'.")
    });
var publishedContractJson = await File.ReadAllTextAsync(outputPath);
using (var publishedDocument = JsonDocument.Parse(publishedContractJson))
{
    var publishedRoot = publishedDocument.RootElement;
    Require(publishedRoot.GetProperty("tick").GetInt64() == 43, "published contract tick");
    Require(
        publishedRoot.GetProperty("worldId").GetString() == activation.WorldId,
        "published contract world identity");
}
Require(
    Directory.GetFiles(outputDirectory, "*.tmp").Length == 0,
    "atomic transport removes temporary files");

var missingWorldRejected = false;
try
{
    new ContractTelemetryOptions(
        true,
        "renzoverse.unknown",
        catalogPath,
        Path.Combine(outputDirectory, "unresolved", "snapshot.json")).Activate();
}
catch (InvalidDataException)
{
    missingWorldRejected = true;
}
Require(missingWorldRejected, "unknown world identity blocks activation");

var legacyPathRejected = false;
try
{
    new ContractTelemetryOptions(
        true,
        "renzoverse.cavesharp.primary",
        catalogPath,
        "shared/telemetry/cavesharp.json").Activate();
}
catch (InvalidOperationException)
{
    legacyPathRejected = true;
}
Require(legacyPathRejected, "contract output cannot replace legacy telemetry");
Directory.Delete(outputDirectory, recursive: true);

var nonFiniteValueRejected = false;
try
{
    SnapshotContractBuilder.Build(
        legacy with { Cta = float.NaN },
        sourceCorruptionGrid,
        "renzoverse.mock.cave",
        42,
        generatedAt,
        creature => creature.Name);
}
catch (ArgumentOutOfRangeException)
{
    nonFiniteValueRejected = true;
}
Require(nonFiniteValueRejected, "non-finite values rejected");

var emittedJson = string.Empty;
var emitter = new ContractTelemetryEmitter((json, _) =>
{
    emittedJson = json;
    return Task.CompletedTask;
});
await emitter.EmitAsync(
    legacy,
    sourceCorruptionGrid,
    "renzoverse.mock.cave",
    42,
    generatedAt,
    creature => creature.Name switch
    {
        "TunnelRat" => "creature.tunnel-rat.001",
        "StoneCrawler" => "creature.stone-crawler.001",
        _ => throw new InvalidOperationException($"No stable ID for '{creature.Name}'.")
    });
Require(emittedJson == contractJson, "contract emitter output");

var rejectedPublish = false;
var invalidEmitter = new ContractTelemetryEmitter((_, _) =>
{
    rejectedPublish = true;
    return Task.CompletedTask;
});
try
{
    await invalidEmitter.EmitAsync(
        legacy,
        sourceCorruptionGrid,
        "renzoverse.mock.cave",
        -1,
        generatedAt,
        _ => "creature.invalid");
    throw new InvalidOperationException("Negative tick was not rejected.");
}
catch (ArgumentOutOfRangeException)
{
    Require(!rejectedPublish, "invalid contract not published");
}

Console.WriteLine(json);
Console.Error.WriteLine("CaveSharp legacy and contract telemetry harness passed.");

static void Require(bool condition, string field)
{
    if (!condition)
        throw new InvalidOperationException($"Telemetry payload contract failed for '{field}'.");
}
