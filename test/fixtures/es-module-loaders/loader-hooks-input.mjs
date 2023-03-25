import assert from 'assert';
import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';


let resolveCalls = 0;
let loadCalls = 0;

export async function resolve(specifier, context, next) {
  if (specifier.endsWith('loader-store-data.mjs')) {
    return next(specifier, context);
  }

  resolveCalls++;
  let url;

  if (resolveCalls === 1) {
    url = new URL(specifier).href;
    assert.match(specifier, /hooks-input\.mjs$/);
    assert.strictEqual(context.parentURL, undefined);
    assert.deepStrictEqual(context.importAssertions, {});
  } else if (resolveCalls === 2) {
    url = new URL(specifier, context.parentURL).href;
    assert.match(specifier, /experimental\.json$/);
    assert.match(context.parentURL, /hooks-input\.mjs$/);
    assert.deepStrictEqual(context.importAssertions, {
      type: 'json',
    });
  }

  // Ensure `context` has all and only the properties it's supposed to
  assert.deepStrictEqual(Reflect.ownKeys(context), [
    'conditions',
    'importAssertions',
    'parentURL',
  ]);
  assert.ok(Array.isArray(context.conditions));
  assert.strictEqual(typeof next, 'function');

  const returnValue = {
    url,
    format: 'test',
    shortCircuit: true,
  }

  globalThis.PUSH_SYNC(JSON.stringify(returnValue));

  return returnValue;
}

export async function load(url, context, next) {
  if (url.endsWith('loader-store-data.mjs')) {
    return next(url, context);
  }

  const push = globalThis.PUSH_ASYNC();

  loadCalls++;
  const source = await readFile(fileURLToPath(url));
  let format;

  if (loadCalls === 1) {
    assert.match(url, /hooks-input\.mjs$/);
    assert.deepStrictEqual(context.importAssertions, {});
    format = 'module';
  } else if (loadCalls === 2) {
    assert.match(url, /experimental\.json$/);
    assert.deepStrictEqual(context.importAssertions, {
      type: 'json',
    });
    format = 'json';
  }

  assert.ok(new URL(url));
  // Ensure `context` has all and only the properties it's supposed to
  assert.deepStrictEqual(Object.keys(context), [
    'format',
    'importAssertions',
  ]);
  assert.strictEqual(context.format, 'test');
  assert.strictEqual(typeof next, 'function');

  const returnValue = {
    source,
    format,
    shortCircuit: true,
  };

  push(JSON.stringify(returnValue));

  return returnValue;
}
