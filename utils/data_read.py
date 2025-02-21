import pandas as pd
def read():
    orders=pd.read_excel('data.xlsx', sheet_name=0)
    vehicles=pd.read_excel('data.xlsx', sheet_name=1)
    skulimit=pd.read_excel('data.xlsx', sheet_name=2)
    sku=pd.read_excel('data.xlsx', sheet_name=3)
    other=pd.read_excel('data.xlsx', sheet_name=4)
    return orders,vehicles,skulimit,sku,other
if __name__=='__main__':
    print(read()[1])