from solve import solve
if __name__=='__main__':
    destination=3
    if destination==3:
        c1=1 #deprecated
        c2=1 #车辆最少
        c3=2  #车辆SKU种类最少,最大是c3
        PUNISHMENT_VD=1e-3 #尽量大于最小体积
        PUNISHMENT_VN=1e-2  #车载SKU种类尽量不超过限制
        PUNISHMENT_ND=50/31746   #针对destinaion 3, 尽量满足订单需求
        solve(destination=destination,c1=c1,c2=c2,c3=c3,PUNISHMENT_VD=PUNISHMENT_VD,
            PUNISHMENT_VN=PUNISHMENT_VN,PUNISHMENT_ND=PUNISHMENT_ND)
    else:
        c1=1 #deprecated
        c2=1 #车辆最少
        c3=1  #车辆SKU种类最少,最大是1
        PUNISHMENT_VD=1e-3 #尽量大于最小体积
        PUNISHMENT_VN=1e-5  #车载SKU种类尽量不超过限制
        #PUNISHMENT_ND=1/31746   #针对destinaion 3, 尽量满足订单需求
        solve(destination=destination,c1=c1,c2=c2,c3=c3,PUNISHMENT_VD=PUNISHMENT_VD,
            PUNISHMENT_VN=PUNISHMENT_VN)
    
#对于destination3: ND>c3>VN=VD>c2
#对于destination124: c2>c3>VD=VN