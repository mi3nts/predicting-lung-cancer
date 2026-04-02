# NOTES

## Smoking Data Download Pipeline

Date performed: 2026-04-02

Purpose: document the exact workflow used to obtain the County Health Rankings (CHR) smoking data for this repo, so the process is reproducible for later notebook generation and paper writing.

## Official Source

Primary CHR documentation page used to resolve the download links:

`https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation/national-data-documentation-2010-2023`

Important measure page for later methods/discussion:

`https://www.countyhealthrankings.org/health-data/health-factors/health-behaviors/tobacco-use/adult-smoking?year=2019`

## Important Format Note

`CLAUDE.md` describes downloading yearly Excel workbooks and using the "Ranked Measure Data" sheet.

When this download was actually performed on 2026-04-02, the official CHR site clearly exposed year-specific **CSV analytic data** files for 2012-2019. Those CSV analytic files were downloaded instead of Excel workbooks because:

1. They are the current official year-specific analytic downloads published by CHR.
2. They already contain the adult smoking field needed for notebook `02b`.
3. They are simpler and more reliable to parse in the current environment.

Storage still follows the repo plan in `CLAUDE.md`: raw smoking data is stored under `data/raw/chr_smoking/`.

## Exact Download Steps

1. Created the target directory:

```bash
mkdir -p data/raw/chr_smoking
```

2. Resolved the official year-specific CHR analytic download URLs from the CHR documentation page.

3. Downloaded the files with `curl -fL` and saved them as `chr_YEAR.csv` in `data/raw/chr_smoking/`.

Command used:

```bash
cat <<'EOF' > /tmp/chr_urls.txt
2012 https://www.countyhealthrankings.org/sites/default/files/analytic_data2012.csv
2013 https://www.countyhealthrankings.org/sites/default/files/analytic_data2013.csv
2014 https://www.countyhealthrankings.org/sites/default/files/analytic_data2014.csv
2015 https://www.countyhealthrankings.org/sites/default/files/analytic_data2015.csv
2016 https://www.countyhealthrankings.org/sites/default/files/analytic_data2016.csv
2017 https://www.countyhealthrankings.org/sites/default/files/analytic_data2017.csv
2018 https://www.countyhealthrankings.org/sites/default/files/analytic_data2018_0.csv
2019 https://www.countyhealthrankings.org/sites/default/files/media/document/analytic_data2019.csv
EOF

while read -r year url; do
  curl -fL "$url" -o "data/raw/chr_smoking/chr_${year}.csv" || exit 1
done < /tmp/chr_urls.txt
```

## Files Downloaded

- `data/raw/chr_smoking/chr_2012.csv`
- `data/raw/chr_smoking/chr_2013.csv`
- `data/raw/chr_smoking/chr_2014.csv`
- `data/raw/chr_smoking/chr_2015.csv`
- `data/raw/chr_smoking/chr_2016.csv`
- `data/raw/chr_smoking/chr_2017.csv`
- `data/raw/chr_smoking/chr_2018.csv`
- `data/raw/chr_smoking/chr_2019.csv`

All downloaded files were verified as CSV text files.

## Smoking Field Identification

In every yearly file, the smoking variable is present as:

- Human-readable column: `Adult smoking raw value`
- Machine column on row 2 of the file: `v009_rawvalue`

The FIPS column needed for merging is:

- `5-digit FIPS Code`

Other useful columns present in the raw files:

- `State FIPS Code`
- `County FIPS Code`
- `State Abbreviation`
- `Name`
- `Release Year`
- `County Ranked (Yes=1/No=0)`

## Validation Checks Performed

The following checks were run after download:

1. Confirmed the files exist in `data/raw/chr_smoking/`.
2. Confirmed all files are CSV text.
3. Inspected the first rows of each file to verify header layout.
4. Confirmed the smoking field exists in every year.
5. Confirmed smoking values are already stored on a `0-1` scale, not a `0-100` scale.
6. Counted county-level coverage and non-null smoking values by year.
7. Compared adjacent years to detect exact duplicated yearly smoking releases.

## Coverage Summary

Observed from the downloaded files:

| Year | Total rows | County-like rows | Non-null smoking rows | Smoking min | Smoking max |
|------|------------|------------------|------------------------|-------------|-------------|
| 2012 | 3194 | 3192 | 2557 | 0.035 | 0.482 |
| 2013 | 3194 | 3192 | 2587 | 0.000 | 0.478 |
| 2014 | 3194 | 3192 | 2762 | 0.031 | 0.511 |
| 2015 | 3194 | 3192 | 2762 | 0.031 | 0.511 |
| 2016 | 3194 | 3192 | 3191 | 0.069 | 0.412 |
| 2017 | 3196 | 3193 | 3186 | 0.0654620687 | 0.4138995605 |
| 2018 | 3195 | 3193 | 3193 | 0.0673543283 | 0.4275405604 |
| 2019 | 3195 | 3193 | 3193 | 0.0673543283 | 0.4275405604 |

