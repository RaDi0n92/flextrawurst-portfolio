import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../scripts/build_surface.ts', import.meta.url), 'utf8');
const helper = source.slice(source.indexOf('function archiveFetch('), source.indexOf('async function caRohdateiOeffnen('));

test('archive fetch forwards current credentials only to same-origin archive routes', async () => {
  const calls: any[] = [];
  let token = 'synthetic-admin';
  const context: any = {URL, URLSearchParams, Headers,
    location: {href: 'https://example.test/', origin: 'https://example.test', search: '?archkey=synthetic-key'},
    localStorage: {getItem: () => token},
    fetch: (...args: any[]) => {calls.push(args); return Promise.resolve({ok:true});}};
  vm.runInNewContext(helper, context);
  await context.archiveFetch('/api/codegeil/eintraege', {signal: 'synthetic-signal'});
  assert.equal(calls[0][1].headers.get('Authorization'), 'Bearer synthetic-admin');
  assert.equal(calls[0][1].headers.get('X-Archive-Key'), 'synthetic-key');
  assert.equal(calls[0][1].redirect, 'error');
  assert.equal(calls[0][1].cache, 'no-store');
  assert.equal(calls[0][1].signal, 'synthetic-signal');
  assert.equal(calls[0][0], 'https://example.test/api/codegeil/eintraege');
  token = 'Bearer prefixed-admin';
  await context.archiveFetch('/api/codegeil/eintraege');
  assert.equal(calls.pop()[1].headers.get('Authorization'), 'Bearer prefixed-admin');
  token = '';
  context.location.search = '?crawlschluessel=synthetic-crawl';
  await context.archiveFetch('/api/guardianstyle/eintraege');
  assert.equal(calls[1][1].headers.has('Authorization'), false);
  assert.equal(calls[1][1].headers.get('X-Crawl-Key'), 'synthetic-crawl');
  assert.throws(() => context.archiveFetch('https://other.test/api/codegeil/eintraege'));
  assert.throws(() => context.archiveFetch('/api/me'));
  assert.equal(calls.length, 2);
});

test('all existing archive calls use credential helper', () => {
  assert.equal((source.match(/await archiveFetch\('\/api\/(?:code-archaeologie|codegeil|guardianstyle|systemweite-archaeologie)\//g) || []).length, 18);
  assert.equal((source.match(/await fetch\('\/api\/(?:code-archaeologie|codegeil|guardianstyle|systemweite-archaeologie)\//g) || []).length, 0);
});
