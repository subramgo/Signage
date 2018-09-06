library(shiny)
library(shinydashboard)

library(DT)
library(ggplot2)

library(httr)
library(jsonlite)
library(dplyr)
library(anytime)


source('config.R')
##################### Pull data from web service #####################

result <- GET(url_)
data <- jsonlite::fromJSON(content(result, as="text"),  flatten=TRUE)
data['date'] <- anydate(data$date_created)
data['timestamp'] <- anytime(data$date_created)


result <- GET(url.object.track)
tracker.data <- jsonlite::fromJSON(content(result, as="text"),  flatten=TRUE)
tracker.data['date'] <- anydate(tracker.data$date_created)
tracker.data$idx <- as.numeric(rownames(tracker.data))

  
##########################################################################

getAMPM <- function(x){
  a <- as.numeric(format(strptime(x,"%Y-%m-%d %H:%M:%S"),'%H'))
  split.afternoon <- 12
  split.evening <- 17
  greeting <- "Morning"
  if (a >= split.afternoon && a <= split.evening){
    greeting <- "Afternnon"
  }else if (a > split.evening){
    greeting <- "Evening"
  }
  return(greeting)
}

data$greeting <- sapply(data$timestamp, getAMPM)

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


