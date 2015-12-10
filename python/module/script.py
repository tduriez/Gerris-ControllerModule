
def ffForce(forcesList,locList):
	if len(forcesList) > 0:
		force = forcesList[0]
		return force.data.pf[0]
	return 1

def ffpos(forcesList,locList):
	if len(locList) > 0:
		step1 = locList[0]
		varU = step1.data.varMap["U"]
		suma = 0
		for pos in varU:
			suma += pos[1]
		return suma
	return 1

def myfunc(f,l):
	return 2

def bobo(f,l):
	return 0.6;
