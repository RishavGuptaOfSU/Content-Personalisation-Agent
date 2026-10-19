#!/usr/bin/env node
/**
 * Static check: every capitalised JSX component used in a file must be imported
 * or declared in that file.
 *
 * Why this exists: a missing import is NOT a build error for the bundler — the
 * reference only throws at runtime, and only when that branch renders. A Stop
 * button that appears solely while a request is in flight can therefore ship
 * broken and crash the whole tree on first use (which is exactly what happened
 * with `<Square />`). Validating that imports resolve is not enough; this checks
 * the reverse direction.
 *
 *   node scripts/check-jsx-refs.mjs
 *
 * Exits non-zero when anything is unresolved, so it can gate a commit or CI.
 */

import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..', 'src')

/** Names that are always available or handled by the JSX runtime. */
const GLOBALS = new Set(['Fragment', 'React', 'StrictMode', 'Suspense', 'Profiler'])

function walk(dir, acc = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full, acc)
    else if (/\.jsx?$/.test(entry.name)) acc.push(full)
  }
  return acc
}

/** Strip comments and string/template literals so matches come from real code. */
function stripNoise(source) {
  return source
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/(^|[^:])\/\/[^\n]*/g, '$1 ')
    .replace(/`(?:\\[\s\S]|[^`\\])*`/g, '``')
    .replace(/'(?:\\.|[^'\\])*'/g, "''")
    .replace(/"(?:\\.|[^"\\])*"/g, '""')
}

function declaredNames(source) {
  const names = new Set(GLOBALS)

  // import Default, { a, b as c }, * as ns from '...'
  for (const match of source.matchAll(/import\s+([\s\S]+?)\s+from\s+['"][^'"]+['"]/g)) {
    const clause = match[1]
    const braced = [...clause.matchAll(/\{([\s\S]*?)\}/g)].map((m) => m[1]).join(',')
    for (const piece of braced.split(',')) {
      const name = piece.trim().split(/\s+as\s+/).pop()
      if (name) names.add(name.trim())
    }
    const outside = clause.replace(/\{[\s\S]*?\}/g, '').replace(/\*\s+as\s+(\w+)/g, (_, n) => {
      names.add(n)
      return ''
    })
    for (const piece of outside.split(',')) {
      const name = piece.trim()
      if (/^\w+$/.test(name)) names.add(name)
    }
  }

  // Local declarations, including destructured ones.
  for (const match of source.matchAll(/(?:const|let|var)\s+([A-Za-z_$][\w$]*)/g)) names.add(match[1])
  for (const match of source.matchAll(/(?:function|class)\s+([A-Za-z_$][\w$]*)/g)) names.add(match[1])
  /** `{ a, b: Alias = fallback }` -> adds `a` and `Alias`. */
  function addDestructured(body) {
    let depth = 0
    let current = ''
    const pieces = []
    for (const ch of body) {
      if ('([{'.includes(ch)) depth++
      else if (')]}'.includes(ch)) depth--
      if (ch === ',' && depth === 0) {
        pieces.push(current)
        current = ''
      } else current += ch
    }
    pieces.push(current)

    for (const piece of pieces) {
      // Take the binding side of `key: binding`, then drop any `= default`.
      const binding = piece.includes(':') ? piece.slice(piece.indexOf(':') + 1) : piece
      const name = binding.split('=')[0].replace(/[.\s]/g, '')
      if (/^[A-Za-z_$][\w$]*$/.test(name)) names.add(name)
    }
  }

  // Destructuring assignments: `const { a, b: C } = x`
  for (const match of source.matchAll(/\{([^{}]*)\}\s*=[^=]/g)) addDestructured(match[1])
  // Destructured function/component parameters, including multi-line ones:
  // `function Foo({ icon: Icon = Inbox, title })` and `({ a, b }) =>`
  for (const match of source.matchAll(/\(\s*\{([\s\S]*?)\}\s*\)/g)) addDestructured(match[1])
  // Plain arrow parameters: `(event) =>`
  for (const match of source.matchAll(/\(([^(){}]*)\)\s*=>/g)) {
    for (const piece of match[1].split(',')) {
      const name = piece.trim().split(/[:=]/)[0].trim()
      if (/^[A-Za-z_$][\w$]*$/.test(name)) names.add(name)
    }
  }
  return names
}

let problems = 0
const files = walk(ROOT)

for (const file of files) {
  const raw = fs.readFileSync(file, 'utf8')
  // Imports/declarations are read from the RAW text: stripNoise() blanks string
  // literals, which would destroy the module specifier and match nothing.
  const declared = declaredNames(raw)
  // Usage is read from the stripped text so commented-out or quoted JSX is not
  // mistaken for real code.
  const source = stripNoise(raw)

  const used = new Set()
  // <Component ...>  and  <Component.Sub ...>
  for (const match of source.matchAll(/<([A-Z][\w$]*)/g)) used.add(match[1])

  for (const name of used) {
    if (!declared.has(name)) {
      console.log(`  MISSING  <${name}>  used in ${path.relative(ROOT, file)} but never imported`)
      problems++
    }
  }
}

console.log(
  problems === 0
    ? `checked ${files.length} files — every JSX component is imported or declared`
    : `${problems} unresolved JSX reference(s)`,
)
process.exit(problems === 0 ? 0 : 1)
