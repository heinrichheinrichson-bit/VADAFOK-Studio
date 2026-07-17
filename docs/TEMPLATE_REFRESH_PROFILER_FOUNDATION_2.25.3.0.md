# Template RefreshProfiler Foundation — 2.25.3.0

This release adds an optional in-memory profiler below `TemplateRefreshManager`.
It is disabled by default and therefore does not collect data during normal use.

## API

- `manager.set_profiling(True|False)`
- `manager.refresh_profile()`
- `manager.reset_profile()`

The snapshot contains call counts and total, last, maximum and average elapsed
seconds per refresh gateway. Exceptions raised by the existing refresh logic are
never swallowed.

No UI, persistence, rendering order or legacy wrapper is changed in this phase.
