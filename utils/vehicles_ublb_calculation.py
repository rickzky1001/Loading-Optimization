from typing import List
import math
import pandas as pd
#逻辑：找装载力最弱的车，需要多少辆，做为一个ub, 增加1/4辆
def max_vehicles_calculation(demands,destination: int,vehicles: pd.DataFrame)->int:
    order_for_destination=demands[demands['Destination']==destination]
    total_weight=(order_for_destination['Weight']*order_for_destination['Qty']).sum()
    total_volume=(order_for_destination['Volume']*order_for_destination['Qty']).sum()
    maximal_v=math.ceil(total_volume/vehicles['Upper Limit Volume'].min())
    maximal_w=math.ceil(total_weight/vehicles['Upper Limit_Weight'].min())
    return max(maximal_v,maximal_w)+int(1/4*max(maximal_v,maximal_w))
#逻辑：找装载力最强的车，需要多少辆，做为一个lb
def min_vehicles_calculation(demands,destination: int,vehicles: pd.DataFrame)->int:
    order_for_destination=demands[demands['Destination']==destination]
    total_weight=(order_for_destination['Weight']*order_for_destination['Qty']).sum()
    total_volume=(order_for_destination['Volume']*order_for_destination['Qty']).sum()
    minimal_v=math.floor(total_volume/vehicles['Upper Limit Volume'].max())
    minimal_w=math.floor(total_weight/vehicles['Upper Limit_Weight'].max())
    return min(minimal_v,minimal_w)
