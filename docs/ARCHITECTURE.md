# Architecture

## v2.7.3 Equal Spacing

Equal Spacing differs from basic Distribute:

- Basic Distribute equalizes X/Y positions.
- Equal Spacing equalizes the visible gap between object edges.

Horizontal:
- left boundary = min(x)
- right boundary = max(x + width)
- gap = (right - left - sum(widths)) / (n - 1)

Vertical:
- top boundary = min(y)
- bottom boundary = max(y + height)
- gap = (bottom - top - sum(heights)) / (n - 1)
