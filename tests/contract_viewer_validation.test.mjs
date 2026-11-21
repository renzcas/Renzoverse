import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { validateTelemetry, validateWorld } from '../renzoverse_vault/renzo-verse/site/contract-validation.mjs';

const fixturePath = new URL(
  '../spine_runtime/mock_bus/telemetry_stream.json',
  import.meta.url
);
const worldPath = new URL(
  '../spine_runtime/mock_bus/world_state.json',
  import.meta.url
);
const snapshots = JSON.parse(await readFile(fixturePath, 'utf8'));
const worldFixture = JSON.parse(await readFile(worldPath, 'utf8'));
const world = { ...worldFixture, worldId: snapshots[0].worldId };

test('accepts complete v1 telemetry and authored world fixtures', () => {
  assert.equal(validateWorld(world), world);
  assert.equal(validateTelemetry(snapshots[0], world.worldId), snapshots[0]);
});

test('rejects unsupported versions, missing envelope, and mismatched world', () => {
  assert.throws(
    () => validateTelemetry({ ...snapshots[0], schemaVersion: '2.0.0' }),
    /Unsupported telemetry schema version/
  );
  const missingWorld = { ...snapshots[0] };
  delete missingWorld.worldId;
  assert.throws(() => validateTelemetry(missingWorld), /worldId/);
  assert.throws(
    () => validateTelemetry(snapshots[0], 'renzoverse.other.world'),
    /does not match/
  );
});

test('rejects incomplete or non-finite creature values without coercion', () => {
  const invalidCreature = structuredClone(snapshots[0]);
  delete invalidCreature.creatures[0].hunger;
  assert.throws(() => validateTelemetry(invalidCreature), /hunger/);

  const nonFiniteGrid = structuredClone(snapshots[0]);
  nonFiniteGrid.corruptionGrid[0][0] = Number.NaN;
  assert.throws(() => validateTelemetry(nonFiniteGrid), /finite number/);
});

test('rejects duplicate stable entity identities and invalid UTC timestamps', () => {
  const duplicateIds = structuredClone(snapshots[0]);
  duplicateIds.creatures[1].entityId = duplicateIds.creatures[0].entityId;
  assert.throws(() => validateTelemetry(duplicateIds), /duplicated/);

  assert.throws(
    () => validateTelemetry({ ...snapshots[0], generatedAt: 'not-a-time' }),
    /RFC 3339 UTC/
  );
});

test('rejects duplicate world definition identities', () => {
  const duplicateRegion = structuredClone(world);
  duplicateRegion.regions.push({ ...duplicateRegion.regions[0] });
  assert.throws(() => validateWorld(duplicateRegion), /duplicated/);
});
