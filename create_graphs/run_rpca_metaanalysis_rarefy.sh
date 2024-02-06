#!/bin/bash

#SBATCH -J rpca-with-mucosa
#SBATCH --time=10:00:00         # Walltime
#SBATCH --mem-per-cpu=64000     # memory/cpu (in MB)
#SBATCH --ntasks=1              # 1 tasks
#SBATCH --cpus-per-task=1       # number of cores per task
#SBATCH --nodes=1               # number of nodes
#SBATCH --mail-type=ALL         #Mail to recive
#SBATCH --mail-user=btakacs@health.ucsd.edu

<<com
Date: 12/11/23

Goal: Run rpca scripts
Qiita ID # 14283 
com

#Conda env: qiime2-2022.11
"""
qiime tools import \
  --input-path 188082_61035_analysis_16S_Deblur202109ReferencephylogenyforSEPPGreengenes138BIOMreferencehitbiomTrimminglength150_insertion_filter.biom \
  --output-path ./mucosa_added_results/rpca_with_mucosa/imported_with_mucosa.qza \
  --input-format BIOMV210Format \
  --type "FeatureTable[Frequency]"
"""
qiime feature-table rarefy \
    --i-table /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/12_01_feature_table_filtered_2211.qza \
    --p-sampling-depth 13000 \
    --p-no-with-replacement \
    --o-rarefied-table ./mucosa_added_results/rpca_with_mucosa/rarefied_with_mucosa.qza

qiime gemelli auto-rpca \
    --i-table ./mucosa_added_results/rpca_with_mucosa/rarefied_with_mucosa.qza \
    --p-min-feature-count 500 \
    --p-min-sample-count 5 \
    --o-biplot ./mucosa_added_results/rpca_with_mucosa/rarefied_ordination.qza \
    --o-distance-matrix ./mucosa_added_results/rpca_with_mucosa/rarefied_distance.qza

#The taxonomy file comes from unzipping the gg-13-8-taxonomy.qza file

qiime emperor biplot \
    --i-biplot ./mucosa_added_results/rpca_with_mucosa/rarefied_ordination.qza \
    --m-sample-metadata-file /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/11_29_meta_unfiltered.qza \
    --m-feature-metadata-file /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/classification/taxonomy.tsv \
    --o-visualization ./mucosa_added_results/rpca_with_mucosa/rarefied_biplot.qzv \
    --p-number-of-features 8

qiime diversity beta-group-significance \
    --i-distance-matrix ./mucosa_added_results/rpca_with_mucosa/rarefied_distance.qza \
    --m-metadata-file /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/11_29_meta_unfiltered.qza \
    --m-metadata-column study_title \
    --p-method permanova \
    --p-pairwise True \
    --p-permutations 10000 \
    --o-visualization ./mucosa_added_results/rpca_with_mucosa/rarefied_study_title_significance.qzv

qiime diversity beta-group-significance \
    --i-distance-matrix ./mucosa_added_results/rpca_with_mucosa/rarefied_distance.qza \
    --m-metadata-file /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/11_29_meta_unfiltered.qza \
    --m-metadata-column tissue_type \
    --p-method permanova \
    --p-pairwise True \
    --p-permutations 10000 \
    --o-visualization ./mucosa_added_results/rpca_with_mucosa/rarefied_tissue_type_significance.qzv

qiime diversity beta-group-significance \
    --i-distance-matrix ./mucosa_added_results/rpca_with_mucosa/rarefied_distance.qza \
    --m-metadata-file /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/11_29_meta_unfiltered.qza \
    --m-metadata-column fixation_method \
    --p-method permanova \
    --p-pairwise True \
    --p-permutations 10000 \
    --o-visualization ./mucosa_added_results/rpca_with_mucosa/rarefied_fixation_method_significance.qzv

qiime qurro loading-plot \
    --i-ranks ./mucosa_added_results/rpca_with_mucosa/rarefied_ordination.qza \
    --i-table /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/12_01_feature_table_filtered_2211.qza \
    --m-sample-metadata-file /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/11_29_meta_unfiltered.qza \
    --m-feature-metadata-file /projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/classification/taxonomy.tsv \
    --o-visualization ./mucosa_added_results/rpca_with_mucosa/rarefied_qurro_plot.qzv
    
echo 'done'
