# Complete Study Methodology

## From mice to humans: A multi-omic predictive framework for translational immunology

*Companion methods document to the manuscript submitted to **Genes and Immunity** (currently under review).*

---

## I. INTRODUCTION & RESEARCH FRAMEWORK

### I.A Study Rationale & Objectives
- **Core Scientific Question:** To what degree do murine models accurately mirror human blood transcriptomic dynamics during vaccination, acute bacterial infection, and systemic sterile injury?
- **The Translational Conundrum:** Individual orthologous gene-level correlations between mice and humans are frequently poor or inconsistent, casting doubt on preclinical murine translatability.
- **Central Hypothesis:** Higher-order biological structures—specifically functional pathways, Blood Transcription Modules (BTMs), and coordinated gene networks—are evolutionarily conserved across species, retaining high predictive fidelity even when individual gene effect sizes diverge.
- **Key Findings (as reported in the manuscript):**
  1. **Functional modules were more conserved between species than individual orthologous genes**, and module-level correlations exceeded gene-level correlations in every condition.
  2. **Translational accuracy depended on stimulus intensity:** acute infections and injuries engaged conserved signatures with higher concordance, while single-dose inactivated/subunit vaccination diverged.
  3. **Adding evolutionary and regulatory layers improved prediction.** Mouse rank and direction did not predict human responses on their own; adding sequence evolution, TF features, CRE architecture, CTCF status and BTM membership raised the random forest to $R^2 = 0.23$ for human rank transfer and ROC-AUC $= 0.85$ for directional concordance. A lasso-penalised logistic model was marginally better for shared-LEG classification (ROC-AUC $0.617$ predictive / $0.627$ explanatory).
  4. **Expression divergence between orthologs was associated with divergent *cis*-regulatory architecture** (promoter/enhancer turnover and TF sharing) rather than protein-coding sequence identity or codon evolution.

### I.B Study Design
- **Comparative Design:** Parallel time-course blood transcriptomic profiling of matched perturbations across humans (*Homo sapiens*) and laboratory mice (*Mus musculus*).
- **Perturbations Analyzed:** Inactivated and subunit vaccination (influenza, hepatitis B), acute bacterial infection (*S. aureus*, *E. coli*) and sterile injury (burns, trauma-hemorrhage).
- **Biological Negative Control:** Duchenne's muscular dystrophy (DMD; *mdx* mouse, peak pathological timepoint Day 28), used to benchmark the specificity of the cross-species comparison.
- **Data Repositories:** Publicly available transcriptomic cohorts retrieved from the NCBI Gene Expression Omnibus (GEO) and NCBI BioProject databases.
- **Analytical Trajectory:** Automated data curation $\to$ multi-level quality control $\to$ platform-specific normalization $\to$ probe collapsing & 1:1 ortholog mapping $\to$ linear modeling (limma DGE) $\to$ functional enrichment (BTMs / GSEA) $\to$ macroevolutionary divergence modeling $\to$ predictive classification (ROC/PR/AUC) $\to$ structural/regulatory evolutionary genomics $\to$ multi-modal statistical modeling (`tidymodels`).

---

## II. DATA ACQUISITION & STUDY COHORTS

### II.A Public Repository Search Strategy
1. **BioProject / GEO query:** vaccine-related terms (`"vaccine"`, `"vaccinated"`, `"vaccination"`, `"vaccines"`) combined with the filters `"transcriptome gene expression"`, `"material transcriptome"`, `"capture_whole"` and `"org mammals"`, while **excluding** *Homo sapiens* to focus on non-human mammalian studies.
2. **Organism restriction:** a subsequent query isolated studies specifically related to *Mus musculus* using the organism filter, **excluding** records associated with tumors, cancer and autoimmune diseases.
3. **Assay restriction:** only datasets labelled `"Expression profiling by array"` or `"Expression profiling by high throughput sequencing"` were retained.
4. **Manual annotation:** only studies involving **vaccines against human pathogens** were included. BioProject records were merged with GEO entries using PRJNA accession IDs, and each entry was split to assign unique identifiers based on the **vaccine used, sample source and RNA-sequencing protocol**. Datasets containing only partial methodological information, or focused solely on BCR/TCR repertoire data, were excluded.
5. **Annotation fields:** records were annotated with `GEOquery` and manually curated against the BioProject record and the corresponding publication, capturing sample source, target condition and antigen, vaccine type and adjuvant, time points, doses, administration route, RNA assay method, and availability on the **13Vax / COVID-19Vax atlases** or the **MSigDB Vax collection**. Where information conflicted with the publication, **the GEO record was prioritised** (e.g., immunization route, sample tissue source).

> Of 201 mouse immunization datasets retrieved from GEO, only two microarray datasets matched the human vaccination data in our atlases by tissue, antigen, vaccine type, target condition, time points and adjuvants. **GSE120661** (influenza + hepatitis B) was carried forward; **GSE182858** (influenza vaccination in "dirty" mice) could not be directly compared with the human cohort owing to divergent sampling schedules (3 hours before/after immunisation vs. days 1, 3 and 7) and was not used.

### II.B Clinical Metadata Harmonization
- **Time alignment:** for human injury datasets, time elapsed since injury (originally in hours) was converted to days.
- **Discretization:** samples were binned into categorical timepoints aligned to the mouse sample-collection schedule:

