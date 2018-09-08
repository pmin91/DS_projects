# This is an example of developing a script locally with the West Nile Virus data to share on Kaggle
# Once you have a script you're ready to share, paste your code into a new script at:
#  https://www.kaggle.com/c/predict-west-nile-virus/scripts/new

# For working locally, you want to be in west_nile_scripts/working. 
# This command will move you to there, if you're in west_nile_scripts/src (where this file is).
setwd("../working") # Not necessary for scripts running on Kaggle

library(ggmap) # If you haven't yet, do this: install.packages("ggmap")  

data_dir <- "../input"
wnv <- read.csv(file.path(data_dir, "train.csv"))

# Ggmap is used to download and plot map images. Scripts don't have access to the network, so 
# the map data is included as an input file. 
# I downloaded it with the command: mapdata <- get_openstreetmap(bbox = c(-88.0, 41.6, -87.5, 42.1), color="bw", scale = round(606250/4))
mapdata <- readRDS(file.path(data_dir, "mapdata_copyright_openstreetmap_contributors.rds"))

# Shows where there are measurement points
ggmap(mapdata) + geom_point(aes(x=Longitude, y=Latitude), data=wnv)