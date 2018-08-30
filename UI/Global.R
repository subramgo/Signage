library(shiny)
library(shinydashboard)

library(DT)
library(ggplot2)

library(httr)
library(jsonlite)
library(dplyr)
library(anytime)

app_name <- "Signage Data Analysis"
company_uri <- 'http://www.johnsoncontrols.com/buildings/building-management/data-enabled-business/digital-midmarket-platform'


##################### Pull data from web service #####################

url = "http://178.128.68.231:5000/api/v1/signage/"
result <- GET(url)
data <- jsonlite::fromJSON(content(result, as="text"),  flatten=TRUE)
data['date'] <- anydate(data$date_created)
data['timestamp'] <- anytime(data$date_created)


url = "http://178.128.68.231:5000/api/v1/signage/object_track"
result <- GET(url)
tracker.data <- jsonlite::fromJSON(content(result, as="text"),  flatten=TRUE)
tracker.data['date'] <- anydate(tracker.data$date_created)

  
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


########################################################################


