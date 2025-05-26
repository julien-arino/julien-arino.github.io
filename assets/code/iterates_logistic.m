close all;

f=inline('r.*x.*(1-x)','x','r');

x=0:0.01:1;

r=3.5;
n=10;

X=f(x,r);

for i=2:n,
    X=[X;f(X(end,:),r)];
end;

for i=1:10,
    plot(x,x,x,X(i,:))
    pause(1)
end