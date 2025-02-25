from utils.data_read import read
from utils.vehicles_ublb_calculation import max_vehicles_calculation,min_vehicles_calculation
import utils.data_process
from utils.set_start_values import set_start_values
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB,quicksum
from typing import List
def solve(time,lr_solution,destination:int,c2,c3,PUNISHMENT_VD,PUNISHMENT_VN,PUNISHMENT_ND=5/31746)->None:
    orders,vehicles,skulimit,sku,other=read()
    valid_sku=utils.data_process.filter(orders=orders,sku=sku)
    print('总SKU种类:',len(valid_sku))
    demands=pd.merge(orders,sku,on='SKU')
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
    max_sku_qty=demand_des['Qty'].max()
    print('需求量最大的sku数量:',max_sku_qty)



    model = gp.Model("loading_optimization")
    VT = model.addVars(len(vehicle_types), vtype=GRB.BINARY, name="VT")#vehicle type
    IA = model.addVars(vehicle_ub, vtype=GRB.BINARY, name="IA")#is_active
    LA = model.addVars(vehicle_ub, len(sku_des), vtype=GRB.INTEGER,lb=0, name="LA")#Loading_amount
    sku_demand=demand_des['Qty'].values
    for v in range(vehicle_ub):
        for i in range(len(sku_des)):
            #LA[v, i].ub = sku_demand[i]
            LA[v, i].ub = max_sku_qty
    LA_Bi = model.addVars(vehicle_ub, len(sku_des), vtype=GRB.BINARY, name="LA_Bi")#该sku是否为空,Loading_Binary

    if destination!=3:
        #订单满足约束
        model.addConstrs(
            (quicksum(LA[v,i] for v in range(vehicle_ub) )
            >=sku_demand[i] for i in range(len(sku_des)))
            , "order_limit")

    #只能选择一种车
    model.addConstr(VT.sum()==1,'only_one_vehicle')
    #LA_Bi：若LA!=0,则LA_Bi为0,若LA=0,则LA_Bi为1
    epsilon = 1e-6
    for v in range(vehicle_ub):
        for i in range(len(sku_des)):
            model.addConstr(LA[v, i] <= epsilon + M * (1 - LA_Bi[v, i]),'LA>0->LA_Bi=0')#LA=0,恒成立,当LA>0,则LA_Bi=0
            model.addConstr(LA[v, i] >= epsilon - M *LA_Bi[v, i],'LA=0->LA_Bi=1')#,当LA>0,恒成立,当LA=0,LA_Bi=1

    #车辆未激活时LA为0
    model.addConstrs((LA[v, i] <= IA[v] * sku_demand[i] for v in range(vehicle_ub) for i in range(len(sku_des))), f"active_loading_{v}_{i}")

    #hard constraint
    #上下限约束,约束量: vehicle_ub
    ULV=vehicles['Upper Limit Volume'].values
    ULW=vehicles['Upper Limit_Weight'].values
    model.addConstrs(
        (quicksum(LA[v,i]*demand_des.iloc[i]['Weight'] for i in range(len(sku_des)))
        <= quicksum(ULW[j]*VT[j] for j in range(4)) for v in range(vehicle_ub) ), name="upper_weight_limit")
    model.addConstrs(
        (quicksum(LA[v,i]*demand_des.iloc[i]['Volume'] for i in range(len(sku_des))) 
        <= quicksum(ULV[j]*VT[j] for j in range(4)) for v in range(vehicle_ub) ), "upper_volumn_limit")

    #soft constraint
    #每辆车的装车体积尽量不低于车辆载容下限。VD>0无所谓，VD<0就惩罚 Volume difference
    LLV=vehicles['Lower Limit Volume'].values
    VD_diff_expr=[(((
        quicksum(LA[v, i]*demand_des.iloc[i]['Volume'] for i in range(len(sku_des))) #第v个车的载量体积
                     -quicksum(LLV[j]*VT[j] for j in range(4))#该车的最小体积限制
                     ))) #若车辆没激活，此车不惩罚,想办法把IA加进去
                     for v in range(vehicle_ub)]
    #由于VD_diff_expr是二次还要×VD，gurobipy不能三次相乘，构造辅助变量VD_diff,约束其等于VD_diff_expr
    VD_diff=model.addVars(vehicle_ub,vtype=GRB.CONTINUOUS,name="VD_diff")
    model.addConstrs((VD_diff[v]==VD_diff_expr[v]*IA[v] for v in range(vehicle_ub)),'VD_diff=VD_diff_EXPR*IA') 
    VD_z=model.addVars(vehicle_ub, vtype=GRB.BINARY,name="VD_z")
    model.addConstrs(
        (VD_diff_expr[v]>=-M*VD_z[v] for v in range(vehicle_ub)),'VD<0->VD_z=1'#当VD>0,恒成立,当VD<0,则VD_z[v]=1
    )
    model.addConstrs(
        (VD_diff_expr[v]<=M*(1-VD_z[v]) for v in range(vehicle_ub)),'VD>0->VD_z=0'#当VD<0,恒成立,当VD>0,则VD_z[v]=0
    )
    #罚数是负的，目标：让他接近0，最大化
    VD_penalty_expr=PUNISHMENT_VD*quicksum(VD_diff[v]*VD_z[v] for v in range(vehicle_ub))
    #每辆车装载的SKU种类数量尽量不超过设定值。VN>0无所谓，VN<0就惩罚 Variety number
    sku_limit_des=skulimit.loc[skulimit['Source']==1,'Maximum SKU Count'].values[0]
    VN_diff_expr=[(len(sku_des)-quicksum(LA_Bi[v,i] for i in range(len(sku_des)))-sku_limit_des) for v in range(vehicle_ub)]
    VN_z=model.addVars(vehicle_ub, vtype=GRB.BINARY,name="VN_z")
    model.addConstrs(
        (VN_diff_expr[v]<=M*VN_z[v] for v in range(vehicle_ub)),'VN>0->VN_z=1'#当VN<0,恒成立,当VN>0,则VN_z[v]=1
    )
    model.addConstrs(
        (VN_diff_expr[v]>=-M*(1-VN_z[v]) for v in range(vehicle_ub)),'VN<0->VN_z=0'#当VN>0,恒成立,当VN<0,则VN_z[v]=0
    )

    #罚数是正的，目标：让他接近0，最小化, 若目标函数最大化，加个负号
    VN_penalty_expr=PUNISHMENT_VN*quicksum(VN_diff_expr[v]*VN_z[v] for v in range(vehicle_ub))
    #若destination==3,则尽量满足订单量需求，减小差的sku件数,num Diff
    if destination==3:
        ND_diff_expr=[sku_demand[i]-quicksum(LA[v,i] for v in range(vehicle_ub)) for i in range(len(sku_des)) ]
        ND_z=model.addVars(len(sku_des), vtype=GRB.BINARY,name="ND_z")
        model.addConstrs(
            (ND_diff_expr[i]<=M*ND_z[i] for i in range(len(sku_des))),'ND>0->ND_z=1'#当ND<0,恒成立,当ND>0,则ND_z[i]=1
        )
        model.addConstrs(
            (ND_diff_expr[i]>=-M*(1-ND_z[i]) for i in range(len(sku_des))),'ND<0->ND_z=0'#当ND>0,恒成立,当ND<0,则ND_z[i]=0
        )
         #destination3离运完大概差31746件
        #罚数是正的，目标：让他接近0，最小化, 若目标函数最大化，加个负号
        ND_penalty_expr=PUNISHMENT_ND*quicksum(ND_diff_expr[i]*ND_z[i] for i in range(len(sku_des)))
    else:
        ND_penalty_expr=0
    #目标函数: 
    # 1.发货量最大+车辆最少+SKU尽量集中装车
    # 2.VD.sum()最大化, -VN.sum()最大化
    # 3.-ND.sum()最大化
    obj2=-IA.sum()
    obj2=obj2/vehicle_ub
    obj3=quicksum(quicksum(LA_Bi[v,i] for i in range(len(sku_des))) for v in range(vehicle_ub))
    obj3=obj3/(len(sku_des)*vehicle_ub)

    model.setObjective((
        c2*obj2+
        c3*obj3+
        VD_penalty_expr+
        (-VN_penalty_expr)+
        (-ND_penalty_expr)
        ) ,GRB.MAXIMIZE)
    model.write('loading_optimization.rlp')
    model.update()
    if lr_solution is not None:
        set_start_values(model,lr_solution)
    model.update()
    model.setParam('TimeLimit', time)
    model.optimize()

    # 输出小目标值
    if model.status == GRB.OPTIMAL:
        print("Optimal solution found:")

    obj2_value =c2*( -sum(IA[v].X for v in range(vehicle_ub))/vehicle_ub )
    obj3_value =c3*( sum(LA_Bi[v, i].X for v in range(vehicle_ub) for i in range(len(sku_des)))/(len(sku_des)*vehicle_ub))
    VD_diff_expr=[(quicksum(LA[v, i].X*demand_des.iloc[i]['Volume'] for i in range(len(sku_des)))-quicksum(LLV[j]*VT[j].X for j in range(4)))*IA[v].X for v in range(vehicle_ub)]
    VN_diff_expr=[(len(sku_des)-quicksum(LA_Bi[v,i].X for i in range(len(sku_des)))-sku_limit_des) for v in range(vehicle_ub)]
    VD_penalty_expr_value=PUNISHMENT_VD*sum(VD_diff_expr[v]*VD_z[v].X for v in range(vehicle_ub))
    VN_penalty_expr_value=-PUNISHMENT_VN*sum(VN_diff_expr[v]*VN_z[v].X for v in range(vehicle_ub))
    print('最大化以下：')
    print(f"obj2 value: {obj2_value}")
    print(f"obj3 value: {obj3_value}")
    print(f"VD_penalty_expr value: {VD_penalty_expr_value}")
    print(f"VN_penalty_expr value: {VN_penalty_expr_value}")
    if destination==3:
        ND_diff_expr=[sku_demand[i]-quicksum(LA[v,i].X for v in range(vehicle_ub)) for i in range(len(sku_des)) ]
        ND_penalty_expr_value=-PUNISHMENT_ND*sum(ND_diff_expr[i]*ND_z[i].X for i in range(len(sku_des)))
        print(f"ND_penalty_expr value: {ND_penalty_expr_value}")
    print(f"目标函数值: {model.objVal}")
    VT_values = model.getAttr('x', VT)
    for k in range(len(vehicle_types)):
        if VT_values[k]!=0:
            print(f'模型选择了车型{k+1}')
    IA_values = model.getAttr('x', IA)
    print(f'模型激活了{sum(IA_values[i] for i in range(vehicle_ub))}量车')
    LA_values = model.getAttr('x', LA)
    v_list=[]
    sku_list=[]
    for v in range(vehicle_ub): #注意，有可能不激活的车也装载了，也有可能不。请后续检查
        v_list.append(v)
        lst=[]
        for i in range(len(sku_des)):
            lst.append(LA_values[(v,i)])
        sku_list.append(lst)
    LA_Bi_values = model.getAttr('x', LA_Bi)
    VC=[]#Variety Count
    for v in range(vehicle_ub):
        VC.append(len(sku_des)-sum(LA_Bi_values[(v,i)]for i in range(len(sku_des))))
    with pd.ExcelWriter(rf'result/loading_D{destination}.xlsx') as writer:
        pd.DataFrame(np.array(sku_list)).to_excel(writer, sheet_name='Loading_amount', index=True,header=sku_des)
        pd.DataFrame(np.array(VC)).to_excel(writer, sheet_name='sku_variety_count', index=True)                      
        pd.DataFrame(np.array(sku_list).sum(axis=0).reshape(1,-1)).to_excel(writer, sheet_name='SKU_amount', index=True,header=sku_des)  