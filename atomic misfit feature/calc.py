# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : calc.py
# Time       ：2025/3/6 16:49
# Author     ：oWoo
# Description：
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def fit_deg2(x, y):
    coeffs = np.polyfit(x, y, deg=2)
    return coeffs[0]*2

if __name__ == '__main__':
    filepath = "/Users/kaioneer/Documents/data/misfit-atm"
    mod_type = 'compress'
    colors = ['dodgerblue', 'crimson', 'seagreen', 'violet', 'darkgoldenrod', 'darkorange', 'tomato', 'darkgray',
              'olivedrab']

    filename = f"{filepath}/txt/aveV.txt"
    with open(filename, 'r') as file:
        lines = [line.strip().split() for line in file.readlines()]

    sorted_lines = sorted(lines, key=lambda x: float(x[0]))
    vol_tot = [float(x[1]) for x in sorted_lines]
    avevol_atm = [float(x[2]) for x in sorted_lines]

    K_tot = []
    K_mean = []
    K_var = []
    epi_mean = []
    epi_var = []
    result = pd.DataFrame()
    # random = [5,6,80,84,86,96]
    for i in range(0,14):
        ran = i
        # filename = f"{filepath}/txt/{mod_type}_txt/{mod_type}_{ran}.txt"
        filename = f"{filepath}/txt/{mod_type}_{ran}.txt"
        vol_strn = []
        pe_tot = []
        with open(f"{filename}", 'r') as file:
            for line in file:
                line = line.strip()
                if mod_type=='compress':
                    strn = 1 - float(line.split()[1])
                else:
                    strn = float(line.split()[1])
                # pe = float(line.split()[2]) /vol_tot[i-1] * 1.6 * 10**2    # energy density (GPa)
                pe = float(line.split()[2]) / vol_tot[i] * 1.6 * 10 ** 2  # energy density (GPa)
                vol_strn.append(strn)
                pe_tot.append(pe)

        pe_tot = np.array(pe_tot)
        pe_tot = pe_tot - pe_tot[0]
        K = fit_deg2(vol_strn, pe_tot)
        K_tot.append(K)

        K_atm = []
        # filename1 = f"{filepath}/txt/{mod_type}_txt/{mod_type}_vol_{ran}.txt"
        # filename2 = f"{filepath}/txt/{mod_type}_txt/{mod_type}_pe_{ran}.txt"
        filename1 = f"{filepath}/txt/{mod_type}_vol_{ran}.txt"
        filename2 = f"{filepath}/txt/{mod_type}_pe_{ran}.txt"
        with open(f"{filename1}", 'r') as file1, open (f"{filename2}", 'r') as file2:
            for line1, line2 in zip(file1, file2):
                line1 = line1.strip()
                line2 = line2.strip()
                vol = [float(x) for x in line1.split()[2:]]
                pe = [float(x) * 1.6 * 10**2 for x in line2.split()[2:]]     # energy
                pe_den = np.array([y/x for x, y in zip(vol, pe)])
                pe_den = pe_den - pe_den[0]
                k = fit_deg2(vol_strn[:450], pe_den[:450])
                K_atm.append(k)
        df = pd.DataFrame(K_atm)
        result = pd.concat([result, df], axis=1)


        # K_min = min(K_atm)
        # K_max = max(K_atm)
        # bins = np.linspace(K_min, K_max, 50)
        # # plt.hist(K_atm, bins=bins, color=f'{colors[i - 1]}', edgecolor='black', density=True,
        # #                  label=f'x_Cu={i * 0.1:.1f}')
        #
        # K_atm = np.array(K_atm)
        # epi = K_atm/np.mean(K_atm) - 1
        #
        # K_mean.append(np.mean(K_atm))
        # K_var.append(np.var(K_atm))
        # epi_mean.append(np.mean(epi))
        # epi_var.append(np.var(epi))
        print(f'{i} is finished!!!')


    # fig, ax1 = plt.subplots()
    #
    # ax1.plot([x*0.1 for x in range(1,10)], K_mean, 'g-o')
    # ax1.set_xlabel('x_Cu')
    # ax1.set_ylabel('Ave', color='g')
    # ax1.tick_params(axis='y', labelcolor='g')
    # ax2 = ax1.twinx()
    # ax2.plot([x*0.1 for x in range(1,10)], K_var, 'b-o')
    # ax2.set_ylabel('Var', color='b')
    # ax2.tick_params(axis='y', labelcolor='b')
    #
    # plt.savefig(f"{filepath}/pic/{mod_type}.png")

    # result = pd.DataFrame({'K_tot': K_tot,
    #                             'K_mean': K_mean,
    #                             'K_var': K_var,
    #                              'epi_mean':  epi_mean,
    #                               'epi_var': epi_var})
    # result.to_excel(f"{filepath}/{mod_type}_tot_n.xlsx", index=False, engine='openpyxl')
    result.to_excel(f"{filepath}/dist_epik.xlsx", index=False, engine='openpyxl')