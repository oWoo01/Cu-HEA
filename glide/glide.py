# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : glide.py
# Time       ：2024/12/4 16:21
# Author     ：oWoo
# Description：
"""
from multiprocessing.managers import Value

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import glob
import re


def rmv_outlier(data_ini, time):
    result = [data_ini[0]]
    tt = [time[0]]
    for p in range(1, len(data_ini)):
        if data_ini[p] >= (result[-1] - 1):
            if data_ini[p] >= (result[-1] + 10):
                # print('+100 success')
                # print('%s,%s,%s,%s' % (p, data_ini[p], result[-1], result[-2]))
                data_ini[p:] = data_ini[p:] - np.ones(len(data_ini[p:])) * data_ini[p] \
                               + np.ones(len(data_ini[p:])) * 2 * result[-1] - np.ones(len(data_ini[p:])) * result[-2]
            result.append(data_ini[p])
            tt.append(time[p])

    return result, tt

def local_slope(x, y, w):
    slopes = np.zeros_like(x)

    for i in range(len(x)):
        start = max(i - w, 0)
        end = min(i + w + 1, len(x))

        x_window = x[start:end]
        y_window = y[start:end]

        dx = x_window[-1] - x_window[0]
        dy = y_window[-1] - y_window[0]

        if dx != 0:
            window_slope = dy / dx
        else:
            window_slope = 0

        slopes[i] = window_slope

    return slopes

if __name__ == '__main__':
    filepath = "/Users/kaioneer/Documents/data/cuhea-lowc"
    # a_list = [3.56838135,
    #         3.576466461,
    #         3.584893816,
    #         3.593551078,
    #         3.602438646,
    #         3.61129988,
    #         3.613487429,
    #         3.615674171,
    #         3.617849199,
    #         3.619999223]
    # c = [0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.925, 0.95, 0.975, 1.0]
    a_list = [3.538082579,
                3.545456417,
                3.552933253,
                3.560473002]
    c = [0, 0.1, 0.2, 0.3]
    T = [300,600,900]   # temperature
    config = [6, 7, 8, 9, 10]
    dt = 0.004 * 50
    b = [i * 2 ** 0.5 / 2 for i in a_list]

    window = 5 # 前后分别window个点
    thres = 2
    # record_v = pd.DataFrame(columns=['x_Cu', 'temperature', 'stress',
    #                                  'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10'])
    record_v = pd.DataFrame(columns=['x_Cu', 'temperature', 'stress',
                                     'config6', 'config7', 'config8', 'config9', 'config10'])

    for a in range(len(c)):
        for j in T:
            files = glob.glob(f"{filepath}/txt-{6}/dislx_{a}_{j}K_*MPa.txt")
            pattern = re.compile(fr"dislx_{a}_{j}K_(\d+)MPa\.txt")
            str = sorted([int(pattern.search(f).group(1)) for f in files if pattern.search(f)])
            for k in str:
                new = [c[a], j, k]
                plt.figure()
                plt.xlabel('t (ps)')
                plt.ylabel('x (Å)')
                for cf in config:
                    print(c[a], j, cf)
                    try:
                        filename = f"{filepath}/txt-{cf}/dislx_{a}_{j}K_{k}MPa.txt"
                        with open(filename, 'r', encoding='utf-8') as f:
                            xs = [float(line.strip()) for line in f.readlines()]

                        data = pd.DataFrame()
                        data['x'] = xs
                        data = data[data['x']>1]
                        time = list(np.linspace(0, dt * (len(data)-1), len(data)))
                        xs = list(data['x'] - data['x'].iloc[0])
                        data = data.sort_values(by='x')

                        xs_n, time_n = rmv_outlier(xs, time)
                        data_ = pd.DataFrame()
                        data_['t'] = time_n
                        data_['x'] = xs_n
                        data_.to_csv(f'{filepath}/x-t/{a}_{j}K_{k}MPa_{cf}.txt')
                        v_local_mean, blabla, _, _, _= st.linregress(time_n[125:], xs_n[125:])
                        if v_local_mean < 0:
                            v_local_mean = 0

                        # # ------------------------------------
                        # slps = local_slope(time_n, xs_n, window)
                        # v_local = [s for s in slps[125:] if np.abs(s) > thres]
                        #
                        # if not v_local:
                        #     v_local_mean = 0
                        #     v_std = 0
                        # else:
                        #     v_local_mean = np.nanmean(v_local)
                        #     v_std = np.nanstd(v_local)
                        #     if v_local_mean < 0:
                        #         v_local_mean = 0
                        #         v_std = 0
                        # # ------------------------------------

                        plt.plot(time_n, xs_n, label=f'config{cf}')
                        new.append(v_local_mean)
                    except FileNotFoundError:
                        print(f"dislx of {a}_{j}K_{k}MPa not found. Skipping")
                    except ValueError as e:
                        print(f"dislx of {a}_{j}K_{k}MPa Error: {e}")
                        print(f"{len(time_n)}")
                        v_local_mean = 0
                        new.append(v_local_mean)

                # new_v = pd.DataFrame([new], columns=['x_Cu', 'temperature', 'stress',
                #                       'config6', 'config7', 'config8', 'config9', 'config10'])
                new_v = pd.DataFrame([new], columns=['x_Cu', 'temperature', 'stress',
                                     'config6', 'config7', 'config8', 'config9', 'config10'])
                record_v = pd.concat([record_v, new_v])

                plt.legend()
                plt.savefig(f'{filepath}/pic/x-t/x-t-{a}-{j}K-{k}MPa.png')
                plt.close()
    record_v['v'] = np.mean(record_v.iloc[:,3:], axis=1)
    record_v['std'] = np.std(record_v.iloc[:, 3:], axis=1)
    record_v.to_excel(f"{filepath}/v.xlsx", index=False, engine='openpyxl')

    # # calculate average velocity of all configureations
    # data = pd.read_excel(f"{filepath}/v.xlsx")
    # # char = pd.read_excel(f"{filepath}/chars.xlsx")
    # char = pd.DataFrame(columns=['x_Cu', 'temperature', 'drag coefficient', 'threshold stress'])
    # flag = 0
    # for i in c:
    #     plt.figure()
    #     plt.title(f"x_Cu={i}")
    #     plt.xlabel('τ/MPa')
    #     plt.ylabel('v/(Å/ps)')
    #     for j in T:
    #         subset = data[(data['x_Cu']==i) & (data['temperature']==j)]     # subset = data[(data['x_Cu']==i) & (data['v']<9)]
    #         tau = subset['stress']
    #         v = subset['v']
    #         std = subset['std']
    #         indices = np.where(v>0.1)
    #         if indices[0].size == 0:
    #             print(f'dislcation is not activated when x_Cu={i} at {j}K')
    #             break
    #         else:
    #             left = indices[0][0]
    #         plt.errorbar(tau, v, yerr=std, fmt='-o', capsize=5, label=f'{j}K')
    #         btau = [float(tt) * b[flag] for tt in tau]
    #         calc_B = pd.DataFrame({'x': v.iloc[left:], 'y': btau[left:]})
    #         calc_B = calc_B.dropna(axis=0, how='any')
    #         B, t, _, _, _ = st.linregress(list(calc_B['x']), list(calc_B['y']))
    #
    #         new = pd.DataFrame({'x_Cu': [i], 'temperature': [j], 'drag coefficient': [B],
    #                            'threshold stress':[t/b[flag]]})
    #         char = pd.concat([char, new])
    #         # plt.scatter(t/b, 0, color='r')
    #     flag += 1
    #     # plt.ylim(-1,20)
    #     plt.legend()
    #     plt.savefig(f"{filepath}/pic/v-τ-{i:.2f}.png")
    #     plt.close()
    # flag = 0
    #
    #
    # for j in T:
    #     plt.figure()
    #     plt.title(f"T={j}K")
    #     plt.xlabel('τ/MPa')
    #     plt.ylabel('v/(Å/ps)')
    #     for i in c:
    #         subset = data[(data['x_Cu']==i) & (data['temperature']==j)]
    #         tau = subset['stress']
    #         v = subset['v']
    #         std = subset['std']
    #         plt.errorbar(tau, v, yerr=std, fmt='-o', capsize=5, label=f'x_Cu={i:.3f}')
    #     plt.legend()
    #     plt.savefig(f"{filepath}/pic/v-τ-{j}K.png")
    #     plt.close()
    #
    # char.to_excel(f"{filepath}/chars.xlsx", index=False, engine='openpyxl')

    # plt.figure()
    # plt.title('threshold stress')
    # plt.xlabel('x_Cu')
    # plt.ylabel('τ0 (MPa)')
    # theory = [161.798087,
    #         235.4077684,
    #         179.8180839,
    #         198.5372566,
    #         236.036747,
    #         287.5392715]
    # plt.plot(c, theory, '-o', label='300K(Curtin)')
    # for j in T:
    #     subset = char[char['temperature']==j]
    #     x = subset['x_Cu']
    #     y = subset['threshold stress']
    #     plt.plot(x, y, '-o', label=f"{j}K(MD)")
    # plt.legend()
    # # plt.ylim(200, 300)
    # plt.savefig(f"{filepath}/pic/τ-x.png")
    # plt.close()
    #
    # plt.figure()
    # plt.title('threshold stress')
    # plt.xlabel('T')
    # plt.ylabel('τ0 (MPa)')
    # for i in c:
    #     subset = char[char['x_Cu']==i]
    #     x = subset['temperature']
    #     y = subset['threshold stress']
    #     plt.plot(x, y, '-o', label=f"{i:.2f}")
    # plt.legend()
    # plt.savefig(f"{filepath}/pic/τ-T.png")
    # plt.close()
    #

    #
    #
    # # calculate threshold stress at 0K
    # char = pd.read_excel(f"{filepath}/chars.xlsx")
    # t0 = []
    # for i in c:
    #     subset = char[char['x_Cu']==i]
    #     x = subset['temperature']
    #     y = subset['threshold stress']
    #     k, y0, _, _, _ = st.linregress(x, y)
    #     t0.append(y0)
    # print(t0)



