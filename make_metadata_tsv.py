#!/usr/bin/env python3

import argparse
import pandas as pd
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Create metadata.tsv with assembly and read paths"
    )
    parser.add_argument(
        "--samples",
        required=True,
        help="Text file with one sample ID per line"
    )
    parser.add_argument(
        "--assembly-dir",
        required=True,
        help="Directory containing assemblies (e.g. /prj/DECODE/EA_DATA/assembly)"
    )
    parser.add_argument(
        "--reads-dir",
        required=True,
        help="Directory containing reads (e.g. /prj/DECODE/rsn_viruses/mvip/reads)"
    )
    parser.add_argument(
        "--out",
        default="metadata.tsv",
        help="Output metadata file (default: metadata.tsv)"
    )
    args = parser.parse_args()

    # Read sample list
    samples = (
        pd.read_csv(args.samples, header=None, comment="#")
        .iloc[:, 0]
        .astype(str)
        .str.strip()
    )
    samples = samples[samples != ""]

    if samples.empty:
        raise ValueError("No samples found in sample list")

    # Build metadata
    meta = pd.DataFrame({
        "Sample_number": range(1, len(samples) + 1),
        "Sample": samples,
        "Assembly_Path": [
            str(Path(args.assembly_dir) / f"{s}.fasta") for s in samples
        ],
        "Read_Path": [
            str(Path(args.reads_dir) / f"{s}_filtered.R1.fq.gz") for s in samples
        ]
    })

    # Write output
    meta.to_csv(args.out, sep="\t", index=False)

    print(f"[OK] Wrote {args.out}")
    print(f"[OK] Samples: {len(meta)}")

if __name__ == "__main__":
    main()

