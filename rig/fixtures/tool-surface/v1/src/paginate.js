// paginate.js — pagination helpers for a list view.
//
// Part of a frozen measurement-rig fixture (rig/fixtures/tool-surface/v1).
// Do not edit — a fix here is a different fixture and would invalidate any
// runs.jsonl row keyed on fixture_digest. Changes land in a new v2/
// directory instead (sdd/measurement-rig/design.md, Decision 4).

function clampPageSize(size, min = 1, max = 100) {
  if (size < min) return min;
  if (size > max) return max;
  return size;
}

function pageCount(total, pageSize) {
  if (pageSize <= 0) return 0;
  return Math.ceil(total / pageSize);
}

function pageForIndex(index, pageSize) {
  return Math.floor(index / pageSize) + 1;
}

function pageSlice(items, page, pageSize) {
  const start = page * pageSize;
  const end = start + pageSize;
  return items.slice(start, end);
}

module.exports = { clampPageSize, pageCount, pageForIndex, pageSlice };
