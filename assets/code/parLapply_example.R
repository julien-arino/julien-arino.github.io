R0 = function(p) {
  return(p$beta*p$S0/p$gamma)
}

one_run_R0 = function(p,param) {
  for (pp in names(p))
    param[[pp]] = p[[pp]]
  return(R0(param))
}

param = list()
param$beta = 1e-6
param$S0 = 10000
param$gamma = 1/4.5 # Average duration of infection

nb_sims = 10000 # nb of simulations of each type
param_vary = list()
for (i in 1:nb_sims) {
  param_vary[[i]] = list()
  param_vary[[i]]$beta = runif(1, min = 1e-9, max = 1e-4)
}
for (i in (nb_sims+1):(2*nb_sims)) {
  param_vary[[i]] = list()
  param_vary[[i]]$S0 = runif(1, min = 1000, max = 100000)
}
for (i in (2*nb_sims+1):(3*nb_sims)) {
  param_vary[[i]] = list()
  param_vary[[i]]$beta = runif(1, min = 1e-9, max = 1e-4)
  param_vary[[i]]$S0 = runif(1, min = 1000, max = 100000)
}

RUN_PARALLEL = TRUE
if (RUN_PARALLEL) {
  # Detect number of cores, use all but 1
  no_cores <- parallel::detectCores() - 1
  # Threadripper 3990X (or anything with 128 cores of more): need to limit 
  # number of running processes.
  if (no_cores > 124) {
    no_cores = 124
  }
  # Initiate cluster
  tictoc::tic()
  cl <- parallel::makeCluster(no_cores)
  # Export needed variables
  parallel::clusterExport(cl,
                          c("R0",
                            "one_run_R0",
                            "param"))
  # Run computation
  result = parallel::parLapply(cl = cl, X = param_vary,
                               fun =  function(x) one_run_R0(x,param))
  # Stop cluster
  parallel::stopCluster(cl)
  tictoc::toc()
} else {
  tictoc::tic()
  result = lapply(X = param_vary,
                  FUN = function(x) one_run_R0(x,param))
  tictoc::toc()
}

result = unlist(result)
result.df = data.frame(beta = result[1:nb_sims],
                       S0 = result[(nb_sims+1):(2*nb_sims)],
                       beta_S0 = result[(2*nb_sims+1):(3*nb_sims)])
png("~/parLapply_example_plot.png", width = 800, height = 800)
boxplot(result.df)
dev.off()
crop_figure("~/parLapply_example_plot.png")

