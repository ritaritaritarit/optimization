# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 03:06:47 2021

@author: Rita
"""
#data:
Demandin10years=[[1000,1200,1800,1200,1000,1400,1600,1000],
                 [1200,1440,2250,1440,1200,1750,2000,1440],
                 [1400,1680,2700,1680,1400,2100,2400,1680],
                 [1600,1920,3150,1920,1600,2450,2800,1920],
                 [1800,2160,3600,2160,1800,2800,3200,2160],
                 [2000,2400,4050,2400,2000,3150,3600,2400],
                 [2200,2640,4500,2640,2200,3500,4000,2640],
                 [2400,2880,4950,2880,2400,3850,4400,2880],
                 [2600,3120,5400,3120,2600,4200,4800,3120],
                 [2800,3360,5850,3360,2800,4550,5200,3360]]#10*8
Capacity=[16000,12000,14000,10000,13000] #units
Construction_Cost=[2000,1600,1800,900,1500]# (1000's of $)
AnnualOperating_Cost =[420,380,460,280,340] # (1000's of $)
Reopening_Cost=[190,150,160,100,130] # (1000's of $)
Shutdown_Cost=[170,120,130,80,110] # (1000's of $)
year1_plant_to_warehouse = [[0.12,0.13,0.08,0.05],[0.1,0.03,0.1,0.09],[0.05,0.07,0.06,0.03],[0.06,0.03,0.07,0.07],[0.06,0.02,0.04,0.08]]
Whtocust= [[0.09,0.1,0.06,0.05,0.08,0.09,0.02,0.12],[0.05,0.07,0.12,0.04,0.03,0.09,0.03,0.08],[0.06,0.09,0.07,0.09,0.09,0.04,0.11,0.07],[0.07,0.08,0.09,0.06,0.1,0.07,0.06,0.09]]

def creat(n):
    result=[]
    result.append(n)
    for i in range(9):
        n = 1.03*n
        result.append(n)
    return(result)

def count_cost1(list1):
    result =[]
    result.append(list1)
    for n in range(1,10):
        ep_list1 =[]
        for i in list1:
            ep_list1.append(i* (1.03 ** n))
        result.append(ep_list1)
    return(result)
    
def count_cost2(list1):
    result =[]
    result.append(list1)
    for n in range(1,10):
        ep_list1 =[]
        for i in list1:
            ep_list2 = []
            for j in i:
                ep_list2.append(j * (1.03 ** n))
            ep_list1.append(ep_list2)
        result.append(ep_list1)
    return(result)

def combine(list1,list2):
    result =[]
    for i in range(len(list1)):
        tem =[]
        for j in range(len(list1[i])):
            tem.append(list1[i][j]+list2[i][j])
        result.append(tem)
    return result
            
#index for all
year=range(len(Demandin10years))
#year=[0,1,2,3,4,5,6,7,8,9]#i=10
plant=[0,1,2,3,4]#j=5
warehouse=[0,1,2,3]#k=4
retailcenter= [0,1,2,3,4,5,6,7]#r=8

#data for productline
Construction_Cost10 = count_cost1(Construction_Cost)#10*5
AnnualOperating_Cost10 = count_cost1(AnnualOperating_Cost)
Reopening_Cost10 = count_cost1(Reopening_Cost)
Shutdown_Cost10 = count_cost1(Shutdown_Cost)
com_cons_reop = combine(Construction_Cost10,Reopening_Cost10)#combine construction and reopening cost

Capacity#at 5 plant
Demandin10years #10year*8retailcenter
#data for warehouse
pltowh10 = count_cost2(year1_plant_to_warehouse)#10*5*4
whtocust10 = count_cost2(Whtocust)#10*4*8
#data for material
alloy = creat(0.02)
widget = creat(0.15)
widgetcheap= creat(0.12)

import gurobipy as gb
from gurobipy import GRB

# create model
m = gb.Model()

#add variables
#productionlinevariables:(as well as objectives)
openvar=m.addVars(year,plant,vtype=GRB.BINARY,obj=AnnualOperating_Cost10,name="openvar")
construction=m.addVars(year,plant,vtype=GRB.BINARY,obj=Construction_Cost10,name="construction")
shutdown=m.addVars(year,plant,vtype=GRB.BINARY,obj=Shutdown_Cost10,name="shutdown")
reopen=m.addVars(year,plant,vtype=GRB.BINARY,obj=Reopening_Cost10,name="reopen")
Fvars=m.addVars(year,plant,vtype=GRB.CONTINUOUS,lb=0,name="Fvars")#product flugel at each plant for eachyear
MM=m.addVar(obj=1)###tie the object together

#warehousevariables:
WFvars=m.addVars(year,plant,warehouse,vtype=GRB.CONTINUOUS,lb=0,obj=pltowh10,name="WF")#10*5*4#
WFOvars=m.addVars(year,warehouse,retailcenter,vtype=GRB.CONTINUOUS,lb=0,obj=whtocust10,name="WFO")#
svars=m.addVars(year,warehouse,vtype=GRB.CONTINUOUS,lb=0,name="svars")#Sik=units of flugel saved as stock in the warehouse k in year i

#materialvariables:
alpha1=m.addVars(year,plant,vtype=GRB.CONTINUOUS,lb=0,name="alpha1")#controlwidgetcost
alpha2=m.addVars(year,plant,vtype=GRB.CONTINUOUS,lb=0,name="alpha2")#controlwidgetcost
alpha3=m.addVars(year,plant,vtype=GRB.CONTINUOUS,lb=0,name="alpha3")#controlwidgetcost
w1=m.addVars(year,plant,vtype=GRB.BINARY,name="w1")#controlwidgetcost
w2=m.addVars(year,plant,vtype=GRB.BINARY,name="w2")#controlwidgetcost

#objective:
#product objective: is above
#add 2 material objective:
m.addConstr(MM==sum(0*alpha1[i,j]+9000*widget[i]*alpha2[i,j]+(9000*widget[i]+39000*widgetcheap[i])*alpha3[i,j] for i in year for j in plant)+sum(Fvars[i,j]*4.7*alloy[i] for i in year for j in plant))

#minimize
m.modelSense = GRB.MINIMIZE

# add constraints
#plant constraints
#open:
m.addConstrs((construction.sum(i,'*')<=1 for i in year for j in plant ) ,"construction will only happen once at most for 10 year period for each line")
m.addConstrs((openvar[0,j] == construction[0,j] for j in plant ) ,"newly constructed year1")
m.addConstrs((openvar[1,j] == (construction[0,j]+construction[1,j]) for j in plant ) ,"newly constructed year2")
#for 2-10
m.addConstrs((openvar[2,j]== (construction[0,j]+construction[1,j]+construction[2,j]) for j in plant ) ,"newly constructed")
m.addConstrs((openvar[3,j]== (construction[0,j]+construction[1,j]+construction[2,j]+construction[3,j]) for j in plant ) ,"newly constructed")
m.addConstrs((openvar[4,j]== (construction[0,j]+construction[1,j]+construction[2,j]+construction[3,j]+construction[4,j]) for j in plant ) ,"newly constructed")
m.addConstrs((openvar[5,j]== (construction[0,j]+construction[1,j]+construction[2,j]+construction[3,j]+construction[4,j]+construction[5,j]) for j in plant ) ,"newly constructed")
m.addConstrs((openvar[6,j]== (construction[0,j]+construction[1,j]+construction[2,j]+construction[3,j]+construction[4,j]+construction[5,j]+construction[6,j]) for j in plant ) ,"newly constructed")
m.addConstrs((openvar[7,j]== (construction[0,j]+construction[1,j]+construction[2,j]+construction[3,j]+construction[4,j]+construction[5,j]+construction[6,j]+construction[7,j]) for j in plant ) ,"newly constructed")
m.addConstrs((openvar[8,j]== (construction[0,j]+construction[1,j]+construction[2,j]+construction[3,j]+construction[4,j]+construction[5,j]+construction[6,j]+construction[7,j]+construction[8,j]) for j in plant ) ,"newly constructed")
m.addConstrs((openvar[9,j]== (construction[0,j]+construction[1,j]+construction[2,j]+construction[3,j]+construction[4,j]+construction[5,j]+construction[6,j]+construction[7,j]+construction[8,j]+construction[9,j]) for j in plant ) ,"newly constructed")

#shutdown
m.addConstrs((shutdown[0,j]==0 for j in plant ) ,"Shutdown")#shutdown cannot happen in year 1
m.addConstrs(((openvar[0,j]-openvar[1,j])<= (shutdown[1,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[1,j]-openvar[2,j])<= (shutdown[2,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[2,j]-openvar[3,j])<= (shutdown[3,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[3,j]-openvar[4,j])<= (shutdown[4,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[4,j]-openvar[5,j])<= (shutdown[5,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[5,j]-openvar[6,j])<= (shutdown[6,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[6,j]-openvar[7,j])<= (shutdown[7,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[7,j]-openvar[8,j])<= (shutdown[8,j]) for j in plant ) ,"Shutdown")
m.addConstrs(((openvar[8,j]-openvar[9,j])<= (shutdown[9,j]) for j in plant ) ,"Shutdown")

#reopen cannot happen in year 1 and 2:
m.addConstrs((reopen[0,j]==0 for j in plant ) ,"reopen")
m.addConstrs((reopen[1,j]==0 for j in plant ) ,"reopen")
#reopen for year 3-10
m.addConstrs(((openvar[2,j]-openvar[1,j])<= (reopen[2,j]+construction[2,j]) for j in plant ) ,"reopen")
m.addConstrs(((openvar[3,j]-openvar[2,j])<= (reopen[3,j]+construction[3,j]) for j in plant ) ,"reopen")
m.addConstrs(((openvar[4,j]-openvar[3,j])<= (reopen[4,j]+construction[4,j]) for j in plant ) ,"reopen")
m.addConstrs(((openvar[5,j]-openvar[4,j])<= (reopen[5,j]+construction[5,j]) for j in plant ) ,"reopen")
m.addConstrs(((openvar[6,j]-openvar[5,j])<= (reopen[6,j]+construction[6,j]) for j in plant ) ,"reopen")
m.addConstrs(((openvar[7,j]-openvar[6,j])<= (reopen[7,j]+construction[7,j]) for j in plant ) ,"reopen")
m.addConstrs(((openvar[8,j]-openvar[7,j])<= (reopen[8,j]+construction[8,j]) for j in plant ) ,"reopen")
m.addConstrs(((openvar[9,j]-openvar[8,j])<= (reopen[9,j]+construction[9,j]) for j in plant ) ,"reopen")

#reopen for year 3-10 additionally
m.addConstrs(((reopen[2,j]+construction[2,j])<=1 for j in plant ) ,"reopen")
m.addConstrs(((reopen[3,j]+construction[3,j])<=1 for j in plant ) ,"reopen")
m.addConstrs(((reopen[4,j]+construction[4,j])<=1 for j in plant ) ,"reopen")
m.addConstrs(((reopen[5,j]+construction[5,j])<=1 for j in plant ) ,"reopen")
m.addConstrs(((reopen[6,j]+construction[6,j])<=1 for j in plant ) ,"reopen")
m.addConstrs(((reopen[7,j]+construction[7,j])<=1 for j in plant ) ,"reopen")
m.addConstrs(((reopen[8,j]+construction[8,j])<=1 for j in plant ) ,"reopen")
m.addConstrs(((reopen[9,j]+construction[9,j])<=1 for j in plant ) ,"reopen")

m.addConstrs(((reopen[i,j]+construction[i,j])<=1 for i in year for j in plant ) ,"reopen and construction cannot happen in same year")
m.addConstrs(((openvar[i,j]+shutdown[i,j])<=1 for i in year for j in plant ) ,"open and shutdown cannot happen in same year")
m.addConstrs((reopen.sum('*',j)<=4 for i in year for j in plant ) ,"reopen cannot exceeds 4 times for one plant in 10 years")
#reopen cannot happen if no shutdown
m.addConstrs((reopen.sum('*',j)<=shutdown.sum('*',j) for i in year for j in plant ) ,"reopen cannot happen if no shutdown")


#warehouse constaints:
#Capacitycontrol
m.addConstrs((Fvars[i,j]<= (Capacity[j]*openvar[i,j]+Capacity[j]*construction[i,j]+Capacity[j]*reopen[i,j]) for i in year for j in plant ) ,"Capacitycontrol")
#if close, should not produce any:9000000000 is a random big enough figure
m.addConstrs((Fvars[i,j]<=9000000000*openvar[i,j] for i in year for j in plant for k in warehouse) ,"flow into warehouse") #for each plant j all flow into 4 warehouse
#every year flow into warehouse should equals to each plant produce
m.addConstrs((Fvars[i,j]==WFvars.sum(i,j,'*') for i in year for j in plant for k in warehouse) ,"flow into warehouse") #for each plant j all flow into 4 warehouse
#last year inventory will be 0
m.addConstrs((svars[9,k]==0 for k in warehouse),"last year inventory will be 0")
#meet demand
m.addConstrs((WFOvars.sum(i,'*',r)==Demandin10years[i][r] for i in year for k in warehouse for r in retailcenter),"meet demand")
#first year do not have inventory from before
m.addConstrs((WFvars.sum(0,'*',k)==(WFOvars.sum(0,k,'*')+svars[0,k]) for j in plant for k in warehouse for r in retailcenter),"first year do not have inventory from before")
#2-10 years for each warehouse inventory should be balance
m.addConstrs(((WFvars.sum(1,'*',k)+svars[0,k])==(WFOvars.sum(1,k,'*')+svars[1,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(2,'*',k)+svars[1,k])==(WFOvars.sum(2,k,'*')+svars[2,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(3,'*',k)+svars[2,k])==(WFOvars.sum(3,k,'*')+svars[3,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(4,'*',k)+svars[3,k])==(WFOvars.sum(4,k,'*')+svars[4,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(5,'*',k)+svars[4,k])==(WFOvars.sum(5,k,'*')+svars[5,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(6,'*',k)+svars[5,k])==(WFOvars.sum(6,k,'*')+svars[6,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(7,'*',k)+svars[6,k])==(WFOvars.sum(7,k,'*')+svars[7,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(8,'*',k)+svars[7,k])==(WFOvars.sum(8,k,'*')+svars[8,k]) for k in warehouse),"for each warehouse inventory should be balance")
m.addConstrs(((WFvars.sum(9,'*',k)+svars[8,k])==WFOvars.sum(9,k,'*') for k in warehouse ),"for each warehouse inventory should be balance")

#m.addConstrs(((WFvars.sum(9,'*',k)+svars[8,k])==(WFOvars.sum(9,k,'*')+svars[9,k]) for year[9] in year for j in plant for k in warehouse for r in retailcenter),"for each warehouse inventory should be balance")
m.addConstrs((svars[i,k]<=12000 for i in year for k in warehouse),"maximum for a warehouse to handle")
m.addConstrs((WFvars.sum(i,'*',k)<=12000 for i in year for j in plant for k in warehouse),"each warehouse max flow in")
m.addConstrs((WFOvars.sum(i,k,'*')<=12000 for i in year for k in warehouse for r in retailcenter),"each warehouse max flow out")

#for 2-10 years ave inventory not exceed 4000:
m.addConstrs(((svars[0,k]+svars[1,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[1,k]+svars[2,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[2,k]+svars[3,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[3,k]+svars[4,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[4,k]+svars[5,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[5,k]+svars[6,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[6,k]+svars[7,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[7,k]+svars[8,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs(((svars[8,k]+svars[9,k])<=4000*2 for k in warehouse),"ave inventory not exceed 4000")
m.addConstrs((svars[0,k]<=4000*2 for k in warehouse),"first year ave inventory not exceed 4000")

#material constaints:
m.addConstrs((Fvars[i,j]*4.7<=60000 for i in year for j in plant),"max lbs of alloy per year at each plant j")
m.addConstrs((Fvars[i,j]==0*alpha1[i,j]+3000*alpha2[i,j]+16000*alpha3[i,j] for i in year for j in plant),"for wiget assembly at each plant j used")
m.addConstrs((alpha1[i,j]+alpha2[i,j]+alpha3[i,j]==1 for i in year for j in plant), "control wiget assembly")
m.addConstrs((w1[i,j]+w2[i,j]==1 for i in year for j in plant), "control wiget assembly")
m.addConstrs((alpha1[i,j]<=w1[i,j] for i in year for j in plant), "control wiget assembly")
m.addConstrs((alpha2[i,j]<=w1[i,j]+w2[i,j] for i in year for j in plant), "control wiget assembly")
m.addConstrs((alpha3[i,j]<=w2[i,j] for i in year for j in plant), "control wiget assembly")

m.optimize()
m.write ("finalflugel.lp")

#for v in m.getVars():
  # print('%s %g' % (v.Fvars, v.x))
  
#for v in m.getVars():
#    print(v.x)

#print(m.getAttr(GRB.Attr.X, m.getVars()))

print(m.getAttr('VarName', m.getVars()), m.getAttr('x', m.getVars()))

'''
print('SOLUTION:')
for i in year:
    if constructioncondition[i].x > 0.99:
        print('Plant %s open' % (i+1))
        for j in plant:
            if Fvars[i,j].x > 0:
                print('Transport %g units to warehouse %s' % ((Fvars[i,j].x, (j+1))))
    else:
        print('Plant %s closed' % (i+1))

'''
print('\n\n\nINVENTORY:')
for i in year:
    for k in warehouse:
        print('For year %g, warehouse %s has %g units to of inventory.' % (((i+1),(k+1),svars[i,k].x)))

print("Obj: ",m.objVal)