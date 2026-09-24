#!/usr/bin/env Rscript
# =============================================================================
# export_article_data.R
#
# Export the data that powers the immersive "Explore" edition of the
# Mouse2Human manuscript into compact JSON under docs/article-data/.
#
# Reads the study's own artefacts (CSV + .rds produced by the analysis
# notebooks) and writes one JSON file per chart. Re-run after a new
# manuscript version, then rebuild the site.
#
#   Rscript scripts_notebooks/export_article_data.R
# =============================================================================

# ── project library (renv) ───────────────────────────────────────────────────
root <- tryCatch(here::here(), error = function(e) getwd())
libs <- list.files(file.path(root, "renv", "library"),
                   pattern = "^R-", full.names = TRUE)
libs <- libs[order(libs, decreasing = TRUE)]
if (length(libs)) .libPaths(c(libs[1], .libPaths()))

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(readr)
  library(jsonlite)
})

out_dir <- file.path(root, "docs", "article-data")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

wrote <- character(0)
write_json_df <- function(x, name, digits = 4) {
  path <- file.path(out_dir, name)
  x <- as.data.frame(x)
  x[] <- lapply(x, function(col) {
    if (is.numeric(col)) round(col, digits) else col
  })
  jsonlite::write_json(x, path, auto_unbox = TRUE, na = "null",
                       digits = NA, pretty = FALSE)
  wrote <<- c(wrote, name)
  cat(sprintf("  ✓ %-26s %6d rows\n", name, nrow(x)))
}
read_rds <- function(...) readRDS(file.path(root, ...))
read_csv2 <- function(...) suppressMessages(readr::read_csv(file.path(root, ...),
                                                            show_col_types = FALSE))

cat("Exporting Explore data →", out_dir, "\n\n")

# ── 1 · Fig. 7 — model performance -------------------------------------------
try({
  rows <- list()
  for (spec in list(
        list(f = "Modelling/Tables/rank_loco.csv", task = "Human rank transfer", metric = "rsq"),
        list(f = "Modelling/Tables/direction_loco.csv", task = "Directional concordance", metric = "roc_auc"),
        list(f = "Modelling/Tables/shared_loco.csv", task = "Shared LEGs", metric = "roc_auc"))) {
    df <- read_csv2(spec$f)
    metric <- intersect(c(spec$metric, "rmse", "pr_auc"), names(df))[1]
    rows[[length(rows) + 1]] <- data.frame(
      task = spec$task, model = df$model, feature_set = df$feature_set,
      framing = df$framing, metric = metric, value = df[[metric]],
      stringsAsFactors = FALSE)
  }
  perf <- bind_rows(rows)
  write_json_df(perf, "fig7-perf.json", 5)
})

# ── 2 · Fig. 7 — gene explorer (observed vs predicted) -----------------------
try({
  ge <- read_csv2("Modelling/Tables/observed_vs_predicted.csv") %>%
    select(hgnc_symbol, treatment, pathogen, timepoint_comparison,
           status_original, rank_mouse, rank_human, sign_mouse,
           sign_concordant, mean_log2fc_mouse, mean_log2fc_human,
           pred_rank, pred_direction)
  write_json_df(ge, "fig7-genes.json", 3)
})

# ── 3 · Fig. 7 — priority convergent genes -----------------------------------
try({
  pr <- read_csv2("Modelling/Tables/priority_relevant_convergent_top20.csv")
  write_json_df(pr, "fig7-priority.json", 4)
})

# ── 4 · Fig. 7 — feature importance + lasso coefficients ---------------------
try({
  imp <- bind_rows(
    readRDS(file.path(root, "Modelling/Models/imp_rank.rds")) %>% mutate(task = "Human rank transfer"),
    readRDS(file.path(root, "Modelling/Models/imp_direction.rds")) %>% mutate(task = "Directional concordance"),
    readRDS(file.path(root, "Modelling/Models/imp_shared.rds")) %>% mutate(task = "Shared LEGs"))
  write_json_df(imp, "fig7-importance.json", 4)
  coefs <- readRDS(file.path(root, "Modelling/Models/coefs_shared.rds")) %>%
    select(feature_name_original, estimate, std.error, conf.low, conf.high,
           p.value, feature_set, framing)
  write_json_df(coefs, "fig7-coefs.json", 4)
})

