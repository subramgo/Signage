function(input, output) {

  
  ############### Render UI ################################
  
  
  output$choose_location <- renderUI({
    selectInput("locationid",span(icon("map"),"Location"),as.list(unique(data$location)))
  })
  
  output$choose_camera <- renderUI({
    selectInput("cameraid", span(icon("camera-retro"),"Camera"), as.list(selections$cameras))
  })
  
  
  
  ### These subsets will be used throughout the rest of the dashboard.
  selections <- reactiveValues()
  observe({
    
    locationid = NULL
    cameraid = NULL
    if (is.null (input$locationid) ){
      locationid = 'nordstrom'
      cameraid   =  'display2-camera'
    }else{
      locationid <- input$locationid
      cameraid <- input$cameraid
    }
    selections$cameras <- unique( data[data$location == locationid ,c('camera_id')] )
    selections$data <- data[data$location == locationid & data$camera_id == cameraid,]
    
    # Face Count by day
    face.count <- selections$data %>% group_by(date) %>% summarise(Face_Count = sum(no_faces))
    #face.count$date <- as.character(face.count$date)
    selections$face.count <- face.count
    

    # Distance data - mean distance by date -
    distance.data <- selections$data[c('date','distance')]
    distance.data$mean_distance <- mapply(mean, distance.data$distance)
    distance.data$distance <- NULL
    selections$distance.data <- na.omit(distance.data)

    # Average distance by day
    dist.avg <- selections$distance.data %>% group_by(date) %>% summarise(Distance = mean(mean_distance))
    selections$dist.avg <- dist.avg
    
    
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
    ggplot(tracker.data, aes(x=time_alive)) + geom_histogram(color="olivedrab",fill="olivedrab2") + 
      theme_minimal() + xlab("View time (seconds)") + ylab("Number of Unique Persons") +
      theme(panel.border = element_rect(colour = "lightblue", fill=NA, size=2),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18)) +
      ggtitle("Persons")
  })

  output$faceCountPlot <- renderPlot({
    ggplot(selections$face.count, aes(x=factor(date), y=Face_Count)) + 
      geom_col(color="darkorange",fill="darkorange2") +
      scale_color_brewer(palette="Dark2") + theme_minimal() +
      theme(plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) + 
            ggtitle("Impressions") + ylab("Impression Count") + xlab("") + coord_flip() 
  })

  output$distAvgPlot <- renderPlot({
    ggplot(selections$dist.avg, aes(x=factor(date), y=Distance)) + 
      geom_col(color="goldenrod",fill="goldenrod3") +
      scale_color_brewer(palette="Light") + 
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 90, hjust = 1),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) + 
      ggtitle("Distance") + ylab("Average Distance") + xlab("")
  })
  
  output$timeAlivePlot <- renderPlot({
    
    p<-ggplot(tracker.data, aes(x=factor(date), y=time_alive, color=factor(date))) + 
          geom_jitter(position=position_jitter(0.2)) + theme_minimal() +
      theme(axis.text.x = element_text(angle = 90, hjust = 1),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) +   
      ggtitle("Time Alive") + xlab("Date") + ylab("Time Alive (seconds")
    
    p
    
      })
    
  output$viewGroupPlot <- renderPlot({
    ggplot(selections$group.data, aes(x="", y=Size, fill=factor(no_faces))) + 
      geom_bar(stat="identity",width=1,show.legend = TRUE) + theme_classic() +
      ggtitle("Groups Split") + xlab("") + ylab("") + scale_fill_discrete(name = "People Groups") +
      theme(axis.text.x=element_blank(),axis.text.y=element_blank(),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),panel.border = element_rect(colour = "lightblue", fill=NA, size=2))
    
  })
  
}