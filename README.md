# predicting-lung-cancer

County-level lung cancer mortality prediction for the contiguous United States using socioeconomic, atmospheric, meteorological, livestock, and smoking predictors.

## Overview

This project models county-level age-standardized lung cancer mortality from 2012 to 2019 with XGBoost and SHAP-based interpretation. The core question is whether atmospheric predictors remain important after county-level smoking rate is included explicitly in the model.

## Main Result

The main 45-predictor model achieved:

- test `R^2 = 0.875`
- test `RMSE = 5.40` deaths per 100,000
- test `MAE = 3.91` deaths per 100,000

The leading predictors in the full model were:

- `bachelor's degree or higher (%)`
- `smoking rate`
- `FoT formaldehyde above the 75th percentile`
- `wet-bulb temperature`
- `sulphate aerosol mixing ratio`

A comparison model using only smoking, socioeconomic, and demographic predictors performed worse:

- test `R^2 = 0.797`
- test `RMSE = 6.88`
- test `MAE = 5.12`

This comparison shows that the broader predictor set added county-level predictive information beyond smoking plus county-level socioeconomic and demographic predictors.

## Data Sources

The project integrates five data sources:

- **IHME**: county-level age-standardized lung cancer mortality
- **ACS 5-year estimates**: socioeconomic and demographic predictors
- **CAMS EAC4 / ERA5**: atmospheric and meteorological predictors
- **FAO Gridded Livestock of the World**: livestock density predictors
- **County Health Rankings**: adult smoking rate

Additional geographic input for the choropleth map comes from the 2019 U.S. Census TIGER county geometry.

## Repository Layout

- [`notebooks/`](notebooks): end-to-end data processing, modeling, supplementary figures, and the smoking-plus-SES comparison model
- [`data/`](data): raw inputs, processed tables, combined datasets, and modeling outputs
- [`generate_lung_cancer_choropleth.py`](generate_lung_cancer_choropleth.py): reproducible script for the 2019 lung cancer mortality choropleth

## Notebook Workflow

The main workflow is:

1. `00_single_year_lung_cancer_mortality.ipynb`
2. `01_preprocessing_fips_lung_cancer.ipynb`
3. `02_fetch_merge_acs_variables.ipynb`
4. `02b_fetch_merge_smoking_data.ipynb`
5. `03_combine_features_by_year.ipynb`
6. `04_cleaning_dataset.ipynb`
7. `05_combine_all_datasets.ipynb`
8. `06_feature_analysis_demographics.ipynb`
9. `07_feature_analysis_weather.ipynb`
10. `08_create_final_reduced_dataset.ipynb`
11. `09_xgboost_bayesian_optimization.ipynb`
12. `10_additional_paper_figures.ipynb`
13. `11_xgboost_smoking_socioeconomic_only.ipynb`

Notebook `09` produces the main model, SHAP rankings, permutation importance, and ablation outputs. Notebook `11` fits the smoking-plus-socioeconomic comparison model.

## Key Outputs

Important output files include:

- [`data/outputs/modeling/xgboost/table1_metrics_all_features.csv`](data/outputs/modeling/xgboost/table1_metrics_all_features.csv)
- [`data/outputs/modeling/xgboost/table5_ablation_comparison.csv`](data/outputs/modeling/xgboost/table5_ablation_comparison.csv)
- [`data/outputs/modeling/xgboost_smoking_ses/table1_metrics_smoking_ses.csv`](data/outputs/modeling/xgboost_smoking_ses/table1_metrics_smoking_ses.csv)
- [`paper/Figures/fig1_lung_cancer_mortality_map_2019.png`](paper/Figures/fig1_lung_cancer_mortality_map_2019.png)

## Reproducibility

To regenerate the lung cancer choropleth map:

```bash
conda run -n main_env python generate_lung_cancer_choropleth.py
```

This script reads:

- `data/raw/census_tiger_tl_2019_us_county.zip`
- `data/processed/preprocessed_fips_lung_cancer/preprocessed_lung_cancer_fips_2019.csv`

and writes:

- `paper/Figures/fig1_lung_cancer_mortality_map_2019.png`

## Notes

- Smoking is included explicitly as a predictor.
- `is_post_2015` is a measurement-control variable for the County Health Rankings methodology change and is not a scientific finding.
