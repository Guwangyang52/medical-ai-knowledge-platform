# Continuous-outcome meta-analysis runner script

dir.create("output", showWarnings = FALSE, recursive = TRUE)
dir.create("logs", showWarnings = FALSE, recursive = TRUE)

required_packages <- c("meta")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop("Missing required R packages: ", paste(missing_packages, collapse = ", "))
}

library(meta)

input_file <- Sys.getenv("MAKP_INPUT_FILE", unset = "data/sample_continuous_meta.csv")
if (!file.exists(input_file)) {
  stop("Input file not found: ", input_file)
}

if (grepl("\\.xlsx?$", input_file, ignore.case = TRUE)) {
  if (!requireNamespace("readxl", quietly = TRUE)) {
    stop("Package readxl is required for Excel input files.")
  }
  mydata <- readxl::read_excel(input_file)
} else {
  mydata <- read.csv(input_file, check.names = FALSE, fileEncoding = "UTF-8-BOM")
}

required_columns <- c("First_author", "Year", "n.e", "mean.e", "sd.e", "n.c", "mean.c", "sd.c")
missing_columns <- setdiff(required_columns, names(mydata))
if (length(missing_columns) > 0) {
  stop("Missing required columns: ", paste(missing_columns, collapse = ", "))
}

if (any(mydata$sd.e <= 0, na.rm = TRUE) || any(mydata$sd.c <= 0, na.rm = TRUE)) {
  stop("Standard deviations must be greater than 0.")
}

study_labels <- paste(mydata$First_author, mydata$Year, sep = "-")

meta1 <- metacont(
  n.e, mean.e, sd.e,
  n.c, mean.c, sd.c,
  data = mydata,
  studlab = study_labels,
  sm = "MD",
  common = TRUE,
  random = TRUE,
  method.tau = "REML"
)

writeLines(capture.output(summary(meta1)), "output/meta_summary.txt")

result_table <- data.frame(
  study = meta1$studlab,
  effect = meta1$TE,
  se = meta1$seTE,
  stringsAsFactors = FALSE
)
write.csv(result_table, "output/result_table.csv", row.names = FALSE, fileEncoding = "UTF-8")

png("output/forest_plot.png", width = 2400, height = 1800, res = 220)
forest(meta1, digits = 3)
dev.off()

png("output/funnel_plot.png", width = 1800, height = 1600, res = 220)
funnel(meta1)
dev.off()

bias_lines <- c()
egger_test <- tryCatch(
  metabias(meta1, method.bias = "Egger", k.min = 3),
  error = function(e) e
)
bias_lines <- c(bias_lines, "Egger test:", capture.output(print(egger_test)), "")

begg_test <- tryCatch(
  metabias(meta1, method.bias = "Begg", k.min = 3),
  error = function(e) e
)
bias_lines <- c(bias_lines, "Begg test:", capture.output(print(begg_test)))
writeLines(bias_lines, "output/publication_bias.txt")

sensitivity <- metainf(meta1, pooled = "random")
writeLines(capture.output(summary(sensitivity)), "output/sensitivity_summary.txt")

png("output/sensitivity_plot.png", width = 2400, height = 1800, res = 220)
forest(sensitivity)
dev.off()

if ("Subgroups" %in% names(mydata)) {
  meta2 <- metacont(
    n.e, mean.e, sd.e,
    n.c, mean.c, sd.c,
    data = mydata,
    studlab = study_labels,
    sm = "MD",
    subgroup = Subgroups,
    common = TRUE,
    random = TRUE,
    method.tau = "REML"
  )

  writeLines(capture.output(summary(meta2)), "output/subgroup_summary.txt")

  png("output/subgroup_forest_plot.png", width = 2600, height = 2000, res = 220)
  forest(meta2, digits = 3)
  dev.off()
}

cat("Analysis completed successfully.\n")
cat("Input rows:", nrow(mydata), "\n")
cat("Outputs written to output/\n")
