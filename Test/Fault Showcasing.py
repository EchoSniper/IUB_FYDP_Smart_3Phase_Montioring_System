%% Coded by Raafiu Ashiquzzaman Mahmood 2010732 
clear all; close all; clc;

%% Load Data from CSV File
filename = 'your_file.csv'; % Replace 'your_file.csv' with your actual file name
data = readmatrix(filename);

% Assigning columns to phases
R = data(:, 1); % Phase A (Column 1)
B = data(:, 2); % Phase B (Column 2)
Y = data(:, 3); % Phase C (Column 3)
N = data(:, 4); % Ground (Column 4)

%% Applying Wavelet Decomposition of Current Reading
[cA, LA] = wavedec(R, 1, 'db4');
[cB, LB] = wavedec(B, 1, 'db4');
[cC, LC] = wavedec(Y, 1, 'db4');
[cN, LN] = wavedec(N, 1, 'db4');

%% Coefficients of Current Values
coefA = detcoef(cA, LA, 1); % Coefficients for Phase A
coefB = detcoef(cB, LB, 1); % Coefficients for Phase B
coefC = detcoef(cC, LC, 1); % Coefficients for Phase C
coefN = detcoef(cN, LN, 1); % Coefficients for Ground

%% Graph Plot
figure;
subplot(4, 1, 1);
plot(coefA);
title('Detail Coefficients for Phase A');
xlabel('Coefficient Index');
ylabel('Amplitude');

subplot(4, 1, 2);
plot(coefB);
title('Detail Coefficients for Phase B');
xlabel('Coefficient Index');
ylabel('Amplitude');

subplot(4, 1, 3);
plot(coefC);
title('Detail Coefficients for Phase C');
xlabel('Coefficient Index');
ylabel('Amplitude');

subplot(4, 1, 4);
plot(coefN);
title('Detail Coefficients for Ground');
xlabel('Coefficient Index');
ylabel('Amplitude');

%% Max Value of Coefficients
m = 10 * max(coefA);
n = 10 * max(coefB);
p = 10 * max(coefC);
q = 10 * max(coefN);

disp('Max Values:');
disp(['Phase A: ', num2str(m)]);
disp(['Phase B: ', num2str(n)]);
disp(['Phase C: ', num2str(p)]);
disp(['Ground: ', num2str(q)]);

%% Conditions for Fault Types
constant = 50; 
neutral = 2; 

if m > constant  
    if n > constant
        if p > constant
            if q > neutral
                disp("Three Phase to Ground Fault is Detected");
            end
        end
    end
end

if m > constant
    if n > constant
        if p > constant
            if q < neutral
                disp("Three Phase Fault is Detected");
            end
        end
    end
end

if m > constant
    if n > constant
        if p < constant
            if q > neutral
                disp("Double Line to Ground Fault (AB-G) is Detected");
            end
        end
    end
end

if m > constant
    if n < constant
        if p > constant
            if q > neutral
                disp("Double Line to Ground Fault (AC-G) is Detected");
            end
        end
    end
end

if m < constant
    if n > constant
        if p > constant
            if q > neutral
                disp("Double Line to Ground Fault (BC-G) is Detected");
            end
        end
    end
end

if m > constant 
    if n > constant
        if p < constant
            if q < neutral
                disp("Line to Line Fault Between Phase A and B is Detected");
            end
        end
    end
end

if m > constant
    if n < constant
        if p > constant
            if q < neutral
                disp("Line to Line Fault Between Phase A and C is Detected");
            end
        end
    end
end

if m < constant 
    if n > constant
        if p > constant
            if q < neutral
                disp("Line to Line Fault Between Phase B and C is Detected");
            end
        end
    end
end

if m > constant 
    if n < constant
        if p < constant
            if q > neutral
                disp("Single Line to Ground Fault in Phase A is Detected");
            end
        end
    end
end

if m < constant
    if n > constant
        if p < constant
            if q > neutral
                disp("Single Line to Ground Fault in Phase B is Detected");
            end
        end
    end
end

if m < constant
    if n < constant
        if p > constant
            if q > neutral
                disp("Single Line to Ground Fault in Phase C is Detected");
            end
        end
    end
end

if m < constant
    if n < constant
        if p < constant
            if q < neutral
                disp("No Fault is Detected. System is Normal");
            end
        end
    end
end

%% The End
