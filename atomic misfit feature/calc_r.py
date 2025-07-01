# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : calc_r.py
# Time       ：2025/3/6 18:40
# Author     ：oWoo
# Description：
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    filepath = "/Users/kaioneer/Documents/data/misfit-atm"

    r_mean = []
    r_var = []
    epi_mean = []
    epi_var = []
    result = pd.DataFrame()
    # for i in [5,6,80,84,86,96]:
    for i in range(0, 14):
        r_atm = []
        filename = f"{filepath}/txt/radius_{i}.txt"
        with open(f"{filename}", 'r') as file:
            for line in file:
                r = float(line.split()[0])
                r_atm.append(r)
        r_atm = np.array(r_atm)
        epi_atm = r_atm/np.mean(r_atm) - 1
        r_mean.append(np.mean(r_atm))
        r_var.append(np.var(r_atm))
        epi_mean.append(np.mean(epi_atm))
        epi_var.append(np.var(epi_atm))
        df = pd.DataFrame(epi_atm)
        result = pd.concat([result, df], axis=1)
        print(i)

    # result = pd.DataFrame({'r_mean': r_mean,
    #                             'r_var': r_var,
    #                              'epi_mean':  epi_mean,
    #                               'epi_var': epi_var})
    result.to_excel(f"{filepath}/dist_epir.xlsx", index=False, engine='openpyxl')


