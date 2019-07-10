---
layout: post
title:  "Ugly loops (R)"
description: "Comparison of loops and vectorised operations in R using the tictoc library."
date:   2019-07-10
categories: simulation
---

The other day, I posted a prototypical example of use of parLapply, somewhat more advanced than the ones in the documentation; see [here](https://julien-arino.github.io/2019/skel-parLapply).

Well, part of the example I gave uses one of my most biggest coding pet peaves, something that I have been fighting against ever since my MatLab days: the dreaded unnecessary *for loop*. As I was teaching myself the use of the `tictoc` library, I thought I would illustrate both.

To keep in the spirit of the example in the post mentioned, we set up variations of up to two parameters, $\beta$ and $S_0$. We set base values for these parameters.

{% highlight r %}
param = list()
param$beta = 1e-6
param$S0 = 10000
{% endhighlight %}

We will try different ranges of number of cases.

{% highlight r %}
nb_sims = c(10000,50000,100000,500000,1000000,5000000,10000000)
{% endhighlight %}

Now loop on the number of cases. First, clear the `tictoc` log, in case it already exists. In each loop, we take note of the time taken to accomplish each group of operations.

{% highlight r %}
tictoc::tic.clearlog()
for (n in nb_sims) {
  # The loop
  print(sprintf("%d - %d",n,which(nb_sims==n)))
  tictoc::tic(sprintf("loop_%d",n))
  param_vary = list()
  for (i in 1:n) {
    param_vary[[i]] = list()
    param_vary[[i]]$beta = runif(1, min = 1e-9, max = 1e-4)
  }
  for (i in (n+1):(2*n)) {
    param_vary[[i]] = list()
    param_vary[[i]]$S0 = runif(1, min = 1000, max = 100000)
  }
  for (i in (2*n+1):(3*n)) {
    param_vary[[i]] = list()
    param_vary[[i]]$beta = runif(1, min = 1e-9, max = 1e-4)
    param_vary[[i]]$S0 = runif(1, min = 1000, max = 100000)
  }
  # Vector version
  tictoc::toc(log = TRUE, quiet = TRUE)
    tictoc::tic(sprintf("vect_%d",n))
  param_vary <- rbind(cbind(runif(n, min = 1e-9, max = 1e-4),
                            rep(param$S0,n)),
                      cbind(rep(param$beta,n),
                            runif(n, min = 1000, max = 100000)),
                      cbind(runif(n, min = 1e-9, max = 1e-4),
                            runif(n, min = 1000, max = 100000)))
  colnames(param_vary) <- c("beta","S0")
  tictoc::toc(log = TRUE, quiet = TRUE)
  # Convert vector to list
  tictoc::tic(sprintf("conv_%d",n))
  param_vary <- lapply(seq_len(nrow(param_vary)),
                       function(i) param_vary[i,])
  tictoc::toc(log = TRUE, quiet = TRUE)
}
log.lst <- tictoc::tic.log(format = FALSE)
{% endhighlight %}

The following is adapted from the `tictoc` documentation.

{% highlight r %}
timings <- cbind(nb_sims,
                 matrix(data = unlist(lapply(log.lst,
                                             function(x) x$toc - x$tic)),
                        nrow = length(nb_sims),
                        ncol = 3,
                        byrow = TRUE))
colnames(timings) <- c("n","loopTime","vectorTime","convertTime")
timings <- as.data.frame(timings)
{% endhighlight %}

Add a few additional pieces of information about timing: the total time in the second case (making the vectors and converting them to lists) as well as acceleration factors when making the vector and in total of the second method.

{% highlight r %}
timings$sumVector <- timings$vectorTime+timings$convertTime
timings$multVector <- round(timings$loopTime/timings$vectorTime,2)
timings$multSumVector <- round(timings$loopTime/timings$sumVector,2)
{% endhighlight %}

Finally, use `knitr` to make a decent looking table of the results.

{% highlight r %}
knitr::kable(timings,format.args = list(big.mark = ",",scientific=FALSE))
{% endhighlight %}

Here is a subset of the results:

|          n| loopTime| vectorTime| convertTime| sumVector| multVector| multSumVector|
|----------:|--------:|----------:|-----------:|---------:|----------:|-------------:|
|     10,000|    0.111|      0.001|       0.035|     0.036|     111.00|          3.08|
|     50,000|    0.337|      0.005|       0.137|     0.142|      67.40|          2.37|
|    100,000|    0.941|      0.011|       0.232|     0.243|      85.55|          3.87|
|    500,000|    5.137|      0.051|       1.422|     1.473|     100.73|          3.49|
|  1,000,000|    8.356|      0.101|       2.420|     2.521|      82.73|          3.31|
|  5,000,000|   72.179|      5.044|      21.246|    26.290|      14.31|          2.75|
| 10,000,000|  203.776|     14.890|      36.895|    51.785|      13.69|          3.94|


Ah, yes, one last thing: when $n$ is large, some of the variables can become quite large (the last matrix by itself is 10.1 Gb). Unless you have pretty decent RAM, don't try this at home.
