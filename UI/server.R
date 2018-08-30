
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(ggplot2)
library(shinythemes)



shinyServer(function(input, output) {

output$personCountTable <- renderTable({
  tracker.stats
})

output$personSummaryTable <- renderTable(({
  tracker.summary
}))
  
  output$choose_location <- renderUI({
    selectInput("locationid","Location",as.list(unique(data$location)))
  })
  
  output$choose_camera <- renderUI({
    selectInput("cameraid", "Camera", as.list(unique(data$camera_id)))
  })

output$distSummaryTable = renderTable({
  distance.table}, bordered ='TRUE',spacing = 'xs',striped='TRUE'
)

output$viewTimePlot <- renderPlot({
  ggplot(tracker.data, aes(x=time_alive)) + geom_histogram() + 
    theme_minimal() + xlab("View time (seconds)") + ylab("Number of Unique Persons")
})

output$densityPlot <- renderPlot({
  p <- ggplot(plot.final, aes(x=Points, y=Feet, color = Feet, shape = Feet)) + 
    geom_jitter(height=0.2) +
    xlim(-0.5,1.5)
  
  p <- p + scale_color_brewer(palette="Dark2") + theme_minimal() + 
    theme(axis.text.x=element_blank(),plot.title = element_text(hjust = 0.5),legend.position="none") + 
    xlab("Screen") + ggtitle("Distance from Pedestal")
   
  p
  
  })

})
