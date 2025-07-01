# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : Fp-all position.py
# Time       ：2025/2/15 20:25
# Author     ：oWoo
# Description：
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.stats import norm
import os


if __name__ == '__main__':
    filepath = "/Users/kaioneer/Documents/data/GSFE/c"
    Elements = ['Fe', 'Ni', 'Cr', 'Co', 'Cu']
    a_list = [3.538082579,
            3.545456417,
            3.552933253,
            3.560473002,
            3.56838135,
            3.576466461,
            3.584893816,
            3.593551078,
            3.602438646,
            3.61129988,
            3.613487429,
            3.615674171,
            3.617849199,
            3.619999223]
    idx = [0, 10, 11, 12, 13]

    folder_name = f"{filepath}/pic"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"文件夹'{folder_name}'已创建。")
    else:
        print(f"文件夹'{folder_name}'已存在。")

    folder_name = f"{filepath}/Fps"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"文件夹'{folder_name}'已创建。")
    else:
        print(f"文件夹'{folder_name}'已存在。")

    for cc in idx:
        a = a_list[cc]   # unit: Å
        n =100
        dx = a/np.sqrt(6)
        x = np.linspace(0, 2*dx, 2*n)

        filename = f"{filepath}/gsfe/gsfe_atom_{cc}.txt"
        ids = []
        eles = []
        data = []
        pos = []
        with open(f"{filename}", 'r') as file:
            for line in file:
                line = line.strip()
                id = int(line.split()[0])
                ele = int(line.split()[1])
                position = [float(x) for x in line.split()[2:5]]
                d = [float(x) for x in line.split()[5:]]
                ids.append(id)
                data.append(d)
                eles.append(ele)
                pos.append(position)

        if 2 * n != len(data[0]):
            print("Attention!!! Setting of 'n' is wrong!!!")

        Fps = []
        for i in range(len(data)):
            y = data[i]
            spline = InterpolatedUnivariateSpline(x, y)
            k = spline.derivative()(x)
            Fps.append(k)

        print(f"{cc} is finished!")
        dfdata = np.column_stack([ids, eles, pos, Fps])
        df = pd.DataFrame(dfdata)
        df.to_excel(f"{filepath}/Fps/Fps_{cc}.xlsx", index=False, engine='openpyxl')


    # # Distribution of Fps at all positions
    # allF = [item for sublist in Fps for item in sublist]
    # min = np.min(allF)
    # max = np.max(allF)
    # bins = np.linspace(min, max, 50)
    # x_test = np.linspace(min, max, 100)
    #
    # mean, std = norm.fit(allF)
    # dist = (mean, std)
    # y_test = norm.pdf(x_test, mean, std)
    # plt.figure()
    # plt.hist(allF, bins=bins, edgecolor='black')
    # plt.xlabel('Fp (eV/Å)')
    # plt.ylabel('PDF')
    # # plt.plot(x_test, y_test)
    # # plt.xlim(0)
    # plt.savefig(f"{filepath}/pic/Fps_dist.png")
    # plt.close()



