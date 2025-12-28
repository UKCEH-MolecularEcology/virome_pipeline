#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# User-configurable paths
# -----------------------------
SAMPLES="450_samples.txt"
ASSEMBLY_DIR="/prj/DECODE/EA_DATA/assembly"
READS_DIR="/prj/DECODE/rsn_viruses/mvip/reads"
OUT="metadata.tsv"

# -----------------------------
# Sanity checks
# -----------------------------
[[ -f "$SAMPLES" ]] || { echo "ERROR: Sample list not found: $SAMPLES" >&2; exit 1; }
[[ -d "$ASSEMBLY_DIR" ]] || { echo "ERROR: Assembly dir not found: $ASSEMBLY_DIR" >&2; exit 1; }
[[ -d "$READS_DIR" ]] || { echo "ERROR: Reads dir not found: $READS_DIR" >&2; exit 1; }
[[ -f "make_metadata_tsv.py" ]] || { echo "ERROR: make_metadata_tsv.py not found in current directory" >&2; exit 1; }

# -----------------------------
# Run metadata generation
# -----------------------------
python make_metadata_tsv.py \
  --samples "$SAMPLES" \
  --assembly-dir "$ASSEMBLY_DIR" \
  --reads-dir "$READS_DIR" \
  --out "$OUT"

# -----------------------------
# Post-run checks
# -----------------------------
echo
echo "Metadata preview:"
head "$OUT"

echo
echo "Checking for missing assembly files:"
awk 'NR>1 && !system("test -f "$3)' "$OUT" || true

echo
echo "Checking for missing read files:"
awk 'NR>1 && !system("test -f "$4)' "$OUT" || true

echo
echo "[OK] Metadata generation complete."

