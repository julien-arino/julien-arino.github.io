---
layout: post
title:  "Compiling R on a Raspberry Pi and getting rid of the 128 threads limitation"
description: "Some considerations on compiling R on a Raspberry Pi to get rid of the 128 threads limitation"
date:   2023-02-05
categories: r-code
featured: true
---

Does that title sound confusing? It should! Clearly, a 4 threaded Raspberry Pi should not hit that annoying "feature" baked in `R` whereby the number of sockets is limited to 125+3. Except that yes, it can, when the Pi used as the head node on a cluster.

## The context

As part of work on COVID-19 response, I was awarded a contract to increase my capacity for at home computing. Of course, some work was still carried out in a proper HPC setting, but there is a benefit to being able to run mid-range stuff efficiently as well as prototype and debug stuff before sending it to some HPC resource. So in March and April 2020, I ordered and built four machines. Actually, make that five: four "proper" machines and a Pi to rule them all. All the pieces required 47 different deliveries and got me on a first name basis with several UPS and Amazon delivery people. After several exchanges, my setup has looked essentially like this:

- 1 Raspberry Pi 4 with 4 GB of RAM running Ubuntu.
- 3 Threadripper 3790X machines running Ubuntu, each with 128 GB RAM and a 500 GB NVMe M.2 HD.
- 1 Threadripper 3990X machine running Ubuntu with 192 GB RAM (and also a 500 GB HD).
- 1 NAS with 4 TB storage.
- 1 swicth connecting all that can (i.e., all but the Pi) using link bonding and the Pi using a single link.

The 3790X have 32 cores/64 threads, the 3990X has 64/128. So my little space heater (hydro bills have been impacted substantially when all the machines run concurrently) has 320 compute threads and 4 on the Pi.

## My original usage

With some tweaking of the BIOS, I gently overclocked the Threadrippers (the 3990X, in particular, is a little sluggish for the type of computations I run) and convinced the motherboards to recognise all the RAM at its posted speed. I started using in production right away, which means I did not bother with my configuration and kept things as simple as possible. 

This is when I hit the "125+3 sockets in `R`" issue the first time: my code was running fine on the 3970X but refusing to run on the 3990X. Dug into it and worked out that setting the number of CPUs to 125 in my calls to `makeCluster` on the 3990X did the trick. With 4 perfectly capable compute nodes and easily parallelisable tasks, it is easy enough to produce a job list and have the Pi distribute it between nodes, have the nodes save the results locally upon completion and have the Pi running periodic "`rsync` repatriations" of the results from the nodes to the NAS. Once the computations were done, I used one of the compute nodes to bring the pieces together. 

## Compiling `R` to remove the 125+3 sockets limitation

Besides using **all** threads on the 3990X, I am also keen to drive all computations from a single designated node (when warranted, of course). I have been meaning to do this for quite a while, but this was rather low on my priority list. (I also want to play around with solutions such as `slurm` or `htcondor`, but this will be for later.)  And here, the 125+3 sockets pops up again: as far as I understand it, the head node needs as many sockets as threads it is talking to, i.e., 320 in my case. 

I have an old refurbished Dell Precision T7600 with two 8 cores E5-2690 Xeons and 128 GB of RAM that can be the head node. But what is the fun in that when I also have a Pi to play with? So, now that I have a bit more time, I decided to bite the bullet and try things out. 

