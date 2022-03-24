# -*- coding: utf-8 -*-
"""final_proj_opt.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/117vlRihsrDcOU6_akg9wBV2MNEiMQl-d
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd drive/MyDrive/

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib.pyplot as plt
from time import process_time 
import pandas as pd
import optperfprofpy
import warnings
from scipy.sparse import dia_matrix


warnings.filterwarnings("ignore")

# %matplotlib inline

def F1(x):
    return np.array([2 * x_i - np.sin(np.abs(x_i)) for x_i in x])


def F2(x):
    f_1 = 2 * x[0] + np.sin(x[0]) - 1
    f_i = [-2 * x[i - 1] + 2 * x[i] + np.sin(x[i]) - 1 for i in range(1, len(x) - 1)]
    f_n = 2 * x[-1] + np.sin(x[-1]) - 1
    return np.array([f_1] + f_i + [f_n])


def F3(x):
    h = 1 / (len(x) + 1)
    f_1 = x[0] - np.exp(np.cos(h * (x[0] + x[1])))
    f_i = [x[i] - np.exp(np.cos(h * (x[i - 1] + x[i] + x[i + 1]))) for i in range(1, len(x) - 1)]
    f_n = x[-1] - np.exp(np.cos(h * (x[-2] + x[-1])))
    return np.array([f_1] + f_i + [f_n])


def F4(x):
    return np.array([np.exp(x_i) - 1 for x_i in x])


def F5(x):
    f_1 = 2.5 * x[0] + x[1] - 1
    f_i = [x[i - 1] + 2.5 * x[i] + x[i + 1] - 1 for i in range(1, len(x) - 1)]
    f_n = x[-2] + 2.5 * x[-1] - 1
    return np.array([f_1] + f_i + [f_n])


def F6(x):
    n = len(x)
    return np.array([np.log(x_i + 1) - x_i / n for x_i in x])


def F7(x):
    f_1 = x[0] * (x[0] ** 2 + x[1] ** 2) - 1
    f_i = [x[i] * (x[i - 1] ** 2 + 2 * (x[i] ** 2) + x[i + 1] ** 2) - 1 for i in range(1, len(x) - 1)]
    f_n = x[-1] * (x[-2] ** 2 + x[-1] ** 2)
    return np.array([f_1] + f_i + [f_n])


def F8(x):
    n = len(x)
    ex = np.ones(n)
    data = np.array([-ex, 2 * ex, -ex])
    offsets = np.array([-1, 0, 1])
    A = dia_matrix((data, offsets), shape=(n, n))
    
    g = np.array([np.exp(x_i) - 1 for x_i in x])

    return A @ x + g

def feval(c):
  c+=1
  return c

def line_search_DLPM(F, x_k, d_k, sigma, r, count):
    alpha = 1
    while True:
        f_x_next = F(x_k + alpha * d_k)
        count = feval(count)
        if - f_x_next.T @ d_k >= sigma * alpha * np.linalg.norm(f_x_next) * (np.linalg.norm(d_k) ** 2):
            break
        alpha = alpha * r
    return alpha, count

def line_search_FCG(F, x_k, d_k, sigma, r, rho, count):
    alpha = 1
    while True:
        f_x_next = F(x_k + rho * alpha * d_k)
        count = feval(count)
        if - f_x_next.T @ d_k >= sigma * rho * alpha * (np.linalg.norm(d_k)**2):
            break
        alpha = alpha * r
    return alpha, count

def DLPM(F, x0):
    
    r = 0.6  # 0 < r < 1
    sigma = 0.01  # sigma > 0
    epsilon = 10e-6  # epsilon > 0
    count = 0

    p = 0.8
    q = -0.1

    x_k = np.copy(x0)
    f_k = F(x_k)
    count = feval(count)

    fs = [np.linalg.norm(f_k)]

    for k in range(5000):
        if k % 500 == 0 and k!= 0:
            print('Iteration: ', k)

        f_k_last = np.copy(f_k)

        # compute direction: d
        if k == 0:
            d = -f_k
        else:
            t = p * (np.linalg.norm(y_k_last) ** 2) / (s_k_last.T @ y_k_last) - q * (s_k_last.T @ y_k_last) / (
                    np.linalg.norm(s_k_last) ** 2)
            Beta = (f_k.T @ y_k_last) / (y_k_last.T @ d) - t * (f_k.T @ s_k_last) / (y_k_last.T @ d)
            d = -f_k + Beta * d

        if np.linalg.norm(d) == 0:
            return np.linalg.norm(f_k), x_k, k, fs, count

        alpha, count = line_search_DLPM(F, x_k, d, sigma, r, count)

        z_k = x_k + alpha * d
        f_z_k = F(z_k)
        count = feval(count)

        if np.linalg.norm(f_z_k) == 0:
            return np.linalg.norm(f_k), x_k, k, fs, count

        x_k = x_k - (f_z_k.T @ (x_k - z_k) * f_z_k) / (np.linalg.norm(f_z_k) ** 2)

        f_k = F(x_k)
        count = feval(count)

        if np.linalg.norm(f_k) <= epsilon:
            return np.linalg.norm(f_k), x_k, k, fs, count

        y_k_last = f_k - f_k_last
        s_k_last = alpha * d

        fs.append(np.linalg.norm(f_k))

def FCG(F, x0):
    r = 0.5
    sigma = 0.01
    t = 1
    rho = 1
    epsilon = 10e-6
    count = 0 

    x_k = np.copy(x0)
    f_k = F(x_k)
    count = feval(count)

    fs = [np.linalg.norm(f_k)]

    for k in range(5000):
        if k % 500 == 0 and k!= 0:
            print('Iteration: ', k)

        # compute direction: d
        if k == 0:
            d = -f_k
        else:
            Beta = t * np.linalg.norm(f_k) / (np.linalg.norm(d))
            d = -(1 + Beta * (f_k.T @ d) / (np.linalg.norm(f_k) ** 2)) * f_k + Beta * d

        if np.linalg.norm(d) == 0:
            return np.linalg.norm(f_k), x_k, k, fs, count

        alpha, count = line_search_FCG(F, x_k, d, sigma, r, rho, count)

        z_k = x_k + alpha * d
        f_z_k = F(z_k)
        count = feval(count)

        if np.linalg.norm(f_z_k) == 0:
            return np.linalg.norm(f_k), x_k, k, fs, count

        x_k = x_k - (f_z_k.T @ (x_k - z_k) * f_z_k) / (np.linalg.norm(f_z_k) ** 2)

        f_k = F(x_k)
        count = feval(count)

        if np.linalg.norm(f_k) <= epsilon:
            return np.linalg.norm(f_k), x_k, k, fs, count

        fs.append(np.linalg.norm(f_k))

    return np.linalg.norm(f_k), x_k, k, fs, count

n = 10000
x0 = np.ones((n, 1))
# F = F3

t1_start = process_time()
norm_f, final_x, iterations, fs, count = DLPM(F1, x0)
t1_stop = process_time()

print(f'DLPM: norm_f: {norm_f}  iterations: {iterations}')
print("Processing time in DLPM in seconds = ", t1_stop-t1_start)
print("Number of function evaluations = ",count)

plt.plot(fs)
plt.title("DLPM")
plt.xlabel("Iterations")
plt.ylabel("Norm f")

plt.show()

t2_start = process_time()
norm_f, final_x, iterations, fs, count = FCG(F1, x0)
t2_stop = process_time()

print(f'FCG: norm_f: {norm_f}  iterations: {iterations}')
print("Processing time in FCG in seconds = ", t2_stop-t2_start)
print("Number of function evaluations = ",count)

plt.figure()
plt.plot(fs)
plt.title('FCG')
plt.xlabel("Iterations")
plt.ylabel("Norm f")

plt.show()

# initial points
n1 = 10000
n2 = 100000

x0_1 = 1 * np.ones((n1, 1))
x0_2 = -0.5 * np.ones((n1, 1))
x0_3 = 0.1 * np.ones((n1, 1))
x0_4 = -10 * np.ones((n1, 1))
x0_5 = -1 * np.ones((n2, 1))
x0_6 = 0.5 * np.ones((n2, 1))
x0_7 = -0.1 * np.ones((n2, 1))
x0_8 = 10 * np.ones((n2, 1))

x0_9 = -1 * np.ones((n1, 1))

p1 = [x0_1, x0_2, x0_3, x0_4, x0_5, x0_6, x0_7, x0_8]
p2 = [x0_1, x0_2, x0_3, x0_6, x0_7]
p3 = [x0_1, x0_2, x0_3, x0_4, x0_5, x0_6, x0_7, x0_8]
p4 = [x0_1, x0_2, x0_3, x0_4, x0_5, x0_6, x0_7]
p5 = [x0_1, x0_2, x0_3, x0_4, x0_5, x0_6, x0_7, x0_8]
p6 = [x0_1, x0_2, x0_3, x0_6, x0_7, x0_8]
p7 = [x0_1, x0_9, x0_7]
p8 = [x0_3, x0_7]

p_inits = [p1, p3, p4, p5, p6, p7, p8]

df_perprof = []
for i, f in enumerate(['F1', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8']):
  print(f)
  inits = p_inits[i]
  for x0 in inits:
    str_x0 = f'{x0[0][0]}, n={x0.shape[0]}'
    print(str_x0)
    for method in ['DLPM', 'FCG']:
      # iter, t, feval, fnorm = eval(method)(eval(f))
      t_start = process_time()
      norm_f, final_x, iterations, fs, count = eval(method)(eval(f), x0)
      t_stop = process_time()
      # iter, t, feval, fnorm = 1, 2, 3, 4
      df_perprof.append([f, str_x0, method, iterations, t_stop-t_start, count, norm_f])
  print()

# df
df_perprof = pd.DataFrame(df_perprof, columns=['F', 'x0', 'Method', 'ITER', 'Time', 'Feval', 'Norm'])
df_perprof

objectives = ['ITER', 'Time', 'Feval']
for objective in objectives:
  taus, solver_vals, solvers, transformed_data = optperfprofpy.calc_perprof(df_perprof, ['F'], [objective], ['Method'])
  optperfprofpy.draw_simple_pp(taus, solver_vals, solvers)
  plt.title(f'performance profile\n respect to {objective}')

from IPython.display import display
for i, f in enumerate(['F1', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8']):
    table = df_perprof[df_perprof['F'] == f].pivot_table(index='x0', columns='Method', values=['ITER', 'Time', 'Feval', 'Norm'])
    display(table)