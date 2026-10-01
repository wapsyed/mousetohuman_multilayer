# Graph Report - mousetohuman_multilayer  (2026-10-01)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 610 nodes · 1016 edges · 58 communities (31 shown, 27 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.76)
- Token cost: 2,470 input · 5,048 output

## Graph Freshness
- Built from commit: `8c30d733`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- HTML Deck PDF Export
- Study Documentation and Codebook
- Limma Differential Expression
- Data Export and Wrangling
- Correlation and DNA Utilities
- PowerPoint Deck Builder
- Sample Matrix Preprocessing
- Expression Distribution Checks
- BTM GSEA Processing
- DEG Classification Performance
- Human-Mouse Correlation Plots
- Human-Mouse Divergence Analysis
- Feature Importance Plots
- LOCO Regression Metrics
- BTM GSEA Correlation
- Shared BTM Process Correlation
- BTM NES Correlation Summary
- CRE CTCF Divergence
- TF Gene Attribute Analysis
- Shared Classification Performance
- Custom ggplot Theme
- Limma Array Weight Modeling
- CRE Homology Comparison
- CDS DNA Distance Analysis
- Priority Gene Scoring
- GSEA Results Processing
- Distance Log2FC Scatter
- Human-Mouse DGE Data
- Human-Mouse Ortholog Mapping
- BTM Module Classification
- Protein Identity Distribution
- Rank Score Comparison
- GSE1025 Dataset
- GSE120661 Dataset
- GSE124533 Dataset
- GSE124689 Dataset
- GSE182858 Dataset
- GSE19668 Dataset
- GSE224584 Dataset
- GSE33341 Dataset
- GSE36809 Dataset
- GSE37069 Dataset
- GSE7404 Dataset
- FluAD Raw QN Data
- FluAD QN Averaged Data
- MSigDB Grouped Gene Sets
- Diagnostic Statistics

