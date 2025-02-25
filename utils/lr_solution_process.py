from utils.data_read import read
from utils.vehicles_ublb_calculation import max_vehicles_calculation,min_vehicles_calculation
import utils.data_process
from utils.set_start_values import set_start_values
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB,quicksum
from typing import List
def lr_solution_process(lr_solution,destination):
    orders,vehicles,skulimit,sku,other=read()
    valid_sku=utils.data_process.filter(orders=orders,sku=sku)
    print('总SKU种类:',len(valid_sku))
    demands=pd.merge(orders,sku,on='SKU')
    demands.to_excel('demands.xlsx',index=False)
    #车辆数ub,lb计算
    vehicle_types = [1,2,3,4]
    M=100000
    if destination!=3:
        vehicle_ub=max_vehicles_calculation(demands=demands,destination=destination,vehicles=vehicles)
    else:
        vehicle_ub=30
    print('最多车辆数:',vehicle_ub)
    demand_des=demands[demands['Destination']==destination]
    sku_des=demand_des['SKU'].values
    sku_demand=demand_des['Qty'].values

    lr_solution_copy=lr_solution.copy()
    #LA和LA_Bi矫正
    for key,value in lr_solution_copy['LA'].items():
        lr_solution_copy['LA'][key]=int(value)
        # if lr_solution_copy['LA'][key]>1:
        #     lr_solution_copy['LA'][key]-=1
        if lr_solution_copy['LA'][key]==1:
            lr_solution_copy['LA'][key]=0
        lr_solution_copy['LA_Bi'][key]=1 if lr_solution_copy['LA'][key]==0 else 0
    if destination==3:
        ND_diff_expr=[int(sku_demand[i]-sum(lr_solution_copy['LA'][v,i] for v in range(vehicle_ub))) for i in range(len(sku_des)) ]
    #ND_z矫正
        k=0
        for key,value in lr_solution_copy['ND_z'].items():
            if ND_diff_expr[key]>0:
                lr_solution_copy['ND_z'][key]=1
            else:
                lr_solution_copy['ND_z'][key]=0
            print(ND_diff_expr[key],lr_solution_copy['ND_z'][key])
            k+=1
        
    return lr_solution_copy