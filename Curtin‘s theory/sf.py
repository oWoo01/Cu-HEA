# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : sf.py
# Time       ：2025/1/11 10:59
# Author     ：oWoo
# Description：calculate the width and other features of stacking faults.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier, CommonNeighborAnalysisModifier,\
    InvertSelectionModifier, DeleteSelectedModifier

def calc_width(sf):
    # calculate the width of the stacking faults
    z_sf = sf.particles['Position'][:, 2]
    y_sf = sf.particles['Position'][:, 1]
    x_sf = sf.particles['Position'][:, 0]

    groups = group_atoms(list(zip(z_sf, x_sf)))
    di = []
    for group in groups:
        di.append(np.max(group) - np.min(group))

    d_sf = np.mean(di)  # width of stacking faults
    std_sf = np.std(di)
    return d_sf, std_sf


def group_atoms(data, threshold=0.5):

    data.sort(key=lambda x: x[0])
    groups = []
    current_group = [data[0][1]]

    for i in range(1, len(data)):
        if data[i][0] - data[i - 1][0] <= threshold:
            current_group.append(data[i][1])
        else:
            groups.append(current_group)
            current_group = [data[i][1]]
    groups.append(current_group)

    return groups




if __name__ == '__main__':
    filepath = "/Users/kaioneer/Documents/data/cuhea-lowtau/data"
    b = 3.552 / 2 ** 0.5     # burgers vector
    numofcf = 10
    c = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]


    width = pd.DataFrame(columns=['x_Cu',
                                  'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10'])
    std = pd.DataFrame(columns=['x_Cu',
                                  'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10'])
    for i in range(len(c)):
        width_i = [c[i]]
        std_i = [c[i]]
        for j in range(numofcf):
            j += 1
            pipeline = import_file(rf"{filepath}/config-{j}/data.{i}_disl")
            data = pipeline.compute()

            # getting atoms in stacking faults
            modifier = CommonNeighborAnalysisModifier()
            pipeline.modifiers.append(modifier)
            modifier = SelectTypeModifier(
                operate_on="particles",
                property="Structure Type",
                types={CommonNeighborAnalysisModifier.Type.HCP}
            )
            pipeline.modifiers.append(modifier)
            pipeline.modifiers.append(InvertSelectionModifier())
            pipeline.modifiers.append(DeleteSelectedModifier())
            sf_atoms = pipeline.compute()  # stacking fault

            width_j, std_j = calc_width(sf_atoms)

            width_i.append(width_j)
            std_i.append(std_j)
        new_width = pd.DataFrame([width_i], columns=['x_Cu',
                             'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10'])
        width = pd.concat([width, new_width])
        new_std = pd.DataFrame([std_i], columns=['x_Cu',
                             'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10'])
        std = pd.concat([std, new_std])

    width['average'] = np.mean(width.iloc[:,1:], axis=1)
    width['std'] = np.std(width.iloc[:, 1:], axis=1)
    std['average'] = np.mean(std.iloc[:,1:], axis=1)
    std['std'] = np.std(std.iloc[:, 1:], axis=1)

    width.to_excel(f"{filepath}/sf_width.xlsx", index=False, engine='openpyxl')
    std.to_excel(f"{filepath}/sf_std.xlsx", index=False, engine='openpyxl')