## God Nodes (most connected - your core abstractions)
1. `Complete Study Methodology` - 50 edges
2. `Article — From mice to humans` - 40 edges
3. `README — From mice to humans` - 36 edges
4. `Codebook — Animals Vax Atlas` - 24 edges
5. `From mice to humans — lab meeting slides` - 21 edges
6. `Explore the data — interactive companion` - 18 edges
7. `Limma Differential Expression` - 16 edges
8. `6_Statistical_Modelling.Rmd` - 15 edges
9. `calculate_correlation_pearson()` - 13 edges
10. `calculate_weighted_correlation_pearson()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `1 Download Standardize Datasets Notebook` --references--> `biomaRt`  [INFERRED]
  scripts_notebooks/1_Download_Standardize_Datasets.qmd → METHODOLOGY.md
- `QualityControl notebook` --calls--> `ArrayQualityMetrics`  [EXTRACTED]
  scripts_notebooks/1.1_QualityControl.qmd → METHODOLOGY.md
- `1 Download Standardize Datasets Notebook` --calls--> `GEOquery`  [EXTRACTED]
  scripts_notebooks/1_Download_Standardize_Datasets.qmd → METHODOLOGY.md
- `Article — From mice to humans` --references--> `MGI`  [EXTRACTED]
  docs/article.qmd → METHODOLOGY.md
- `Article — From mice to humans` --references--> `limma`  [EXTRACTED]
  docs/article.qmd → METHODOLOGY.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Cross-species comparison analyses in DGE script** — scripts_notebooks_3_1_dge_analyses_correlation, scripts_notebooks_3_1_dge_analyses_overlap, scripts_notebooks_3_1_dge_analyses_volcano, scripts_notebooks_3_1_dge_analyses_bionull [EXTRACTED 0.85]
- **BTM functional analysis pipeline** — scripts_notebooks_3_2_compute_gsea_dge_btm_process_genes, scripts_notebooks_3_2_compute_gsea_dge_btm_process_genes_wide, scripts_notebooks_3_2_compute_gsea_dge_btm_mean_process, scripts_notebooks_3_2_compute_gsea_dge_btm_mean_wide, scripts_notebooks_3_2_compute_gsea_gsea_results, scripts_notebooks_3_2_compute_gsea_dge_btm_gsea_mean_wide, scripts_notebooks_3_2_compute_gsea_gsea_btm_results_all_matched [EXTRACTED 0.90]
- **Cross-species classification performance suite** — scripts_notebooks_4_performance_differenttimepoints_classification_performance_compute_genes_degs, scripts_notebooks_4_performance_differenttimepoints_classification_performance_compute_modules, scripts_notebooks_4_performance_differenttimepoints_classification_performance_results, scripts_notebooks_4_performance_differenttimepoints_classification_performance_genes_modules_results, scripts_notebooks_4_performance_differenttimepoints_roc_auc_df, scripts_notebooks_4_performance_differenttimepoints_roc_curve_auc_df, scripts_notebooks_4_performance_differenttimepoints_pr_auc_df, scripts_notebooks_4_performance_differenttimepoints_pr_curve_auc_df [EXTRACTED 0.90]
- **Inter- and intra-species DGE correlation visualizations** — scripts_notebooks_3_1_dge_analyses_correlation_heatmap_all, scripts_notebooks_3_1_dge_analyses_correlation_heatmap_all_degs, scripts_notebooks_3_1_dge_analyses_correlation_heatmap_degs, scripts_notebooks_3_1_dge_analyses_correlation_dotplot_degs, scripts_notebooks_3_1_dge_analyses_correlation_heatmap_intra_human, scripts_notebooks_3_1_dge_analyses_correlation_heatmap_intra_mouse, scripts_notebooks_3_1_dge_analyses_correlation_heatmap_intra_human_mouse, scripts_notebooks_3_1_dge_analyses_human_mouse_log2fc_log2fc_avg_wide_scatterplot [EXTRACTED 0.90]
- **Feature contribution figures (effect / importance / lasso)** — scripts_notebooks_6_statistical_modelling_linear_coefs_plot_rank, scripts_notebooks_6_statistical_modelling_rf_imp_plot_rank, scripts_notebooks_6_statistical_modelling_log_coefs_plot_direction, scripts_notebooks_6_statistical_modelling_rf_imp_plot_direction, scripts_notebooks_6_statistical_modelling_lasso_coefs_plot_shared [EXTRACTED 0.90]
- **Human and mouse DEG datasets merged for cross-species comparison** — saureus_mouse_dge_limma_degs, saureus_human_dge_subsampled_degs, ecoli_mouse_dge_limma_degs, ecoli_human_dge_subsampled_degs, burn_mouse_dge_limma_degs, burn_human_dge_subsampled_degs, trauma_mouse_dge_limma_degs, trauma_human_dge_subsampled_degs, all_human_mouse_dge_limma_degs [EXTRACTED 0.90]
- **LOCO modelling universes (all DEGs / mouse LEGs / BTM scope)** — scripts_notebooks_6_statistical_modelling_df_all, scripts_notebooks_6_statistical_modelling_df_mouse_legs, scripts_notebooks_6_statistical_modelling_df_shared, scripts_notebooks_6_statistical_modelling_score_tbl [EXTRACTED 0.90]
- **Quality-control distribution plots** — scripts_notebooks_1_1_qualitycontrol_distribution_check_avg_plot, scripts_notebooks_1_1_qualitycontrol_distribution_check_avg_boxplot, scripts_notebooks_1_1_qualitycontrol_distribution_check_subject_plot, scripts_notebooks_1_1_qualitycontrol_distribution_check_log2fc_plot, scripts_notebooks_1_1_qualitycontrol_distribution_check_avg_log2fc_boxplot, scripts_notebooks_1_1_qualitycontrol_distribution_check_subject_log2fc_plot [EXTRACTED 0.90]
- **Cross-species correlation analysis (Human vs Mouse, Human vs Human, Mouse vs Mouse)** — scripts_notebooks_1.1_qualitycontrol_cor_human_mouse_timepoint, scripts_notebooks_1.1_qualitycontrol_cor_human_human, scripts_notebooks_1.1_qualitycontrol_cor_mouse_mouse, scripts_notebooks_1.1_qualitycontrol_correlation_long_all_mouse_human_timepoints_summary, scripts_notebooks_1.1_qualitycontrol_correlation_long_all_mouse_human_timepoints_summary_plot [EXTRACTED 0.95]
- **Limma differential expression pipeline** — scripts_notebooks_2_differential_gene_expression_eset_filtered, scripts_notebooks_2_differential_gene_expression_design, scripts_notebooks_2_differential_gene_expression_corfit, scripts_notebooks_2_differential_gene_expression_aw, scripts_notebooks_2_differential_gene_expression_fit, scripts_notebooks_2_differential_gene_expression_fit2, scripts_notebooks_2_differential_gene_expression_results_list, scripts_notebooks_2_differential_gene_expression_all_contrasts_degs [EXTRACTED 0.95]
- **Limma differential expression function chain** — scripts_notebooks_2_differential_gene_expression_lmfit, scripts_notebooks_2_differential_gene_expression_ebayes, scripts_notebooks_2_differential_gene_expression_topttreat, scripts_notebooks_2_differential_gene_expression_makecontrasts, scripts_notebooks_2_differential_gene_expression_arrayweights, scripts_notebooks_2_differential_gene_expression_duplicatecorrelation [EXTRACTED 0.95]
- **Algorithms benchmarked in multilayer modelling** — concept_random_forest, concept_lasso, concept_neural_network, concept_logistic_regression [EXTRACTED 1.00]
- **Curated GEO datasets for mouse–human comparison** — dataset_gse120661, dataset_gse124689, dataset_gse124533, dataset_gse19668, dataset_gse33341, dataset_gse7404, dataset_gse37069, dataset_gse36809, dataset_gse1025, dataset_gse182858, dataset_gse224584 [EXTRACTED 1.00]
- **Gene sets used in the study** — concept_btm, concept_msigdb_hallmarks, concept_immune_go, concept_vaxsigdb [EXTRACTED 1.00]
- **Cross-species evolutionary comparison artifacts** — scripts_notebooks_5_1_evolutionaryanalysis_protein_human_mouse_cds_distance, scripts_notebooks_5_2_evolutionaryanalysis_regulation_cres_type_homology_comparison_dge_legs_stats, scripts_notebooks_5_2_evolutionaryanalysis_regulation_gene_attribute_tf_count_log2fc_stats, tables_functional_analysis_dge_btm_process_genes_diff_bygene_clean_filtered [INFERRED 0.75]
- **Pathogen cohorts analysed with shared QC workflow** — scripts_notebooks_1.1_qualitycontrol_long_expr, scripts_notebooks_1.1_qualitycontrol_long_expr_log2fc_avg, scripts_notebooks_1.1_qualitycontrol_rle_plot, scripts_notebooks_1.1_qualitycontrol_sa_plot, scripts_notebooks_1.1_qualitycontrol_ma_plot, scripts_notebooks_1.1_qualitycontrol_pca_log2fc_expression, scripts_notebooks_1.1_qualitycontrol_distribution_check_subject_raw_qn_log2fc_all [INFERRED 0.80]
- **Human-mouse cross-species dataset harmonization** — scripts_notebooks_1_download_standardize_datasets_getgeo, scripts_notebooks_1_download_standardize_datasets_ensembl_mart, scripts_notebooks_1_download_standardize_datasets_hs_mm_symbol_entrez, scripts_notebooks_1_download_standardize_datasets_eset_human_mouse, scripts_notebooks_1_download_standardize_datasets_normalizebetweenarrays [INFERRED 0.85]
- **Influenza human-vs-mouse quality-control pipeline** — scripts_notebooks_1.1_qualitycontrol_human_mouse_fluad_raw_qn_log2fc, scripts_notebooks_1.1_qualitycontrol_volcano_plot_raw_qn, scripts_notebooks_1.1_qualitycontrol_pca_raw, scripts_notebooks_1.1_qualitycontrol_pca_qn, scripts_notebooks_1.1_qualitycontrol_distribution_check_subject_plot, scripts_notebooks_1.1_qualitycontrol_rle_plot, scripts_notebooks_1.1_qualitycontrol_ma_plot [INFERRED 0.85]

## Communities (58 total, 27 thin omitted)

### Community 0 - "HTML Deck PDF Export"
Cohesion: 0.06
Nodes (36): main(), text_of(), Block, build_bibtex(), caption_kind(), cell_html(), children_html(), classify_heading() (+28 more)

### Community 1 - "Study Documentation and Codebook"
Cohesion: 0.12
Nodes (62): Codebook — Animals Vax Atlas, ape, ArrayQualityMetrics, biomaRt, Blood Transcription Modules (BTMs), butcher, clusterProfiler, cis-regulatory elements (CREs) (+54 more)

### Community 2 - "Limma Differential Expression"
Cohesion: 0.06
Nodes (49): all_human_mouse_dge_limma_degs, all_human_mouse_metadata, all_human_mouse_samples_log2fc, burn_human_dge_subsampled_degs, burn_mouse_dge_limma_degs, Differentially Expressed Genes (DEGs), limma, quantile normalization (+41 more)

### Community 3 - "Data Export and Wrangling"
Cohesion: 0.04
Nodes (39): ann, btm, btm_mod, cds, coefs, cre_long, cres, df (+31 more)

### Community 4 - "Correlation and DNA Utilities"
Cohesion: 0.07
Nodes (14): all_packages, bioc_pkgs, calculate_correlation_pearson(), calculate_pairwise_dna_distance(), calculate_weighted_correlation_pearson(), calculate_weighted_correlation_spearman(), classification_performance_compute_genes_degs(), classification_performance_compute_modules() (+6 more)

### Community 5 - "PowerPoint Deck Builder"
Cohesion: 0.13
Nodes (31): bar(), block_of(), blocks_of(), box(), chrome(), est_lines(), hline(), kicker() (+23 more)

### Community 6 - "Sample Matrix Preprocessing"
Cohesion: 0.06
Nodes (44): ggpairs, influenza_human_mouse_qc_raw_qn_log2fc_avg.rds, influenza_human_mouse_qc_raw_qn_log2fc.rds, all_human_mouse_metadata.rds, all_human_mouse_samples_log2fc.rds, all_human_mouse_samples_log2fc, all_human_mouse_samples_log2fc_annotated, annotation_samples_pca (+36 more)

### Community 7 - "Expression Distribution Checks"
Cohesion: 0.12
Nodes (23): all_human_mouse_samples_log2fc, annotation_samples_pca, clean_matrix_log2fc, clean_matrix_raw, distribution_check_avg_boxplot, distribution_check_avg_log2fc_boxplot, distribution_check_avg_plot, distribution_check_log2fc_plot (+15 more)

### Community 8 - "BTM GSEA Processing"
Cohesion: 0.19
Nodes (14): all_degs, all_human_mouse_dge_limma_degs_matched_control, btm_annotation_genes, df_genes2GSEA, dge_btm_process_genes, dge_btm_process_genes_wide, df_legs, df_legs_ranked (+6 more)

### Community 9 - "DEG Classification Performance"
Cohesion: 0.15
Nodes (14): all_degs_human_mouse_matched_filtered, classification_performance_compute_genes_degs, classification_performance_results, degs_genes_human, genes_roc_allgenes, genes_roc_allgenes_immunegenes, pr_auc_df, pr_auc_heatmap (+6 more)

### Community 10 - "Human-Mouse Correlation Plots"
Cohesion: 0.18
Nodes (12): correlation_dotplot_degs, correlation_filtered_inter_weighted, correlation_filtered_intra, correlation_heatmap_all, correlation_heatmap_all_degs, correlation_heatmap_degs, correlation_heatmap_intra_human, correlation_heatmap_intra_human_mouse (+4 more)

### Community 11 - "Human-Mouse Divergence Analysis"
Cohesion: 0.18
Nodes (11): dge_btm_process_genes_diff_bygene_clean, dge_btm_process_genes_diff_bygene_clean_filtered, difflog2fc_distribution_legs_plot, legs_divergence_plot, legs_error_divergence_plot, legs_error_plot, alignments_human2mouse, alignments_human2mouse_all (+3 more)

### Community 12 - "Feature Importance Plots"
Cohesion: 0.25
Nodes (11): clean_feat, feature_contributions_figure, feature_dictionary, forest_plot, gini_plot, lasso_coefs_plot_shared, lasso_plot, linear_coefs_plot_rank (+3 more)

### Community 13 - "LOCO Regression Metrics"
Cohesion: 0.20
Nodes (11): deg_filter, df_all, direction_metrics, direction_res, gene_annotated_layers, loco_regression, observed_vs_predicted, rank_direction_plot (+3 more)

### Community 14 - "BTM GSEA Correlation"
Cohesion: 0.25
Nodes (9): dge_btm_gsea_mean_wide, gsea_btm_results_all_matched, calculate_weighted_correlation_pearson, cor_labels, cor_labels_mean_long, correlation_long_all_btm_mouse_human_timepoints_summary_heatmap_mean, dge_btm_mean_group_correlation_df, dge_btm_mean_group_correlation_plot (+1 more)

### Community 15 - "Shared BTM Process Correlation"
Cohesion: 0.22
Nodes (9): btm_correlation_process_heatmap, btm_correlation_shared_perc_plots, correlation_processes_bypathogen_time, correlation_processes_bypathogen_time_df, dge_btm_process_genes_correlation, safe_cor_test, shared_perc_plot, shared_perc_plot_df (+1 more)

### Community 16 - "BTM NES Correlation Summary"
Cohesion: 0.22
Nodes (9): calculate_correlation_pearson, cor_labels_nes, correlation_long_all_btm_mouse_human_timepoints_summary_barplot, correlation_long_all_btm_mouse_human_timepoints_summary_heatmap, correlation_long_all_btm_mouse_human_timepoints_summary_lineplot, dge_btm_nes_group_correlation_control_plot, dge_btm_nes_group_correlation_df, dge_btm_nes_group_correlation_plot (+1 more)

### Community 17 - "CRE CTCF Divergence"
Cohesion: 0.22
Nodes (9): cres_type_ctcf_divergence_pooled_plot, cres_type_ctcf_homology_divergence_pooled_plot, cres_type_ctcf_homology_pooled_plot, cres_type_ctcf_matchingpct_divergence_pooled_plot, cres_type_ctcf_matchingpct_pooled_plot, cres_type_divergence_pooled_plot, cres_type_homology_comparison_dge_legs_stats, cres_type_matchingpct_divergence_pooled_plot (+1 more)

### Community 18 - "TF Gene Attribute Analysis"
Cohesion: 0.22
Nodes (9): gene_attribute_chea_clean, gene_attribute_tf_count, gene_attribute_tf_count_legs_plot, gene_attribute_tf_count_legs_pooled_plot, gene_attribute_tf_count_log2fc_stats, gene_attribute_tf_divergence_plot, gene_attribute_tf_divergence_pooled_plot, gene_info_human_log2fc_stats (+1 more)

### Community 19 - "Shared Classification Performance"
Cohesion: 0.25
Nodes (9): btm_ranks, df_mouse_legs, df_shared, loco_classification, min_max, shared_metrics, shared_performance_plot, shared_res_A (+1 more)

### Community 21 - "Limma Array Weight Modeling"
Cohesion: 0.39
Nodes (8): aw (arrayWeights), corfit (duplicateCorrelation), design (model.matrix), df_global_runs, draw_flexible_subset, eset_filtered, fit (lmFit), fluad_human_subsampled_degs

### Community 22 - "CRE Homology Comparison"
Cohesion: 0.25
Nodes (8): cres_annotated, cres_mouse, cres_type_homology_comparison, cres_type_homology_comparison_wide, cres_type_matrix_pct, cres_type_matrix_pct_mouse_human_plot, genes_cres_human, homologous_cres

### Community 23 - "CDS DNA Distance Analysis"
Cohesion: 0.29
Nodes (7): calculate_pairwise_dna_distance, fetch_mouse_cds_chunked, biomaRt::getSequence, human_cds_clean, human_mouse_cds_distance, mouse_cds_clean, ortholog_map

### Community 24 - "Priority Gene Scoring"
Cohesion: 0.33
Nodes (7): model_col, pick_pred, pooled, priority_genes_heatmap, priority_list, score_plot, score_tbl

### Community 25 - "GSEA Results Processing"
Cohesion: 0.40
Nodes (5): autoGSEA, dge_btm_mean_process, dge_btm_mean_wide, gsea_output, gsea_results

### Community 26 - "Distance Log2FC Scatter"
Cohesion: 0.40
Nodes (5): difflog2fc_distance_scatter_condition_plot, difflog2fc_distance_scatter_plot, distance_legs_plot, human_mouse_cds_distance_dge, dge_btm_process_genes_diff_bygene_clean_filtered

### Community 27 - "Human-Mouse DGE Data"
Cohesion: 0.50
Nodes (4): influenza_human_mouse_fit_dge_pairwise2human.rds, all_human_mouse_dge_limma_degs.rds, all_degs_human_mouse, human_degs

### Community 28 - "Human-Mouse Ortholog Mapping"
Cohesion: 0.50
Nodes (4): ensembl_mart (BioMart), FIT.mouse2man, HS_MM_Symbol_Entrez, mouse_fluad_log2summary

### Community 29 - "BTM Module Classification"
Cohesion: 0.50
Nodes (4): btms_df_input, classification_performance_compute_modules, classification_performance_genes_modules_results, dge_btm_mean_process_all_matched_filtered

### Community 30 - "Protein Identity Distribution"
Cohesion: 0.50
Nodes (4): alignments_human2mouse_legs_identity_log2fc_plot, fetch_cds_chunked, gene_info_human_clean_dge, protein_identity_genes_distribution

### Community 31 - "Rank Score Comparison"
Cohesion: 0.67
Nodes (3): cor_label, rank_mouse_vs_rank_human, score_shared_vs_rank

## Knowledge Gaps
- **165 isolated node(s):** `ann`, `btm`, `btm_mod`, `cds`, `coefs` (+160 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 247 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `README — From mice to humans` connect `Study Documentation and Codebook` to `Limma Differential Expression`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `QualityControl notebook` connect `Limma Differential Expression` to `Study Documentation and Codebook`, `Expression Distribution Checks`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `pca_log2fc` connect `Expression Distribution Checks` to `Limma Differential Expression`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **What connects `ann`, `btm`, `btm_mod` to the rest of the system?**
  _165 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `HTML Deck PDF Export` be split into smaller, more focused modules?**
  _Cohesion score 0.05563093622795115 - nodes in this community are weakly interconnected._
- **Should `Study Documentation and Codebook` be split into smaller, more focused modules?**
  _Cohesion score 0.12215758857747223 - nodes in this community are weakly interconnected._
- **Should `Limma Differential Expression` be split into smaller, more focused modules?**
  _Cohesion score 0.06431372549019608 - nodes in this community are weakly interconnected._