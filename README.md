# DiscoVir

written by Lauren Krausfeldt & Poorani Subramanian – bioinformatics@niaid.nih.gov  
updated by Susheel Bhanu Busi – susbus@ceh.ac.uk (UKCEH)

[Pipeline Training Slides](https://github.com/pooranibcbb/virome-pipeline/releases/download/v0.1/bcbb_viral_metagenomics_2023.pdf)

---

## Description

DiscoVir is a pipeline for exploring viruses (ssDNA, dsDNA phage, and giant DNA viruses)
and viral diversity in metagenomes. It can be run via the cloud application
[Nephele](https://nephele.niaid.nih.gov) (under *Explore*) or on HPC systems.

The pipeline accepts:

- **Metagenomic assembly sequences** (`.fasta`; one per sample)
- **Binary alignment map files** (`.bam`; reads mapped back to assemblies, one per sample)

These files can be produced by workflows such as the
[WGSA2 pipeline in Nephele](https://nephele.niaid.nih.gov/pipeline_details/wgsa/).

The pipeline identifies viral genomes using **geNomad**, annotates viral taxonomy and
function (geNomad, DRAM-v, optionally DIAMOND), estimates gene abundances with **VERSE**,
optionally filters genomes using **CheckV**, clusters viral genomes into vOTUs, and
finally reports vOTU abundances and host taxonomy.

---

## Repository Contents

- `Snakefile` – main pipeline definition
- `final_Snakefile` – final integrated pipeline Snakefile
- `config.yaml` – project-specific configuration (paths, options, samples)
- `cluster_setup.smk` – helper for cluster configuration
- `scripts/` – helper scripts (see `scripts/README.md`)
- `docs/README_for_DiscoVir_outputs.md` – detailed description of outputs
- `scripts/run_pipeline.sh` – convenience wrapper for running on NeoHuxley

---

## Creating the Metadata File

The DiscoVir pipeline expects a **metadata table** describing samples and input file
locations. This table is typically named `metadata.tsv` and includes assembly and read
paths for each sample.

### Required format

```text
Sample_number   Sample      Assembly_Path                                  Read_Path
1               A21_2022    /path/to/A21_2022.fasta                         /path/to/A21_2022_filtered.R1.fq.gz
2               A27_2023    /path/to/A27_2023.fasta                         /path/to/A27_2023_filtered.R1.fq.gz
```

### Generating `metadata.tsv` from a sample list

A helper script (`make_metadata_tsv.py`) can be used to generate this file
automatically from a simple text file containing one sample ID per line.

#### Example command

```bash
python make_metadata_tsv.py \
  --samples 450_samples.txt \
  --assembly-dir /prj/DECODE/EA_DATA/assembly \
  --reads-dir /prj/DECODE/rsn_viruses/mvip/reads \
  --out metadata.tsv
```

This will:

- Number samples sequentially
- Construct assembly paths as `{assembly-dir}/{Sample}.fasta`
- Construct read paths as `{reads-dir}/{Sample}_filtered.R1.fq.gz`

The resulting `metadata.tsv` can then be referenced in `config.yaml`.

---

## Running the Pipeline

### Inputs

- One assembly FASTA per sample
- One BAM file (reads mapped to assembly) per sample
- A `metadata.tsv` file describing samples and input paths

All inputs may be real files or symbolic links.

---

### Running on NeoHuxley (UKCEH)

The recommended way to run DiscoVir on NeoHuxley is via the provided wrapper script.

#### `scripts/run_pipeline.sh`

```bash
#!/bin/bash

conda activate /hdd0/susbus/tools/conda_envs/snakemake

snakemake -s final_Snakefile \
  --configfile config.yaml \
  --use-conda \
  --conda-prefix /prj/DECODE/conda_envs \
  --cores 64 \
  --jobs 8 \
  all -rpn -k
```

#### To run

```bash
cd virome-pipeline
./scripts/run_pipeline.sh
```

---

### Running on Locus (NIAID)

1. Clone the repository:
   ```bash
   git clone https://github.com/niaid/virome-pipeline
   ```

2. Copy and edit:
   - `project_config.yaml`
   - `locus_submit_vp.sh`

3. Submit the job:
   ```bash
   qsub ./locus_submit_vp.sh
   ```

---

## Pipeline Overview

![discovir pipeline diagram](docs/discovir.drawio.svg "DiscoVir Pipeline diagram")

---

## Notes

- Originally tested on NIAID’s Locus HPC
- Easily portable to other HPC systems using Snakemake
- Designed for large-scale viral metagenomic datasets
- Compatible with containerised or conda-based environments
- From *RSN analysis*, sample `D53_2022` removed due to persistent errors
---

## References

1. WGSA2 workflow tutorial – https://www.protocols.io/view/wgsa2-workflow-a-tutorial-n92ldm98xl5b/v1  
2. Camargo et al. (2023) *Nature Biotechnology* – geNomad  
3. Shaffer et al. (2020) *Nucleic Acids Research* – DRAM  
4. Buchfink et al. (2021) *Nature Methods* – DIAMOND  
5. Zhu et al. (2016) *bioRxiv* – VERSE  
6. Nayfach et al. (2021) *Nature Biotechnology* – CheckV  
7. BBTools dedupe – https://jgi.doe.gov/data-and-tools/software-tools/bbtools/  
8. Steinegger & Söding (2017) *Nature Biotechnology* – MMseqs2  
9. Roux et al. (2019) *Nature Biotechnology* – MIUViG  
10. Shumate & Salzberg (2021) *Bioinformatics* – Liftoff