| Bin | Label | Bin | Label |
|:---|:---|:---|:---|
| < 1 day | Early Hours | 10–18 days | Day 14 |
| 1–2 days | Day 1 | 18–25 days | Day 21 |
| 2–5 days | Day 3 | > 25 days | Late |
| 5–10 days | Day 7 | | |

- **Grouping:** samples were stratified into **"Trauma"** or **"Burn"** and **"Control"** groups based on subject identifiers.

### II.C Dataset Cohort Matrix

| Stimulus Category | Condition / Agent | Organism | GEO Accession | Tissue Source | Platform |
|:---|:---|:---|:---|:---|:---|
| **Vaccination** | Influenza (Fluad: TIV + MF59) | Mouse | GSE120661 | PBMCs | Microarray |
| **Vaccination** | Influenza (Agrippal, unadjuvanted) | Mouse | GSE120661 | PBMCs | Microarray |
| **Vaccination** | Hepatitis B (Engerix-B + alum) | Mouse | GSE120661 | PBMCs | Microarray |
| **Vaccination** | Hepatitis B (Engerix-B, unadjuvanted) | Mouse | GSE120661 | PBMCs | Microarray |
| **Vaccination** | Influenza (Fluad: TIV + MF59) | Human | GSE124689 | PBMCs | Illumina HT-12 v4 |
| **Vaccination** | Hepatitis B (Engerix-B) | Human | GSE124533 | Whole blood | Illumina HT-12 v4 |
| **Acute Infection** | *S. aureus* bacteremia | Mouse | GSE19668 | Whole blood | Microarray |
| **Acute Infection** | *S. aureus* bacteremia | Human | GSE33341 | Whole blood | Microarray |
| **Acute Infection** | *E. coli* sepsis | Mouse / Human | GSE33341 | Whole blood | Microarray |
| **Sterile Injury** | Severe Burn | Mouse | GSE7404 | Blood | Microarray |
| **Sterile Injury** | Severe Burn | Human | GSE37069 | Whole blood | Microarray |
| **Sterile Injury** | Trauma-hemorrhage | Mouse | GSE7404 | Blood | Microarray |
| **Sterile Injury** | Severe Trauma | Human | GSE36809 | Whole blood | Affymetrix Gene 1.0 ST |
| **Negative control** | Duchenne muscular dystrophy (*mdx*) | Mouse | GSE1025 | Muscle | Affymetrix |

Mouse vaccination cohort metadata (from Supplementary Table 1):

| GEO | Time points | Samples | Doses | Type | Pathogen | Vaccine | Adjuvant | Tissue | Route | Assay |
|:---|:---|:---:|:---:|:---|:---|:---|:---|:---|:---|:---|
| GSE120661 | 4, 8, 24, 48, 72, 168 h | 5 | 1 | Subunit | HBV | Engerix-B | Alum | PBMCs | IM | Microarray |
| GSE120661 | 4, 8, 24, 48, 72, 168 h | 5 | 1 | Subunit | HBV | Engerix-B | None | PBMCs | IM | Microarray |
| GSE120661 | 4, 8, 24, 48, 72, 168 h | 5 | 1 | Inactivated | Influenza | Agrippal | None | PBMCs | IM | Microarray |
| GSE120661 | 4, 8, 24, 48, 72, 168 h | 5 | 1 | Inactivated | Influenza | Fluad® | MF59 | PBMCs | IM | Microarray |
| GSE182858 | −3, 0, 3 h | 13 | 1 | Inactivated | Influenza | Quadri 2019-2020 | None | PBMCs | IN | Bulk *(not used)* |
| GSE182858 | −3, 0, 3 h | 13 | 1 | Inactivated | Influenza | Quadri 2019-2020 | Addavax | PBMCs | IN | Bulk *(not used)* |
| GSE224584 | 2 weeks | 3 | 1 | Polysaccharide | *N. meningitidis* | ACWY | None | Whole blood | n/a | Bulk |

---

## III. QUALITY CONTROL & PREPROCESSING

### III.A Platform-Specific Normalization
Expression matrices were log2-transformed and processed using technology-specific algorithms in `1_Download_Standardize_Datasets.Rmd`:
- **Affymetrix oligonucleotide arrays (Human Gene 1.0 ST):** raw probe cell intensity files (.CEL) were preprocessed with the **Robust Multi-array Average (RMA)** algorithm via `affy`/`oligo`, executing background correction, quantile normalization and median-polish probe-set summarization.
- **Illumina BeadChips & Agilent arrays:** between-array quantile normalization was applied (`limma::normalizeBetweenArrays(method = "quantile")`) to enforce identical empirical distributions across arrays while preserving relative biological rank orders.

### III.B Probe-to-Gene Collapsing & Ortholog Mapping
- **Probe collapsing:** probes mapping to the **same Entrez ID** were collapsed by **selecting the probe with the highest median expression** (rather than averaging, which dampens signal across non-responsive probes).
- **Human reference selection:** when several genes had different Entrez IDs mapping to the same ortholog, the Entrez ID with the **highest median expression** was used as the reference for that gene.
- **Orthology:** to map orthologous genes, we used the **protein-coding genes with one-to-one orthology to human genes provided by the MGI database**. Genes with **multiple orthologs were excluded**. Annotation tables were retrieved via Bioconductor platform packages (`illuminaHumanv4.db`, `hugene10sttranscriptcluster.db`) and `biomaRt`.
- **Baseline contrast:** collapsed genes (by Entrez ID) were used as model input together with their log2-fold changes derived from a baseline contrast against pre-vaccination samples (0 h / Day 0).

