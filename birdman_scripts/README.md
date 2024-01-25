## How to run Birdman

This readme is based on Hazel Dilmore's [MARS Birdman project](https://github.com/ahdilmore/MARS_Birdman)

Steps:
1. Install Birdman according to the instructions in the MARS_Birdman repo, in a new conda env
2. Clone or download this folder to your folder on barnacle
3. Compile your stan model: in your birdman environment run the following in Python
  `import cmdstanpy`
  `cmdstanpy.CmdStanModel(stan_file="[your_path/to/model.stan]")`
5. Change the filepaths and model name in your `model_single.py` file. Use the unrarefied feature table as an input: download the .qza file, change the extension to .zip, and move the `feature_table.biom` file back to barnacle.
6. Chage model name in your `run_birdman_chunked.py` file
7. Modify your `.sh` script: replace slurm email, change input and output paths. Create output folder for the slurm output
8. Run the .sh script from your birdman conda env on the cluster, using `sbatch [name_of_your_.sh_script]`. This will generate the inferences files in the ouput folder specified in the script. This step, depending on the size of the dataset, can take several hours (current time limit is 10 hours). Slurm will send mail notifications when the scripts starts, ends or fails. Additionally, a notification will be sent out if the script reaches 80% of the requested time limit. For each job, a slurm output will be created in the output folder specified in the script. (To check the progress on all jobs, my preferred method is calling `tail *` in the folder). Succesful jobs will end with the "Finished Python script!" message. (Reminder: you can check your running jobs on the cluster by calling `squeue -u [your_username]`)
9. Modify the `summarize-inferences.sh` script, create a folder for the result and run the script with `sbatch` on the birdman inferences files. This will output a .tsv file into the folder specified in the script.
10. Import the .tsv file into the `birdman_analysis.ipynb` Jupyter notebook. Change your filepath, dataset name and add path to your taxonomy file (coming from the sklearn classification) if needed. Taxonomy can be skipped, if your input biom table already has the information. Run the notebook

It can be a good idea to collapse your data on the genus level before running birdman. For this, use the [collapse()](https://docs.qiime2.org/2023.9/plugins/available/taxa/collapse/) qiime2 command. Genus corresponds to taxonomic level 6.

# To get your taxonomy.tsv file:

Download the output of `taxonomy.classification.save` (line 171 in the `metaanalysis_with_greengenes.py` script), change the extension to `.zip`, extract it and find the taxonomy.tsv file in the `data` folder

# To collapse your data:

`import qiime2`

`from qiime2.plugins.taxa.methods import collapse` 

`table = qiime2.Artifact.load("[path to your unrarefied feature table]")` 

`taxonomy = qiime2.Artifact.import_data("FeatureData[Taxonomy]", "[path to your taxonomy.tsv file]")` 

`collapsed_table = collapse(table, taxonomy, 6)` 

`collapsed_table.collapsed_table.save("[output path]")`
