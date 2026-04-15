#!/usr/bin/env python3
"""
Darcy — World Language Master List Builder
===========================================
Builds a canonical registry of languages, dialects, and alternative names
from Ethnologue, Glottolog, and ROLV sources.

Matching hierarchy (strict order):
  1. ISO 639-3 identifier match
  2. Glottolog code match
  3. ROLV code match
  4. Identifier bridging (identifiers co-occurring in the same source record)

Run from repo root:
    python scripts/build_language_master.py
"""

import csv
import os
import re
import shutil
import unicodedata
from collections import defaultdict
from datetime import date

# ── PATHS ──────────────────────────────────────────────────────────────────────

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA      = os.path.join(ROOT, "data")
REFERENCE = os.path.join(ROOT, "workspace", "reference")
WORKING   = os.path.join(ROOT, "workspace", "working")
OUT_DIR   = os.path.join(ROOT, "outputs", "master-lists")
DISC_DIR  = os.path.join(ROOT, "outputs", "discarded")
RPT_DIR  = os.path.join(ROOT, "outputs", "reports")
TODAY    = date.today().isoformat()

SOURCES = {
    "ethnologue_codes": "Ethnologue_LanguageCodes.csv",
    "ethnologue_index": "Ethnologue_LanguageIndex.csv",
    "glottolog":        "Glottolog_languages_and_dialects_geo.csv",
    "rolv_dialects":    "ROLV_dialects.csv",
    "rolv_altnames":    "ROLV_alternatenameindex.csv",
}

OUTPUT_FIELDS = [
    "canonical_name",
    "entity_type",
    "iso_639_code",
    "glottolog_code",
    "rolv_code",
    "parent_language",
    "alternative_names",
    "source_references",
]

# ── NORMALISATION ──────────────────────────────────────────────────────────────

def normalize(text):
    """Lowercase, strip diacritics, remove punctuation, collapse whitespace.
    Used only for matching — never written to output."""
    if not text:
        return ""
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def canonical_name_from_names(names):
    """Pick canonical name: highest frequency across sources, then shortest normalized form."""
    if not names:
        return ""
    freq = defaultdict(int)
    for n in names:
        if n.strip():
            freq[n.strip()] += 1
    if not freq:
        return ""
    max_freq = max(freq.values())
    candidates = [n for n, c in freq.items() if c == max_freq]
    return min(candidates, key=lambda x: len(normalize(x)))

# ── I/O HELPERS ────────────────────────────────────────────────────────────────

