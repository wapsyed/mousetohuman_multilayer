# Statistical Modelling — Mouse-to-Human Transfer

The `Modelling/` folder contains the consolidated **mouse-to-human transfer** pipeline used for the manuscript (**Fig. 7**). It predicts the **human** response gene by gene from a mouse experiment, integrating transcriptomic, evolutionary and regulatory feature layers under **leave-one-condition-out (LOCO)** cross-validation.

---

## I. Scripts & Folder Layout

```
Modelling/
├── 6_Statistical_Modelling.Rmd            # main consolidated pipeline (LOCO)
├── 6_Statistical_Modelling_optionB.Rmd    # alternative/sensitivity formulation (shared-LEG classification)
├── Figures/                               # manuscript + diagnostic figures
│   ├── Fig7_multilayer_modelling.png
│   ├── Shared_Performance_bars.png
│   ├── Rank_Direction_Performance_bars.png
│   └── Models_Coeff_Contributions.png
├── Models/                                # 34 artefacts: metrics, coefficients, importances,
│                                          # out-of-fold predictions and butchered model objects
└── Tables/                                # LOCO metric tables and candidate lists (CSV/RDS)
```

The pipeline is sourced through `scripts_notebooks/required.R` (packages, colours, `theme_vaxgo`).

---

## II. Inputs

| Input | Path | Content |
|:---|:---|:---|
| Gene-annotated feature layers | `tables/human_mouse_statsmodelling_gene_annotated_layers.rds` | Sequence evolution, TF features, cCRE architecture, BTM membership (per gene) |
| Per-gene expression + BTM statistics | `tables/Functional analysis/dge_btm_process_genes_diff_bygene_clean_filtered.rds` | log2FC, SE, adjusted P and BTM/LEG status across conditions |

---

## III. Feature Layers

### III.A Building blocks
| Block | Features |
|:---|:---|
| **Mouse magnitude** | mouse log2FC, absolute rank (overall and within BTMs) |
| **Measurement precision** | inverse standard error (`inverse_se_mouse`) — noise covariate |
| **Sequence evolution** | protein identity (`identity_human2mouse`), CDS Kimura K80 distance (`dist_k80`) |
| **Transcription factors** | total human TFs (`n_tf_total`), mouse–human TF sharing (`pct_tf_shared`) |
| **Cis-regulatory architecture** | PLS/pELS/dELS counts and match percentages, CTCF-bound fractions |
| **Blood transcriptional modules** | BTM membership and BTM-only rank (`rank_mouse_btm`) |

### III.B Feature sets (nested)
Each task compares a **mouse-only baseline** against a **biological layer** set:

| Task | Baseline set | Enriched set |
|:---|:---|:---|
| Shared-LEG classification | `DGE Baseline` | `Full + BTM` |
| Human rank transfer | `Mouse only` | `Mouse + layers` |
| Directional concordance | `Direction only` | `Direction + layers` |

For shared-LEG classification two **framings** are compared:
- **A — predictive:** keeps the mouse magnitude (expression-driven).
- **B — explanatory:** removes the mouse magnitude to test the biological layers alone.

---

## IV. Universes, Targets & Derived Metrics

Two gene universes are defined inside the script:

| Universe | Genes | Used by |
|:---|:---|:---|
| **1 — all human DEGs** (`p_adj_human <= 0.05`) | ranks across all DEGs | Convergence, Rank transfer, Direction |
| **2 — mouse LEGs** (`Shared` and `Mouse only`) | ranks recomputed **within** mouse LEGs | Shared-LEG classification |

**Absolute rank (0–100)** = percentile of $|\log_2\text{FC}| \times -\log_{10}(\text{adjusted } P)$ per condition (high rank = strong **and** significant; direction is ignored):

$$\text{rank} = \text{percent\_rank}\left(|\log_2\text{FC}| \times -\log_{10}(\text{adj. } P)\right) \times 100$$

**Derived metrics and targets:**

| Metric | Definition | Meaning |
|:---|:---|:---|
| `relevance` / `dual_rank` | $\min(\text{rank\_mouse}, \text{rank\_human})$ | high only when strong in **both** species |
| `convergence` / `rank_diff` | $|\text{rank\_mouse} - \text{rank\_human}|$ | low when genes sit at similar ranks |
| `conv_rel` | $\text{dual_rank} \times (1 - \text{rank\_diff}/100)$ | combined relevance **and** convergence (observed prioritisation) |
| `sign_concordant` | $\text{sign}(\log_2\text{FC}_{\text{mouse}}) = \text{sign}(\log_2\text{FC}_{\text{human}})$ | directional concordance (binary) |
| `rank_human` | absolute rank in the human dataset (0–100) | regression target |

---

## V. Cross-Validation

Models are evaluated by **leave-one-condition-out (LOCO)** over the four infection/injury conditions (*S. aureus*, *E. coli*, Burn, Trauma). Every gene is therefore predicted by a model trained **without its own condition**, and all reported metrics come from these out-of-fold predictions — avoiding the optimistic bias of in-sample evaluation.

---

## VI. Algorithms Benchmarked

