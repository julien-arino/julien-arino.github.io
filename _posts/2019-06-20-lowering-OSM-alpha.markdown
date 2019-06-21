---
layout: post
title:  "Lowering the alpha value in an OSM map (R,mapping)"
description: "Simple solution to change the alpha channel (that is, the opacity or transparency) in an OpenStreetMap map in R, using a function that adds an alpha value to a hexadecimal RGB colour specification."
date:   2019-06-20 09:52:00 -0600
categories: mapping
---
The most recent version of the code used in this page (which might be a little different from the one here) can be found [here](https://raw.githubusercontent.com/julien-arino/R-code/master/change_alpha_in_OSM_map.R).

Working on a poster with my postdoc, a problem came up where we wanted to increase the transparency of a map downloaded (and plotted) with `OpenStreetMap`, because the points we were plotting on it were not really visible. The solution is very simple. It goes without saying that you will need the `OpenStreetMap` library installed.

The first thing to do is to create a function to add an alpha value to the hexadecimal colour codes used in the `OpenStreetMap` library. Note that we assume an alpha value in \[0,1\].

{% highlight r %}
add_alpha_to_hex <- function(h,alpha) {
  if ((alpha <0) || (alpha>1))
    return(NA)
  a <- as.hexmode(round(alpha*255))
  # R format for hex colours with alpha is RGBA
  return(paste0(h,a))
}
{% endhighlight %}

Let us load a map of a small region in Winnipeg. We first need the coordinates of the upper left and lower right corners of the box we want to download.

{% highlight r %}
upperLeft <- c(49.8833,-97.1818)
lowerRight <- c(49.86310,-97.15081)
{% endhighlight %}

We also need to specify a map type. We take a cute map type in which alpha effect is easy to see.

{% highlight r %}
map_type <- "stamen-watercolor"
{% endhighlight %}

Download the map. For convenience, we store the tile colours.

{% highlight r %}
Winnipeg_map <- OpenStreetMap::openmap(upperLeft = upperLeft,
                                       lowerRight = lowerRight,
                                       type = map_type)
stored_colours <- Winnipeg_map$tiles[[1]]$colorData
{% endhighlight %}

Finally, we plot the maps for several values of alpha.
{% highlight r %}
for (alpha in seq(0.1, 1, by = 0.1)) {
  fileName = sprintf("~/Documents/DATA/tmp/Winnipeg_part_alpha%1.2f.png",
                     alpha)
  Winnipeg_map$tiles[[1]]$colorData = add_alpha_to_hex(stored_colours,
                                                       alpha)
  png(file = fileName, 
      width = 800, height = 800)
  plot(Winnipeg_map)
  dev.off()
}
{% endhighlight %}

Here are a few examples. First, the unaltered map (with alpha=1).

![Winnipeg neighbourhood alpha=1.0](/assets_pics/Winnipeg_part_alpha1.00.png?style=centered "Winnipeg neighbourhood alpha=1.0")

Second, the map when alpha=0.5.

![Winnipeg neighbourhood alpha=0.5](/assets_pics/Winnipeg_part_alpha0.50.png?style=centered "Winnipeg neighbourhood alpha=0.5")

Finally, a very light map where alpha=0.1.

![Winnipeg neighbourhood alpha=0.1](/assets_pics/Winnipeg_part_alpha0.10.png?style=centered "Winnipeg neighbourhood alpha=0.1")

