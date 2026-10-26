---
name: scientific-visualization
description: Create, audit and revise publication-ready scientific result figures under the scientific-research-project plan/result contract.
---

# Scientific Visualization for Research Results

Use this Skill whenever a formal task creates or revises a scientific figure. It is the project adapter for the installed `scientific-visualization` Skill and preserves the project's five root documents, plan-to-result mapping, source-table lineage and evidence gates.

## Required workflow

1. Read the task's frozen `01_PLAN.md` step, result path, source tables, expected quantities, uncertainty definition and target journal/document type.
2. Choose an honest display: show the relevant observations, denominators, uncertainty, missingness, exclusions and comparison groups. Do not add decorative or unsupported encodings.
3. Use the installed `scientific-visualization` guidance for Matplotlib/Seaborn/Plotly styling. Prefer a reproducible plotting script and vector PDF/SVG output; provide a 300 DPI or higher PNG/TIFF preview when required by the venue.
4. Apply publication checks: final-size typography, units, panel labels, consistent axes, colorblind-safe and grayscale-readable encoding, legible legend, adequate whitespace, no clipping/overlap, and journal dimensions.
5. Record `source_tables`, plotting script, software/environment, input hashes, figure hash, dimensions, DPI/vector status, palette and QC result in the task's `_evidence/` area. The figure must remain in the same canonical task `result_path`.

## Bounded visual self-correction

If visual QC fails, perform a bounded correction loop:

```text
render → inspect against publication checklist → identify visual defect
      → revise plotting script/layout only → render a new attempt
      → re-run data/lineage/QC checks → accept or stop with evidence
```

The loop may change layout, font size, panel arrangement, labels, colors, export format and plotting code. It must not silently change source data, denominators, statistical tests, endpoints, conclusions or the approved scientific scope. Preserve failed previews and QC notes; do not overwrite a formally accepted figure without a new receipt and version.

The evaluator must check the rendered artifact independently of the plotting code. A successful image export is not publication quality. If the figure remains below the target threshold after the bounded attempts, return `revise` or `needs_user` with concrete defects and locators.

## Separation from schematics

Use `scientific-schematics` for conceptual diagrams, mechanisms, architecture and flowcharts. It may use iterative visual review for those diagrams, but it must not invent numeric data or replace the data-figure lineage required here. Use this Skill for plots whose values support a scientific result or conclusion.

## Deliverables

For each formal result figure, deliver:

- the editable/reproducible plotting source;
- a vector master when supported (PDF/SVG/EPS) and the venue-required raster preview;
- a caption stating what the figure measures, units, uncertainty and sample/analysis units;
- a source-table and run/evidence lineage receipt;
- a publication-QC record and, when revised, the previous attempt plus the concrete correction rationale.

Never use a figure's visual polish as evidence of scientific validity. Scientific claims still require the result review, contrary evidence, interpretation and publication gates.
