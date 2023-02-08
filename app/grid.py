import os
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np

grid_pic_dir=os.path.join(os.getcwd(),'app','static','assets','img','grid')


def make_grid_pic(way_id,price,excitation,numbers,ratio):
    _x = np.linspace(numbers[0]/2, numbers[-1]+1000, 90)  # 数量
    _y = np.linspace(price[1]-20, price[-1]+20, 40)  # 单价
    x, y = np.meshgrid(_x, _y)
    x_ratio = deepcopy(x)
    y_ratio = deepcopy(y)
    y_add_up = 0
    # 处理数量系数
    x_ratio[x < numbers[0]] = 0  # 处理区间前面的数据
    for i in range(len(numbers)):
        if i == len(numbers) - 1:  # 超出区间
            x_ratio[x > numbers[i]] = ratio[i]  # 处理区间后面的数据
        else:  # 区间内
            x_ratio[(x > numbers[i]) & (x < numbers[i + 1])] = ratio[i]
    # 处理价格系数
    for i in range(len(price)):
        if i == len(price) - 1:  # 超出区间
            y_ratio[y > price[i]] -= price[i]  # 区间内
            y_ratio[y > price[i]] *= excitation[i]
            y_ratio[y > price[i]] += y_add_up
        else:
            y_ratio[(y > price[i]) & (y < price[i + 1])] -= price[i]  # 区间内
            y_ratio[(y > price[i]) & (y < price[i + 1])] *= excitation[i]
            y_ratio[(y > price[i]) & (y < price[i + 1])] += y_add_up
            y_add_up += (price[i + 1] - price[i]) * excitation[i]
    # x*x->ratio*y->ratio
    z = y_ratio * x_ratio * x/100
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(x, y, z, rstride=1, cstride=1,
                    cmap='viridis', edgecolor='none')
    ax.set_title('way_id:%s'%way_id)
    ax.view_init(elev=22, azim=-137)
    plt.savefig(os.path.join(grid_pic_dir,"%s.jpg"%way_id))

