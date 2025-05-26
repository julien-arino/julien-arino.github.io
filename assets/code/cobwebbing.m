clear all;
close all;

f=inline('r.*x.*(1-x)','x','r');

r = input('Enter the bifurcation parameter r (0 < r < 4): ');
x = input('Enter the starting value x1 (0 < x1 < 1): ');
n = input('Enter the total number of iterations in a sequence n (0 < n < 50): ');
%fig1=figure;

subplot(1,2,2);
axis([0 n 0 1]);
xlabel('Time');
ylabel('x_k');
hold on;

subplot(1,2,1);
title('Cobwebbing in the discrete logistic map');
xlabel('x_k'); 
ylabel('x_{k+1}'); %hold off;
axis([0 1 0 1]); 
hold on;

s = 0 : 0.01 : 1; % a mesh for the unit interval of x
plot(s,s,'g'); % plotting the diagonal y = x
y = f(s,r);
plot(s,y,'b') % plotting the discrete map: y = r*x*(1-x)
for k = 1:n
    x(k+1)=f(x(k),r); % automatic extension of the vector x from scalar
end
plot([x(1), x(1)],[x(1),x(2)],'r'); % the first vertical segment of the picture
plot([x(1),x(1)],[x(1),x(2)],'r');
for k = 2 : n
    % Plot in subfigure 1
    subplot(1,2,1);
    plot([x(k-1),x(k)],[x(k),x(k)],'r'); % a horizonal segment of the picture
    plot([x(k),x(k)],[x(k),x(k+1)],'r'); % a vertical segment of the picture
    % Plot in subfigure 2
    subplot(1,2,2);
    plot([k-1,k],[x(k-1),x(k)]);
    pause(1); % intermediate pause to follow the cobwebbing over time
end