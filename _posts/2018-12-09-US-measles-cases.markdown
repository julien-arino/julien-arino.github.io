---
layout: post
title:  "US measles cases data (epidemiology,R)"
description: "Historical data for the number of cases of measles in the USA from 1944 to the current day, collated from the US CDC data. Plotting of this data in R."
date:   2018-12-09 00:39:22 -0600
categories: datasets
description: blable
---

I am currently finishing up some work started ages ago that deals with spatial aspects in vaccination. The work was motivated by an outbreak of polio that started in northern Nigeria in 2002-2003, following a vaccine scare episode. In order to illustrate the benefits of vaccination, in these days of elevated anti-vaccine activity, I like to use the example of measles. The US data is available online, although like the SARS data that I discussed elsewhere, getting the entire dataset requires a bit of editing. So this post will serve as a means to disseminate the result of my editing of that data. And produce a graph of said data.

Measles strikes close to home for me: as a six year old kid, despite having received vaccination, I caught measles. (The vaccine, especially in early years, was not always most efficacious. This is one of the reasons it was later recommended to administer a booster shot, which makes the vaccine extremely efficacious; see below.)

**Update:** as of 6 June, there had been 1,022 cases of measles in the US in 2019. That is the most cases since the effect of the double dose of vaccine kicked in in the early nineties! The data and figures were updated accordingly.

## Two plots

The first plot is of the reported measles cases in the US during the entire period covered by the data.

![Reported cases of measles in the USA 1944-2019](/assets_pics/measles_US_1944_2019.png)

Illustrated are the three main eras in measles in this data:
1. The pre-vaccine era, which lasted until vaccination started in earnest in 1963.
2. The single-dose vaccine era, from 1963 to 1989.
3. After 1989, it was recommended to use two shots (an initial shot and a booster shot).

The second plot focuses on recent events, with particular focus on one of the roots of anti-vaccine activism.

![Reported cases of measles in the USA 1992-2019](/assets_pics/measles_US_1992_2019.png)

Here, I show the behaviour of measles since 1992. Of particular note here is the publication in the 28 February 1998 issue of The Lancet of an infamous paper by Wakefield and others that purported to show a link between the MMR vaccine and autism.
It took a few years for the effect to be felt, but now, we see regular small outbreaks. The situation is often the following: unvaccinated (US) individual goes abroad, gets infected, comes home and infects a few unvaccinated people.

The Wakefield paper has since been retracted, Wakefield himself has been discredited (although he does retain some influential supporters) and banned from practising medicine in the UK (his country), but as often with vaccine scares, the scars remain.

## Data files