# ── 5 · Fig. 1 — data curation (genus counts + Sankey + studies) -------------
try({
  step2 <- read_csv2("tables/Data curation/datacuration_step2.csv")
  genus <- step2 %>%
    filter(!grepl("cancer|tumor|autoimmune|drug", tolower(title))) %>%
    filter(grepl("vaccin|immuniz", tolower(title))) %>%
    mutate(genus = trimws(sub(" .*$", "", organism))) %>%
    count(genus, sort = TRUE) %>%
    rename(datasets = n)
  write_json_df(genus, "fig1-genus.json")

  sankey_path <- file.path(root, "tables/Data curation/datacuration_annotated_sankey_blood.csv")
  if (file.exists(sankey_path)) {
    # keep the first transition only and drop self-loops: a Sankey must be a DAG
    sk <- read_csv2("tables/Data curation/datacuration_annotated_sankey_blood.csv") %>%
      select(source, target, value, step_from) %>%
      filter(!is.na(source), !is.na(target), value > 0,
             source != target, step_from == 0)
    write_json_df(sk, "fig1-sankey.json")
  }
  ann <- read_csv2("tables/Data curation/datacuration_annotated.csv")
  studies <- ann %>%
    filter(!is.na(gse_id)) %>%
    transmute(gse = gse_id, pathogen = target_pathogen, vaccine = vaccine_type,
              adjuvant = adjuvanted, route = administration_route,
              sample = main_sample_source, sequencing = sequencing, taxon = taxon)
  write_json_df(studies, "fig1-studies.json")
})

# ── 6 · Fig. 2 — DEG counts and standard error by condition -----------------
try({
  dge <- read_rds("tables/Differential gene expression/all_human_mouse_dge_limma_degs.rds")
  summ <- dge %>%
    group_by(organism, pathogen, timepoint) %>%
    summarise(n_total = n(),
              n_sig = sum(adj_p_val < 0.05, na.rm = TRUE),
              median_se = median(se, na.rm = TRUE),
              median_abs_l2fc = median(abs(mean_l2fc), na.rm = TRUE),
              .groups = "drop")
  write_json_df(summ, "fig2-dge.json", 4)
})

# ── 7 · Figs. 4–5 — BTM modules and leading-edge genes -----------------------
try({
  legs <- read_rds("tables/Functional analysis/all_human_mouse_gsea_btm_legs.rds")
  keep <- c("pathogen", "timepoint_comparison", "process", "group", "symbol",
            "mean_l2fc_Mouse", "mean_l2fc_Human", "adj_p_val_Mouse",
            "adj_p_val_Human", "nes_human", "nes_mouse", "status",
            "percent", "ntotal", "treatment", "Mouse_rank", "Human_rank")
  keep <- intersect(keep, names(legs))
  btm <- legs %>% select(all_of(keep)) %>% distinct()
  write_json_df(btm, "fig4-btm.json", 4)

  # module-level table (one row per module × condition) with significance class
  mod_cols <- intersect(
    c("pathogen", "timepoint_comparison", "process", "group", "treatment",
      "nes_mouse", "nes_human", "p_adjust_mouse_gsea", "p_adjust_human_gsea", "percent"),
    names(legs))
  btm_mod <- legs %>%
    select(all_of(mod_cols)) %>%
    distinct() %>%
    mutate(sig = case_when(
      p_adjust_mouse_gsea < 0.05 & p_adjust_human_gsea < 0.05 ~ "significant in both",
      p_adjust_mouse_gsea < 0.05 ~ "significant in mice",
      TRUE ~ "all modules"))
  write_json_df(btm_mod, "fig4-btm-modules.json", 4)
})

