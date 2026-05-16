# Performance Checklist

Cross-skill reference for `@perf` and any agent that ships code paths
users will wait on.

## Bundle size

- Per-route initial JS budget: agree a number in `PLAN.md`. Default ≤ **170 KB
  gzipped** for web app routes.
- Track top 10 largest modules per chunk. Flag any single module > **40 KB
  gzipped** unless explicitly justified.
- No duplicate copies of the same library across chunks.
- Tree-shaking actually working: prove it with a bundle-analyzer screenshot
  or `--analyze` report, not by assumption.

## Render performance

- Target 60 fps interactions. Long tasks > **50 ms** are findings.
- Lists with > 100 items use virtualization.
- Avoid unbounded re-renders: memoize stable callbacks/objects passed to
  children; verify with a profiler trace, not by reading code.
- Images use `width`/`height` (or `aspect-ratio`) to prevent CLS.

## Database / network

- Every query has an explain plan reviewed if it hits a table > 10k rows.
- N+1 queries are CRITICAL findings. Use dataloader / batch / join.
- Indexes match the actual `WHERE` / `ORDER BY` shape.
- HTTP requests are batched where the API supports it; pagination is used
  instead of unbounded scans.
- Cache-Control / ETag set on stable responses; no `no-store` by default.

## Build performance

- Cold build time tracked over time; > **20%** regression in a sprint is a
  finding.
- Incremental builds use a persistent cache (turbo, nx, gradle, …).

## Reporting

Always include the measurement (number + unit + tool) and the budget it
exceeds. "Feels slow" is never a finding.