### III.C Quality Control & Outlier Detection
Quality control was performed with `ArrayQualityMetrics` and `limma` diagnostic plots (Supplementary Information), complemented by visual diagnostics of the log2-transformed data:
1. **Distribution diagnostics:** density plots, boxplots and scatterplots were generated to inspect normalization and between-sample comparability.
2. **Principal Component Analysis (PCA):** PCA was used to identify outliers and batch effects. A significant separation of a subset of human trauma samples was detected and those samples were **excluded**, as the associated metadata did not identify the cause by any covariate (hypothesised to reflect unreported trauma severity).
3. **Relative Log Expression (RLE):** as an additional automated metric across datasets in `1.1_QualityControl.Rmd`:
   $$\text{RLE}_{gi} = \log_2(E_{gi}) - \operatorname{median}_{j}(\log_2(E_{gj}))$$
   Samples exhibiting anomalous IQR divergence or median shifts were flagged and removed when technical confounding was confirmed.

---

## IV. DIFFERENTIAL GENE EXPRESSION

### IV.A Linear Modeling with Limma
Differential gene expression was modeled independently for each condition and species using linear models with Empirical Bayes variance moderation via `limma`:
1. **Low-abundance filtering:** low-abundance genes were removed, retaining only those with a **log2-intensity higher than 6 in at least five samples** to reduce technical noise and improve statistical power.
2. **Model formulation:** for each condition, an unintercepted design matrix was constructed:
   $$\mathbf{Y}_{g} = \mathbf{X}\boldsymbol{\beta}_g + \boldsymbol{\varepsilon}_g, \quad \boldsymbol{\varepsilon}_g \sim \mathcal{N}(0, \sigma_g^2 \mathbf{I})$$
   where $\mathbf{X}$ represents experimental groups parameterized by organism, stimulus and timepoint.
3. **Contrasts:** post-treatment timepoints were contrasted directly against their matched pre-treatment baseline (e.g., $\text{Day 1} - \text{Day 0}$, $\text{Day 3} - \text{Day 0}$, $\text{Day 7} - \text{Day 0}$).
4. **Variance shrinkage (eBayes):** gene-wise sample variances were squeezed toward a global intensity-dependent prior using `limma::eBayes(fit, trend = TRUE, robust = TRUE)`:
   $$\tilde{s}_g^2 = \frac{d_0 s_0^2 + d_g s_g^2}{d_0 + d_g}$$
   The `trend` parameter accounts for the mean–variance relationship, while `robust` limits the influence of outlier genes.

### IV.B Covariates, Batch Effects and Sample Weights
- **Batch:** for the *E. coli* mouse dataset, weight estimation was stratified by experimental batch (`var.group = batch`) to mitigate batch effects while preserving the biological signal of the infection.
- **Longitudinal designs:** individuals were treated as **random effects**; for both longitudinal and case-control human datasets, covariates such as **sex, ethnicity and age** were included as fixed effects in the limma design matrix.
- **Heteroscedasticity:** to account for heteroscedasticity across clinical and experimental samples, sample-quality weights were estimated with `limma::arrayWeights`, ensuring that high-variance samples had a reduced impact on the linear model.

### IV.C Limma vs. Standard t-test (Supplementary Fig. S2)
To ensure robust detection of shared transcriptional signatures, limma was contrasted with conventional metrics used in prior studies (standard paired t-tests). By employing empirical Bayes variance shrinkage and adjusting for demographic covariates and batch effects, **limma significantly outperformed the standard paired t-test** in our datasets — the t-test approach failed to identify significant DEGs in the vaccinated mouse cohorts, which would have led to the erroneous conclusion of limited cross-species conservation. The comparison highlights the sensitivity of limma in paired clinical designs.

### IV.D Sample-size Balancing by Downsampling & Bootstrap
To account for sample-size imbalances between human and mouse studies, human samples were **downsampled to 5** with a **bootstrap over 200 iterations**, and the **median value** was used for the statistics derived from limma.

### IV.E Significance Thresholds & Diagnostics
- **DGE threshold:** genes were classified as significantly differentially expressed (DEGs) if they satisfied:
  $$\text{adj. } P\text{-value (BH FDR)} < 0.05$$
  Effect-size magnitude ($\log_2\text{FC}$) was preserved continuously without arbitrary threshold truncation, to power downstream rank-based pathway analyses.
- **GSEA threshold:** when evaluating functional modules, the standard False Discovery Rate limit was established at:
  $$\text{padj} \le 0.25$$
  capturing broader coordinated pathway trends (especially relevant for weaker stimuli such as vaccination).
- **p-value diagnostics:** raw p-value distributions were inspected across all comparisons. Most conditions showed the expected enrichment of low p-values ($p < 0.05$). In conditions where adjusted p-values yielded fewer significant genes (e.g., some murine injury models), raw p-value histograms lacked the expected peak at zero or showed a conservative upward trend, indicating lower statistical power or high intra-group variability. The murine **Burn and Trauma** datasets exhibited near-uniform adjusted p-value distributions, reflecting the high inter-individual biological variance inherent to cross-sectional studies compared with the longitudinal designs used in the other cohorts.

---

## V. FUNCTIONAL PATHWAY ENRICHMENT (BTMs)

