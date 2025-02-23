#!/home/btakacs/miniconda3/envs/birdman/bin/python
#Type "which python" in your terminal and replace the above line with the output!

#Replace this with a directory path where the slurm outputs will go
#SBATCH --output=/panfs/btakacs/cancer_qiita/birdman/slurm_out_birdman-2-gibs-genus/%x.out
#SBATCH --partition=short
#SBATCH --mem=8G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --time=10:00:00

#Replace this with your own email
#SBATCH --mail-user="btakacs@health.ucsd.edu"
#SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_{80}

import glob
import re
import os

import arviz as az
import pandas as pd

# REPLACE WITH YOUR INFERENCES FILEPATH
for inference_dir in glob.glob('/panfs/btakacs/cancer_qiita/birdman/inferences_birdman-2-genus/*'):

    FEAT_REGEX = re.compile("F\d{4}_(.*).nc")
    omic_ = inference_dir.split('/')[-1]
    #Replace this with a filepath to your results folder. If the folder does not exists, it will be created
    output_folder = ""

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    outfile = output_folder + "/%s.beta_var.tsv" % (omic_)
    all_inf_files = glob.glob(f"{inference_dir}/*.nc")

    def process_dataframe(df, feat_id, suffix=""):
        df = df.copy()
        df.reset_index(inplace=True, drop=True)
        df.columns.name = ""
        df.index = [feat_id]
        df.columns = [x + suffix for x in df.columns]
        return df

    def reformat_multiindex(df, feat_id, suffix=""):
        df = df.copy().reset_index()
        new_df = pd.DataFrame(columns=df.covariate.unique(), index=[feat_id])
        for c in new_df.columns: 
            lower = df.loc[(df['covariate'] == c) & (df['hdi'] == 'lower')]['beta_var'].values[0]
            higher = df.loc[(df['covariate'] == c) & (df['hdi'] == 'higher')]['beta_var'].values[0]
            new_df[c][feat_id] = (lower, higher)
        new_df.columns = [c + suffix for c in new_df.columns]
        return new_df
    
    feat_diff_df_list = []
    for inf_file in all_inf_files:
        try:
            this_feat_id = FEAT_REGEX.search(inf_file).groups()[0]
        except:
            continue        
        this_feat_diff = az.from_netcdf(inf_file).posterior["beta_var"]
        this_feat_diff_mean = this_feat_diff.mean(["chain", "draw"]).to_dataframe().T
        this_feat_diff_std = this_feat_diff.std(["chain", "draw"]).to_dataframe().T
        this_feat_diff_hdi = az.hdi(this_feat_diff).to_dataframe()

        this_feat_diff_mean = process_dataframe(
            this_feat_diff_mean,
            this_feat_id,
            suffix="_mean"
        )
        this_feat_diff_std = process_dataframe(
            this_feat_diff_std,
            this_feat_id,
            suffix="_std"
        )
        this_feat_diff_hdis = reformat_multiindex(
            this_feat_diff_hdi,
            this_feat_id, 
            suffix='_hdi'
        )
        this_feat_diff_df = pd.concat(
            [this_feat_diff_mean, this_feat_diff_std, this_feat_diff_hdis],
            axis=1
        )
        feat_diff_df_list.append(this_feat_diff_df)

    all_feat_diffs_df = pd.concat(feat_diff_df_list, axis=0)
    all_feat_diffs_df.index.name = "Feature"
    all_feat_diffs_df.to_csv(outfile, sep="\t", index=True)

