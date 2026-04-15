# Meet Darcy

Your AI-native data analyst.

Drop in messy source files, tell Darcy what you need, and get clean production-ready CSV and XLSX outputs back on your machine. Darcy inspects local files first, cleans and aligns the data, and saves outputs to `outputs/` — nothing leaves your machine unless you ask.

Built for situations where the real work is cleaning data, aligning schemas, deduplicating records, and making multiple sources link cleanly through codes, names, or identifiers.

## Quick start

1. Open the repo in Claude Code (or Cursor / Copilot — see Compatibility below).
2. Drop source files into `data/` organised by project subfolder.
3. Paste your prep request — clean this, build a master list, map these codes.
4. Darcy copies the relevant files to `workspace/working/` automatically before processing.
5. Review generated files in `workspace/` before approving elevation to `outputs/`.
6. A sanity check report is saved automatically to `outputs/reports/` after every job.

No forms. No setup scripts. Just local files and clear prompts.

## What it produces

| Request | Output |
| --- | --- |
| Clean one source | Cleaned CSV or XLSX → `outputs/cleaned/` |
| Standardize multiple related sources | Aligned files plus mapping tables → `outputs/mappings/` |
| Build a master list | Canonical CSV or XLSX → `outputs/master-lists/` |
| Review source quality before merge | QA file → `outputs/qa/` |
| Resolve entity matching | Link table, alias table, or unresolved review file → `outputs/mappings/` |
| Any job | Sanity check report → `outputs/reports/` |

## Capabilities

Full capability list lives in `capabilities/capabilities.csv`. Need something not listed? Add a new row — Darcy picks it up on the next job, no code required.

| Category | What it covers |
| --- | --- |
| `file_ops` | Load files, batch processing, format standardization, schema alignment, encoding fixes |
| `combine` | Concatenation, joins, unions, cross joins, post-merge deduplication |
| `cleaning` | Duplicates, missing values, whitespace, case, labels, categories, encoding artefacts, diacritics |
| `columns` | Rename, reorder, drop, derive, split, combine, type changes, regex extraction |
| `transform` | Scaling, log transforms, binning, pivoting, feature engineering, unit conversion |
| `datetime` | Parsing, standardization, timezone alignment, resampling, missing intervals |
| `aggregation` | Grouping, rolling metrics, cumulative metrics, ranking, percentiles |
| `filtering` | Sorting, row filtering, top-bottom selection, outlier removal |
| `validation` | Null checks, uniqueness, range checks, data types, referential integrity |
| `text` | Text cleaning, tokenization, fuzzy matching, pattern extraction |
| `viz_prep` | Chart-ready reshaping, label standards, granularity alignment, ranking, percentages |
| `entity_resolution` | Record linkage, canonicalization, alias mapping, provenance, unique ID assignment |
| `governance` | Schema evolution handling and data lineage tracking |
| `output` | Cleaned exports, viz-ready exports, partitioned outputs |
| `pipeline` | Automation, logging, version control, scheduling |

## Folder structure

```text
your-repo/
├── capabilities/
│   └── capabilities.csv         <- supported prep operations (generic, reusable)
├── context/
│   └── instructions/            <- project-specific prep instructions
├── data/                        <- source files, never modified
│   └── {project}/               <- one subfolder per data project
├── workspace/
│   ├── working/                 <- active files being processed
│   └── reference/               <- lookup tables and supporting files
├── outputs/                     <- created by the agent on first job run
│   ├── cleaned/                 <- created when a cleaning job runs
│   ├── master-lists/            <- created when a master list job runs
│   ├── mappings/                <- created when a mapping job runs
│   ├── qa/                      <- created when a QA job runs
│   ├── discarded/               <- records dropped every job (no identifier, failed validation)
│   └── reports/                 <- created on every job (sanity check report)
├── scripts/                     <- processing scripts written by Darcy
├── standards.md                 <- naming, code, and linkage standards
├── CLAUDE.md                    <- agent instructions
├── preferences.json             <- behaviour toggles
└── README.md
```

