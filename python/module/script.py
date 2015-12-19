lastFF = 0.6
lastFF2 = 0.1
lastDrag = 0.1

def ffForce(forcesList,locList):
	global lastFF
	global lastFF2
	global lastDrag
	if len(forcesList) > 0:
		force = forcesList[0]
		drag = force.data.pf[0]*force.data.pf[0] + force.data.vf[0]*force.data.pf[0]
		if drag != lastDrag:
			ff = lastFF -  (drag - lastDrag) / (lastFF - lastFF2)
			lastFF2 = lastFF
			lastFF = ff
			lastDrag = drag 
		return lastFF
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
