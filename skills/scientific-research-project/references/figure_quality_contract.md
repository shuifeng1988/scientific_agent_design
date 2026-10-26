# Publication-ready figure contract

Formal result figures are evidence-bearing artifacts, not decoration. The figure must answer a stated question from the approved `01_PLAN.md` step and trace to real source tables, runs and inputs in the same canonical `result_path`.

## Required checks

- The plot type is appropriate for the data and does not hide observations, missingness, exclusions, denominators or uncertainty.
- Axes, units, transformations, comparisons, sample/analysis units and statistical annotations are explicit.
- Typography remains legible at final journal size; panels, legends and annotations do not overlap or clip.
- Colors are colorblind-safe and the figure remains interpretable in grayscale or with redundant non-color encodings.
- Multi-panel figures use consistent scales, labels, panel letters, spacing and terminology.
- A plotting script, source-table references, software/environment, input hashes, output hash, dimensions and export format are recorded.
- A vector master is preferred for line art; raster images use an appropriate resolution (normally at least 300 DPI, higher where the venue requires it).

The installed `scientific-visualization` Skill is the default method for numeric result figures. Its guidance covers publication styles, journal dimensions, uncertainty displays, accessible palettes and PDF/EPS/SVG/PNG export. The installed `scientific-schematics` Skill is the optional method for conceptual diagrams and flowcharts; it does not replace data lineage or scientific result review.

## Bounded visual correction

When a figure fails these checks, revise only the plotting source, layout, labels, style or export settings, then render and recheck. Preserve each failed preview and the defect/correction record. The correction loop is bounded by the task's attempt budget and stops with `revise` or `needs_user` when the threshold is not met. It may not change source data, denominators, endpoints, statistical conclusions or approved scope.

The final result review must inspect the actual rendered figure and its source-table lineage. Passing dimensions, hashes or file-format checks alone does not establish publication quality or scientific correctness.
