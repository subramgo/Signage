library(shiny)
library(shinydashboard)

library(DT)
library(ggplot2)

library(httr)
library(jsonlite)
library(dplyr)
library(anytime)
library(reshape2)

source('config.R')
##################### Pull data from web service #####################

result <- GET(url_,authenticate("united", "irkbin"))
data <- jsonlite::fromJSON(content(result, as="text"),  flatten=TRUE)
data['date'] <- anydate(data$date_created)
data['timestamp'] <- anytime(data$date_created)

#saveRDS(data,file="data.rds")
#data <- readRDS("data.rds")

result <- GET(url.object.track,authenticate("united", "irkbin"))
tracker.data <- jsonlite::fromJSON(content(result, as="text"),  flatten=TRUE)
tracker.data['date'] <- anydate(tracker.data$date_created)
tracker.data$idx <- as.numeric(rownames(tracker.data))
tracker.data <- tracker.data[tracker.data$time_alive <= 240, ]

#saveRDS(tracker.data,file="tracker.rds")
#tracker.data <- readRDS("tracker.rds")


#result <- GET(url.demographics, authenticate("united","irkbin"))
#demograph.data <- jsonlite::fromJSON(content(result, as="text"),  flatten=TRUE)
#demograph.data['date'] <- anydate(demograph.data$date_created)
#demograph.data$idx <- as.numeric(rownames(demograph.data))


#saveRDS(demograph.data, file="demograph.rds")
#demographics.data <- readRDS("demograph.rds")

#data <- data[data$location == 'nordstrom.store5' & data$camera_id == 'Faceftpcam1.usecondstream',]
#tracker.data <- tracker.data[tracker.data$camera_id == 'Faceftpcam1.usecondstream',]
#demograph.data <- demograph.data[demograph.data$camera_id == 'Faceftpcam1.usecondstream',]




###################### Distance from Pedestal Calcs ######################
getDistance <- function(windows){
  x_min = windows[1]
  y_min = windows[2]
  x_max = windows[3]
  y_max = windows[4]
  area <- (x_max - x_min) * (y_max - y_min)
  resol_A <- 160641.0
  resol_B <- 28800.0
  distance <- (resol_A - area) / (1.0 * resol_B)
  return(distance)
}

find_distance <- function(no_faces, windows){
  windows.num <- as.integer(unlist(strsplit(windows, ",")))
  start_index = 1
  end_index = 4
  distances <- c()
  for (nfaces in 1:no_faces){
    distance = getDistance(windows.num[start_index:end_index])
    start_index = end_index + 1
    end_index = end_index + 4
    distances[nfaces] = distance
    
  } 
  return(distances)
}

data$distance <- mapply(find_distance, data$no_faces, data$windows)

data <- data[data$windows != '',]
########################################################################


