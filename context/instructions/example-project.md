# Master List & Record Linkage — Example Project Instructions

Copy this file, rename it for your project, and fill in the details.
Darcy reads it before every job in this domain.

---

## Project

**Name:** Your project name
**Goal:** Build a single canonical master list by linking records across multiple source files and resolving duplicates into one clean entity per row.
**Source files:** List the files in `data/` that feed this project.

---

## Entity definition

Define what one row in the master list represents:

- **Entity:** e.g. customer, supplier, product, location, organisation
- **Grain:** One row per unique entity — duplicates across sources must be resolved, not stacked

---

## Identifiers

Define the identifier hierarchy used to link records across sources:

| Priority | Identifier | Source field | Notes |
| --- | --- | --- | --- |
| 1 | Primary ID | e.g. `account_id`, `EAN`, `company_reg_no` | Always match on this first |
| 2 | Secondary ID | e.g. `email`, `VAT number` | Use only when primary is absent |
| 3 | Name match | Canonical name only | Only valid if at least one identifier also matches |

**Never merge on name alone.** Name matching without an identifier anchor produces false positives.

---

## Canonical name rule

When the same entity appears with different names across sources:

- Select the name with the highest frequency across sources
- If tied, prefer the name from the most structured source
- If still tied, use the shortest normalised form
- Record all other names as alternative names, not separate entities

---

## Normalisation (apply before any comparison)

- Lowercase
- Remove diacritics
- Remove punctuation
- Trim and collapse whitespace
- Normalised forms are used for matching only — never written to output

---

## Conflict resolution

| Situation | Rule |
| --- | --- |
| Same identifier, different names | Pick canonical name per rule above; store others as alternatives |
| Different identifiers, same record | Bridge only if identifiers co-occur in the same source row |
| Ambiguous match, no shared identifier | Keep as separate entities; flag in QA file |
| Missing identifier on one side | Do not merge; write to discarded file with reason |

---

## Output schema

| Field | Required | Notes |
| --- | --- | --- |
| `canonical_name` | Yes | Resolved canonical label |
| `entity_type` | Yes | e.g. `Customer`, `Supplier`, `Product` |
| `primary_id` | Yes | Must be present or row is discarded |
| `secondary_id` | No | Carry forward if available |
| `alternative_names` | No | Semicolon-separated, deduped, excludes canonical |
| `source_references` | Yes | Which source files contributed to this record |

---

## Known source issues

Document data quality problems here so Darcy handles them consistently:

- e.g. Source A uses `N/A` for missing IDs; Source B leaves the field blank
- e.g. One source uses country alpha-2 codes; another uses full country names
- e.g. Company names include legal suffixes (`Ltd`, `Inc`) inconsistently

---

## Blockers

List anything that would prevent a clean master list from being built:

- e.g. No shared identifier between Source A and Source C — link via Source B as a bridge
- e.g. Date fields not yet standardised — must align before merge
