
# Publish =================================================
library(rsconnect)

rsconnect::deployApp(appName="Signage", account="jci-deb",forceUpdate = TRUE)


# Packages ================================================

install.packages("shinydashboard")
install.packages("DT")
install.packages("httr")
install.packages("dplyr")
install.packages("anytime")

