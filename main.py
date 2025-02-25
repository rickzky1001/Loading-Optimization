from solve import solve
from Linear_Relaxation import lr_solve
from utils.lr_solution_process import lr_solution_process
import sys
import pickle
if __name__=='__main__':
    for destination in [1]:
        if destination==3:
            c1=1 #deprecated
            c2=1 #车辆最少
            c3=2  #车辆SKU种类最少,最大是c3
            PUNISHMENT_VD=1e-3 #尽量大于最小体积
            PUNISHMENT_VN=1e-2  #车载SKU种类尽量不超过限制
            PUNISHMENT_ND=50/31746   #针对destinaion 3, 尽量满足订单需求

            with open(rf'result/lr_solution_D{destination}_f.pkl', 'rb') as file:  # 注意使用二进制模式读取
                lr_solution_raw = pickle.load(file) 
            lr_solution=lr_solution_process(lr_solution_raw,destination=destination)
            solve(time=3000,lr_solution=lr_solution,destination=destination,c2=c2,c3=c3,PUNISHMENT_VD=PUNISHMENT_VD,PUNISHMENT_VN=PUNISHMENT_VN,PUNISHMENT_ND=PUNISHMENT_ND)
        else:
            # lr_solve(time=8500,destination=destination,c2=30,c3=5,PUNISHMENT_VD=1e-3,PUNISHMENT_VN=1e-2)
            # with open(rf'result/lr_solution_D{destination}.pkl', 'rb') as file:  # 注意使用二进制模式读取
            #     lr_solution = pickle.load(file) 
            solve(time=98500,lr_solution=None,destination=destination,c2=30,c3=5,PUNISHMENT_VD=1e-3,PUNISHMENT_VN=1e-2)
    
#对于destination3: ND>c3>VN=VD>c2
#对于destination124: c2>c3>VD=VN