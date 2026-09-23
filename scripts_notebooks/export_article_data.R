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
  ann <- read_csv2("tables/Data curation/datacuration_annotated.csv") %>%
    mutate(genus = trimws(sub(" .*$", "", taxon)))
  genus <- ann %>% count(genus, sort = TRUE) %>% rename(datasets = n)
  write_json_df(genus, "fig1-genus.json")

  sankey_path <- file.path(root, "tables/Data curation/datacuration_annotated_sankey_blood.csv")
  if (file.exists(sankey_path)) {
    sk <- read_csv2("tables/Data curation/datacuration_annotated_sankey_blood.csv") %>%
      select(source, target, value) %>%
      filter(!is.na(source), !is.na(target), value > 0)
    write_json_df(sk, "fig1-sankey.json")
  }
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
})

# ── 8 · Fig. 6 — evolution and regulatory architecture -----------------------
try({
  sc <- read_rds("tables/human_mouse_statsmodelling_gene_annotated_layers.rds")
  keep <- c("hgnc_symbol", "treatment", "pathogen", "status_original",
            "identity_human2mouse", "dist_k80", "abs_log2fc_diff",
            "inverse_se_mouse", "n_tf_total", "pct_tf_shared",
            "n_total_cres_gene", "pct_match_type_PLS", "pct_match_type_pELS",
            "pct_match_type_dELS",
            "pct_match_ctcf_dELS_CTCF-bound", "pct_match_ctcf_pELS_CTCF-bound",
            "rank_mouse", "rank_human", "mean_log2fc_mouse", "mean_log2fc_human")
  keep <- intersect(keep, names(sc))
  evo_all <- sc %>% select(all_of(keep))

  # deterministic subsample for the scatter (keeps the JSON light)
  set.seed(1)
  evo <- evo_all %>% sample_n(min(6000, nrow(evo_all)))
  write_json_df(evo, "fig6-evolution.json", 4)

  # binned summaries for the regression lines
  bins_from <- function(df, col, n = 12) {
    x <- df[[col]]; y <- df$abs_log2fc_diff
    ok <- is.finite(x) & is.finite(y)
    if (sum(ok) < 20) return(NULL)
    br <- quantile(x[ok], probs = seq(0, 1, length.out = n + 1), na.rm = TRUE)
    grp <- cut(x[ok], breaks = unique(br), include.lowest = TRUE)
    agg <- aggregate(y[ok], list(bin = grp), function(v) mean(v, na.rm = TRUE))
    cnt <- aggregate(y[ok], list(bin = grp), length)
    mid <- aggregate(x[ok], list(bin = grp), function(v) mean(v, na.rm = TRUE))
    data.frame(var = col, x = mid$x, y = agg$x, n = cnt$x)
  }
  evo_bins <- bind_rows(
    bins_from(evo_all, "identity_human2mouse"),
    bins_from(evo_all, "dist_k80"))
  if (nrow(evo_bins)) write_json_df(evo_bins, "fig6-evolution-bins.json", 4)

  # regulatory aggregates by CRE type / CTCF status
  reg_rows <- list()
  if ("n_type_PLS" %in% names(sc) && "n_type_pELS" %in% names(sc) && "n_type_dELS" %in% names(sc)) {
    dom <- sc %>%
      mutate(dominant = case_when(
        n_type_PLS >= n_type_pELS & n_type_PLS >= n_type_dELS ~ "PLS",
        n_type_pELS >= n_type_dELS ~ "pELS",
        TRUE ~ "dELS")) %>%
      group_by(dominant) %>%
      summarise(abs_diff = mean(abs_log2fc_diff, na.rm = TRUE),
                n = n(), .groups = "drop") %>%
      transmute(var = "dominant CRE class", bin = dominant, y = abs_diff, n = n)
    reg_rows[[length(reg_rows) + 1]] <- dom
  }
  for (col in c("pct_match_type_pELS", "pct_match_type_dELS",
                "pct_match_ctcf_dELS_CTCF-bound", "pct_match_ctcf_pELS_CTCF-bound")) {
    if (col %in% names(sc)) {
      b <- bins_from(sc, col, n = 6)
      if (!is.null(b)) reg_rows[[length(reg_rows) + 1]] <-
        transmute(b, var = col, bin = as.character(bin))
    }
  }
  if (length(reg_rows)) write_json_df(bind_rows(reg_rows), "fig6-regulation.json", 4)
})

cat("\nDone —", length(wrote), "files written to docs/article-data/\n")
