import numpy as np
from PIL import Image

#assumindo que 
# rows = eixo X
# depth = eixo Y
# cols = eixo Z
rows= nX = 316
depth= nY = 1027
cols= nZ = 392

print("abrindo phantom")
phantom = np.fromfile("phantom.bin", dtype=np.float32)
phantom = phantom.reshape((cols, rows, depth))
print("phantom aberto")
#phantom[z][x][y]


##
# Escreva o código aqui
##
dx = 0.2
dy = 0.2
dz = 1

Xp1 = -(316/2)*dx #xpmax = (316/2)*dx  #+- 31.6mm
Yp1 = 0 #ypmax = 1027*0.2 = 205.4
Zp1 = 0 #zpmax = 392

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

emissores = [(91.247,694.027),(78.271,695.61),(65.268,696.951),(52.241,698.048),(39.197,698.902),(26.139,699.512),(13.072,699.878),(0,700),(-13.072,699.878),(-26.139,699.512),(-39.197,698.902),(-52.241,698.048),(-65.268,696.951),(-78.271,695.61),(-91.247,694.027)]


#fazer o loop pra cada receptor
#*Detector[15][2048][1792]
detectors = np.array([[[0 for k in range(1792)]for j in range(2048)] for i in range(15)])
iEmissor = 0
print("iniciando loop")
#for emissor in emissores:
emissor = (91.247,694.027)
iDetector = 0
for xDetector in np.arange(-143.29,143.43,0.14):
    jDetector = 0
    for yDetector in np.arange(0.7,250.95,0.14):
        x1 = emissor[0]
        z1 = emissor[1]
        y1 = 0
        x2 = xDetector
        y2 = yDetector
        z2 = 0
        #pegar pontos minimo e máximo de intersecção do raio com o phantom
        aMin = np.nanmax(
            [   0, 
                np.nanmin(
                    [aX(1,x1,x2),
                    aX(nX,x1,x2)]),
                np.nanmin([aY(1,y1,y2),
                        aY(nY,y1,y2)]), 
                np.nanmin([aZ(1,z1,z2),
                        aZ(nZ,z1,z2)])])
        aMax = np.nanmin([1, np.nanmax([aX(1,x1,x2),aX(nX,x1,x2)]), np.nanmax([aY(1,y1,y2),aY(nY,y1,y2)]), np.nanmax([aZ(1,z1,z2),aZ(nZ,z1,z2)])])
        if(aMax<= aMin):
            print('para td, n intercepta')
            continue
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
            currAlpha = aX(i,x1,x2)
            if aMin <= currAlpha and currAlpha <= aMax:
                alphas.append(currAlpha)
        for j in range(int(jMin),int(jMax+1)):
            currAlpha = aY(j,y1,y2)
            if aMin <= currAlpha and currAlpha <= aMax: 
                alphas.append(currAlpha)
        for k in range(int(kMin),int(kMax+1)):
            currAlpha = aZ(k,z1,z2)
            if aMin <= currAlpha and currAlpha <= aMax:
                alphas.append(currAlpha)
        alphas.append(aMax)
        alphas.sort()

        n = (int(iMax)-int(iMin)+1)+(int(jMax)-int(jMin)+1)+(int(kMax)-int(kMin)+1)+1

        d = 0
        length = np.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
        for m in range(1,len(alphas)):
            # print('rodou o for')
            aMid = (alphas[m] + alphas[m-1])/2
            im = 1+ (x1 + aMid *(x2-x1) - xPlano(1))/dx
            jm = 1+ (y1 + aMid *(y2-y1) - yPlano(1))/dy
            km = 1+ (z1 + aMid *(z2-z1) - zPlano(1))/dz
            d+= (alphas[m]-alphas[m-1])*phantom[int(km)-1][int(im)-1][int(jm)-1]
            #phantom[z][x][y]
        d*=length

        detectors[iEmissor][iDetector][jDetector] = d
        jDetector += 1
    print("i= " + str(iDetector) + " feito")
    iDetector += 1
        # print(str(d))

iEmissor+=1
print("colocando valores entre 0 e 255: ")
img = detectors[0]/(detectors[0].max()/255)
print("criando e salvando imagem")
Image.fromarray(img).save("emissor1","JPEG")


print("fim do código")