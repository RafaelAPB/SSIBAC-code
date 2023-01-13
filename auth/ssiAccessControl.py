import casbin
from dataObject import Object
from subject import Subject
from dataObject import ObjectSSI

path_conf = 'abacSSI.conf'
e = casbin.Enforcer(path_conf)

#Subject wants to access object that requires him to prove certain attributes; Subject wants to access object whereby the proof follows a certain schema
#We  want to identify each subject by their did
sub = Subject('did:sov:rafael')

#The decision field corresponds to the proof verification status. Can be true or false.
obj = ObjectSSI('did','true')
obj2 = ObjectSSI('did','false')
act = 'read'


if e.enforce(sub, obj, act):
    print("allow")
    pass
else:
    print("deny")
    pass
