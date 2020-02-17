clear all; close all; clc;

L = logspace(-6,0,1000);
h = 6.63e-34; %physical_constant("PlanchNumber");
c = 3e8;
lambda = 405e-9;

deadtime = 1.5e-8;
Ep = h * c / lambda;
A = (3e-3)^2;
pde = 0.5;%*10^-4.135;
pde2=0.5;
T  = 1e-9;
N = 14410;

alpha = A * pde / (N*Ep);

Long_count = N * alpha * T * L ./ (1 + alpha * deadtime * L);
my_count = pde2 * L * A * T / Ep;


figure();
semilogx(L,Long_count,'g--','linewidth',2);
hold on;
semilogx(L,my_count,'b.','linewidth',2);