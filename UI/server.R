function(input, output) {

  ### These subsets will be used throughout the rest of the dashboard.
  selections <- reactiveValues()
  observe({
    selections$cameras <- unique( data[data$location == input$locationid,c('camera_id')] )
    
    selections$data <- data[data$location == input$locationid && data$camera_id == input$cameraid,]
    
    # Face Count by day
    face.count <- selections$data %>% group_by(date) %>% summarise(Face_Count = sum(no_faces))
    #face.count$date <- as.character(face.count$date)
    selections$face.count <- face.count
    
    # Average distance by day
    dist.avg <- selections$data %>% group_by(date) %>% summarise(Distance = mean(distance))
    selections$dist.avg <- dist.avg
    
    
    # Distance data - mean distance by date -
    distance.data <- selections$data[c('date','distance')]
    distance.data$mean_distance <- mapply(mean, distance.data$distance)
    distance.data$distance <- NULL
    selections$distance.data <- na.omit(distance.data)
    
    
    # Group size
    group.data <- selections$data %>% group_by(no_faces) %>% summarise(Size = n())
    selections$group.data <- group.data
    
    # Tracking summaries and stats
    tracker.stats <- tracker.data[tracker.data$camera_id==input$cameraid,] %>%
        group_by(date,time_alive) %>%
        summarise(Person_Count = n())
    tracker.stats$date <- as.character(tracker.stats$date)
    tracker.summary <- tracker.stats %>%
      group_by(date) %>%
      summarise('Unique Person' = sum(Person_Count), 'Avg View Time (in seconds)' = mean(time_alive))
    names(tracker.stats) <- c("Date","View Time ( in seconds)", "Number of People" )
    
    selections$tracker.stats <- tracker.stats
    selections$tracker.summary <- tracker.summary
  })
  
  
  ############### Render UI ################################
  
  
  output$choose_location <- renderUI({
    selectInput("locationid",span(icon("map"),"Location"),as.list(unique(data$location)))
  })
  
  output$choose_camera <- renderUI({
    selectInput("cameraid", span(icon("camera-retro"),"Camera"), as.list(selections$cameras))
  })
  
  
  ################## Render Tables #########################
  
  output$personCountTable <- renderTable({
    selections$tracker.stats
  },bordered = TRUE)
  
  output$personSummaryTable <- renderTable(({
    selections$tracker.summary
  }), bordered = TRUE)
  
  
  
  
  
  output$distSummaryTable = renderTable({
    distance.table <- selections$distance.data %>% group_by(date) %>% summarise(Distance = mean(mean_distance, na.rm=TRUE))
    distance.table$date <- as.character(distance.table$date)
    distance.table <- distance.table[order(as.Date(distance.table$date, "%Y-%m-%d"), decreasing = TRUE),]
    names(distance.table) <- c("Date","Avg Distance (Feet)")
    distance.table <- distance.table
    distance.table}, bordered =TRUE
  )
  
  ####################### Render Plots ############################

  output$densityPlot <- renderPlot({
    #### Distance Plot data calculation
    plot.data.1 <- selections$distance.data %>%
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
    
    
    p <- ggplot(plot.final, aes(x=Points, y=Feet, color = Feet, shape = Feet)) + 
      geom_jitter(height=0.2) +
      xlim(-0.25,1.25)
    
    p <- p + scale_color_brewer(palette="Dark2") + theme_minimal() + 
      theme(axis.text.x=element_blank(), plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) + 
      xlab("Screen") + ggtitle("Distance from Pedestal")
    
    p
    
  })
  
  
  
    output$viewTimePlot <- renderPlot({
    ggplot(tracker.data, aes(x=time_alive)) + geom_histogram(color="darkblue",fill="lightblue") + 
      theme_minimal() + xlab("View time (seconds)") + ylab("Number of Unique Persons") +
      theme(panel.border = element_rect(colour = "lightblue", fill=NA, size=2),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18)) +
      ggtitle("Persons")
  })

  output$faceCountPlot <- renderPlot({
    ggplot(selections$face.count, aes(x=date, y=Face_Count)) + 
      geom_col(color="darkblue",fill="lightblue") +
      scale_color_brewer(palette="Dark2") + theme_minimal() +
      theme(plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) + 
            ggtitle("Impressions") + ylab("Impression Count") + xlab("") + coord_flip()
  })

  output$distAvgPlot <- renderPlot({
    ggplot(selections$dist.avg, aes(x=date, y=Distance)) + 
      geom_col(color="darkblue",fill="lightblue") +
      scale_color_brewer(palette="Dark2") + theme_minimal() +
      theme(plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) + 
      ggtitle("Distance") + ylab("Average Distance") + xlab("")
  })
  
  output$timeAlivePlot <- renderPlot({
    ggplot(tracker.data, aes(x=idx, y=time_alive, fill=date)) + 
      geom_area(color="darkblue",fill="lightblue", show.legend = TRUE) + theme_minimal() + expand_limits(y=0) +
      ggtitle("Time Alive") + xlab("") +
      theme(legend.position = c(0, 1),legend.justification = c(0, 1),axis.text.x=element_blank(),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),panel.border = element_rect(colour = "lightblue", fill=NA, size=2))
  })
    
  output$viewGroupPlot <- renderPlot({
    ggplot(selections$group.data, aes(x="", y=Size, fill=no_faces)) + 
      geom_bar(stat="identity",width=1,color="darkblue",fill="lightblue",show.legend = TRUE) + theme_minimal() +
      ggtitle("Groups Split") + xlab("") + ylab("") +
      theme(legend.position = c(0, 1),legend.justification = c(0, 1),legend.box = "horizontal",axis.text.x=element_blank(),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),panel.border = element_rect(colour = "lightblue", fill=NA, size=2))
    
  })
  
}