### V.A Blood Transcription Modules (BTMs)
The primary analytical unit for immune-response evaluation comprised **346 Blood Transcription Modules** (Li et al., *Nat Immunol* 2014), capturing specific leukocyte subsets (T cells, B cells, NK cells, monocytes, neutrophils, dendritic cells) and intrinsic functional states (interferon response, inflammatory chemokines, cell cycle). Modules are grouped hierarchically into 16 broader physiological domains. The BTM dataset was retrieved from a previous publication.

### V.B Pre-ranked Gene Set Enrichment Analysis
For each contrast, orthologous genes were **pre-ranked** by the product of effect size and statistical significance:
$$\text{Rank}(g) = \log_2\text{FC}_g \times \left(-\log_{10}(\text{adjusted } P_g)\right)$$
Gene set enrichment analysis (GSEA) was performed with **`clusterProfiler`**, testing for the non-random distribution of module members within the ranked transcriptome. Enrichment scores were normalized for gene-set size ($NES$). Module-level cross-species enrichment concordance was then evaluated using **Pearson correlation coefficients ($r$) on the NES**, and MSigDB Hallmark gene sets were used in parallel as an independent functional reference.

---

## VI. CROSS-SPECIES COMPARATIVE ANALYSES

Notebooks `3.1_DGE_analyses.Rmd`, `3.2_Compute_GSEA.Rmd` and `3.3_Functional_Analyses.Rmd` consolidate all conditions into unified comparative frameworks (manuscript **Figs. 4–5**).

### VI.A Correlation Tests (Gene and Module Level)
- **Gene-level:** cross-species comparisons were evaluated using **weighted Spearman rank correlations ($\rho$)**, with weights defined as the **inverse standard error ($1/SE$)** of the murine effect-size estimates.
- **Module-level:** module enrichment concordance was evaluated with **Pearson correlation ($r$)** weighted by **$-\log_{10}(\text{adjusted } P)$** from GSEA.
- **Stratified filtering:** to evaluate the effect of statistical stringency on translatability, correlations were computed and compared across nested module subsets:
  1. **All enriched modules** (unfiltered).
  2. **Mouse-significant modules** ($\text{padj} \le 0.25$ in the mouse model).
  3. **Dual-significant modules** ($\text{padj} \le 0.25$ concordantly in both human and mouse).
- **Visualization:** intra- and inter-species correlation matrices over time (Supplementary Fig. S4), and gene-level scatter plots of log2FC per condition with DEGs highlighted (Supplementary Fig. S5; L2FC distributions in Supplementary Fig. S3).

### VI.B Effect-Size Divergence & Inverse-Variance Weighting
For each 1:1 orthologous gene pair across matched experimental conditions:
1. **Directional effect-size divergence:**
   $$\Delta \log_2\text{FC} = \log_2\text{FC}_{\text{Human}} - \log_2\text{FC}_{\text{Mouse}}$$
2. **Coefficient of variation (CV):**
   $$CV = \frac{SD}{|\text{mean } \log_2\text{FC}|}$$
3. **Inverse-variance statistical weighting:** to ensure that downstream cross-species correlation and distance evaluations were not biased by noisy low-expression probes, joint standard-error-based inverse weights were formulated:
   $$W_{SE} = \frac{1}{SE_{\text{Human}}^2 + SE_{\text{Mouse}}^2}$$
   where $SE$ represents the standard error from the linear-model fit.

### VI.C Leading-Edge Gene (LEG) Conservation (Fig. 5)
- **Extraction:** for each enriched BTM ($\text{padj} \le 0.25$), the **Leading-Edge Genes (LEGs)** — genes accounting for the core enrichment signal prior to the peak running enrichment score — were extracted for both species.
- **Categorization:** genes within each module were partitioned into **Shared LEGs** (leading edge in both species), **Human-specific LEGs**, **Mouse-specific LEGs** and **Non-LEGs**.
- **Key observations:** shared LEGs accounted for **67.5–79 %** of mouse LEGs in statistically significant enriched modules. Shared LEGs showed higher expression and a **lower $1/SE$** than Not-Shared LEGs (Wilcoxon–Mann–Whitney, adjusted $P < 2.22\times10^{-16}$ and $P < 0.00058$, respectively), although $1/SE$ did not differ significantly in burn and trauma ($P = 0.62$ and $0.39$).
- **Visualization:** proportions and counts are visualized via stacked and faceted barplots across conditions.

### VI.D Gene Rank Conservation in Core Immune Modules
- **Objective:** evaluate the conservation of intra-module gene prioritization between human and mouse.
- **Focal module:** illustrated using the *"immune activation — generic cluster"* (BTM M37.0; 347 genes), representing innate inflammatory, Toll-like receptor and chemokine signaling programs.
- **Composite rank metric:** for each gene $g$, a rank score combining effect size and statistical significance was formulated:
  $$\text{Rank Score}_g = \log_2(\text{FC}_g) \times \left(-\log_{10}(P\text{-value}_g)\right)$$
- **Ranking vector:** all orthologous module genes were ranked in descending order separately within human ($\text{Rank}_H$) and mouse ($\text{Rank}_M$); Spearman rank correlation was calculated between the two vectors.
- **Visual mapping:** a parallel-axis rank trajectory plot connects gene positions between human (left axis, H) and mouse (right axis, M) — shared LEGs, human-specific LEGs, mouse-specific LEGs and non-LEGs are distinguished by line colour.

---

## VII. MODEL EVALUATION (ROC / PR FRAMEWORK)

