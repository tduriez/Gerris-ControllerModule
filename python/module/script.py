
def ff(forcesList,locList):
	print "Inside defined ff function"
	print len(forcesList)
	if len(forcesList) > 0:
		force = forcesList[0]
		print force.data.pf[0]
		return force.data.pf[0]
	return 1

def myfunc(f,l):
	return 2