Interpretation:

- Pre-2016 coverage is materially lower than 2016+, which is consistent with the CHR methodology change described in `CLAUDE.md`.
- Post-2016 coverage is nearly complete at the county level.

## Important Data Findings

1. The files include national and state rows, not just county rows.
2. Notebook `02b` must therefore filter to county rows before creating the final smoking dataset.
3. The smoking values appear to already be proportions in the range `0-1`, so no percentage-to-proportion conversion should be applied unless a later file check contradicts this.
4. `2014` and `2015` have identical smoking values across all overlapping counties.
5. `2018` and `2019` also have identical smoking values across all counties.

Those duplicated year pairs appear to be characteristics of the official CHR releases, not download errors.

## Mental Note: County Coverage Discrepancy Across Years

This is important for later modeling and paper writing.

The number of counties with non-null smoking data is **not constant** across 2012-2019:

- 2012: `2506`
- 2013: `2536`
- 2014: `2711`
- 2015: `2711`
- 2016: `3140`
- 2017: `3136`
- 2018: `3142`
- 2019: `3142`

So the stacked county-year dataset created later in the pipeline will be an **unbalanced panel** if notebook `05` uses the planned inner join on `['fips', 'Year']`.

This is not automatically a bug. It means that:

1. Pre-2016 years will contribute fewer county-year observations than post-2016 years.
2. Some counties will appear only in later years.
3. The final merged modeling dataset will likely have different row counts by year.

## Mental Note: Balanced vs Unbalanced Panel

If the analysis were forced to use only counties that have non-null smoking data in **all 8 years**, the all-years intersection from the smoking files is:

- Counties present with smoking data in all 8 years: `2348`

The union across all years is:

- Counties present with smoking data in at least one year: `3149`

Therefore, forcing a perfectly balanced 8-year smoking panel would drop:

- `801` counties from the union of available smoking observations

Current recommendation:

1. Keep the main pipeline as planned with the year-specific inner join on `fips` + `Year`.
2. Do **not** force a perfectly balanced panel as the default dataset.
3. Report year-specific county counts after the final smoking merge and after the final full merge.
4. Mention in the paper that CHR smoking coverage expands after 2016, likely reflecting the documented methodology change.
5. If needed later, run a balanced-panel sensitivity analysis as a robustness check.

## Mental Note For The Paper

When writing the paper, explicitly acknowledge that:

1. County coverage for smoking is lower in 2012-2015 than in 2016-2019.
2. The period indicator `is_post_2015` accounts for the CHR methodology break, but it does not by itself eliminate the fact that county coverage changes across years.
3. The main analysis uses the available county-year observations after merging, rather than restricting to a perfectly balanced county panel.

## Recommended Extraction Rules For Notebook 02b

Notebook `02b_fetch_merge_smoking_data.ipynb` should use the downloaded CSV files and follow this extraction logic:

1. Read each file from `data/raw/chr_smoking/chr_YEAR.csv`.
2. Use `5-digit FIPS Code` as the county identifier.
3. Use `Adult smoking raw value` as the smoking variable.
4. Rename columns to:
   - `fips`
   - `Year`
   - `smoking_rate`
5. Zero-pad `fips` to 5 digits.
6. Filter out the national row and all state summary rows.
7. Keep only county observations.
8. Add `is_post_2015 = (Year >= 2016).astype(int)`.
9. Save the result to `data/processed/smoking_by_year/smoking_all_years.csv`.

## Filtering Guidance For Notebook 02b

The raw CHR CSV files contain multiple non-county rows, so county filtering should be explicit.

Safe filtering logic:

1. Convert `5-digit FIPS Code` to a zero-padded string.
2. Drop `00000` and any national aggregate row.
3. Drop state summary rows where `County FIPS Code == "000"`.
4. Keep rows where county FIPS is a real 5-digit county code.

## Methodology Note For The Paper

For the paper, note that:

1. CHR adult smoking data was downloaded from the official County Health Rankings analytic data releases for 2012-2019.
2. The smoking field used was `Adult smoking raw value`.
3. A period indicator `is_post_2015` is required to account for the CHR measurement-method break between 2012-2015 and 2016-2019.
4. The raw CHR files used in this repo are CSV analytic releases stored locally in `data/raw/chr_smoking/`.