### VII.A One-Sided p-values
Because limma produces **two-sided** p-values, **one-sided** p-values were recalculated from the moderated $t$-statistics — using the **upper tail for upregulated genes** ($\log_2\text{FC} > 0$) and the **lower tail for downregulated genes** ($\log_2\text{FC} < 0$). The resulting one-sided p-values were subsequently adjusted for multiple hypothesis testing using the **Benjamini–Hochberg** false discovery rate correction.

### VII.B Reference Truth & Control Models
Model performance was evaluated using **receiver operating characteristic (ROC)** analysis to assess the ability to classify up- and down-regulated genes. The corresponding **human dataset was used as the reference "truth"**, while predictions from the mouse model were compared against it. Two control models were generated:
- a **"perfect" model**, which exactly replicated the human truth labels; and
- a **"negative control" model**, based on the **DMD** (*mdx*) gene expression table.

### VII.C Scoring and Metrics
- For each gene and timepoint, **prediction probabilities** were defined as $(1 - \text{adjusted one-sided } P)$, and **ROC and precision–recall (PR) curves** were constructed.
- The **area under the curve (AUC)** was then computed to measure predictive performance (`pROC`, `yardstick`).
- The **same framework was applied to functional modules**, using the NES and the $-\log_{10}(\text{adjusted } P)$ derived from GSEA. This ROC-based framework evaluates **module-level transfer** (manuscript Fig. 4b), and AUCs for acute infections and injuries were markedly higher than the near-random DMD baseline (Fig. 4c).

---

## VIII. EVOLUTIONARY GENOMICS: PROTEIN CODING VS. CIS-REGULATORY ARCHITECTURE

Notebooks `5.1_EvolutionaryAnalysis_Protein.Rmd` and `5.2_EvolutionaryAnalysis_Regulation.Rmd` assess whether transcriptomic divergence is governed by structural coding evolution or regulatory rewiring (manuscript **Fig. 6a–e**).

### VIII.A Coding Sequence (CDS) Acquisition & Longest Isoform Selection
1. **Source:** coding sequences (CDS) and amino-acid sequences for human–mouse protein-coding genes with **confidence score = 1** were obtained from Ensembl via `biomaRt`, retaining Ensembl protein identity values.
2. **Partitioned retrieval:** due to query volume and server timeout constraints, mouse CDS records were programmatically split into 3 balanced partitions (`target_map_mouse_part1`, `part2`, `part3`) and queried in chunks of 100 genes.
3. **Isoform resolution (longest canonical CDS):** because alternative splicing produces multiple transcripts per Ensembl Gene ID, a filtering step retained only the **longest coding sequence**:
   $$\text{Canonical CDS}_g = \arg\max_{t \in \mathcal{T}_g} \left( \operatorname{nchar}(\text{coding}_{g,t}) \right)$$
   Records with `"Sequence unavailable"` or non-coding annotations were purged.

### VIII.B Pairwise Nucleotide Global Alignment & Distance Computation
1. **Sequence sanitization:** leading/trailing whitespace and newline delimiters were stripped, and nucleotide sequences were converted to uppercase.
2. **Global Needleman–Wunsch alignment:** pairwise global alignment was performed with `pwalign::pairwiseAlignment(type = "global")` between human and mouse CDS strings:
   ```r
   dna_align <- pwalign::pairwiseAlignment(
     Biostrings::DNAString(human_cds),
     Biostrings::DNAString(mouse_cds),
     type = "global"
   )
   ```
3. **Conversion to alignment object:** aligned pattern and subject strings — preserving gap characters (`'-'`) — were converted to character matrices and to `DNAbin` objects via `ape::as.alignment()` and `ape::as.DNAbin()`.
4. **Kimura 2-parameter (K80) distance:** molecular evolutionary distances were computed with `ape::dist.dna(bin_dna, model = "K80")`. The K80 model corrects for multiple hits and differential rates between transitions ($P$) and transversions ($Q$):
   $$d_{\text{K80}} = -\frac{1}{2}\ln(1 - 2P - Q) - \frac{1}{4}\ln(1 - 2Q)$$
   Jukes–Cantor (JC69) distances were computed in parallel as a sensitivity control.
5. **Protein sequence identity:** amino-acid sequence identity percentages (`identity_human2mouse` and `identity_mouse2human`) were extracted from Ensembl BioMart homology tables.

### VIII.C Cis-Regulatory Element (cCRE) Architecture from ENCODE
Candidate cis-regulatory elements (cCREs) were integrated from the **ENCODE project via the SCREEN portal**:
- **References:** the complete **human (GRCh38)** and **mouse (mm10)** cCRE catalogues, together with **homologous cCREs**, were downloaded.
- **Functional classes analyzed:** human cCREs categorized as **PLS** (promoter-like signatures), **pELS** (proximal enhancer-like signatures) or **dELS** (distal enhancer-like signatures), then classified by whether they were **CTCF-bound or CTCF-non-bound**.
- **Assignment and comparison:** cCREs were **assigned to their associated human genes** and subsequently compared to the **annotated murine cCREs**. The total number of cCREs that **matched between species in terms of type (PLS, pELS, dELS) and CTCF binding status** was calculated, determining the corresponding percentage for each category.

