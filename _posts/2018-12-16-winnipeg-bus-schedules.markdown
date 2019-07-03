---
layout: post
title:  "Buses or ants? (R,data,mapping)"
description: "R code for plotting the activity of bus stops during a typical day in Winnipeg, using data downloaded from Winnipeg Transit. Shows how to make movies from the results using convert (ImageMagick) and animation (R library)."
date:   2018-12-16 00:39:22 -0600
categories: winnipeg
---
The most recent version of the code used in this page (which might be a little different from the one here) can be found [here](https://raw.githubusercontent.com/julien-arino/R-code/master/plotWpgStopSchedules_v1.R).


The city of Winnipeg has some interesting data available online as part of its open data initiative. The main entry point into that data is this [page](https://data.winnipeg.ca/ "Winnipeg Open Data portal").

One city service that contributes to this system is [Winnipeg Transit](https://winnipegtransit.com/en). They have several types of data. In a later entry, I will discuss the use of online queries; here, I use some static data that is available [here](http://gtfs.winnipegtransit.com/google_transit.zip). A description of the different files in the archive can be found [here](https://developers.google.com/transit/gtfs/reference/?csw=1).

As a regular bus user, public transit afficionado and someone interested in population movement, I was curious to use this data to study some ideas about population movement. The first step was to do a simple, somewhat fun representation of the information.

We will use three libraries: `lubridate`, which helps with date manipulation, `OpenStreetMap` for getting maps and converting coordinates and `animation`, as a way to create a movie. So make sure these are installed. You will also need the program `convert`, part of the ImageMagick suite. Installing the latter under Linux is easy; for Windows users, the situation is a bit more tricky, although you may want to consider the Linux subsystem. More on that later.

To keep things easy, let us change the directory to the one where the code lies and below which both the data and the figures directories will be located.
I am assuming that you downloaded the file from the link above and unzipped it in a subdirectory called `staticSchedule`. If generating a gif image, you will also need to create a subdirectory called `tmpFig`.

{% highlight r %}
setwd("~/Documents/DATA/WinnipegTransit")
{% endhighlight %}

We set the day of the query (updated recently). Because we want one "day" worth of transport, from start of movement
around 5:00 to end of movement around 2:00 next day, it will be useful to have the next day as well.

{% highlight r %}
YYYY = 2019
MM = 07
DD = 04
Q_date = lubridate::ymd(sprintf("%s-%s-%s",YYYY,MM,DD))
Q_date_p1 = lubridate::ymd(Q_date)+1
{% endhighlight %}

We now load and process `calendar.txt`, one of the components of the static schedule. This is a short file, giving the code of the type of operation (weekday, Saturday, Sunday), which is then used in the main stop schedule to single out the stop schedule for that type of operation. Note that when determining day of the week, `lubridate` starts with 1 on Sundays.

{% highlight r %}
calendar <- read.csv("staticSchedule/calendar.txt",
                     stringsAsFactors = FALSE)
calendar$start_date = lubridate::ymd(calendar$start_date)
calendar$end_date = lubridate::ymd(calendar$end_date)
idx = intersect(which(calendar$start_date <= Q_date),
                which(calendar$end_date >= Q_date_p1))
calendar = calendar[idx,]
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
{% endhighlight %}

At this point, `calendar` should be reduced to a single line. We now load the remaining files that are needed for the plot. (Note that during Fall and Winter terms for universities, not all weekdays are the same, so the tests above should actually differentiate between Monday, Wednesday, Friday on the one hand and Tuesday, Thursday on the other. This was written when school was not in session..)

{% highlight r %}
stop_times <- read.csv("staticSchedule/stop_times.txt",
                       stringsAsFactors = FALSE)
stops <- read.csv("staticSchedule/stops.txt",
                  stringsAsFactors = FALSE)
trips <- read.csv("staticSchedule/trips.txt",
                  stringsAsFactors = FALSE)
{% endhighlight %}

The files are loaded, we use merge (i.e., JOIN in the SQL world) to make a data frame containing all the required information. Note that this step is not necessary, it just makes plotting much easier.

{% highlight r %}
monster_frame = merge(x = stop_times,
                      y = stops,
                      by.x = "stop_id",
                      by.y = "stop_id")
monster_frame = merge(x = monster_frame,
                      y = trips,
                      by.x = "trip_id",
                      by.y = "trip_id")
{% endhighlight %}

Now we have a data frame with many columns. We select the rows (over 300,000 of them) corresponding to the chosen type of service selected in `calendar`. We then order the entries and make explicit the hour and minutes.

{% highlight r %}
idx = which(monster_frame$service_id %in% calendar$service_id)
monster_frame = monster_frame[idx,]
monster_frame = monster_frame[order(monster_frame$arrival_time),]
monster_frame$HH = as.numeric(substr(monster_frame$arrival_time,1,2))
monster_frame$MM = as.numeric(substr(monster_frame$arrival_time,4,5))
monster_frame = monster_frame[,c("arrival_time","HH","MM",
                                 "stop_lat",
                                 "stop_lon")]
{% endhighlight %}

Finally, we add latitude and longitude in Mercator format, which is used for plotting.

{% highlight r %}
monster_frame$x = OpenStreetMap::projectMercator(monster_frame$stop_lat,
                                                 monster_frame$stop_lon)[,1]
monster_frame$y = OpenStreetMap::projectMercator(monster_frame$stop_lat,
                                                 monster_frame$stop_lon)[,2]
{% endhighlight %}


Note that since the list is sorted by time, this allows for much faster processing during plotting. Now prepare the plots: download the map from OpenStreetMap.

{% highlight r %}
Winnipeg_upperLeft = c(max(monster_frame$stop_lat),
                       min(monster_frame$stop_lon))
Winnipeg_lowerRight = c(min(monster_frame$stop_lat),
                        max(monster_frame$stop_lon))
Winnipeg_map <- OpenStreetMap::openmap(upperLeft = Winnipeg_upperLeft,
                                       lowerRight = Winnipeg_lowerRight,
                                       type = "osm-public-transport")
{% endhighlight %}


## First animation method - using convert

Finally, the plot itself. We plot minute by minute, generating one image for each.

{% highlight r %}
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
{% endhighlight %}

Last piece: make an external call to `convert` (from `ImageMagick`) to
create a gif file with all the individual, minute by minute plots.

{% highlight r %}
my_command <- 'convert tmpFig/*.png -delay 3 -loop 0 Winnipeg_buses.gif'
system(my_command)
{% endhighlight %}

It is not unlikely that you will get an error when executing this last command. This is due to the default policy of ImageMagick in terms of memory allocation. In this case, under Linux, you need to edit `/etc/ImageMagick-6/policy.xml`. Here is what the relevant lines read on my machine:
{% highlight xml %}
<policymap>
  <!-- <policy domain="resource" name="temporary-path" value="/tmp"/> -->
  <policy domain="resource" name="memory" value="2GiB"/>
  <policy domain="resource" name="disk" value="2GiB"/>
</policymap>
{% endhighlight %}



The result is not the movement of buses themselves, but the activity of
bus stops along the route.

![Buses or ants?](https://server.math.umanitoba.ca/~jarino/images/Winnipeg_buses.gif "Buses moving around")

The problem here is file size (so much so that I could not post it on github). Also, the conversion itself can be quite time consuming. The next method addresses some of these issues.

## Second animation method - using animation

The `animation` library uses `ffmpeg`, so this should be installed on your machine. (As often, this is a trivial task under Linux, it might be a bit more of a headache under Windows.)
