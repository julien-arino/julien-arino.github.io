tc = 0
S0 = 999
I0 = 1

tf = 50

b = 1
d = 1/(70*365.25)
beta = 0.00025
gamma = 1/7

S = S0
I = I0

tt = tc
ii = I

while (tc<tf) {
  eta = b+d*S+d*I+beta*S*I+gamma*I
  tau = rexp(1,eta)
  num = runif(1)
  if (num <= b/eta) {
    S = S+1
  } else if (num <= b/eta+d*S/eta) {
    S = S-1
  } else if (num <= (b+d*S+d*I)/eta) {
    I = I-1
  } else if (num <= (b+d*S+d*I+beta*S*I)/eta) {
    S = S-1
    I = I+1
  } else {
    S = S+1
    I = I-1
  }
  tc = tc+tau
  tt = append(tt,tc)
  ii = append(ii,I)
}

plot(tt,ii,xlab="Time",ylab="Number of infectious",
     main="One trajectory of a CTMC SIS model",
     type="l")