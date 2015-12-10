
def ffForce(forcesList,locList):
	print "Inside defined ff function"
	print len(forcesList)
	if len(forcesList) > 0:
		force = forcesList[0]
		print force.data.pf[0]
		return force.data.pf[0]
	return 1

def ffpos(forcesList,locList):
	print "Inside defined ffpos function"
	print len(locList)
	if len(locList) > 0:
		step1 = locList[0]
		varU = step1.data.varMap["U"]
		suma = 0
		for pos in varU:
			suma += pos[1]
			print pos[1]
		return suma
	return 1

def myfunc(f,l):
	return 2

def bobo(f,l):
	return 0.6;