### VIII.D Statistical Relationships with Expression Divergence (Fig. 6a–e)
Continuous relationships between sequence/regulatory features (sequence identity, Kimura distance, TF counts, CRE multiplicities) and expression divergence ($|\Delta\log_2\text{FC}|$) were fitted using **ordinary least-squares (OLS) linear models** and formally tested using monotonic **Spearman rank correlation coefficients**, to account for non-normality and heteroscedasticity:
- **(6a)** greater protein identity correlated negatively, whereas greater Kimura distance correlated positively, with expression divergence.
- **(6b)** transcription-factor counts and the percentage of TFs shared between mouse and human correlated negatively with $|\Delta\log_2\text{FC}|$.
- **(6c)** CRE abundance correlated positively with divergence for pELS and dELS, while PLS showed no significant relationship.
- **(6d)** the percentage of matching elements between species (conserved vs. turned-over) showed class-specific associations.
- **(6e)** CRE counts by class and CTCF binding status showed stronger effects for CTCF-bound pELS and comparable positive effects for dELS, while PLS maintained weak or non-significant trends.

---

## IX. MULTILAYER MACHINE-LEARNING MODELLING (`tidymodels`)

The consolidated **mouse-to-human transfer** pipeline (`Modelling/6_Statistical_Modelling.Rmd`) integrates evolutionary, regulatory and transcriptomic metrics to predict the **human** response gene by gene (manuscript **Fig. 7**). An alternative/sensitivity formulation for shared-LEG classification is provided in `Modelling/6_Statistical_Modelling_optionB.Rmd`.

```
Modelling/
├── 6_Statistical_Modelling.Rmd            # main consolidated pipeline (LOCO)
├── 6_Statistical_Modelling_optionB.Rmd    # alternative formulation (shared-LEG classification)
├── Figures/                               # Fig7_multilayer_modelling.png, performance bars, coefficients
├── Models/                                # metrics, coefficients, importances, out-of-fold predictions, butchered models
└── Tables/                                # LOCO metric tables (CSV) and candidate lists
```

### IX.A Feature Table (Fig. 7a)
A gene-wise feature table was assembled from:
1. **Mouse differential-expression summary:** mouse log2FC, $1/SE$, mouse absolute rank (overall and within BTMs).
2. **Structural coding evolution:** protein identity (`identity_human2mouse`), CDS Kimura distance (`dist_k80`).
3. **Cis-regulatory architecture:** PLS/pELS/dELS counts and match percentages, CTCF-bound fractions.
4. **Transcription-factor features:** total human TFs (`n_tf_total`), mouse–human TF sharing (`pct_tf_shared`).
5. **Functional annotation:** BTM membership (immune vs. non-immune designation).

### IX.B Feature Layers (Two Nested Sets)
Instead of six independent layers, the pipeline uses two nested feature sets, separating the transferable biological signal from the mouse magnitude:
1. **DGE Baseline** — mouse differential-expression summary only.
2. **Full + BTM** — adds the biological layers (sequence evolution, TF features, CRE architecture, CTCF status and BTM membership).

For the classification task, two framings are compared:
- **A (predictive):** retains the mouse magnitude.
- **B (explanatory):** removes the mouse magnitude to test the biological layers alone.

### IX.C Universes, Targets and Ranks
Two gene universes are defined:
1. **All human DEGs** ($\text{p\_adj\_human} \le 0.05$) — rank transfer and direction.
2. **Mouse LEGs** (`Shared` or `Mouse only`, BTM scope) — shared-LEG classification.

Each gene receives an **absolute rank (0–100)** from the percentile of $|\log_2\text{FC}| \times -\log_{10}(\text{adjusted } P)$ within its universe and condition:
$$\text{rank} = \text{percent\_rank}\left(|\log_2\text{FC}| \times -\log_{10}(\text{adj. } P)\right) \times 100$$
Targets:
- **Rank transfer:** `rank_human` (continuous, 0–100).
- **Direction:** `sign_concordant = sign(Log2FC_mouse) == sign(Log2FC_human)` (binary).
- **Shared-LEG classification:** `Shared` vs `Mouse only` (binary).

Derived metrics: $\text{rank\_diff} = |\text{rank\_mouse} - \text{rank\_human}|$ (**convergence**) and $\text{dual\_rank} = \min(\text{rank\_mouse}, \text{rank\_human})$ (**relevance**).

### IX.D Leave-One-Condition-Out Cross-Validation
To avoid optimistic bias, models are evaluated by **leave-one-condition-out (LOCO)** cross-validation over the four infection/injury folds (*S. aureus*, *E. coli*, Burn, Trauma), so that **every gene is predicted by a model trained without its condition**. These out-of-fold predictions feed both the metrics and the exported scores.

### IX.E Algorithms Benchmarked (Fig. 7b)
Four paradigms were compared under identical recipes (`step_dummy`, `step_zv`/`step_nzv`, `step_corr` for classification at threshold 0.9, and `step_normalize`), all implemented in `tidymodels`:
1. **Linear/logistic regression** (baseline).
2. **Lasso** (`glmnet`, `mixture = 1`, penalty = 0.01). Skipped automatically when fewer than two predictors remain.
3. **Random forest** (`ranger`, 500 trees, `mtry = 8`, `min_n = 5`).
4. **Neural network** (`nnet`, one hidden layer of 10 units, `epochs = 200`, weight decay 0.01).

Feature importance was assessed by **log-odds** (logistic), **standardized effects** (linear), **lasso coefficients** (penalized) and **Gini importance** (random forest) — Supplementary Fig. S7.

