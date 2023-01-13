import casbin
from dataObject import Object

#Future work: SSI-based access control?
#Using simple policy: if data object field Owner is the same as subject, allow
path_conf = 'abac.conf'
e = casbin.Enforcer(path_conf)

#p, rafael, paper, read
#p, benedikt, paper, write
obj = Object('data1','rafael')
obj2 = Object('data2','benedikt')

sub = "rafael"  # the user that wants to access a resource.

act = "read"  # the operation that the user performs on the resource.



print(sub, 'is trying to access', obj, 'whose owner is', obj.owner, 'abac yields', e.enforce(sub, obj, act))
print(sub, 'is trying to access', obj2, 'whose owner is', obj2.owner, 'abac yields', e.enforce(sub, obj2, act))

if e.enforce(sub, obj, act):
    #give access to resource
    pass
else:
    # deny the request, show an error
    pass



