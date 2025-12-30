#!/usr/bin/env python3

"""
Requires python >= 3.9 and pandas

"""

import argparse
import pandas as pd
import sys
import os.path

parser = argparse.ArgumentParser()
default_column = 'pfam_hits'
parser.add_argument("pipelinedir", help="directory containing pipeline outputs - including sample directories")
parser.add_argument("samplelist", help="file containing list of samples - should be names of sample directories that you want to include in the summary table - one per line")
parser.add_argument("-d", "--dramv", help="which dramv directory do you want to use the annotations from. e.g. dramv or amgs (default: %(default)s)", default="amgs")
parser.add_argument("-r", "--verse", help="which verse directory do you want to use the abundances from.  (default: %(default)s)", default="amgs/abund_amgs")
parser.add_argument("-v", "--value", help="what value from abundance file to fill in the table (default: %(default)s)", choices = ['count', 'cpm', 'rpk'], default = 'count')
parser.add_argument("-s", "--suffix", help="suffix for file with abundances (default: %(default)s)", default = "_amgs.count.gene.cpm.txt")
parser.add_argument("--debug", help="print debug messages", action='store_true')
args = parser.parse_args()

if args.debug: print(args, file=sys.stderr)


def read_abund(abundfile, amgtable, value, sample):
    """abundfile: abundance filename - output of verse
       amgtable: corresponding DRAM-v AMG table from read_amg
       value: which value column from abundfile to include
       sample: sample name associated with file
    """
    # If AMG table is empty, nothing to merge -> return empty table with expected columns
    if amgtable is None or amgtable.empty:
        return pd.DataFrame(columns=list(amgtable.columns) + [value] if amgtable is not None else
                            ['gene', 'gene_id', 'gene_description', 'sample', value])

    # Abundance file missing/empty -> return empty
    if (not os.path.exists(abundfile)) or (os.path.getsize(abundfile) == 0):
        print(f"[WARN] {sample}: missing/empty abundance file: {abundfile}; returning empty table.", file=sys.stderr)
        return pd.DataFrame(columns=list(amgtable.columns) + [value])

    a = pd.read_csv(abundfile, sep='\t')

    # Ensure required merge and value columns exist
    if 'gene' not in a.columns:
        print(f"[WARN] {sample}: abundance file has no 'gene' column: {abundfile}; returning empty table.", file=sys.stderr)
        return pd.DataFrame(columns=list(amgtable.columns) + [value])

    if value not in a.columns:
        print(f"[WARN] {sample}: abundance file missing value column '{value}': {abundfile}; returning empty table.", file=sys.stderr)
        return pd.DataFrame(columns=list(amgtable.columns) + [value])

    # Inner merge keeps only genes that are AMGs for that sample
    out = a.merge(amgtable, how='inner', on='gene')

    if out.empty:
        return pd.DataFrame(columns=list(amgtable.columns) + [value])

    out = out[list(amgtable.columns) + [value]]
    return out


def read_amg(amgfile, sample):
    cols = ['gene', 'gene_id', 'gene_description']

    # Missing/empty file -> return empty with expected schema
    if (not os.path.exists(amgfile)) or (os.path.getsize(amgfile) == 0):
        print(f"[WARN] {sample}: missing/empty AMG file: {amgfile}; returning empty table.", file=sys.stderr)
        return pd.DataFrame(columns=cols + ['sample'])

    a = pd.read_csv(amgfile, sep='\t')

    # Missing required columns -> return empty with expected schema
    missing = [c for c in cols if c not in a.columns]
    if missing:
        print(f"[WARN] {sample}: missing columns {missing} in {amgfile}; returning empty table.", file=sys.stderr)
        return pd.DataFrame(columns=cols + ['sample'])

    a = a[cols].copy()
    a['sample'] = sample
    return a


# ---- read in samples (ignore blanks) ----
with open(args.samplelist, 'r') as f:
    samples = [s.strip() for s in f if s.strip()]

# ---- make lists of sample abundance files and amg summary files ----
abundlist = {sample: os.path.join(args.pipelinedir, sample, args.verse, sample + args.suffix) for sample in samples}
amglist   = {sample: os.path.join(args.pipelinedir, sample, args.dramv, "dramv-distill", "amg_summary.tsv") for sample in samples}

# ---- read in AMG and abundance files ----
amgtabs = {sample: read_amg(amglist[sample], sample) for sample in samples}
abundtabs = [read_abund(abundlist[sample], amgtabs[sample], args.value, sample) for sample in samples]

# ---- concatenate abundance tables ----
# If everything is empty, create a correctly-shaped empty long table
if len(abundtabs) == 0 or all(df.empty for df in abundtabs):
    longtab = pd.DataFrame(columns=['gene_id', 'gene_description', 'sample', args.value])
else:
    longtab = pd.concat(abundtabs, ignore_index=True)

# ---- pivot to wide ----
finaltab = pd.pivot_table(
    longtab,
    values=args.value,
    index=['gene_id', 'gene_description'],
    columns='sample',
    fill_value=0,
    aggfunc='sum'
)

finaltab.to_csv(sys.stdout, sep="\t")

