import numpy as np
from izracun import *
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [9, 6]
plt.rc('font', size=14)

# Branje, obdelava podatkov:
podatki = np.loadtxt("tocke.txt")
podatki = podatki.reshape([24, 11])
prt 	= 0

izmerjene = np.array([])
for i in podatki:
	izmerjene = np.append(izmerjene, i[-3:]) 
izmerjene = izmerjene.reshape(24, 3)
izmerjene[:, 0] = izmerjene[:, 0] - podatki[:, 7]

# Izracun:
rezultati = np.array([])  
for i in podatki:
	rezultati = np.append(rezultati, (izracun(i, "R600A", prt)))
rezultati = rezultati.reshape(24, 4)
rezultati[:, 1] = rezultati[:, 1] - podatki[:, 7]

napake = np.array([]) 
for i in range(0, len(rezultati)):
	for j in range(0, 3):	
		napake = np.append(napake, abs((rezultati[i][j+1] - izmerjene[i][j]) / izmerjene[i][j]) * 100)
napake = napake.reshape(24, 3)

# Izpis relativnih napak:
print("-------T_s_o-----------w-----------eps-------")
print(napake)

# Izris diagramov (shrani v ./slike)
p1 = np.array([0, 36])
o = np.array(["razlika temperatur [K]", "masni tok [kg/s]", "izkoristek prenosnika [%]" ])
for i in range(0, 3):
	x = izmerjene[:, i]
	y = rezultati[:, i+1]
	p1y = np.linspace(min(y) * 0.3, max(y)*1.9, 100)
	p1x = 1.1 * p1y
	p2y = np.linspace(min(y) * 0.3, max(y)*1.9, 100)
	p2x = 0.9 * p2y

	plt.figure()
	plt.plot(x, y, "bo");
	plt.plot(p1x, p1y, "k-", label="+/- 10%");
	plt.plot(p2x, p2y, "k-");
	plt.xlim(min(y) * 0.7, max(y) * 1.3)
	plt.ylim(min(y) * 0.7, max(y) * 1.3)
	plt.xlabel(f"Izračunani podatki, {o[i]}")
	plt.ylabel(f"Izmerjeni podatki, {o[i]}")
	plt.legend()
	plt.grid();
	plt.savefig(f"./slike/graf{i}.png");


# Stevilo meritev, ki odstopajo za vec kot 10%:
napakeT	= np.transpose(napake)
cez_10 	= np.array([])  
avg 	= np.array([])  
n 	= 0

for i in napakeT:
	for j in range(0, len(napakeT[0])):
		if(i[j]	>= 10):	n = n+1
	
	avg 	= np.append(avg, sum(i) / len(i)) 
	cez_10 	= np.append(cez_10, n) 
	n = 0

print("Povprečno odstopanje:", avg)
print("Št. odstopanj čez 10%:", cez_10)

