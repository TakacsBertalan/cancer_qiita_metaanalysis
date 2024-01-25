import qiime2
from tempfile import mkdtemp
from qiime2.plugins import demux, deblur, quality_filter, \
                           metadata, feature_table, alignment, \
                           phylogeny, diversity, emperor, feature_classifier, \
                           taxa, composition, fragment_insertion
from qiime2.plugins.alignment.methods import mafft
import pandas as pd
from qiime2.plugins.diversity_lib.methods import faith_pd
from qiime2.plugins.fragment_insertion.methods import sepp
from qiime2.plugins.fragment_insertion.methods import filter_features
import sklearn
import os

# Importing the data and the metadata
qza_table = qiime2.Artifact.load("./183565_feature-table.qza")
meta = qiime2.Metadata.load("./60286_60286_analysis_mapping_14117_14149_14201_14232_updated.txt")

# Adding a new tissue_type column to metadata
studies = set(meta.to_dataframe()['study_title'])
study_tissue_type = {}

for s in studies:
    if "breast" in s.lower():
        study_tissue_type[s] = "breast"
    elif "lung" in s.lower():
        study_tissue_type[s] = "lung"
    elif "CRC" in s or "colorectal" in s.lower() or "gut" in s.lower():
        study_tissue_type[s] = "colorectal"
    elif "gastric" in s.lower():
        study_tissue_type[s] = "gastric"
    else:
        study_tissue_type[s] = ""

study_tissue_type["PC_tumor_16SampSeq"] = "pancreatic"
study_tissue_type["Microbiome of bladder tissue and urine of bladder cancer patients"] = "bladder"

tissue_type_list = []
for i in meta.to_dataframe()['study_title']:
    tissue_type_list.append(study_tissue_type[i])

# Adding fixation_method column based on the publications    
fixation_method = {"PRJNA665618": "FFPE", "PRJNA604455": "Fresh tissue", "PRJNA487683": "Fresh frozen", "PRJNA641258": "FFPE", "PRJNA325650": "Fresh frozen", "PRJNA356414": "Fresh frozen", "PRJNA647170": "Fresh frozen", "PRJNA637875": "Fresh frozen", "PRJNA404030":"Fresh frozen", "PRJNA632856":"Fresh frozen", "PRJNA586753": "Fresh frozen", "PRJNA508819":"Fresh frozen", "PRJNA606879":"unknown", "PRJNA325649":"FFPE", "PRJNA667135": "Fresh frozen" }
fixation_method_list = []

for i in meta.to_dataframe()['study_accession']:
    fixation_method_list.append(fixation_method[i])

titles = []
# Fixing that one paper with "/" in it's title

for i in meta.to_dataframe()["study_title"]:
    if "/" not in i:
        titles.append(i)
    else:
        new_title = i.replace("/","_")
        titles.append(new_title)

#Adding everything to a dataframe and converting back to a qiime2 metadata object
df = meta.to_dataframe()
df["tissue_type"] = tissue_type_list
df["fixation_method"] = fixation_method_list
df["study_title"] = titles
df["qiita_study_title"] = titles

meta = qiime2.Metadata(df)

meta.save("./11_09_meta_unfiltered.qza")

# Inclusion criteria
#criterion = "[primary_experimental_variable] IN () OR [isolation source] IN () OR [host_disease] IN ('ADC', 'SRCC', 'colorectal cancer') OR [env_material]='biopsy'" 
criterion = "[primary_experimental_variable] IN ('Tumour', 'tumor tissue sample', 'CRC','lung adenocarcinoma', 'lung squamous cell carcinoma',"\
"'WNHa_T', 'BNHa_T', 'WNHb_T', 'on_tumor_site', 'NRM','R_M', 'Tissue', 'ADC', 'SRCC', 'colorectal cancer', 'on-tumor_site', 'Patient', 'cancer tissue', 'tumoral') "\
"OR [sample_site]='affected bronchial' OR [env_material]='biopsy'" 

# Thresholds for filtering samples and features
min_feature_per_sample= 1000
min_per_feature = 3

# Filter FeatureTable[Frequency] with feature-table filter-samples method to remove samples with a small library size
sample_filtered_data = feature_table.methods.filter_samples(table=qza_table, min_frequency=min_feature_per_sample, metadata=meta, where=criterion)

# Filter FeatureTable[Frequency] with feature-table filter-features method to remove very rare features
feature_filtered_data = feature_table.methods.filter_features(table=sample_filtered_data.filtered_table, min_frequency=min_per_feature)

# Visualize the filtered table
vis_filtered_data = feature_table.visualizers.summarize(table=feature_filtered_data.filtered_table, sample_metadata=meta)
vis_filtered_data.visualization.save('./slurm_results/filtered_table_visualization.qzv')

meta.save("./11_07_meta_filtered_2211.qza")
feature_filtered_data.filtered_table.save("./11_07_feature_table_filtered_2211.qza")

# Write sequences into a fasta file
with open('./slurm_results/sepp_sequences.fna', 'w') as f:
    for seq in feature_filtered_data.filtered_table.view(pd.DataFrame).columns:
        f.write('>%s\n%s\n' % (seq, seq))

