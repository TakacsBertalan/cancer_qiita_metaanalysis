from pkg_resources import resource_filename

import biom
from birdman import SingleFeatureModel
import numpy as np
import pandas as pd

#Replace with your model path
#When you run the script the first time, make sure to run the following to compile your model
#On a barnacle terminal, type in python
#In python, call in the following commands:
#import cmdstanpy
#cmdstanpy.CmdStanModel(stan_file="path/to/model.stan")
#quit() to quit python
MODEL_PATH = "/panfs/btakacs/cancer_qiita/birdman/birdman_2_scripts/birdman/src/model_single.stan"
#Replace with your metadata path
MD = pd.read_table("/projects/cancer_qiita/btakacs/metaanalysis/mucosa_added_results/11_29_meta_filtered.qza",
                   sep="\t", index_col='#SampleID')

#You can give a new name to your model here, make sure to change it in the run_birdman_chunked.py script as well
class CancerQiitaModelSingle(SingleFeatureModel):
    def __init__(
        self,
        table: biom.Table,
        feature_id: str,

        beta_prior: float = 2.0,
        disp_scale: float = 0.5,
        re_prior: float = 2.0,
        num_iter: int = 500,
        num_warmup: int = 1000,
        **kwargs
    ):
        super().__init__(
            table=table,
            feature_id=feature_id,
            model_path=MODEL_PATH,
            num_iter=num_iter,
            num_warmup=num_warmup,
            **kwargs
        )

        study_series = MD["study_title"].loc[self.sample_names]
        samp_study_map = study_series.astype("category").cat.codes + 1
        self.studies = np.sort(study_series.unique())
#Replace with your own formula
#The simplest way is putting the variables you're intested in separated by +
        self.create_regression(formula="fixation_method + tissue_type", metadata=MD)

        D = table.shape[0]
        A = np.log(1 / D)

        param_dict = {
            "depth": np.log(table.sum(axis="sample")),
            "num_study": len(self.studies),
            "study_map": samp_study_map.values,
            "B_p": beta_prior,
            "disp_scale": disp_scale,
            "re_p": re_prior,
            "A": A
        }
        self.add_parameters(param_dict)

        self.specify_model(
            params=["beta_var", "base_phi", "study_re", "study_disp"],
            dims={
                "beta_var": ["covariate"],
                "study_re": ["study"],
                "study_disp": ["study"],
                "log_lhood": ["tbl_sample"],
                "y_predict": ["tbl_sample"]
            },
            coords={
                "covariate": self.colnames,
                "tbl_sample": self.sample_names,
                "study": self.studies
            },
            include_observed_data=True,
            posterior_predictive="y_predict",
            log_likelihood="log_lhood"
        )
