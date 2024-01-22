How to run Birdman

This readme is based on Hazel Dilmore's [MARS Birdman project](https://github.com/ahdilmore/MARS_Birdman)
1. Install Birdman according to the instructions in the MARS_Birdman repo
2. Clone or download this folder to your barnacle folder
3. Modify your model_single.py file and compile your stan model file
4. Modify your run_birdman_chunked.py file
5. Modify your .sh script
6. Run the .sh script from your birdman conda env on the cluster. This will generate the inferences files in the ouput folder specified in the script. This step, depending on the size of the dataset, can take multiple hours (current time limit is 10 hours). Slurm will send mail notifications when the scripts starts, ends or fails. Additionally, a notification will be sent out if the script reaches 80% of the requested timelimit. For each job, a slurm output will be created in the output folder specified in the script. (To check the progress, my preferred method is calling `tail *` in the folder). Succesful jobs will end with the "Finished Python script!" message.
7. Modify the summarize-inferences.sh script and run it on the birdman inferences files. This will output a .tsv file into the folder specified in the script.
8. Import the .tsv file into the birdman_analysis.ipynb Jupyter notebook