# import the fasta file as a FeatureData[Sequence] artifact
sequences = qiime2.Artifact.import_data(type='FeatureData[Sequence]', view='./slurm_results/sepp_sequences.fna')

# visualize artifact and save both visualization and artifact
vis_sequences = feature_table.visualizers.tabulate_seqs(data=sequences)
sequences.save('./slurm_results/sequences.qza')

# Generating and importing the Greengenes tree built with Sepp

"""
greengenes_sep_reference = qiime2.Artifact.load("./sepp-refs-gg-13-8.qza")

sepp_tree = sepp(sequences, greengenes_sep_reference)

sepp_tree.tree.save("./slurm_results/sepp_rooted_tree.qza")

sepp_tree = qiime2.Artifact.load("./slurm_results/sepp_rooted_tree.qza")
"""

sepp_tree = qiime2.Artifact.load("./phylogenetic_trees/10_24_sepp_rooted_tree.qza")

#Alpha rarefaction graph
rarefaction = diversity.actions.alpha_rarefaction(table = feature_filtered_data.filtered_table,
                                                  max_depth = 50000,
                                                  phylogeny = sepp_tree,
                                                  metadata = meta)


rarefaction.visualization.save("./slurm_results/with_sepp_tree/11_09_rarefaction.qzv")


# Calculating alpha and beta diversity metrics

def calculate_metrics_and_save(input_table, output_folder, meta):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    core_metrics = diversity.pipelines.core_metrics_phylogenetic(table = input_table,
                                                             phylogeny = sepp_tree,
                                                             sampling_depth = 13000,
                                                             metadata = meta)
    
    core_metrics_dict = {"bray_curtis_emperor": core_metrics.bray_curtis_emperor, "bray_curtis_pcoa": core_metrics.bray_curtis_pcoa_results, "bray_curtis_distance_matrix": core_metrics.bray_curtis_distance_matrix, "jaccard_emperor": core_metrics.jaccard_emperor, "jaccard_pcoa": core_metrics.jaccard_pcoa_results, "jaccard_distance_matrix": core_metrics.jaccard_distance_matrix, "unweighted_unifrac_emperor": core_metrics.unweighted_unifrac_emperor, "unweighted_unifrac_pcoa": 
core_metrics.unweighted_unifrac_pcoa_results, "unweighted_unifrac_distance_matrix": core_metrics.unweighted_unifrac_distance_matrix,"weighted_unifrac_emperor": core_metrics.weighted_unifrac_emperor, "weighted_unifrac_pcoa": core_metrics.weighted_unifrac_pcoa_results, "weighted_unifrac_distance_matrix": core_metrics.weighted_unifrac_distance_matrix}
    
    mdc_dict = {"study_title_mdc": meta.get_column('qiita_study_title'), "tissue_type_mdc": meta.get_column('tissue_type')}
    
    for key in core_metrics_dict:
        core_metrics_dict[key].save(output_folder + "/" + key)
        if "distance_matrix" in key:
            for mdc in mdc_dict:
                diversity.actions.beta_group_significance(core_metrics_dict[key], mdc_dict[mdc], pairwise = True, permutations = 100000).visualization.save(output_folder + "/" + key)
    
    diversity.actions.alpha_group_significance(alpha_diversity=core_metrics.evenness_vector, metadata=meta).visualization.save(output_folder + "/" + "evenness_significance")
    diversity.actions.alpha_group_significance(core_metrics.faith_pd_vector, meta).visualization.save(output_folder + "/" + "faithphd_significance")

    
# Splitting fixation methods
ffpe_data = feature_table.methods.filter_samples(table=feature_filtered_data.filtered_table, metadata =meta, where = "[fixation_method]='FFPE'")
fresh_frozen_data = feature_table.methods.filter_samples(table=feature_filtered_data.filtered_table, metadata =meta, where = "[fixation_method]='Fresh frozen'")
    
calculate_metrics_and_save(ffpe_data.filtered_table, "./slurm_results/with_sepp_tree/only_ffpe", meta)
calculate_metrics_and_save(fresh_frozen_data.filtered_table, "./slurm_results/with_sepp_tree/only_fresh_frozen", meta)

# Taxonomic classification

sepp_filtered_table,sepp_removed_table = filter_features(feature_filtered_data.filtered_table,sepp_tree)

gg_classifier = qiime2.Artifact.load("/projects/cancer_qiita/btakacs/metaanalysis/phylogenetic_trees/gg-13-8-99-nb-weighted-classifier.qza")

taxonomy = feature_classifier.methods.classify_sklearn(reads = sequences,
                                                       classifier = gg_classifier)

taxonomy.classification.save("./slurm_results/with_sepp_tree/classification/gg_138_taxonomy.qza")

taxonomy_classification = metadata.visualizers.tabulate(taxonomy.classification.view(qiime2.Metadata))
taxonomy_classification.visualization.save("./slurm_results/with_sepp_tree/classification/gg_138_taxonomy_classification")


taxa_bar_plot = taxa.visualizers.barplot(sepp_filtered_table, taxonomy.classification, meta)
taxa_bar_plot.visualization.save("./slurm_results/with_sepp_tree/classification/gg_138_taxa_bar_plot.qzv")
