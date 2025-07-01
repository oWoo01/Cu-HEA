# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : misfitV.py
# Time       ：2025/2/21 19:45
# Author     ：oWoo
# Description：
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

if __name__ == '__main__':
    filepath = "/Users/kaioneer/Documents/data/misfit"
    a_list = [3.545456417,
            3.552933253,
            3.560473002,
            3.56838135,
            3.576466461,
            3.584893816,
            3.593551078,
            3.602438646,
            3.61129988]
    data = pd.read_csv(f'{filepath}/averaged_lc.txt', header=None, sep=' ')
    data.columns = ['c_Cu', 'ele', 'No.ele', 'c_ele', 'lc']

    c_Cu = data['c_Cu'].unique()
    df1 = pd.DataFrame(columns=['c_Cu', 'par_Fe', 'par_Ni', 'par_Cr', 'par_Co', 'par_Cu'])
    df2 = pd.DataFrame(columns=['c_Cu', 'delV_Fe', 'delV_Ni', 'delV_Cr', 'delV_Co', 'delV_Cu'])
    for i in range(len(c_Cu)):
        c = c_Cu[i]
        a = a_list[i]
        subset = data[data['c_Cu'] == c]
        par = [c]
        delV = [c]
        c_allele = [(1-c)/4, (1-c)/4, (1-c)/4, (1-c)/4, c]
        for j in range(5):
            sub2set = subset[subset['No.ele'] == j]
            x = sub2set.iloc[:, 3].values
            y = sub2set.iloc[:, 4].values
            cs = CubicSpline(x, y)
            k = cs.derivative()(x[1])
            par.append(k.tolist())

        new_df1 = pd.DataFrame([par], columns=['c_Cu', 'par_Fe', 'par_Ni', 'par_Cr', 'par_Co', 'par_Cu'])
        df1 = pd.concat([df1, new_df1], ignore_index=True)

        par = par[1:]
        for j in range(5):
            deL = 3/4*a**2 * (par[j] - np.dot(par, c_allele))
            delV.append(deL)
        new_df2 = pd.DataFrame([delV], columns=['c_Cu', 'delV_Fe', 'delV_Ni', 'delV_Cr', 'delV_Co', 'delV_Cu'])
        df2 = pd.concat([df2, new_df2], ignore_index=True)

    with pd.ExcelWriter(f'{filepath}/misfitV.xlsx') as writer:
        df1.to_excel(writer, sheet_name='Sheet1', index=False)
        df2.to_excel(writer, sheet_name='Sheet2', index=False)


