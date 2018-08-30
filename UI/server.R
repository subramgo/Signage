function(input, output) {

  ### These subsets will be used throughout the rest of the dashboard.
  selections <- reactiveValues()
  observe({
    selections$cameras <- unique( data[data$location == input$locationid,c('camera_id')] )
    
    selections$data <- data[data$location == input$locationid && data$camera_id == input$cameraid,]
    
    # Distance data - mean distance by date
    distance.data <- selections$data[c('date','distance')]
    distance.data$mean_distance <- mapply(mean, distance.data$distance)
    distance.data$distance <- NULL
    selections$distance.data <- na.omit(distance.data)
    
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
  
  output$choose_location <- renderUI({
    selectInput("locationid",span(icon("map"),"Location"),as.list(unique(data$location)))
  })
  
  output$choose_camera <- renderUI({
    selectInput("cameraid", span(icon("camera-retro"),"Camera"), as.list(selections$cameras))
  })
  
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
      theme(axis.text.x=element_blank(),plot.title = element_text(hjust = 0.5),legend.position="none") + 
      xlab("Screen") + ggtitle("Distance from Pedestal")
    
    p
    
  })
  
  output$personCountTable <- renderTable({
    selections$tracker.stats
  })
  
  output$personSummaryTable <- renderTable(({
    selections$tracker.summary
  }))
  
  output$distSummaryTable = renderTable({
    distance.table <- selections$distance.data %>% group_by(date) %>% summarise(Distance = mean(mean_distance, na.rm=TRUE))
    distance.table$date <- as.character(distance.table$date)
    distance.table <- distance.table[order(as.Date(distance.table$date, "%Y-%m-%d"), decreasing = TRUE),]
    names(distance.table) <- c("Date","Avg Distance (Feet)")
    distance.table <- distance.table
    distance.table}, bordered ='TRUE',spacing = 'xs',striped='TRUE'
  )
  
  output$viewTimePlot <- renderPlot({
    ggplot(tracker.data, aes(x=time_alive)) + geom_histogram() + 
      theme_minimal() + xlab("View time (seconds)") + ylab("Number of Unique Persons")
  })

}