+ Concatenated US Centers for Disease Control and Prevention Morbidity and Mortality Weekly Report for notifiable diseases, aggregated by year, from 1944 to 1993 and by month for 1994 and 1995: [file](https://raw.githubusercontent.com/julien-arino/datasets/master/CDC_MMWR_notifiableDiseasesYearly_1944_1995.txt). This file contains the raw data.
+ Yearly number of reported cases of measles in the USA from 1944 to 2019: [file](https://raw.githubusercontent.com/julien-arino/datasets/master/measles_reportedCases_USA_1944_2019.csv). For the period 1944 to 1995, the data comes from the file above. For the years following, data originates from more dynamic pages at [CDC](https://www.cdc.gov/measles/cases-outbreaks.html).


## Some remarks about making the plots

### Making a nice y axis for plots

The y-axis on the plots use a function that I adapted from another I found somewhere on the web (Stack Overflow, almost surely). There is most likely a prettier way to do this, but this one works.

{% highlight r %}
make_y_axis <- function(yrange) {
  y_max <- yrange[2]
  if (y_max < 1000) {
    # Do almost nothing
    factor <- 1
    ticks <- pretty(yrange)
    labels <- format(ticks, big.mark=",", scientific=FALSE)
  } else if (y_max < 10000) {
    # Label with ab,cde
    factor <- 1
    ticks <- pretty(yrange)
    labels <- format(ticks, big.mark=",", scientific=FALSE)
  } else if (y_max < 1000000) {
    # Label with K
    factor <- 1/1000
    ticks <- pretty(yrange*factor)
    labels <- paste(ticks,"K",sep="")
  } else if (y_max < 1000000000) {
    # Label with M
    factor <- 1/1000000
    ticks <- pretty(yrange*factor)
    labels <- paste(ticks,"M",sep="")
  } else {
    # Label with B
    factor <- 1/1000000000
    ticks <- pretty(yrange*factor)
    labels <- paste(ticks,"B",sep="")
  }
  # Remove 0unit, just have 0
  if ("0K" %in% labels) {
    labels[which(labels=="0K")]="0"
  }
  if ("0M" %in% labels) {
    labels[which(labels=="0M")]="0"
  }
  if ("0B" %in% labels) {
    labels[which(labels=="0B")]="0"
  }
  y_axis <- list(factor=factor,ticks=ticks,labels=labels)
  return(y_axis)
}
{% endhighlight %}

To make the function easier to use, let us call it from within a modified plot function. The function returns the parameters for the modified y-axis, so that they can be further used in the plot.

{% highlight r %}
# PLOT_HR_YAXIS
#
# Plot data using a human readable y-axis
plot_hr_yaxis <- function(x, y, ...) {
  y_range = range(y, na.rm = TRUE)
  y_axis <- make_y_axis(y_range)
  plot(x,y*y_axis$factor,
       yaxt = "n", ...)
  axis(2, at = y_axis$ticks,
       labels = y_axis$labels,
       las = 1, cex.axis=0.8)
  return(y_axis)
}
{% endhighlight %}

For plots that are simpler than the one above, it is a good idea to just wrap the above operations in a function.
To use this function, you need to call it on your data. I show the use with the code for the first of the two plots above. The data frame `measles` contains the loaded measles data.

{% highlight r %}
png(file = "measles_US_1944_2019.png",
    width = 1280, height = 720)
y_axis <- plot_hr_yaxis(measles$year, measles$reported_cases,
                        type = "b", lwd=1, lty = 2,
                        xlab = "Year",
                        ylab = "Reported # cases of measles / year",
                        xaxt = "n")
axis(1, at = c(1944,1960,1980,2000,2019))
# Vaccination started in 1963
polygon(x = c(1962.5,max(measles$year)+0.5,max(measles$year)+0.5,1962.5),
        y = c(0,0,par("usr")[4],par("usr")[4]),
        col = "grey85", border = "grey85")
# Recommended second dose started in 1989
polygon(x = c(1988.5,max(measles$year)+0.5,max(measles$year)+0.5,1988.5),
        y = c(0,0,par("usr")[4],par("usr")[4]),
        col = "grey75", border = "grey75")
# Redraw stuff covered by the polygons
abline (h=0, lty = 3)
abline (h=par("usr")[4])
abline (v=par("usr")[2])
lines(measles$year, measles$reported_cases*y_axis$factor,
      type = "b", lwd=1.5, lty = 2)
dev.off()
{% endhighlight %}



### Cropping pdf and png results

The following function is called with the same file name as used for the plot output just after the call to `dev.off()`. Of course, this requires to have functioning `pdftk` and `convert` program line commands available. (Windows people: it can be done. Not my problem here. Maybe I will explain elsewhere.)

{% highlight r %}
crop_figure = function(fileFull) {
  fileName = tools::file_path_sans_ext(fileFull)
  fileExt = tools::file_ext(fileFull)
  if (fileExt == "pdf") {
    command_str = sprintf("pdfcrop %s",fileFull)
    system(command_str)
    command_str = sprintf("mv %s-crop.pdf %s.pdf",fileName,fileFull)
    system(command_str)
  }
  if (fileExt == "png") {
    command_str = sprintf("convert %s -trim %s-trim.png",fileFull,fileName)
    system(command_str)
    command_str = sprintf("mv %s-trim.png %s",fileName,fileFull)
    system(command_str)
  }
}
{% endhighlight %}