# ── 8 · Fig. 6 — evolution and regulatory architecture -----------------------
try({
  # (a–b) protein identity and Kimura distance vs expression divergence
  gi <- read_rds("tables/Gene and Protein sequences/human_mouse_gene_info_dge_clean.rds")
  cds <- read_rds("tables/Gene and Protein sequences/human_mouse_cds_distance.rds") %>%
    select(hgnc_symbol, dist_k80)
  evo_all <- gi %>%
    left_join(cds, by = c("gene" = "hgnc_symbol")) %>%
    filter(is.finite(abs_log2fc_diff))
  set.seed(1)
  evo <- evo_all %>% sample_n(min(6000, nrow(evo_all)))
  write_json_df(evo, "fig6-evolution.json", 4)

  bins_from <- function(df, col, n = 12) {
    x <- df[[col]]; y <- df$abs_log2fc_diff
    ok <- is.finite(x) & is.finite(y)
    if (sum(ok) < 20) return(NULL)
    br <- unique(quantile(x[ok], probs = seq(0, 1, length.out = n + 1), na.rm = TRUE))
    if (length(br) < 3) return(NULL)
    grp <- cut(x[ok], breaks = br, include.lowest = TRUE)
    mid <- aggregate(x[ok], list(bin = grp), function(v) mean(v, na.rm = TRUE))
    agg <- aggregate(y[ok], list(bin = grp), function(v) mean(v, na.rm = TRUE))
    cnt <- aggregate(y[ok], list(bin = grp), length)
    data.frame(var = col, x = mid$x, y = agg$x, n = cnt$x)
  }
  evo_bins <- bind_rows(
    bins_from(evo_all, "identity_human2mouse"),
    bins_from(evo_all, "dist_k80"))
  if (nrow(evo_bins)) write_json_df(evo_bins, "fig6-evolution-bins.json", 4)

  # (c–f) cis-regulatory architecture: CRE type, CTCF status and matching
  cres <- read_rds("tables/Regulation/cres_type_homology_comparison_dge_legs_stats.rds") %>%
    filter(is.finite(abs_log2fc_diff))
  agg_by <- function(df, col, label, keep = NULL) {
    out <- df %>%
      group_by(bin = .data[[col]]) %>%
      summarise(y = mean(abs_log2fc_diff, na.rm = TRUE), n = n(), .groups = "drop") %>%
      mutate(var = label)
    if (!is.null(keep)) out <- out %>% filter(bin %in% keep)
    out %>% filter(!is.na(bin))
  }
  reg <- bind_rows(
    agg_by(cres, "match_cretype", "CRE type match", c("Same", "Different")),
    agg_by(cres, "match_ctcf", "CTCF match", c("Same", "Different")),
    agg_by(cres, "type_human", "CRE class (human)", c("PLS", "pELS", "dELS")),
    agg_by(cres, "match_homology_group", "CRE homology group"))
  if (nrow(reg)) write_json_df(reg, "fig6-regulation.json", 4)
})

# ── 9 · Fig. 4 — gene-level correlation (human vs mouse log2FC) --------------
try({
  wide <- read_rds("tables/Differential gene expression/all_human_mouse_log2fc_avg_wide_labels.rds")
  gc <- wide %>%
    transmute(pathogen = pathogen_human, timepoint = timepoint_comparison, gene = human_symbol,
              lfc_human = mean_log2fc_human, lfc_mouse = mean_log2fc_mouse,
              same = diff_sign_binary == "Same") %>%
    filter(is.finite(lfc_human), is.finite(lfc_mouse))
  meta <- gc %>% group_by(pathogen) %>%
    summarise(n = n(),
              rho = suppressWarnings(cor(lfc_mouse, lfc_human, use = "complete.obs")),
              .groups = "drop")
  write_json_df(meta, "fig4-genecorr-meta.json", 4)
  set.seed(2)
  write_json_df(gc %>% sample_n(min(20000, nrow(gc))), "fig4-genecorr.json", 3)
})

# ── 10 · Fig. 6 — |Δlog2FC| vs CRE count, per CRE type (colour = CTCF) --------
try({
  sc <- read_rds("Modelling/Models/score_table_v2.rds")
  cre_long <- bind_rows(
    sc %>% transmute(gene = hgnc_symbol, type = "PLS", n = coalesce(n_type_PLS, 0),
                     ctcf_bound = coalesce(`n_ctcf_PLS_CTCF-bound`, 0) > 0, abs_diff = abs_log2fc_diff),
    sc %>% transmute(gene = hgnc_symbol, type = "pELS", n = coalesce(n_type_pELS, 0),
                     ctcf_bound = coalesce(`n_ctcf_pELS_CTCF-bound`, 0) > 0, abs_diff = abs_log2fc_diff),
    sc %>% transmute(gene = hgnc_symbol, type = "dELS", n = coalesce(n_type_dELS, 0),
                     ctcf_bound = coalesce(`n_ctcf_dELS_CTCF-bound`, 0) > 0, abs_diff = abs_log2fc_diff)
  ) %>%
    filter(is.finite(abs_diff)) %>%
    group_by(gene, type) %>%
    summarise(n = mean(n, na.rm = TRUE),
              ctcf_bound = any(ctcf_bound, na.rm = TRUE),
              abs_diff = mean(abs_diff, na.rm = TRUE),
              .groups = "drop") %>%
    filter(is.finite(n), n > 0)
  if (nrow(cre_long)) write_json_df(cre_long, "fig6-cre-type.json", 4)
})

cat("\nDone —", length(wrote), "files written to docs/article-data/\n")
