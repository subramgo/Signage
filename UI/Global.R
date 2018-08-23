library(httr)
library(jsonlite)
library(dplyr)
library(anytime)


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

#########################  Object Tracker Stas ############################

tracker.stats <- tracker.data %>%
                  group_by(date,time_alive) %>%
                  summarise(Person_Count = n())


tracker.stats$date <- as.character(tracker.stats$date)

tracker.summary <- tracker.stats %>%
                    group_by(date) %>%
                    summarise('Unique Person' = sum(Person_Count), 'Avg View Time (in seconds)' = mean(time_alive))

names(tracker.stats) <- c("Date","View Time ( in seconds)", "Number of People" )
  
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
distance.data <- data[c('date','distance')]
distance.data$mean_distance <- mapply(mean, distance.data$distance)
distance.data$distance <- NULL
distance.data <- na.omit(distance.data)

# Distance table - mean distance by date
distance.table <- distance.data %>%
                  group_by(date) %>%
                  summarise(Distance = mean(mean_distance, na.rm=TRUE))
distance.table$date <- as.character(distance.table$date)
names(distance.table) <- c("Date","Avg Distance (Feet)")


#### Distance Plot data calculation
plot.data.1 <- distance.data %>%
                group_by(ceiling(mean_distance)) %>%
                summarise(count = n())
plot.final <- read.table(text = "",
                 col.names = c("Feet", "Points"))

for (row in 1:nrow(plot.data.1)){
  no.points <- as.numeric(plot.data.1[row, 'count'])
  feet      <- as.numeric(plot.data.1[row,'ceiling(mean_distance)'])
  

  df.inter <- data.frame(Feet = rep(feet, no.points), 
                         Points = sample(1:9, no.points, replace=TRUE)/10)

  plot.final <- rbind(plot.final, df.inter)
  
  
  
  
}

plot.final$Feet <- as.factor(plot.final$Feet)

########################################################################