Four paradigms are compared under identical `tidymodels` recipes (dummy encoding, near-zero-variance and correlation filtering, normalization):

1. **Linear / logistic regression** — baseline.
2. **Lasso** (`glmnet`, `mixture = 1`) — skipped when fewer than two predictors remain.
3. **Random forest** (`ranger`) — the best model for rank transfer and direction.
4. **Neural network** (`nnet`) — single hidden layer.

Feature importance is extracted as **log-odds** (logistic), **standardized effects** (linear), **lasso coefficients** and **Gini importance** (random forest).

---

## VII. Results (out-of-fold, LOCO)

### VII.A Shared leading-edge gene classification (ROC-AUC)
| Feature set | Framing | Lasso | Neural Net | Logistic | Random Forest |
|:---|:---|:---:|:---:|:---:|:---:|
| `Full + BTM` | A — predictive | **0.617** | 0.615 | 0.601 | 0.572 |
| `Full + BTM` | B — explanatory | **0.627** | 0.603 | 0.611 | 0.622 |
| `DGE Baseline` | A — predictive | 0.473 | 0.461 | 0.476 | 0.459 |

### VII.B Human rank transfer ($R^2$ / RMSE)
| Feature set | Random Forest | Neural Net | Lasso | Linear |
|:---|:---:|:---:|:---:|:---:|
| `Mouse + layers` | **R² = 0.234** (RMSE 25.35) | 0.068 | 0.072 | 0.072 |
| `Mouse only` | 0.0006 | 0.025 | — | 0.019 |

### VII.C Directional concordance (ROC-AUC)
| Feature set | Random Forest | Neural Net | Logistic | Lasso |
|:---|:---:|:---:|:---:|:---:|
| `Direction + layers` | **0.849** (PR-AUC 0.928) | 0.619 | 0.529 | 0.517 |
| `Direction only` | 0.511 | 0.511 | 0.511 | — |

**Interpretation.** Mouse rank and direction do **not** transfer on their own (Mouse only / Direction only ≈ chance). Adding the biological layers produced the conserved signal, with a marked increase in random forest $R^2$ for human rank and ROC-AUC for directional concordance. For shared-LEG classification the lasso was only marginally better than the unregularized linear model, indicating that LEG sharing is largely captured by a **linear, modular** signal, whereas rank and direction are predominantly **non-linear and multivariate**.

---

## VIII. Out-of-Fold Scores

The best model per task produces four complementary scores (each gene scored by a model trained without its condition):

| Score | Definition | Use |
|:---|:---|:---|
| `score_shared` | probability of being a shared LEG | prioritise conserved pathway drivers |
| `score_rank` | predicted human absolute rank (0–100) | forecast human response magnitude |
| `score_direction` | probability of concordant direction | forecast direction of change |
| `score_translational` | $\text{score\_rank} \times \text{score\_direction}$ | combined translational potential |

An additional **observed prioritisation** axis (`conv_rel` = relevance × convergence) operates on genes measured in both species, so the two axes answer different questions: **observed cross-species agreement** versus **predicted human response**.

---

## IX. Output Artefacts

### `Modelling/Models/` (34 files)
- **Metrics:** `metrics_shared.rds`, `metrics_rank.rds`, `metrics_direction.rds`, `metrics_shared_optionB.rds`, plus legacy `metrics_task*`
- **Coefficients:** `coefs_shared.rds`, `coefs_lasso_shared.rds`, `coefs_rank.rds`, `coefs_direction.rds`
- **Importance:** `imp_shared.rds`, `imp_rank.rds`, `imp_direction.rds`
- **Out-of-fold predictions:** `pred_shared.rds`, `pred_rank.rds`, `pred_direction.rds`
- **Trained models (butchered, `compress = "xz"`):** `rf_model_{shared,rank,direction}.rds`, `nn_model_{shared,rank,direction}.rds`, `lasso_model_shared.rds`
- **Consolidated tables:** `score_table_v2.rds`, `master_class_*_v2.rds`, `master_reg_*_v2.rds`

### `Modelling/Tables/`
`shared_loco.csv`, `shared_loco_optionB.csv`, `rank_loco.csv`, `direction_loco.csv`, `observed_vs_predicted.{csv,rds}`, `priority_relevant_convergent_top20.csv`

### `Modelling/Figures/`
`Fig7_multilayer_modelling.png`, `Shared_Performance_bars.png`, `Rank_Direction_Performance_bars.png`, `Models_Coeff_Contributions.png`

---

## X. Applying the Models to New Data

```r
model_rank <- readRDS("Modelling/Models/rf_model_rank.rds")
preds      <- predict(model_rank, new_data)
```

To make the workflow reusable, the companion repository **[`mousetohuman_predict`](https://github.com/wapsyed/mousetohuman_predict)** provides a step-by-step R Markdown notebook that applies the trained models to new murine datasets (DGE input → GSEA → prediction → scores).

---

## XI. Reproducing

```r
renv::restore()
source("Modelling/6_Statistical_Modelling.Rmd")
```

Environment: **R 4.5.2** / Bioconductor 3.22 (see `renv.lock`). All methods are described in detail in [`METHODOLOGY.md`](METHODOLOGY.md).
