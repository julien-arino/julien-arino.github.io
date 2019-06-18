library(lubridate)
library(OpenStreetMap)

setwd("~/Documents/DATA/WinnipegTransit")

YYYY = 2019
MM = 07
DD = 04
# Query is for a "day" worth of transport, from start of movement 
# around 5:00 to end of movement around 2:00 next day. 
# So set date and date of next day.
Q_date <- lubridate::ymd(sprintf("%s-%s-%s",YYYY,MM,DD))
Q_date_p1 <- lubridate::ymd(Q_date)+1

# Load the calendar file to find code for chosen day.
calendar <- read.csv("staticSchedule/calendar.txt", 
                     stringsAsFactors = FALSE)
# Find which entries in calendar have the chosen date
calendar$start_date = lubridate::ymd(calendar$start_date)
calendar$end_date = lubridate::ymd(calendar$end_date)
idx = intersect(which(calendar$start_date <= Q_date),
                which(calendar$end_date >= Q_date_p1))
calendar = calendar[idx,]
# Which day of the week is start of service (Q_date)
# lubridate starts Sunday by default (so 1=Sunday)
day_week = lubridate::wday(Q_date)
if (day_week %in% seq(2,6))
  # Weekday service
  idx = which(calendar$monday == 1)
if (day_week == 7)
  # Saturday service
  idx = which(calendar$saturday == 1)
if (day_week == 1)
  # Sunday service
  idx = which(calendar$sunday == 1)
calendar = calendar[idx,]

# Load other required files
stop_times <- read.csv("staticSchedule/stop_times.txt", 
                       stringsAsFactors = FALSE)
stops <- read.csv("staticSchedule/stops.txt", 
                  stringsAsFactors = FALSE)
trips <- read.csv("staticSchedule/trips.txt", 
                  stringsAsFactors = FALSE)

# Make one giant data frame and progressively prune
monster_frame = merge(x = stop_times,
                      y = stops,
                      by.x = "stop_id",
                      by.y = "stop_id")
monster_frame = merge(x = monster_frame,
                      y = trips,
                      by.x = "trip_id",
                      by.y = "trip_id")
idx = which(monster_frame$service_id %in% calendar$service_id)
monster_frame = monster_frame[idx,]
monster_frame = monster_frame[order(monster_frame$arrival_time),]
monster_frame$HH = as.numeric(substr(monster_frame$arrival_time,1,2))
monster_frame$MM = as.numeric(substr(monster_frame$arrival_time,4,5))
monster_frame = monster_frame[,c("arrival_time","HH","MM",
                                 "stop_lat",
                                 "stop_lon")]
# Add lat/lon in Mercator format
monster_frame$x = OpenStreetMap::projectMercator(monster_frame$stop_lat,
                                                 monster_frame$stop_lon)[,1]
monster_frame$y = OpenStreetMap::projectMercator(monster_frame$stop_lat,
                                                 monster_frame$stop_lon)[,2]

# Download map for plotting
Winnipeg_upperLeft = c(max(monster_frame$stop_lat)+0.01, 
                       min(monster_frame$stop_lon)-0.01)
Winnipeg_lowerRight = c(min(monster_frame$stop_lat)-0.01, 
                        max(monster_frame$stop_lon)+0.01)
Winnipeg_map <- OpenStreetMap::openmap(upperLeft = Winnipeg_upperLeft,
                                       lowerRight = Winnipeg_lowerRight,
                                       type = "osm-public-transport")

# Plot minute per minute bus stop activity.
# Because stop activity is sorted, we can just make our way down
# the vector
curr_MM = -1
for (i in 1:length(monster_frame$arrival_time)) {
  if (monster_frame$MM[i] != curr_MM) {
    if (i>1) {
      dev.off()
    }
    if (monster_frame$HH[i] <= 23) {
      date_time = sprintf("%s %02d:%02d",
                          Q_date,
                          monster_frame$HH[i],
                          monster_frame$MM[i])
      plotName = sprintf("tmpFig/%s_%02d:%02d.png",
                         Q_date,
                         monster_frame$HH[i],
                         monster_frame$MM[i])
    }
    if (monster_frame$HH[i] > 23) {
      date_time = sprintf("%s %02d:%02d",
                          Q_date_p1,
                          (monster_frame$HH[i]-24),
                          monster_frame$MM[i])
      plotName = sprintf("tmpFig/%s_%02d:%02d.png",
                         Q_date_p1,
                         monster_frame$HH[i],
                         monster_frame$MM[i])
    }
    # Just to know where we are currently as it takes a while
    print(date_time)
    # Set up the plot
    png(plotName)
    plot(Winnipeg_map)
    title(main = sprintf("%s",date_time))
    # Update current time/date
    curr_MM = monster_frame$MM[i]
  }
  points(x = round(as.numeric(as.character(monster_frame$x[i]))),
         y = round(as.numeric(as.character(monster_frame$y[i]))),
         pch = 19)
}
dev.off()

my_command <- 'convert tmpFig/*.png -delay 3 -loop 0 Winnipeg_buses.gif'
system(my_command)
