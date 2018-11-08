function(input, output) {

  ############### Render UI ################################
  
  
  output$choose_location <- renderUI({
    selectInput("locationid",span(icon("map"),"Location"),as.list(unique(data$location)))
  })
  
  output$choose_camera <- renderUI({
    selectInput("cameraid", span(icon("camera-retro"),"Camera"), as.list(unique(data$camera_id)))
  })
  
  
  
  ### These subsets will be used throughout the rest of the dashboard.
  selections <- reactiveValues()

  observe({

    locationid = NULL
    cameraid = NULL
    if (is.null (input$locationid) ){
      locationid = 'nordstrom.store5'
      cameraid   =  'Faceftpcam1.usecondstream'
    }else{
      locationid <- input$locationid
      cameraid <- input$cameraid
    }
    selections$cameras <- unique( data[data$location == locationid ,c('camera_id')] )
    selections$data <- data[data$location == locationid & data$camera_id == cameraid,]
    selections$gender.overall <- demograph.data[demograph.data$location == locationid & demograph.data$camera_id == cameraid,]

    # TODO remove outliers from selections.data

    # Face Count by day
    face.count <- selections$data %>% group_by(date) %>% summarise(Face_Count = sum(no_faces))
    #face.count$date <- as.character(face.count$date)
    selections$face.count <- face.count

    # Gender Overall Count
    # gender.overall <- selections$gender.overall[c('male_count','female_count')]
    # gender.overall <- gender.overall %>% replace(is.na(.), 0) %>% summarise_all(funs(sum))
    # gender.overall <- melt(gender.overall, id.vars = 'variable')
    # gender.overall[,2] <- NULL
    # names(gender.overall) <- c("Gender","Count")
    # selections$gender.overall <- gender.overall



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
    selections$tracker.data <- tracker.data[tracker.data$camera_id==input$cameraid,]

  })
  # 
  # 
  
  ################## Render Tables #########################
  
  output$personCountTable <- renderTable({
    selections$tracker.stats
  },bordered = TRUE)

  output$personSummaryTable <- renderTable({
    selections$tracker.summary
  }, bordered = TRUE)


  output$debugTable <- renderDataTable({
    selections$data[,c('windows','no_faces','timestamp','distance')]
  })


  output$distSummaryTable = renderTable({
    distance.table <- selections$distance.data %>% group_by(date) %>% summarise(Distance = mean(mean_distance, na.rm=TRUE))
    distance.table$date <- as.character(distance.table$date)
    distance.table <- distance.table[order(as.Date(distance.table$date, "%Y-%m-%d"), decreasing = TRUE),]
    names(distance.table) <- c("Date","Avg Distance (Feet)")
    distance.table <- distance.table
    distance.table}, bordered =TRUE
  )

  # ####################### Render Plots ############################
  # 
  ########### plot.set.1 ############################################
  output$impressionsPlot <- renderPlot({
    ggplot(selections$face.count, aes(x=factor(date), y=Face_Count)) +
      geom_col(color="darkorange",fill="darkorange2") +
      scale_color_brewer(palette="Dark2") + theme_minimal() +
      theme(plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) +
            ggtitle("Impressions") + ylab("Impression Count") + xlab("") + coord_flip()
  })
  # 
  output$distAvgPlot <- renderPlot({
    ggplot(selections$dist.avg, aes(x=factor(date), y=Distance)) +
      geom_col(color="goldenrod",fill="goldenrod3") +
      scale_color_brewer(palette="BrBG") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 90, hjust = 1),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) +
      ggtitle("Distance") + ylab("Average Distance (feet)") + xlab("")
  })

  output$viewTimeScatter <- renderPlot({
    p<-ggplot(selections$tracker.data, aes(x=factor(date), y=time_alive, color=factor(date))) +
          geom_jitter(position=position_jitter(0.2)) + theme_minimal() +
      theme(axis.text.x = element_text(angle = 90, hjust = 1),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),legend.position="none",panel.border = element_rect(colour = "lightblue", fill=NA, size=2)) +
      ggtitle("View Time") + xlab("Date") + ylab("View Time (seconds)")
    p
  })
  # 
  
  

  
  
  
  
  ############## plot.set.2 #########################################################
  # # TODO there's an error with the aesthetics in this plot
  
  output$groupingsPlot <- renderPlot({
    ggplot(selections$group.data, aes(x="", y=Size, fill=factor(no_faces))) +
      geom_bar(stat="identity",show.legend = TRUE) + theme_classic() +
      ggtitle("Imp. Group Size") + xlab("") + ylab("") + scale_fill_discrete(name = "Group Size") +
      theme(
        axis.text.x=element_blank(),axis.text.y=element_blank()
        ,plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5)
        ,axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18)
        ,panel.border = element_rect(colour = "lightblue", fill=NA, size=2)
      )
  })

  # TODO error
  output$distanceDensity <- renderPlot({
    #### Distance Plot data calculation
    plot.data.1 <- selections$distance.data %>%
      group_by(ceiling(mean_distance)) %>%
      summarise(count = n())
    plot.final <- read.table(text = "",col.names = c("Feet", "Points"))

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
      xlab("Screen") + ggtitle("Distance")

    p

  })

  output$viewTimeDensity <- renderPlot({
    ggplot(selections$tracker.data, aes(x=time_alive)) + geom_histogram(color="olivedrab",fill="olivedrab2") +
      theme_minimal() + xlab("View time (seconds)") + ylab("Number of Unique Persons") +
      theme(panel.border = element_rect(colour = "lightblue", fill=NA, size=2),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18)) +
      ggtitle("View Time")
  })
  
  #################################################################################
  
  # 
  # output$genderPlot <- renderPlot({
  #   ggplot(selections$gender.overall, aes(x="", y=Count, fill=factor(Gender))) +
  #     geom_bar(stat="identity",width=1,show.legend = TRUE) + theme_classic() +
  #     ggtitle("Gender Split") + xlab("") + ylab("") + scale_fill_discrete(name = "Gender") +
  #     theme(axis.text.x=element_blank(),axis.text.y=element_blank(),plot.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=24, hjust = 0.5),axis.title = element_text(family = "Trebuchet MS", color="#666666", face="bold", size=18),panel.border = element_rect(colour = "lightblue", fill=NA, size=2))
  # 
  # })

}