import casbin
import time
from dataObject import Object
import matplotlib
import matplotlib.pyplot as plt

#SIMPLE POLICY, PI1
path_conf = 'abac.conf'
path_conf_10 = 'abac_10.conf'
path_conf_100 = 'abac_100.conf'
e = casbin.Enforcer(path_conf)
#e10 = casbin.Enforcer(path_conf_10)
#e100 = casbin.Enforcer(path_conf_100)
iteration_number = [1,10,100,1000,10000,1000000]
execution_times = []
iterations_per_second = []
#p, rafael, paper, read
obj = Object('data1','rafael')
sub = "rafael"  # the user that wants to access a resource.
act = "read"  # the operation that the user performs on the resource.

for i in iteration_number:
    start = time.time()
    for j in range(0, i):
        e.enforce(sub, obj, act)
    end = time.time()
    total_time = end - start

    print("Time for " , i, " iterations: ", total_time)
    execution_times.append(total_time)
    print(end - start)
    print(i/total_time, " iterations per second")
    iterations_per_second.append(int(i/total_time))

fig, ax = plt.subplots()
ax.plot(execution_times, iteration_number)

ax.set(xlabel='time (s)', ylabel='access control requests')
ax.grid()

fig.savefig("test.png")
plt.show()



