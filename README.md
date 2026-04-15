# Agentic Data Preparation Framework

A local-first, file-in file-out framework for data cleaning, standardization, linkage, and master-list building. Drop it into any repo, point your AI coding tool at `CLAUDE.md`, and give it messy source files plus a prep goal. The agent inspects local files first, cleans and aligns the data, and saves outputs to `outputs/` — nothing leaves your machine unless you ask it to.

Built for situations where the real work is cleaning data, aligning schemas, deduplicating records, and making multiple sources link cleanly through codes, names, or identifiers.

## Quick start

1. Open the repo in Claude Code (or Cursor / Copilot — see Compatibility below).
2. Drop source files into `data/` organized by project subfolder.
3. Copy files you want to work on into `workspace/working/`.
4. Paste your prep request — clean this, build a master list, map these codes.
5. Review generated files in `workspace/` before approving elevation to `outputs/`.
6. A sanity check report is saved automatically to `outputs/reports/` after every job.

No forms. No setup scripts. Just local files and clear prompts.

## What it produces

| Request | Output |
| --- | --- |
| Clean one source | Cleaned CSV or XLSX in `outputs/cleaned/` |
| Standardize multiple related sources | Aligned files plus mapping tables |
| Build a master list | Canonical CSV or XLSX in `outputs/master-lists/` |
| Review source quality before merge | QA file in `outputs/qa/` |
| Resolve entity matching | Link table, alias table, or unresolved review file |
| Any job | Sanity check report in `outputs/reports/` |

## Capabilities

Full capability list lives in `capabilities/capabilities.csv`.

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
agentic-da/
├── capabilities/
│   └── capabilities.csv         <- supported prep operations (generic, reusable)
├── context/
│   └── instructions/            <- project-specific prep instructions
├── data/                        <- source files, never modified
│   └── {project}/               <- one subfolder per data project
├── workspace/
│   ├── working/                 <- active files being processed
│   └── reference/               <- lookup tables and supporting files
├── outputs/
│   ├── cleaned/                 <- cleaned single-source files
│   ├── master-lists/            <- canonical linked entity lists
│   ├── mappings/                <- code maps, alias maps, link tables
│   ├── qa/                      <- review files, rejects, unresolved matches
│   ├── reports/                 <- sanity check reports, one per job
│   └── xlsx/                    <- spreadsheet exports when needed
├── sources.md                   <- source registry, keys, and join notes
├── standards.md                 <- naming, code, and linkage standards
├── CLAUDE.md                    <- agent instructions
├── preferences.json             <- behaviour toggles
└── README.md
```

## Data flow

```text
data/          →   workspace/working/   →   outputs/
(untouched)        (staging, active)        (reviewed and confirmed only)
```

- Files in `data/` are never modified. Copy them into `workspace/` before processing.
- `workspace/` is the staging layer. All intermediate files live here.
- Files are only moved to `outputs/` after explicit user review and approval.
- Every job produces a report in `outputs/reports/` recording what was reviewed, what changed, what files were written, and which source versions were used.

## Versioning

When a new version of a source file arrives:

- The existing file is renamed with a version suffix: e.g. `LanguageCodes_v1.csv`
- The new file takes the clean name: `LanguageCodes.csv`
- A `_versions.md` log in the same folder records each version with its date and change note
- Output filenames include a date tag and source version: e.g. `language-master_v2_2026-04-15.csv`

## Compatibility

| Tool | Instruction file |
| --- | --- |
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursor/rules/agent-da.mdc` |
| GitHub Copilot | `.github/copilot-instructions.md` |

All three instruction files are kept in sync through the pre-commit hook. One-time setup after cloning:

```bash
git config core.hooksPath .githooks
```
