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
        width = 12
        , tabPanel(
          title = "Distance"
          , h3("Statistics on how far viewers are from the pedestal")
          , fluidRow(
              box(width=6,plotOutput("densityPlot"))
            , box(width=6,tableOutput("distSummaryTable"))
          )
        )
        , tabPanel(
          title = "Unique Views"
          , h2("Unique Views")
          , fluidRow(column(8, h3("How much time people spend watching the display")))
          , fluidRow(column(4, plotOutput("viewTimePlot")),
                     column(8,tableOutput("personCountTable")))
          , fluidRow(column(4,tableOutput(("personSummaryTable")) ))
          )
        )
      )
    )
)