### IX.F Performance Metrics (Fig. 7c,d)
- **Classification (shared LEGs, direction):** ROC-AUC and PR-AUC (`yardstick`).
- **Regression (rank transfer):** $R^2$ and RMSE.

Out-of-fold LOCO results (best feature set per task):

| Task | Metric | Random Forest | Neural Network | Lasso | Linear |
|:-----|:-------|:-------------:|:--------------:|:-----:|:------:|
| Shared LEGs (predictive, Full + BTM) | ROC-AUC | 0.572 | 0.615 | **0.617** | 0.601 |
| Shared LEGs (explanatory, Full + BTM) | ROC-AUC | 0.622 | 0.603 | **0.627** | 0.611 |
| Human rank transfer (Mouse + layers) | $R^2$ | **0.234** | 0.068 | 0.072 | 0.072 |
| Directional concordance (Direction + layers) | ROC-AUC | **0.849** | 0.619 | 0.517 | 0.529 |

The **random forest was the best algorithm for human rank transfer and directional concordance**, whereas the **lasso was marginally better for shared-LEG classification by ROC-AUC**. The lasso improved only marginally over the unregularized linear model for shared-LEG classification and not at all for rank transfer or direction, indicating that the transferable signal for rank and direction is predominantly **non-linear and multivariate**, while LEG sharing is largely captured by a **linear, modular** signal. Mouse-only features reduced every algorithm to near chance for direction, whereas adding the BTM context raised the random forest to $R^2 = 0.23$ for human rank and ROC-AUC $= 0.85$ for directional concordance.

### IX.G Translational Scores
Scores were derived from the **out-of-fold predictions of the best model per task**, so that every gene is scored by a model trained without its condition. Two complementary axes are captured — **observed cross-species agreement** versus **predicted human response magnitude**:
- `score_shared` — probability of being a shared LEG.
- `score_rank` — predicted human absolute rank (0–100).
- `score_direction` — probability of concordant direction.
- `score_translational` — $\text{score\_rank} \times \text{score\_direction}$.

In addition, an **observed prioritisation score** multiplies cross-species convergence by the **observed** directional concordance and ranks genes measured in both species. The predictive `score_translational` instead multiplies the predicted human rank by the predicted concordance probability, forecasting the human response for new murine data.

### IX.H Model Serialisation and Application
The best workflows are reduced with `butcher()` and stored with `compress = "xz"` (`rf_model_*.rds`, `nn_model_*.rds` in `Modelling/Models/`) so they can be reloaded and applied to new mouse experiments with `predict()`. To make the workflow reusable, a step-by-step R Markdown notebook applies the trained models to a new murine dataset (DGE input → GSEA → prediction → scores).

### IX.I Output Artefacts
- **Metrics:** `metrics_shared.rds`, `metrics_rank.rds`, `metrics_direction.rds`, `metrics_shared_optionB.rds`
- **Coefficients:** `coefs_shared.rds`, `coefs_lasso_shared.rds`, `coefs_rank.rds`, `coefs_direction.rds`
- **Importance:** `imp_shared.rds`, `imp_rank.rds`, `imp_direction.rds`
- **Out-of-fold predictions:** `pred_shared.rds`, `pred_rank.rds`, `pred_direction.rds`
- **Trained models (butchered, `compress = "xz"`):** `rf_model_{shared,rank,direction}.rds`, `nn_model_{shared,rank,direction}.rds`, `lasso_model_shared.rds`
- **Consolidated tables:** `score_table_v2.rds`, `master_class_*_v2.rds`, `master_reg_*_v2.rds`
- **LOCO metric tables (`Modelling/Tables/`):** `shared_loco.csv`, `shared_loco_optionB.csv`, `rank_loco.csv`, `direction_loco.csv`, `observed_vs_predicted.{csv,rds}`, `priority_relevant_convergent_top20.csv`
- **Figures (`Modelling/Figures/`):** `Fig7_multilayer_modelling.png`, `Shared_Performance_bars.png`, `Rank_Direction_Performance_bars.png`, `Models_Coeff_Contributions.png`

---

## X. LIMITATIONS & FUTURE DIRECTIONS

- **Cohort size & metadata:** murine cohorts were small, constraining statistical power; the scarcity of datasets with sufficient metadata limited generalizability.
- **Genetic diversity:** the analysis was restricted to two inbred strains (**C57BL/6** and **CB6F1**), narrowing the phenotypic heterogeneity captured. Because host genetics shapes translatability, low correlation in some modules may reflect **strain–hypothesis mismatch** (Th1-biased C57BL/6 vs. Th2-biased BALB/c) rather than species-level failure.
- **Biological/experimental mismatches:** laboratory mice are immunologically naïve whereas humans carry complex exposure histories (evident in the Fluad® data); mouse vaccinations were **single-dose** whereas human inactivated/subunit vaccines typically use **prime-boost**, limiting comparison of adaptive trajectories; human burn/trauma datasets lacked standardized **severity scores**, precluding adjustment for this confounder.
- **Genomic resolution:** analyses relied on Ensembl-annotated **one-to-one orthologs**. The ~50 % amino-acid identity baseline captures evolutionary relatedness but not domain-topology conservation, rewiring of protein–protein interactions, or the distinction between neutral and functionally impactful mutations.
- **Not yet included:** regional constraint (**PhastCons/phyloP**), systematic **transposable-element** mapping, and expression of associated TFs. Confounders such as baseline expression, gene length, GC content, CRE sequence alignment and substitution-rate acceleration were not controlled.
- **Scope of the scores:** scores were derived from **blood-based BTMs** and require testing in other tissues and gene sets (e.g., **MSigDB**, **Gene Ontology**).
- **Future work:** test prime-boost and adjuvanted regimens for low-immunogenicity platforms, refine ortholog regulatory annotation, standardize clinical metadata, align strain with the hypothesis, and match timepoints by **biological equivalence** rather than chronological time.

