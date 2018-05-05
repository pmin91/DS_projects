[Kaggle Scripts](https://www.kaggle.com/c/predict-west-nile-virus/scripts) are a great way to share models, visualizations, or analyses with other Kagglers.

You can run scripts right on Kaggle without ever downloading the data, but for iterating on your script, you'll probably find it's easier to work locally (and then copy your script to Kaggle for sharing).

## Directory Structure

It helps to set up the same directory structure that we have running on Kaggle. (Then you don't have to change any paths when copying the script to Kaggle.) [This file](https://www.kaggle.com/c/predict-west-nile-virus/download/west_nile.zip) sets up the directory structure (including all of the competition data):

- `input`: this contains all of the data files for the competition
- `working`: on Kaggle, scripts run with this as the working directory. We recommend you do the same thing locally to avoid mixing output files with source files.
- `src`: Source scripts. We've provided some examples to get you started.

## Python and R Environments

We have Github repositories showing our [R](https://github.com/Kaggle/docker-r) and [Python](https://github.com/Kaggle/docker-python) environments are set up. We plan to make it very easy to work with the exact same environment locally, but at this point it may be easier to work with whatever environment you already have. (If you use Python or R packages locally that turn out to be missing in our online environment, we can probably add them for you.)

Do make sure you're using Python 3, though. 

[Conda](http://conda.pydata.org/docs/intro.html) is great for managing Python environments.

## RMarkdown

If `src/measurement_locations.Rmd` is the RMarkdown file you want to render as HTML, you can say:

`Rscript render_rmarkdown.R src/measurement_locations.Rmd`

Then open `working/output.html` to view the results!

## Command Line Execution

In your shell, you can navigate to the `working` directory, and run a script by saying:

`Rscript ../src/measurement_locations.R`

or

`python ../src/measurement_locations.py`

# R

We all love RStudio for interactive work. If you open a script in `src` in RStudio, your working directory will probably default to `src`. So we've included a line in the example that switches you to `working` at the top of the script.


# Python

While we don't support iPython Notebooks in Scripts at this point, we know many people like to work in notebooks interactively. We've included an example notebook. The comments indicate the couple small changes required for transitioning to a script.
