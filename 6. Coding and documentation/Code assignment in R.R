
# Sets the path to the parent directory of RR classes
setwd("Z:\\File folders\\Teaching\\Reproducible Research\\2023\\Repository\\RRcourse2023\\6. Coding and documentation")

#   Import data from the O*NET database, at ISCO-08 occupation level.
# The original data uses a version of SOC classification, but the data we load here
# are already cross-walked to ISCO-08 using: https://ibs.org.pl/en/resources/occupation-classifications-crosswalks-from-onet-soc-to-isco/

# The O*NET database contains information for occupations in the USA, including
# the tasks and activities typically associated with a specific occupation.

task_data = read.csv("Data\\onet_tasks.csv")
# isco08 variable is for occupation codes
# the t_* variables are specific tasks conducted on the job

# read employment data from Eurostat
# These datasets include quarterly information on the number of workers in specific
# 1-digit ISCO occupation categories. (Check here for details: https://www.ilo.org/public/english/bureau/stat/isco/isco08/)
library(readxl)                     

# Use a loop to read all ISCO sheets into a list
isco_list <- list()
for (i in 1:9) {
  isco_list[[i]] <- read_excel("Data\\Eurostat_employment_isco.xlsx", sheet = paste0("ISCO", i))
  isco_list[[i]]$ISCO <- i  # Add occupation category
}

# Combine all ISCO datasets into one
all_data <- do.call(rbind, isco_list)

# Define a list of countries to dynamically calculate totals
countries <- c("Belgium", "Spain", "Poland")

# Calculate worker totals and shares for each country using loops
for (country in countries) {
  total_country <- rowSums(sapply(isco_list, function(df) df[[country]]))
  all_data[[paste0("total_", country)]] <- rep(total_country, 9)
  all_data[[paste0("share_", country)]] <- all_data[[country]] / all_data[[paste0("total_", country)]]
}

# Process task data for 1-digit ISCO level
library(stringr)
task_data$isco08_1dig <- as.numeric(substr(task_data$isco08, 1, 1))

# Calculate the mean task values at a 1-digit level
aggdata <- aggregate(. ~ isco08_1dig, data = task_data, FUN = mean, na.rm = TRUE)

# Combine the data
library(dplyr)
combined <- merge(all_data, aggdata, by.x = "ISCO", by.y = "isco08_1dig", all.x = TRUE)

# Function to standardize task variables for each country
standardize_task <- function(task_data, share_data) {
  mean_value <- weighted.mean(task_data, share_data, na.rm = TRUE)
  sd_value <- sqrt(weighted.mean((task_data - mean_value)^2, share_data, na.rm = TRUE))
  return((task_data - mean_value) / sd_value)
}

# Standardize Non-routine cognitive analytical tasks for each country and task
tasks <- c("t_4A2a4", "t_4A2b2", "t_4A4a1")
for (country in countries) {
  for (task in tasks) {
    combined[[paste0("std_", country, "_", task)]] <- standardize_task(combined[[task]], combined[[paste0("share_", country)]])
  }
  combined[[paste0(country, "_NRCA")]] <- rowSums(combined[paste0("std_", country, "_", tasks)], na.rm = TRUE)
  combined[[paste0("std_", country, "_NRCA")]] <- standardize_task(combined[[paste0(country, "_NRCA")]], combined[[paste0("share_", country)]])
}

# Calculate country-level mean NRCA over time
agg_results <- list()
for (country in countries) {
  combined[[paste0("multip_", country, "_NRCA")]] <- combined[[paste0("std_", country, "_NRCA")]] * combined[[paste0("share_", country)]]
  agg_results[[country]] <- aggregate(combined[[paste0("multip_", country, "_NRCA")]], by = list(combined$TIME), FUN = sum, na.rm = TRUE)
}

# Plot results for each country
for (country in countries) {
  plot(agg_results[[country]][, 2], xaxt = "n", main = paste("NRCA Over Time -", country), ylab = "NRCA", xlab = "Time")
  axis(1, at = seq(1, nrow(agg_results[[country]]), length.out = 10), labels = agg_results[[country]][seq(1, nrow(agg_results[[country]]), length.out = 10), 1])
}