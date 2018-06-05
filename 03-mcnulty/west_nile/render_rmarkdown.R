rmd_file <- commandArgs(TRUE)[1]

working_dir <- "../working" # rmarkdown starts in same directory as source file

library(rmarkdown)
library(knitr)
opts_knit[['set']](root.dir = working_dir)
render(rmd_file, output_file = 'output.html', output_dir = working_dir, intermediates_dir = working_dir)