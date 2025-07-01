# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : disl_line(own).py
# Time       ：2025/3/13 16:43
# Author     ：oWoo
# Description：
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.ma.extras import apply_along_axis
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier, CommonNeighborAnalysisModifier,\
    InvertSelectionModifier, DeleteSelectedModifier, ExpressionSelectionModifier




if __name__ == '__main__':
    filepath = ("/Users/kaioneer/Documents/data/manifold")
    c = np.concatenate((np.linspace(0,0.9,10), np.linspace(0.925,1.0,4)))

    for i in range(c):
        ic = c[i]
        pipeline = import_file(f"{filepath}/data.{i}_disl")
        data = pipeline.compute()
        y = data.particles['Position'][:,1]     # y-coordinate of all particles
        yhi = max(y)
        ylo = min(y)
        modifier1 = CommonNeighborAnalysisModifier()
        pipeline.modifiers.append(modifier1)
        modifier2 = SelectTypeModifier(
            operate_on="particles",
            property="Structure Type",
            types={CommonNeighborAnalysisModifier.Type.OTHER}
        )
        pipeline.modifiers.append(modifier2)
        pipeline.modifiers.append(InvertSelectionModifier())
        pipeline.modifiers.append(DeleteSelectedModifier())
        modifier3 = ExpressionSelectionModifier(expression = f'Position.Y > {ylo}+10 && Position.Y < {yhi}-10')
        pipeline.modifiers.append(modifier3)
        pipeline.modifiers.append(InvertSelectionModifier())
        pipeline.modifiers.append(DeleteSelectedModifier())
        disl_line = pipeline.compute()
        position = disl_line.particles['Position'][:,[0,2]]     # x: burgers vector z: line vector
        x_ave = np.mean(position[:,0])
        leading = position[position[:,0] > x_ave]
        trailing = position[position[:,0] < x_ave]

        plt.figure(figsize=(6,12))
        plt.scatter(leading[:,0], leading[:,1], label='leading')
        plt.scatter(trailing[:,0], trailing[:,1], label='trailing')
        plt.xlabel('x [110] (Å)')
        plt.ylabel('z [112] (Å)')
        plt.legend()
        plt.savefig(f'{filepath}/disl_line.png')

        # manifold
        deltax2 = []
        deltaz2 = []
        for m in range(len(leading)):
            for n in range(m+1):
                dx2 = (leading[m, 0] - leading[n, 0]) ** 2
                dz2 = (leading[m, 1] - leading[n, 1]) ** 2
                deltax2.append(dx2)
                deltaz2.append(dz2)
        plt.figure()
        plt.plot(deltaz2, deltax2, 'o', label='leading')
        plt.legend()
        plt.xlabel('$dz^2 (Å^2)$')
        plt.ylabel('$dx^2 (Å^2)$')
        plt.title('zbox=80 (length of dislocation 348 Å)')
        plt.savefig(f"{filepath}/manifold-leading.png")


        deltax2 = []
        deltaz2 = []
        for m in range(len(trailing)):
            for n in range(m+1):
                dx2 = (trailing[m, 0] - trailing[n, 0]) ** 2
                dz2 = (trailing[m, 1] - trailing[n, 1]) ** 2
                deltax2.append(dx2)
                deltaz2.append(dz2)
        plt.figure()
        plt.plot(deltaz2, deltax2, 'o', label='trailing')
        plt.legend()
        plt.xlabel('$dz^2 (Å^2)$')
        plt.ylabel('$dx^2 (Å^2)$')
        plt.title('zbox=80 (length of dislocation 348 Å)')
        plt.savefig(f"{filepath}/manifold-trailing.png")


