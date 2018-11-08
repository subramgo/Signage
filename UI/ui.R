dbHeader <- dashboardHeader( title = span( icon("desktop"), app_name, icon("fire") ) 
                             , tags$li(
                               a(href = company_uri
                             , img(src = 'jci_logo_wb.png', title = "Johnson Controls", height = "50px")
                             , style = "padding-top:3px; padding-bottom:3px;"), class = "dropdown"
                             )
)

############# Location selector ##############
loc.selector <- fluidRow(
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

############## plot sets #####################
plot.set.1 <- fluidRow(
  box(width=4, plotOutput("impressionsPlot"))
  , box(width=4, plotOutput("distAvgPlot"))
  , box(width=4, plotOutput("viewTimeScatter"))
)


plot.set.2 <- fluidRow(
    box(width=4, plotOutput("groupingsPlot"))
  , box(width=4, plotOutput("distanceDensity"))
  , box(width=4, plotOutput("viewTimeDensity"))
)


############# tables sets ################################
tables.set.1 <- fluidRow(
   box(width=4,tableOutput("personCountTable"))
  ,box(width=4, tableOutput("personSummaryTable"))
  ,box(width=4, tableOutput("distSummaryTable"))
)

#############################################################

debug.window <- fluidRow(
  box(width=12, dataTableOutput("debugTable"))
)


dashboardPage( 
    title = app_name
  , dbHeader
  , dashboardSidebar(sidebarMenu(id = 'sidebar') , disable = TRUE )
  , dashboardBody(
      title = "Dashboard"
    , loc.selector
    , tabBox(
        width = 12
        ,tabPanel(
           title ="Mission Control"
          ,plot.set.1
          ,plot.set.2
          ,tables.set.1
        )
        ,tabPanel(
          title="Debug Window",
          debug.window
        )
      )
    )
  )


