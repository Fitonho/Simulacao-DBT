import numpy as np


cols= nX = 392
rows= nY = 316
depth= nZ = 1027

phantom = np.fromfile("phantom.bin", dtype=np.float32)
phantom = phantom.reshape((cols, rows, depth))

##
# Escreva o código aqui
##
dx = 0.2
dy = 0.2
dz = 1

Xp1 = -(392/2)*dx #xpmax = (392/2)*dx
Yp1 = 0 #ypmax = 316*0.2 = 63.2
Zp1 = 0 #zpmax = 1027

def X(a, x1, x2):
    return x1 + a*(x2-x1)
def Y(a, y1,y2):
    return y1 + a*(y2-y1)
def Z(a,z1,z2):
    return z1 + a*(z2-z1)

def xPlano(i):
    return Xp1 + (i-1)*dx
def yPlano(j):
    return Yp1 + (j-1)*dy
def zPlano(k):
    return Zp1 + (k-1)*dz
#!acertar divisão por 0
def aX(n , x1 , x2):
    return (xPlano(n)-x1)/(x2-x1)
def aY(n, y1, x2):
    return (yPlano(n)-y1)/(y2-y1)
def aZ(n, z1, z2):
    return (zPlano(n)-z1)/(z2-z1)

#para cada raio:
x1 = 0
y1 = 0
z1 = 700
x2 = 10
y2 = 10
z2 = 0


#pegar pontos minimo e máximo de intersecção do raio com o phantom
aMin = np.amax([0, np.amin([aX(1,x1,x2),aX(cols,x1,x2)]), np.amin([aY(1,y1,y2),aY(rows,y1,y2)]), np.amin([aZ(1,z1,z2),aZ(depth,z1,z2)])])
aMax = np.amin([1, np.amin([aX(1,x1,x2),aX(cols,x1,x2)]), np.amin([aY(1,y1,y2),aY(rows,y1,y2)]), np.amin([aZ(1,z1,z2),aZ(depth,z1,z2)])])
if(aMax<= aMin):
    print('para td, n intercepta')
#descobrir os indices i,j,k que estão entre aMin e aMax:
if (x2-x1)>=0:
    iMin = nX - (xPlano(nX) - aMin * (x2-x1) - x1)/dx
    iMax = 1 + (x1 + aMax * (x2 - x1) - xPlano(1))/dx
else:
    iMin = nX - (xPlano(nX) - aMax * (x2-x1) -x1)/dx
    iMax = 1 + (x1 + aMin * (x2 - x1) - xPlano(1))/dx
if (y2-y1)>=0:
    jMin = nY - (yPlano(nY) - aMin * (y2-y1) - y1)/dy
    jMax = 1 + (y1 + aMax * (y2 - y1) - yPlano(1))/dy
else:
    jMin = nY - (yPlano(nY) - aMax * (y2-y1) -y1)/dy
    jMax = 1 + (y1 + aMin * (y2 - y1) - yPlano(1))/dy
if (z2-z1)>=0:
    kMin = nZ - (zPlano(nZ) - aMin * (z2-z1) - z1)/dz
    kMax = 1 + (z1 + aMax * (z2 - z1) - zPlano(1))/dz
else:
    kMin = nZ - (zPlano(nZ) - aMax * (z2-z1) -z1)/dz
    kMax = 1 + (z1 + aMin * (z2 - z1) - zPlano(1))/dz

#agora, com os indices minimos e maximos encontrados,
#achar o alpha de cada um
#*se der caca, pode ser o sort()
alphas = [aMin]

for i in range(int(iMin),int(iMax+1)):
    alphas.append(aX(i,x1,x2))
for j in range(int(iMin),int(iMax+1)):
    alphas.append(aY(i,y1,y2))
for k in range(int(iMin),int(iMax+1)):
    alphas.append(aZ(i,z1,z2))
alphas.append(aMax)
alphas.sort()

n = (iMax-iMin+1)+(jMax-jMin+1)+(kMax-kMin+1)+1

d = 0
length = np.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
print(n)
for m in range(1,int(n)):
    print('rodou o for')
    aMid = (alphas[m] + alphas[m-1])/2
    im = 1+ (x1 + aMid *(x2-x1) - xPlano(1))/dx
    jm = 1+ (y1 + aMid *(y2-y1) - yPlano(1))/dy
    km = 1+ (z1 + aMid *(z2-z1) - zPlano(1))/dz
    d+= (alphas[m]-alphas[m-1])*phantom[im][jm][km]
d*=length

print(d)