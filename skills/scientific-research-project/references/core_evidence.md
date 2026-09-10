# Identify the evidence on which the research actually depends

Read with research_depth.md when appraising, drafting/revising a design, or interpreting a principal result. Distinguish methodological inspiration from scientific evidence. An external Skill, an Agent's synthesis, a repository's popularity, a successful command or a checksum does not establish a scientific claim.

## Three separate provenance chains

1. **Prior scientific evidence:** primary studies, measurements, experiments or domain-appropriate theoretical proofs behind the rationale. Identify DOI/accession/version, methods and exact figure/table/section, observation and independent units, controls, uncertainty, limitations and actual access depth. A review helps discovery; trace decision-critical claims to their underlying evidence when accessible. Label abstract-only or inaccessible evidence, rather than implying a full-text review.
2. **This project's decisive evidence:** the actual data or formal derivation needed to distinguish the focal hypothesis from alternatives. Before execution label it planned/unverified; afterwards link the verified source/version → input/selection → task/run/method → output table rows/figure → estimate/uncertainty → bounded conclusion. In a reanalysis, public data remain externally collected, even though our analysis is new. Simulations establish properties under specified assumptions, not an observed biological effect. In a review, the extracted primary-study evidence is the empirical basis; do not invent new experiments.
3. **Corroboration and challenge:** independent validation, orthogonal measurements, negative controls and contradictory evidence. Record independence at the participant/animal/cohort/study level. Two publications or modalities using the same samples are not automatically independent. Do not promote supportive associations into causal or functional proof.

## Put the decisive chain where the reader can see it

00_PROJECT.md must include a short, explicit answer to “Where does the central evidence come from?” followed by a claim-to-evidence table. Keep essential rows in 00, details in 01/03 and existing provenance; a link alone is insufficient.

| Claim/Q | Evidence role | Primary source/data ID and version | Measurement and independent unit | Decisive comparison/control | Task → planned/actual output locator | Availability/QC | Can establish / cannot establish |
|---|---|---|---|---|---|---|---|

Adapt rows to the discipline, but distinguish background, discovery, validation and contrary evidence explicitly. For each central claim specify what observation would weaken it, which assumption is indispensable, and what happens if the strongest dataset or control is unavailable. Core means decisive for the inference, not the biggest dataset, newest paper or most prestigious journal.

Every relevant 01_PLAN task names the rows it generates or tests, why the measurement answers the question, and the evidence it does NOT provide. Results READMEs/Word reports preserve the same linkage with actual denominators, excluded/failed units, uncertainty and result locators. Mark external findings, project observations and Agent inference separately. An input hash establishes integrity, not scientific validity; technical preparation is not decisive research evidence.

Before design approval or scientific release, review whether the central conclusion could survive removal of its key evidence, whether corroboration is genuinely independent, and whether required measurements are present. If not, narrow the claim or propose additional evidence for discussion; do not fabricate availability, silently switch endpoints or relabel an untested mechanism as established. This is an Agent/reviewer obligation, not an implemented semantic guarantee from the CLI.
