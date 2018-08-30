
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(DT)
library(shinythemes)

shinyUI(
  navbarPage(theme = shinytheme("sandstone"),
      "Signage Data Analysis",
      tabPanel("Home",
          sidebarPanel(
            h3("Camera and Location"),
            
            uiOutput("choose_location"),
            uiOutput("choose_camera")
          ),
            # Show a plot of the generated distribution
            mainPanel(
              tabsetPanel(type = "tabs",
                tabPanel("Distance",
                    fluidRow(column(8, h3("Statistics on how far the viewers are standing from the pedestal"))),
                    fluidRow(
                    column(8,
                    
                    plotOutput("densityPlot")
                    ),
                    column(4,
                    tableOutput("distSummaryTable")
                    )
                    )
                    
                ),
                tabPanel("Unique Views",
                    fluidRow(column(8, h3("How much time people spend watching the display"))),
                    fluidRow(column(4, plotOutput("viewTimePlot")),
                             column(8,tableOutput("personCountTable"))
                             ),     
                    fluidRow(column(4,tableOutput(("personSummaryTable")) ))
                )
              
            ) # End tab Panel
          ) # End main Panel
        )
    )# End Navbar Page
)# End ShinyUI