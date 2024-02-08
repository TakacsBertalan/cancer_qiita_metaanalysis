import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sys import argv
from statannotations.Annotator import Annotator

##Usage from terminal: python create_plot.py [path to your tsv file] [plot type: box/violin]
##Make sure that your input data is tsv format and has a shannon_entropy column
##Or modify this script to fit your needs

filepath = argv[1]
plot_type = argv[2]

metadata = pd.read_csv(filepath, sep = "\t", index_col = "id") 
metadata = metadata.drop("#q2:types")

#Change this to your variable you're interested in. It needs to be the name of one of the columns in metadata
plot_by = "tissue_type"
#Color the box/violin plot based on this variable. It needs to be the name of one of the columns in the metadata. It can be the same as plot_by
color_box_by = "tissue_type"
#Color the swarmplot points based on this variable. It needs to be the name of one of the columns in the metadata. It should be the different from color_box_by.
#For color ideas see the QIIME2 color list at the end of the document. 
color_swarm_by = "fixation_method"


metadata["shannon_entropy"] = metadata.shannon_entropy.astype("float")
metadata = metadata.sort_values([plot_by])
sns.set_style(style='darkgrid', rc={"axes.facecolor":"lightgrey"})
my_palette = sns.color_palette("deep", desat = 0.8)

def create_boxplot():
	bx = sns.boxplot(x=plot_by,
	y="shannon_entropy",
	data=metadata,
	hue = color_box_by,
	palette = "tab10")
	plt.show()

def add_stats(plot):
	unique_methods = metadata[plot_by].unique()
	pairs = [(unique_methods[i], unique_methods[j]) for i in range(len(unique_methods)) for j in range(i+1, len(unique_methods))]
	annotator = Annotator(plot, pairs, data=metadata, x=plot_by, y='shannon_entropy')
	annotator.configure(test='Kruskal', comparisons_correction='Bonferroni', text_format='star', loc='outside', verbose=2)
	annotator.apply_and_annotate()
	
def create_violin_and_swarm():
	violin = sns.violinplot(x = plot_by, y ='shannon_entropy', data = metadata, hue = color_box_by, palette = my_palette)
	swarm = sns.swarmplot(x = plot_by, y ='shannon_entropy', data = metadata, hue = color_swarm_by, s = 4.22)
	sns.move_legend(swarm, "center left", bbox_to_anchor=(1,0.5))
	#Comment out the next line if you don't want to add statistical comparisons
	add_stats(violin)
	plt.show()

if plot_type == "box":
	create_boxplot()
else:
	create_violin_and_swarm()


"""
List of QIIME2 distinct colors
        "#ff0000",
        "#0000ff",
        "#f27304",
        "#008000",
        "#91278d",
        "#ffff00",
        "#7cecf4",
        "#f49ac2",
        "#5da09e",
        "#6b440b",
        "#808080",
        "#f79679",
        "#7da9d8",
        "#fcc688",
        "#80c99b",
        "#a287bf",
        "#fff899",
        "#c49c6b",
        "#c0c0c0",
        "#ed008a",
        "#00b6ff",
        "#a54700",
        "#808000",
        "#008080",
"""
