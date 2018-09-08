# Predicting Movie Opening Weekend Gross Using Linear Regression

## Notebook organization
All of the working files are in jupyter notebooks. If you are only interested in web scraping and data collection, you may find them in 01 - Luther notebook. These notebooks are sequenctial.

#### 01 - Luther (Web Scraping & Data Collection)
Code for scraping data from BoxOfficeMojo (has 3 different parts), Google trends data using Pytrends API, Youtube statistics data using Google API, critic ratings using OMDB API, and converting unemployment csv file into a pandas dataframe.

#### 02 - Luther (Data Cleaning & Merging)
This notebook begins with loading all the dataframes(pickle) that were saved from part 01, merging them together, and cleaning the data.

#### 03 - Luther (Linear Regression)
The final notebook loads up the merged dataframe obtained from part 2, splits the data into training and test set, run crossvalidation to choose hyperparameters, and finally evaluate model performance on the test set.

#### 01-03 "Test" notebooks
These notebooks are for running the code for Avengers (2018) to see how well my model performed on predicting the opening gross for this particular movie.

### Data folder
The data (some in csv, but mostly in pkl form) can be found in this folder.

### Details of this project can be found in my [Medium blogpost](https://medium.com/@pmin91/how-i-tried-to-predicted-the-opening-gross-for-the-avengers-infinity-war-using-data-science-3fd2beb9512d).