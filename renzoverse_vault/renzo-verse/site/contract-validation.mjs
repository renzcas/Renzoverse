const isObject = (value) =>
  value !== null && typeof value === 'object' && !Array.isArray(value);

const requireString = (value, path) => {
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new Error(`${path} must be a non-empty string`);
  }
};

const requireFiniteNumber = (value, path) => {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`${path} must be a finite number`);
  }
};

export function validateWorld(world) {
  if (!isObject(world)) throw new Error('World document must be an object');
  if (world.schemaVersion !== '1.0.0') throw new Error('Unsupported world schema version');
  for (const field of ['worldId', 'worldVersion', 'name']) {
    requireString(world[field], `world.${field}`);
  }
  for (const [field, idField] of [
    ['regions', 'regionId'],
    ['entityTypes', 'entityTypeId']
  ]) {
    if (!Array.isArray(world[field])) throw new Error(`world.${field} must be an array`);
    const ids = new Set();
    world[field].forEach((item, index) => {
      if (!isObject(item)) throw new Error(`world.${field}[${index}] must be an object`);
      requireString(item[idField], `world.${field}[${index}].${idField}`);
      requireString(item.name, `world.${field}[${index}].name`);
      if (ids.has(item[idField])) {
        throw new Error(`world.${field}[${index}].${idField} is duplicated`);
      }
      ids.add(item[idField]);
    });
  }
  return world;
}

export function validateTelemetry(snapshot, expectedWorldId) {
  if (!isObject(snapshot)) throw new Error('Telemetry snapshot must be an object');
  if (snapshot.schemaVersion !== '1.0.0') {
    throw new Error(`Unsupported telemetry schema version: ${snapshot.schemaVersion}`);
  }
  requireString(snapshot.worldId, 'telemetry.worldId');
  if (expectedWorldId && snapshot.worldId !== expectedWorldId) {
    throw new Error(`Telemetry world '${snapshot.worldId}' does not match '${expectedWorldId}'`);
  }
  if (!Number.isSafeInteger(snapshot.tick) || snapshot.tick < 0) {
    throw new Error('telemetry.tick must be a non-negative safe integer');
  }
  requireString(snapshot.generatedAt, 'telemetry.generatedAt');
  if (
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(snapshot.generatedAt) ||
    !Number.isFinite(Date.parse(snapshot.generatedAt))
  ) {
    throw new Error('telemetry.generatedAt must be an RFC 3339 UTC date-time');
  }
  requireFiniteNumber(snapshot.threat, 'telemetry.threat');
  requireFiniteNumber(snapshot.cta, 'telemetry.cta');
  requireFiniteNumber(snapshot.corruption, 'telemetry.corruption');
  requireString(snapshot.ctaBoss, 'telemetry.ctaBoss');
  requireString(snapshot.directive, 'telemetry.directive');
  if (!Array.isArray(snapshot.creatures)) {
    throw new Error('telemetry.creatures must be an array');
  }
  const entityIds = new Set();
  snapshot.creatures.forEach((creature, index) => {
    const path = `telemetry.creatures[${index}]`;
    if (!isObject(creature)) throw new Error(`${path} must be an object`);
    requireString(creature.entityId, `${path}.entityId`);
    if (entityIds.has(creature.entityId)) throw new Error(`${path}.entityId is duplicated`);
    entityIds.add(creature.entityId);
    requireString(creature.name, `${path}.name`);
    for (const field of [
      'health',
      'aggression',
      'hunger',
      'x',
      'y',
      'corruptionExposure'
    ]) {
      requireFiniteNumber(creature[field], `${path}.${field}`);
    }
    if (typeof creature.isAfraid !== 'boolean') {
      throw new Error(`${path}.isAfraid must be a boolean`);
    }
  });
  if (!Array.isArray(snapshot.corruptionGrid)) {
    throw new Error('telemetry.corruptionGrid must be an array');
  }
  snapshot.corruptionGrid.forEach((row, rowIndex) => {
    if (!Array.isArray(row)) {
      throw new Error(`telemetry.corruptionGrid[${rowIndex}] must be an array`);
    }
    row.forEach((value, columnIndex) => {
      requireFiniteNumber(value, `telemetry.corruptionGrid[${rowIndex}][${columnIndex}]`);
    });
  });
  return snapshot;
}