## Folder guide

| Folder | What goes in it |
| --- | --- |
| `data/` | Original source files, organised by project subfolder. Never modified directly. |
| `workspace/working/` | Intermediate outputs written during processing. Inspectable before anything is elevated to `outputs/`. |
| `workspace/reference/` | Source files copied from `data/` and used as lookups to inform the job — not being cleaned themselves. |
| `context/instructions/` | One Markdown file per project defining prep rules, match logic, and standards for that domain. |
| `capabilities/` | The master list of supported prep operations. Generic and reusable across all projects. |
| `scripts/` | Processing scripts written by Darcy when a job requires code. Controlled by `commitScripts` in preferences. |
| `outputs/` | Confirmed, reviewed files only. Subfolders are created by the agent when a job runs. |
| `outputs/discarded/` | Records dropped during every job — no identifier, failed validation, or unresolvable conflict. Never silently lost. |
| `standards.md` | Cross-project defaults for naming, codes, entity matching, and date formats. |
| `preferences.json` | Behavioural toggles — controls what Darcy confirms, commits, and writes. See Preferences below. |

## Preferences

All behaviour toggles live in `preferences.json`. Darcy reads this file at the start of every session.

| Setting | Default | What it does |
| --- | --- | --- |
| `commitOutputs` | `false` | Allow files in `outputs/` to be committed to git. |
| `commitWorkspace` | `false` | Allow files in `workspace/` to be committed to git. |
| `commitContext` | `false` | Allow files in `context/` to be committed to git. |
| `commitScripts` | `false` | Allow files in `scripts/` to be committed to git. |
| `pushAfterCommit` | `false` | Push to remote automatically after every commit. |
| `confirmBeforeSave` | `true` | Ask before writing any output file. |
| `confirmBeforeCommit` | `true` | Ask before committing. |
| `confirmBeforeGenerate` | `true` | Ask for confirmation when the request is ambiguous. |
| `runEvidenceCheck` | `true` | Inspect `data/`, `workspace/`, and context files before starting any job. |
| `includeSanityCheck` | `true` | Write a sanity check report to `outputs/reports/` after every job. |
| `updateSourceRegistry` | `true` | Offer to update `standards.md` when new source rules appear. |
| `language` | `"en-US"` | Writing language for outputs. Supports `"en-US"` and `"en-GB"`. |

When a `commit*` setting is changed to `true`, Darcy updates `.gitignore` automatically to unignore that folder. `data/` is always ignored regardless of any setting.

## Data flow

```text
data/              →   workspace/reference/    (source lookups, untouched)
                   →   workspace/working/      (intermediate outputs)
                   →   outputs/                (reviewed and confirmed only)
```

- Files in `data/` are never modified. Darcy copies them into `workspace/` automatically.
- Source files used as lookups go to `workspace/reference/`. Files being actively processed go to `workspace/working/`.
- All intermediate outputs are written to `workspace/working/` so the state is inspectable before anything is confirmed.
- Records dropped during processing are always written to `outputs/discarded/` — nothing is silently lost.
- Files are only moved to `outputs/` after explicit user review and approval.
- Output subfolders are created by the agent when a job runs — nothing is pre-built.
- Every job produces a sanity check report in `outputs/reports/`.

## Versioning

When a new version of a source file arrives:

- The existing file is renamed with a version suffix: e.g. `customers_v1.csv`
- The new file takes the clean name: `customers.csv`
- A `_versions.md` log in the same folder records each version with its date and change note
- Output filenames include a date tag and source version: e.g. `customers-master_v2_2026-04-15.csv`

## Compatibility

This framework is built for Claude Code. The instruction file is `CLAUDE.md`.

It can also be adapted for Cursor (`.cursor/rules/`) or GitHub Copilot (`.github/copilot-instructions.md`) by copying the contents of `CLAUDE.md` into the relevant instruction file for that tool.
