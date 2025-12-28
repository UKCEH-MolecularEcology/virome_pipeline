#!/bin/bash 

conda activate /hdd0/susbus/tools/conda_envs/snakemake

snakemake -s final_Snakefile --configfile config.yaml --use-conda --conda-prefix /prj/DECODE/conda_envs --cores 64 --jobs 8 all -rpn -k

