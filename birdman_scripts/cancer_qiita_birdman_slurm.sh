#!/bin/bash
#Replace this with your working directory
#SBATCH --chdir=/panfs/btakacs/cancer_qiita/birdman

#Replace this with a directory path where the slurm outputs will go. This directory needs to be created before running birdman!
#This will create a slurm output file for each chunk
#SBATCH --output=/panfs/btakacs/cancer_qiita/birdman/zebra_gibs_species/%x.%a.out

#SBATCH --partition=short

#Replace this with your own email
#SBATCH --mail-user="btakacs@health.ucsd.edu"

#SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_{50,80,90}
#SBATCH --mem=64G
#SBATCH --nodes=1
#SBATCH --partition=short
#SBATCH --cpus-per-task=4
#SBATCH --time=10:00:00
#SBATCH --array=1-40

#Replace this with a name for your job (this can be anything)
#SBATCH --job-name=birdman-2-species

pwd; hostname; date

set -e

echo Chunk $SLURM_ARRAY_TASK_ID / $SLURM_ARRAY_TASK_MAX

#Replace this with name for the run (this can be anything)
TABLEID="cancer_qiita_metaanalysis_birdman-2-gibs-species"
#Replace this with your feature table file. It needs to be in .biom format (download the .qza file, change the extension to .zip and unzip it)
TABLE="/projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/11_29_feature_table_filtered.biom"
# Replace these with your filepaths. If the directories don't exist, they will be created
SLURMS="/panfs/btakacs/cancer_qiita/birdman/slurm_out_birdman-2-gibs-species/"$TABLEID
OUTDIR="/panfs/btakacs/cancer_qiita/birdman/inferences_birdman-2-gibs-species/"$TABLEID
LOGDIR="/panfs/btakacs/cancer_qiita/birdman/logs_birdman-2-gibs-species/"$TABLEID
mkdir -p $SLURMS
mkdir -p $OUTDIR
mkdir -p $LOGDIR

echo Starting Python script...
# REPLACE WITH YOUR SCRIPT PATH 
time python /panfs/btakacs/cancer_qiita/birdman/birdman_2_scripts/birdman/src/gibs_run_birdman_chunked.py \
    --table $TABLE \
    --inference-dir $OUTDIR \
    --num-chunks $SLURM_ARRAY_TASK_MAX \
    --chunk-num $SLURM_ARRAY_TASK_ID \
    --logfile "${LOGDIR}/chunk_${SLURM_ARRAY_TASK_ID}.log" && echo Finished Python script!

