// tools/types_and_sql_from_schema.mjs
// Liest schema.json und erzeugt:
// 1) packages/core/src/types/db.ts
// 2) apps/main/src/db/migrations/001_init.sql

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url)); // robust auf Windows
const root = path.resolve(here, '..');                     // Repo-Root (.. aus tools/)
const candidates = [
  path.join(root, 'schema.json'),
  path.join(process.cwd(), 'schema.json')
];

const schemaPath = candidates.find(p => fs.existsSync(p));
if (!schemaPath) {
  console.error('❌ schema.json nicht gefunden. Erwartet unter:\n - ' + candidates.join('\n - '));
  console.error('💡 Tipp: zuerst ausführen:  python .\\tools\\schema_extractor.py');
  process.exit(1);
}

function loadSchema() {
  const raw = fs.readFileSync(schemaPath, 'utf8');
  return JSON.parse(raw);
}

function sqliteToTs(t) {
  t = String(t || '').toUpperCase();
  if (t.includes('INT')) return 'number';
  if (t.includes('REAL') || t.includes('FLOA') || t.includes('DOUB')) return 'number';
  if (t.includes('BLOB')) return 'Uint8Array';
  // TEXT/NUMERIC → string als Default (für ISO/JSON/Flex)
  return 'string';
}

function genTypes(schema) {
  const lines = [];
  lines.push(`export type ID = string;`);
  for (const [tname, tdef] of Object.entries(schema.tables)) {
    const iface = tname.replace(/(^|_)([a-z])/g, (_, __, c) => c.toUpperCase()); // snake_case → PascalCase
    lines.push(`\nexport interface ${iface} {`);
    for (const [col, cdef] of Object.entries(tdef.columns)) {
      const ts = sqliteToTs(cdef.type);
      const optional = cdef.notNull ? '' : '?';
      lines.push(`  ${col}${optional}: ${col === 'id' ? 'ID' : ts};`);
    }
    lines.push(`}`);
  }
  return lines.join('\n') + '\n';
}

function genSql(schema) {
  const lines = [];
  lines.push(`PRAGMA foreign_keys = ON;`);
  for (const [tname, tdef] of Object.entries(schema.tables)) {
    lines.push(`\nCREATE TABLE IF NOT EXISTS ${tname} (`);
    const cols = [];
    for (const [col, cdef] of Object.entries(tdef.columns)) {
      const parts = [`  ${col} ${cdef.type || 'TEXT'}`];
      if (cdef.pk) parts.push('PRIMARY KEY');
      if (cdef.notNull) parts.push('NOT NULL');
      if (cdef.default) parts.push(`DEFAULT ${cdef.default}`);
      cols.push(parts.join(' '));
    }
    for (const fk of (tdef.fks || [])) {
      const ondel = fk.onDelete ? ` ON DELETE ${fk.onDelete}` : '';
      cols.push(`  FOREIGN KEY (${fk.column}) REFERENCES ${fk.refTable}(${fk.refColumn})${ondel}`);
    }
    lines.push(cols.join(',\n'));
    lines.push(`);`);
    const idxCols = (tdef.indexes || []);
    let i = 0;
    for (const col of idxCols) {
      lines.push(`CREATE INDEX IF NOT EXISTS idx_${tname}_${col}_${i++} ON ${tname}(${col});`);
    }
  }
  return lines.join('\n') + '\n';
}

function writeFile(p, content) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content, 'utf8');
  console.log('✔ Wrote', path.relative(root, p));
}

function main() {
  console.log('📄 schema.json:', schemaPath);
  const schema = loadSchema();

  const typesPath = path.join(root, 'packages', 'core', 'src', 'types', 'db.ts');
  writeFile(typesPath, genTypes(schema));

  const sqlPath = path.join(root, 'apps', 'main', 'src', 'db', 'migrations', '001_init.sql');
  writeFile(sqlPath, genSql(schema));
}

main();
