# Prep Standards

These are the default standards for cleaning, standardization, linkage, and master-list outputs.

## Naming

- Use one canonical label for each entity, market, status, and category.
- If a source uses multiple labels for the same thing, document the mapping before merging.
- Prefer stable business-friendly names over source-specific abbreviations.

## Codes and identifiers

- Prefer stable codes and IDs over free-text names for linking.
- When multiple IDs exist, document which one is primary and which ones are fallback fields.
- Do not create a new canonical ID without documenting the rule used to assign it.

## Entity matching

- Match on exact IDs first.
- Use secondary identifiers only when the primary key is missing.
- Use entity-name matching only with an explicit rule and a review step for ambiguous matches.
- Record low-confidence matches in a working note before they are accepted into a master list.

## Dates and formats

- Use ISO-style dates where possible.
- Standardize date and timestamp formats before combining sources.
- Call out timezone assumptions whenever date logic spans regions or systems.

## Output rules

- The target output should state its grain clearly.
- Master lists should define one canonical record per entity.
- Keep provenance fields where they help trace the record back to the source.
