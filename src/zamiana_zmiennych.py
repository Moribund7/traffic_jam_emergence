n=10 #liczba samochodow
t=0.5 #s
v_0 = 36 #km/h
R = 5*n #m
a_min = -9 #m/s**2 maksymalne hamowania
a_avg = 1.5 #m/s**2


omega=(v_0*t)/(R*3.6)
epsilon_min=abs(a_min*t*t/R)
epsilon_avg=abs(a_avg*t*t/R)