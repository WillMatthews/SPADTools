clear all; close all; clc;

L = logspace(-3,1,1000);
h = 6.63e-34; %physical_constant("PlanchNumber");
c = 3e8;
lambda = 405e-9;

deadtime = 1.5e-8;
Ep = h * c / lambda;
A = (3e-3)^2;
pde = 0.5;%*10^-4.135;
T  = 1;%e-9;
N = 14410;

my_alpha   = A * pde / (N*Ep);

my_count1   = N * my_alpha   * T * L ./ (1 + my_alpha   * deadtime * L);
%deadtime = 1e-9;
%N = 14410;
fprintf("d/N is %3.2e", deadtime/N);
my_alpha   = A * pde / (N*Ep);
my_count2   = N * my_alpha   * T * L ./ (1 + my_alpha   * deadtime * L);
physical_limit = pde * L * A * T / Ep;


figure();
semilogx(L,my_count1,'g--','linewidth',2);
hold on;
semilogx(L,my_count2,'r-', 'linewidth',2);
semilogx(L,physical_limit,'b.','linewidth',2);
legend("Real", "Modified", "Limit");
grid on; grid minor;
xlabel("Light Intensity at SiPM");
ylabel("Count rate");