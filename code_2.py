def T_avg(x):
    if 0<=x and x<=1:
        return 1
    elif 1<x and x<1.5:
        return (1.5-x)/0.5
    else:
        return 0

def T_max(x):
    if 0<=x and x<=1.5:
        return 1
    elif 1.5<x and x<2:
        return (2-x)/0.5

    else:
        return 0


def R_high(x):
    if 0<=x and x<=0.98:
        return 0
    elif 0.98<x and x<1:
        return (x-0.98)/0.02
    else:
        return 1
t_avg=0.5
t_tag=1.5
t_max=0




T=[0]*25
t_m=0
t_max=max(T)
t_avg=sum(T)/25
for i in range(25):
    if T[i]<t_tag:
        t_m=t_m+1/25

        
t_avg=1.44
t_max=1.85
t_m=0.6
t_avg1=T_avg(t_avg)
t_max1=T_max(t_max)
R_high1=R_high(t_m)




m=0.444*t_avg1 +0.084*t_max1+0.472*R_high1
print(m)
if m<0.5:
    m=0
else:
    m=1


