dbHeader <- dashboardHeader( title = span( icon("desktop"), app_name, icon("fire") ) 
                             , tags$li(a(href = company_uri,
                                         img(src = 'jci_logo_wb.png',
                                             title = "Johnson Controls", height = "50px"),
                                         style = "padding-top:3px; padding-bottom:3px;"),
                                       class = "dropdown")
)

dashboardPage( 
    title = app_name
  , dbHeader
  , dashboardSidebar(sidebarMenu(id = 'sidebar') , disable = TRUE )
  , dashboardBody(
    title = "Dashboard"
    , fluidRow(
        box(
            status = "primary"
          , solidHeader = FALSE
          , collapsible = FALSE
          , uiOutput("choose_location")
          , width=6
        )
      , box(
            status = "primary"
          , solidHeader = FALSE
          , collapsible = FALSE
          , uiOutput("choose_camera")
          , width=6
          )
      )
    , fluidRow(
        tabBox(
        width = 12,
        tabPanel(
          title ="Mission Control"
          ,fluidRow(
                    column(3, plotOutput("faceCountPlot"))
                    ,column(3, plotOutput("distAvgPlot"))
                    ,column(3, plotOutput("timeAlivePlot"))
                    )

          ,fluidRow(
            column(3, plotOutput("densityPlot")),
            column(3, plotOutput("viewTimePlot")),
            column(3, plotOutput("viewGroupPlot"))
          ))
        
              
          ,fluidRow(
             column(3,tableOutput("personCountTable"))
            ,column(3, tableOutput(("personSummaryTable"))
            ,column(3, tableOutput("distSummaryTable"))
                    
          )
          
          
          
        )
        
        )
      )
    )
)

