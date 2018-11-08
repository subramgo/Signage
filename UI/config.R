app_name <- "Signage Data Analysis"
company_uri <- 'http://www.johnsoncontrols.com/buildings/building-management/data-enabled-business/digital-midmarket-platform'

base_url = "http://0.0.0.0:5000"
#http://178.128.68.231:5000
url_ = paste(base_url,"api/v1/signage/",sep="/")

url.object.track = paste(base_url, "api/v1/signage/object_track",sep="/")
url.demographics = paste(base_url, "api/v2/signage/demographics",sep="/")