First step, remove the 128 sockets limitation. Extremely easy: just compile `R` from sources. Which was deceptively easy, even on the Pi. This should not have been a surprise for someone coming from the days of yore when Linux did not have `deb` or `rpm` and every program installation required compilation. I took some inspiration [here](https://www.psyctc.org/Rblog/posts/2021-03-26-compiling-r-on-a-raspberry-pi-4/), but will point out that I had virtually none of the steps described there to follow, as I had had to install most of the software required for compilations prior to that.

The process is easy. Download the `R` source code from [here](https://cran.r-project.org/sources.html). (I used the [patched release](https://stat.ethz.ch/R/daily/R-patched.tar.gz).) Extract the tarball and move into the resulting directory. See some information [here](https://parallelly.futureverse.org/reference/availableConnections.html) about setting the maximum allowed number of connections, but in short: edit the file `src/main/connections.c` and replace
```c
#define NCONNECTIONS 128
```
with whatever limit you want to impose. There is some discussion [here](https://github.com/HenrikBengtsson/Wishlist-for-R/issues/28) on potential issues related to the number chosen; completely ignoring these issues, I decided to pick 1024.

Then `configure`, `make` (`make -j4`, perhaps) and `sudo make install` and you are in business. One remark, though: I prefer for the `R` executables and libraries to reside in `/usr` rather than `/usr/local` (for consistency with `deb` install of the standard code). Also, if you are going to run `rstudio-server`, you **must** compile for a shared `R` library. So, in short, instead of a simple `./configure`, I ran
```bash
./configure --prefix=/usr --enable-R-shlib
```

That latter point is worth mentioning: yes, `rstudio-server` on a Pi! I just recently realised that although the main `rstudio-server` site does not list it, `rstudio` and `rstudio-server` are available for `arm64` as [daily builds](https://dailies.rstudio.com/). And that `R` shared lib is important in this context: `rstudio-server` will not work otherwise.

## Taking it for a spin

Simple call to check things are working. Run the following code, adapting to your setup. (Note that this implies you have set up your machines to use shared key `ssh`.) Note that in the code here, I have not yet used the adapted version of `R` on the 3990X, so I am limiting things to 125 threads there.

{% highlight R %}
node0 <- '192.168.0.50'
node1 <- '192.168.0.51'
node2 <- '192.168.0.52'
node3 <- '192.168.0.53'
node4 <- '192.168.0.54'
machineAddresses <- list(
  list(host = node0, user = 'jarino', ncore = 2),
  list(host = node1, user = 'jarino', ncore = 64),
  list(host = node2, user = 'jarino', ncore = 64),
  list(host = node3, user = 'jarino', ncore = 64),
  list(host = node4, user = 'jarino', ncore = 125)
)
spec <- lapply(machineAddresses,
               function(machine) {
                 rep(list(list(host=machine$host, user=machine$user)),
                     machine$ncore)
               })
spec <- unlist(spec, recursive=FALSE)
parallelCluster <- parallel::makeCluster(type = 'PSOCK',
                                         master = node0,
                                         spec = spec)
print(parallelCluster)
if(!is.null(parallelCluster)) {
  parallel::stopCluster(parallelCluster)
  parallelCluster <- c()
}
{% endhighlight %}


Then, calling `test_cluster.R` this code and running it from the command line,
```bash
jarino@node0:~/CODE$ Rscript test_cluster.R 
socket cluster with 319 nodes on hosts ‘192.168.0.50’, ‘192.168.0.51’, ‘192.168.0.52’, ‘192.168.0.53’, ‘192.168.0.54’
```
So we are good! For comparison, running from a node with a "standard" `R` without the number of sockets increased (modifying the head node to be `node1`), we get the usual error:
```bash
jarino@node1:~/CODE$ Rscript test_cluster.R 
Error in socketConnection("localhost", port = port, server = TRUE, blocking = TRUE,  : 
  all connections are in use
Calls: <Anonymous> ... makePSOCKcluster -> newPSOCKnode -> socketConnection
Execution halted
Error in gzfile(file, "rb") : all connections are in use
Calls: <Anonymous> -> cleanup -> loadNamespace -> readRDS -> gzfile
```

Two final remarks.
1. The call to `makeCluster` can be quite lengthy (several minutes), even in this simple case with no functions or libraries to declare to the workers, so it is important to decide whether this level of parallelisation is required; if not, things may run much faster on 4 separate computers with result agregation as described earlier.
2. Clearly, this setup will require, in most instances, to have the code running on the compute nodes store the result locally there rather than return results to the head node. Indeed, only small sized return values would not quickly overwhelm the Pi's small RAM.