def read_csv(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

# ── STEP 1: Copy sources to workspace ──────────────────────────────────────────

def copy_sources():
    os.makedirs(REFERENCE, exist_ok=True)
    missing = []
    for key, filename in SOURCES.items():
        src = os.path.join(DATA, filename)
        dst = os.path.join(REFERENCE, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  Copied  {filename} → workspace/reference/")
        else:
            missing.append(filename)
            print(f"  MISSING {filename} — will skip")
    return missing

# ── STEP 2: Load sources ───────────────────────────────────────────────────────

def load_sources():
    loaded = {}
    for key, filename in SOURCES.items():
        path = os.path.join(REFERENCE, filename)
        if os.path.exists(path):
            loaded[key] = read_csv(path)
            print(f"  Loaded  {filename}: {len(loaded[key]):,} rows")
        else:
            loaded[key] = []
    return loaded

# ── STEP 3: Build entity registry ─────────────────────────────────────────────

def build_registry(sources):
    """
    Central registry keyed by a stable internal key.
    Each record holds all identifiers, names, type, parent, and source refs.
    """

    entities = {}          # key -> record dict
    glotto_to_key = {}     # glottocode -> entity key (for bridging)

    def _new_record(iso="", glottocode="", rolv_code="", entity_type="Language", parent_iso=""):
        return {
            "iso":         iso,
            "glottocode":  glottocode,
            "rolv_code":   rolv_code,
            "names":       [],
            "entity_type": entity_type,
            "parent_iso":  parent_iso,
            "source_refs": set(),
        }

    def get_or_create_by_iso(iso):
        if iso not in entities:
            entities[iso] = _new_record(iso=iso)
        return entities[iso]

    # ── Ethnologue_LanguageCodes: canonical language records ──────────────────
    print("  Ethnologue_LanguageCodes ...")
    for row in sources.get("ethnologue_codes", []):
        iso  = row.get("LangID", "").strip()
        name = row.get("Name",   "").strip()
        if not iso or not name:
            continue
        rec = get_or_create_by_iso(iso)
        rec["names"].append(name)
        rec["entity_type"] = "Language"
        rec["source_refs"].add("Ethnologue_LanguageCodes")

    # ── Ethnologue_LanguageIndex: alternate names and dialects ────────────────
    print("  Ethnologue_LanguageIndex ...")
    for row in sources.get("ethnologue_index", []):
        iso       = row.get("LangID",   "").strip()
        name_type = row.get("NameType", "").strip().upper()
        name      = row.get("Name",     "").strip()
        if not iso or not name:
            continue

        if name_type in ("L", "A", "LA", "P", "LP"):
            # Language name or alternate name — attach to parent ISO record
            rec = get_or_create_by_iso(iso)
            rec["names"].append(name)
            rec["source_refs"].add("Ethnologue_LanguageIndex")

        elif name_type == "D":
            # Dialect — separate entity, parent is the ISO language
            dial_key = f"eth_dial_{iso}_{normalize(name)}"
            if dial_key not in entities:
                entities[dial_key] = _new_record(entity_type="Dialect", parent_iso=iso)
            entities[dial_key]["names"].append(name)
            entities[dial_key]["source_refs"].add("Ethnologue_LanguageIndex")

    # ── Glottolog: languages and dialects with glottocodes ────────────────────
    print("  Glottolog ...")
    for row in sources.get("glottolog", []):
        glottocode = row.get("glottocode", "").strip()
        name       = row.get("name",       "").strip()
        isocodes   = row.get("isocodes",   "").strip()
        level      = row.get("level",      "").strip().lower()
        if not glottocode or not name:
            continue
        if level not in ("language", "dialect"):
            continue

        # Only use isocodes if it looks like a valid ISO 639-3 (3 lowercase letters)
        iso = isocodes if re.match(r"^[a-z]{3}$", isocodes) else ""

        if iso:
            # Bridge to existing ISO record
            rec = get_or_create_by_iso(iso)
            if not rec["glottocode"]:
                rec["glottocode"] = glottocode
            rec["names"].append(name)
            rec["source_refs"].add("Glottolog")
            if level == "dialect" and rec["entity_type"] == "Language":
                pass  # keep as Language; Glottolog dialect classification alone doesn't override
            glotto_to_key[glottocode] = iso
        else:
            # No ISO — use glottocode as the primary key
            g_key = f"glotto_{glottocode}"
            if g_key not in entities:
                entities[g_key] = _new_record(
                    glottocode=glottocode,
                    entity_type="Language" if level == "language" else "Dialect",
                )
            else:
                if not entities[g_key]["glottocode"]:
                    entities[g_key]["glottocode"] = glottocode
            entities[g_key]["names"].append(name)
            entities[g_key]["source_refs"].add("Glottolog")
            glotto_to_key[glottocode] = g_key

    # ── ROLV_dialects: dialect records with ROLV codes ────────────────────────
    print("  ROLV_dialects ...")
    for row in sources.get("rolv_dialects", []):
        rolv_code    = row.get("dialect_code",  "").strip()
        iso          = row.get("language_code", "").strip()
        dialect_name = row.get("dialect_name",  "").strip()
        lang_name    = row.get("language_name", "").strip()
        if not rolv_code or not dialect_name:
            continue

        # Enrich parent language record
        if iso:
            parent_rec = get_or_create_by_iso(iso)
            if lang_name:
                parent_rec["names"].append(lang_name)
            parent_rec["source_refs"].add("ROLV_dialects")

        rolv_key = f"rolv_{rolv_code}"
        if rolv_key not in entities:
            entities[rolv_key] = _new_record(
                rolv_code=rolv_code,
                entity_type="Dialect",
                parent_iso=iso,
            )
        else:
            if not entities[rolv_key]["rolv_code"]:
                entities[rolv_key]["rolv_code"] = rolv_code
            if iso and not entities[rolv_key]["parent_iso"]:
                entities[rolv_key]["parent_iso"] = iso
        entities[rolv_key]["names"].append(dialect_name)
        entities[rolv_key]["source_refs"].add("ROLV_dialects")

    # ── ROLV_alternatenameindex: variant names for ROLV dialects ─────────────
    print("  ROLV_alternatenameindex ...")
    for row in sources.get("rolv_altnames", []):
        rolv_code = row.get("dialect_code", "").strip()
        variant   = row.get("variant_name", "").strip()
        if not rolv_code or not variant:
            continue
        rolv_key = f"rolv_{rolv_code}"
        if rolv_key in entities:
            entities[rolv_key]["names"].append(variant)
            entities[rolv_key]["source_refs"].add("ROLV_alternatenameindex")

    print(f"  Registry size: {len(entities):,} entities")
    return entities

# ── STEP 4: Build output rows ──────────────────────────────────────────────────

def build_output_rows(entities):
    rows = []
    discarded_rows = []

    for key, rec in entities.items():
        iso        = rec["iso"]
        glottocode = rec["glottocode"]
        rolv_code  = rec["rolv_code"]
        names      = [n.strip() for n in rec["names"] if n.strip()]

        parent_iso = rec["parent_iso"]

        # Hard constraint: at least one identifier required.
        # For dialects, a known parent_iso counts as an identifier link.
        has_identifier = bool(iso or glottocode or rolv_code or
                              (rec["entity_type"] == "Dialect" and parent_iso))
        if not has_identifier or not names:
            discarded_rows.append({
                "internal_key":    key,
                "names":           "; ".join(names),
                "entity_type":     rec["entity_type"],
                "reason":          "no identifier" if not has_identifier else "no names",
                "source_references": "; ".join(sorted(rec["source_refs"])),
            })
            continue

        canonical = canonical_name_from_names(names)
        alt_names = sorted(set(n for n in names if n != canonical))

        rows.append({
            "canonical_name":    canonical,
            "entity_type":       rec["entity_type"],
            "iso_639_code":      iso,
            "glottolog_code":    glottocode,
            "rolv_code":         rolv_code,
            "parent_language":   rec["parent_iso"],
            "alternative_names": "; ".join(alt_names),
            "source_references": "; ".join(sorted(rec["source_refs"])),
        })

    rows.sort(key=lambda r: normalize(r["canonical_name"]))

    # Write intermediate files to workspace/working/
    os.makedirs(WORKING, exist_ok=True)

    raw_path = os.path.join(WORKING, f"language-registry-raw_{TODAY}.csv")
    write_csv(raw_path, rows, OUTPUT_FIELDS)
    print(f"  Raw registry → workspace/working/language-registry-raw_{TODAY}.csv")

    os.makedirs(DISC_DIR, exist_ok=True)
    disc_path = os.path.join(DISC_DIR, f"language-discarded_{TODAY}.csv")
    write_csv(disc_path, discarded_rows,
              ["internal_key", "names", "entity_type", "reason", "source_references"])
    print(f"  Discarded    → outputs/discarded/language-discarded_{TODAY}.csv")

    print(f"  Output rows  : {len(rows):,}")
    print(f"  Discarded    : {len(discarded_rows):,}  (no identifier or no names)")
    return rows, discarded_rows

# ── STEP 5: Write master list ──────────────────────────────────────────────────

def write_master(rows):
    out_path = os.path.join(OUT_DIR, f"language-master_{TODAY}.csv")
    write_csv(out_path, rows, OUTPUT_FIELDS)
    print(f"  Saved: {out_path}")
    return out_path

# ── STEP 6: Write sanity check report ─────────────────────────────────────────

def write_report(rows, discarded_rows, out_path, sources, missing_sources):
    os.makedirs(RPT_DIR, exist_ok=True)
    rpt_path = os.path.join(RPT_DIR, f"language-master-report_{TODAY}.md")

    languages = sum(1 for r in rows if r["entity_type"] == "Language")
    dialects  = sum(1 for r in rows if r["entity_type"] == "Dialect")
    with_iso   = sum(1 for r in rows if r["iso_639_code"])
    with_glotto = sum(1 for r in rows if r["glottolog_code"])
    with_rolv  = sum(1 for r in rows if r["rolv_code"])
    with_alts  = sum(1 for r in rows if r["alternative_names"])

    with open(rpt_path, "w", encoding="utf-8") as f:
        f.write(f"# Language Master List — Sanity Check Report\n\n")
        f.write(f"**Date:** {TODAY}\n\n")

        f.write(f"## Sources reviewed\n\n")
        for key, filename in SOURCES.items():
            count = len(sources.get(key, []))
            status = "MISSING — excluded" if filename in missing_sources else f"{count:,} rows"
            f.write(f"- `{filename}` — {status}\n")

        f.write(f"\n## Output files written\n\n")
        f.write(f"- `{out_path}` — master list\n")
        f.write(f"- `workspace/working/language-registry-raw_{TODAY}.csv` — raw registry before elevation\n")
        f.write(f"- `outputs/discarded/language-discarded_{TODAY}.csv` — {len(discarded_rows):,} records dropped (no identifier)\n")
        f.write(f"- `{rpt_path}` — this report\n")

        f.write(f"\n## Record counts\n\n")
        f.write(f"- Total records: {len(rows):,}\n")
        f.write(f"- Languages: {languages:,}\n")
        f.write(f"- Dialects: {dialects:,}\n")
        f.write(f"- Records with ISO 639-3 code: {with_iso:,}\n")
        f.write(f"- Records with Glottolog code: {with_glotto:,}\n")
        f.write(f"- Records with ROLV code: {with_rolv:,}\n")
        f.write(f"- Records with alternative names: {with_alts:,}\n")
        f.write(f"- Discarded (no identifier or no names): {len(discarded_rows):,}\n")

        f.write(f"\n## Join keys used\n\n")
        f.write(f"- Primary: ISO 639-3 (`LangID` / `isocodes` / `language_code`)\n")
        f.write(f"- Secondary: Glottolog code\n")
        f.write(f"- Tertiary: ROLV dialect code\n")

        f.write(f"\n## Blockers\n\n")
        if missing_sources:
            for f_name in missing_sources:
                f.write(f"- `{f_name}` not found in `data/` — excluded from this run\n")
        else:
            f.write(f"- None\n")

        f.write(f"\n## Source versions\n\n")
        f.write(f"- All sources taken from `data/` as-is on {TODAY}\n")

    print(f"  Saved: {rpt_path}")
    return rpt_path

# ── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n=== Darcy — World Language Master List ===\n")

    print("Step 1: Copying sources to workspace/working/ ...")
    missing = copy_sources()

    print("\nStep 2: Loading sources ...")
    sources = load_sources()

    print("\nStep 3: Building entity registry ...")
    entities = build_registry(sources)

    print("\nStep 4: Building output rows ...")
    rows, discarded_rows = build_output_rows(entities)

    print("\nStep 5: Writing master list ...")
    out_path = write_master(rows)

    print("\nStep 6: Writing sanity check report ...")
    write_report(rows, discarded_rows, out_path, sources, missing)

    print("\n=== Done ===\n")
