import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sys import argv


##Usage: python create_plot.py [filepath] [plot type: box/violin]
##Make sure that your input data is tsv format and has a shannon_entropy column
##Or modify this script to fit your needs


filepath = argv[1]

plot_type = argv[2]

metadata = pd.read_csv(filepath, sep = "\t", index_col = "id") 
metadata = metadata.drop("#q2:types")

metadata["shannon_entropy"] = metadata.shannon_entropy.astype("float")
metadata = metadata.sort_values(["tissue_type"])
sns.set_style(style='darkgrid', rc={"axes.facecolor":"lightgrey"})
my_palette = sns.color_palette("deep", desat = 0.8)

def create_boxplot():
	bx = sns.boxplot(x="tissue_type",
	y="shannon_entropy",
	data=metadata,
	hue = "tissue_type",
	palette = "tab10")
	plt.show()
			   
def create_violin_and_swarm():
	sns.set_style(style='darkgrid', rc={"axes.facecolor":"lightgrey"})
	my_palette = sns.color_palette("deep", desat = 0.8)
	violin = sns.violinplot(x ='tissue_type', y ='shannon_entropy', data = metadata, hue = "tissue_type", palette = my_palette)
	swarm = sns.swarmplot(x ='tissue_type', y ='shannon_entropy', data = metadata, hue = "fixation_method", palette = {"FFPE":"#ffff00", "Fresh frozen": "#0000ff", "Other": "#f27304"}, s = 4.22)
	sns.move_legend(swarm, "center left", bbox_to_anchor=(1,0.5))
	swarm.set(xlabel = "Fixation method")
	plt.show()

if plot_type == "box":
	create_boxplot()
else:
	create_violin_and_swarm()

