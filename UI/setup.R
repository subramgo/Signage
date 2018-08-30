
# Publish =================================================
library(rsconnect)

rsconnect::deployApp(appName="Signage", account="jci-deb",forceUpdate = TRUE)