---

## XI. COMPUTATIONAL REPRODUCIBILITY & DATA AVAILABILITY

### XI.A Environment Management via `renv`
All analyses were executed under **R version 4.5.2** (Bioconductor 3.22). Complete computational environments are pinned in `renv.lock`. The project environment can be restored via:
```r
renv::restore()
```

### XI.B Code & Data Availability
- **Primary repository (processing, modelling & manuscript code):** `https://github.com/wapsyed/mousetohuman_multilayer`
- **Companion repository (step-by-step prediction notebook + extensible model-building framework):** `https://github.com/wapsyed/mousetohuman_predict`
- All source code, dataset-processing scripts and model-training pipelines are released under an **MIT license**, allowing the community to audit, adapt and continuously retrain the architecture with additional perturbation models, booster vaccine regimens and emerging multi-omic layers.

---

## XII. REFERENCES

1. **BTMs:** Li S, et al. Molecular signatures of antibody responses derived from a systems biology approach. *Nature Immunology*. 2014;15(2):195-204.
2. **limma:** Ritchie ME, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Research*. 2015;43(7):e47.
3. **clusterProfiler:** Wu T, et al. clusterProfiler 4.0: A universal enrichment tool for interpreting omics data. *The Innovation*. 2021;2(3):100141.
4. **fgsea:** Korotkevich G, Sukhov V, Budin N, Shpak B, Artyomov MN, Sergushichev A. Fast gene set enrichment analysis. *bioRxiv*. 2021; doi:10.1101/060012.
5. **biomaRt:** Durinck S, Spellman PT, Birney E, Huber W. Mapping identifiers for the integration of genomic datasets with the R/Bioconductor package biomaRt. *Nature Protocols*. 2009;4(8):1184-1191.
6. **pwalign:** Pagès H. *pwalign: Efficient pairwise sequence alignments*. R Package Version 1.0.0; 2024.
7. **ape:** Paradis E, Schliep K. ape 5.0: an environment for modern phylogenetics and evolutionary analyses in R. *Bioinformatics*. 2019;35(3):526-528.
8. **ENCODE cCREs:** The ENCODE Project Consortium. Expanded encyclopaedias of DNA elements in the human and mouse genomes. *Nature*. 2020;583:699-710.
9. **SCREEN portal:** ENCODE Project Consortium. The ENCODE Portal and SCREEN cCRE registry. https://screen.wenglab.org
10. **MSigDB:** Liberzon A, et al. The Molecular Signatures Database (MSigDB) hallmark gene set collection. *Cell Systems*. 2015;1(6):417-425.
11. **MGI:** Bult CJ, et al. Mouse Genome Informatics (MGI): the unified mouse genome database. *Nucleic Acids Research*. 2019;47(D1):D801-D806.
12. **ArrayQualityMetrics:** Kauffmann A, Gentleman R, Huber W. arrayQualityMetrics — a bioconductor package for quality assessment of microarray data. *Bioinformatics*. 2009;25(3):415-416.
13. **GEOquery:** Davis S, Meltzer PS. GEOquery: a bridge between the Gene Expression Omnibus (GEO) and BioConductor. *Bioinformatics*. 2007;23(14):1846-1847.
14. **tidymodels:** Kuhn M, Wickham H. *Tidymodels: a collection of packages for modeling and machine learning using tidyverse principles*. 2020. https://www.tidymodels.org
15. **ranger:** Wright MN, Ziegler A. ranger: A fast implementation of random forests for high dimensional data in C++ and R. *Journal of Statistical Software*. 2017;77(1):1-17.
16. **glmnet:** Friedman J, Hastie T, Tibshirani R. Regularization paths for generalized linear models via coordinate descent. *Journal of Statistical Software*. 2010;33(1):1-22.
17. **nnet:** Venables WN, Ripley BD. *Modern Applied Statistics with S* (4th ed.). Springer; 2002. (R package `nnet`.)
18. **pROC:** Robin X, et al. pROC: an open-source package for R and S+ to analyze and compare ROC curves. *BMC Bioinformatics*. 2011;12(1):77.
19. **yardstick:** Kuhn M, Vaughan D, Hvitfeldt E. *yardstick: Tidy characterizations of model performance*. 2024. https://yardstick.tidymodels.org
20. **butcher:** Kuhn M, Silge J. *butcher: Model butchering for R*. 2024. https://butcher.tidymodels.org
21. **tidyverse:** Wickham H, et al. Welcome to the tidyverse. *Journal of Open Source Software*. 2019;4(43):1686.
22. **ComplexHeatmap:** Gu Z, Eils R, Schlesner M. Complex heatmaps reveal patterns and correlations in multidimensional genomic data. *Bioinformatics*. 2016;32(18):2847-2849.
23. **FIT:** Andres-Terre M, et al. Integrated, multi-cohort analysis identifies conserved transcriptional signatures across multiple respiratory viruses. *Immunity*. 2015;43(6):1199-1211.
