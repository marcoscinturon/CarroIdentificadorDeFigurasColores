import numpy as np
import cv2
import sys
import time
import sim
import random

def closeCon():
    sim.simxFinish(-1)
    
def initCon():
    clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
    #comprobamos que se haya podido conectar con CoppeliaSim
    if clientID!=-1:
        print("conexión establecida!")
    else:
        sys.exit("Error: No se puede conectar")
        #ocurre cuando se lanza primero python y después vrep. Debe hacerse al contrario
    return clientID


def initConfigMotor(clientID):
    #Guardamos los motores del robot:
    error_izq, motor_izquierdo = sim.simxGetObjectHandle(clientID, "Pioneer_p3dx_leftMotor", sim.simx_opmode_oneshot_wait)
    error_der, motor_derecho = sim.simxGetObjectHandle(clientID, "Pioneer_p3dx_rightMotor", sim.simx_opmode_oneshot_wait)

    if error_izq or error_der:
        sys.exit("Error: No se puede conectar con los motores")
    else:
        print("motor listo")
        return motor_izquierdo, motor_derecho
    
def readSensor(clientID, sensorHandle):
    ret, estado_sensor, arr1, object_detected, arr2 = sim.simxReadProximitySensor(clientID, sensorHandle, sim.simx_opmode_streaming)
    return estado_sensor

def move_Up(clientID, motor_izquierdo, motor_derecho, velocidad):
    #Avanzar hacia adelante durante t segundos
    sim.simxSetJointTargetVelocity(clientID, motor_izquierdo, velocidad, sim.simx_opmode_streaming)
    sim.simxSetJointTargetVelocity(clientID, motor_derecho, velocidad, sim.simx_opmode_streaming)
    #time.sleep(2)

def move_Down(clientID, motor_izquierdo, motor_derecho, velocidad):
    #Avanzar hacia adelante durante t segundos
    sim.simxSetJointTargetVelocity(clientID, motor_izquierdo, -velocidad, sim.simx_opmode_streaming)
    sim.simxSetJointTargetVelocity(clientID, motor_derecho, -velocidad, sim.simx_opmode_streaming)
    #time.sleep(2)

def move_Left(clientID, motor_izquierdo, motor_derecho, velocidadIzq, velocidadDer):
    sim.simxSetJointTargetVelocity(clientID, motor_izquierdo, velocidadIzq , sim.simx_opmode_streaming)
    sim.simxSetJointTargetVelocity(clientID, motor_derecho, velocidadDer, sim.simx_opmode_streaming)

def move_Right(clientID, motor_izquierdo, motor_derecho, velocidadDer, velocidadIzq):
    sim.simxSetJointTargetVelocity(clientID, motor_izquierdo, velocidadIzq, sim.simx_opmode_streaming)
    sim.simxSetJointTargetVelocity(clientID, motor_derecho, velocidadDer, sim.simx_opmode_streaming)

def stop_Motors(clientID, motor_izquierdo, motor_derecho):
    sim.simxSetJointTargetVelocity(clientID, motor_izquierdo, 0, sim.simx_opmode_streaming)
    sim.simxSetJointTargetVelocity(clientID, motor_derecho, 0, sim.simx_opmode_streaming)
    time.sleep(2)

def initCamera(clientID):
    _, cameraObject0 =sim.simxGetObjectHandle(clientID, "Vision_sensor0", sim.simx_opmode_oneshot_wait)
    _, cameraObject1 =sim.simxGetObjectHandle(clientID, "Vision_sensor1", sim.simx_opmode_oneshot_wait)
    _, resolution0, imageCamera0 = sim.simxGetVisionSensorImage(clientID, cameraObject0, 0, sim.simx_opmode_streaming)
    _, resolution1, imageCamera1 = sim.simxGetVisionSensorImage(clientID, cameraObject1, 0, sim.simx_opmode_streaming)
    time.sleep(1)
    return cameraObject0, cameraObject1

def getImageBGR(clientID, cameraObject):
    _, resolution, image = sim.simxGetVisionSensorImage(clientID,cameraObject,0,sim.simx_opmode_buffer)
    img = np.array(image, dtype = np.uint8)
    img.resize([resolution[1], resolution[0], 3])
    img = np.rot90(img,2)
    img = np.fliplr(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def figColor(imagenHSV):
    # Rojo
    rojoBajo1 = np.array([0, 100, 20], np.uint8)
    rojoAlto1 = np.array([10, 255, 255], np.uint8)
    rojoBajo2 = np.array([175, 100, 20], np.uint8)
    rojoAlto2 = np.array([180, 255, 255], np.uint8)

    #Verde
    verdeBajo = np.array([36, 100, 20], np.uint8)
    verdeAlto = np.array([70, 255, 255], np.uint8)

    #Azul
    azulBajo = np.array([120, 100, 20], np.uint8)
    azulAlto = np.array([140, 255, 255], np.uint8)

    #Amarillo
    amarilloBajo = np.array([32, 100, 20], np.uint8)
    amarilloAlto = np.array([48, 255, 255], np.uint8)

    # Se buscan los colores en la imagen, segun los límites altos 
    # y bajos dados
    maskRojo1 = cv2.inRange(imagenHSV, rojoBajo1, rojoAlto1)
    maskRojo2 = cv2.inRange(imagenHSV, rojoBajo2, rojoAlto2)
    maskRojo = cv2.add(maskRojo1, maskRojo2)
    maskVerde = cv2.inRange(imagenHSV, verdeBajo, verdeAlto)
    maskAzul = cv2.inRange(imagenHSV, azulBajo, azulAlto)
    maskAmarillo = cv2.inRange(imagenHSV, amarilloBajo, amarilloAlto)
	
    cntsRojo = cv2.findContours(maskRojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] 	
    cntsVerde = cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] 
    cntsAzul = cv2.findContours(maskAzul, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] 
    cntsAmarillo = cv2.findContours(maskAmarillo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] 
    

    if len(cntsRojo)>0:
        color = 'Rojo'
    elif len(cntsVerde)>0:
        color = 'Verde'
    elif len(cntsAzul)>0:
        color = 'Azul'
    elif len(cntsAmarillo)==0:
        color = 'Amarillo'

    return color

def binRojo (imagenHSV):
    rojoBajo1 = np.array([0, 100, 20], np.uint8)
    rojoAlto1 = np.array([10, 255, 255], np.uint8)
    """rojoBajo2 = np.array([175, 100, 20], np.uint8)
    rojoAlto2 = np.array([180, 255, 255], np.uint8)"""

    maskRojo1 = cv2.inRange(imagenHSV, rojoBajo1, rojoAlto1)
    #maskRojo2 = cv2.inRange(imagenHSV, rojoBajo2, rojoAlto2)
    #maskRojo = cv2.add(maskRojo1, maskRojo2)
    return maskRojo1

def binVerde (imagenHSV):
    verdeBajo = np.array([36, 100, 20], np.uint8)
    verdeAlto = np.array([70, 255, 255], np.uint8)

    maskVerde = cv2.inRange(imagenHSV, verdeBajo, verdeAlto)
    return maskVerde

def binAzul (imagenHSV):
    azulBajo = np.array([120, 50, 50], np.uint8)
    azulAlto = np.array([140, 255, 255], np.uint8)

    maskAzul = cv2.inRange(imagenHSV, azulBajo, azulAlto)
    return maskAzul

def binAmarillo (imagenHSV):
    amarilloBajo = np.array([20, 100, 20], np.uint8)
    amarilloAlto = np.array([32, 255, 255], np.uint8)

    maskAmarillo = cv2.inRange(imagenHSV, amarilloBajo, amarilloAlto)
    return maskAmarillo

def figName(contorno):
	epsilon = 0.01*cv2.arcLength(contorno,True)
	approx = cv2.approxPolyDP(contorno,epsilon,True)

	if len(approx) == 3:
		namefig = 'Triangulo'

	elif len(approx) == 4:
		namefig = 'Cuadrado'

	elif len(approx) == 6:
		namefig = 'Hexagono'

	else:
		namefig = ''

	return namefig
    
def getPosiciones(clientID, objeto):
    while (True):
        PosObjeto=sim.simxGetObjectPosition(clientID, objeto, -1, sim.simx_opmode_streaming)
        if (PosObjeto[0]==0):
            break
    return PosObjeto     

def findPosicionObjeto(clientID, figura, color):
    posicion=[]
    _, HexaRojo = sim.simxGetObjectHandle(clientID, "Hexag2", sim.simx_opmode_oneshot_wait)
    posHexaRojo= getPosiciones(clientID, HexaRojo)[1]

    _, HexaVerde = sim.simxGetObjectHandle(clientID, "Hexag3", sim.simx_opmode_oneshot_wait)
    posHexaVerde= getPosiciones(clientID, HexaVerde)[1]

    _, HexaAzul = sim.simxGetObjectHandle(clientID, "Hexag4", sim.simx_opmode_oneshot_wait)
    posHexaAzul= getPosiciones(clientID, HexaAzul)[1]

    _, TriangRojo = sim.simxGetObjectHandle(clientID, "triang2", sim.simx_opmode_oneshot_wait)
    posTriangRojo= getPosiciones(clientID, TriangRojo)[1]

    _, TriangAzul = sim.simxGetObjectHandle(clientID, "triang3", sim.simx_opmode_oneshot_wait)
    posTriangAzul= getPosiciones(clientID, TriangAzul)[1]

    _, TriangVerde = sim.simxGetObjectHandle(clientID, "triang4", sim.simx_opmode_oneshot_wait)
    posTriangVerde= getPosiciones(clientID, TriangVerde)[1]

    _, CuadVerde = sim.simxGetObjectHandle(clientID, "Cuboid2", sim.simx_opmode_oneshot_wait)
    posCuadVerde= getPosiciones(clientID, CuadVerde)[1]

    _, CuadAzul = sim.simxGetObjectHandle(clientID, "Cuboid3", sim.simx_opmode_oneshot_wait)
    posCuadAzul= getPosiciones(clientID, CuadAzul)[1]

    _, CuadRojo = sim.simxGetObjectHandle(clientID, "Cuboid4", sim.simx_opmode_oneshot_wait)
    posCuadRojo= getPosiciones(clientID, CuadRojo)[1]
    
    matriz=[["Hexagono", "Rojo", posHexaRojo],
            ["Hexagono", "Verde", posHexaVerde],
            ["Hexagono", "Azul", posHexaAzul],
            ["Triangulo", "Rojo",  posTriangRojo],
            ["Triangulo", "Azul", posTriangAzul],
            ["Triangulo", "Verde", posTriangVerde],
            ["Cuadrado", "Verde", posCuadVerde],
            ["Cuadrado", "Azul", posCuadAzul],
            ["Cuadrado", "Rojo", posCuadRojo]]

    for i in range (9):
        for j in range(3):
            if matriz[i][0]==figura and matriz[i][1]==color:
                posicion=matriz[i][2]
    return posicion
   
def main():
    closeCon()
    clientID = initCon()
    if clientID!=-1:
        #inicializar objetos
        bandera=False
        cx2=0
        _, esfera =sim.simxGetObjectHandle(clientID, "Sphere0", sim.simx_opmode_oneshot_wait)
        _, brazo =sim.simxGetObjectHandle(clientID, "Brazo", sim.simx_opmode_oneshot_wait)
        boolean=False
        cond=True
        lista=[]
        M_izq, M_der = initConfigMotor(clientID)
        cameraObject0, cameraObject1 = initCamera(clientID)
        figura=""
        while(1):
            #convertir imagen a BGR
            imgBGR = getImageBGR(clientID, cameraObject1)
            imgBGR0 = getImageBGR(clientID, cameraObject0)
            #procesamiento
            #convertir img a hsv y detectar colores
            hsv = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)
            col = figColor(hsv)

            hsv0 = cv2.cvtColor(imgBGR0, cv2.COLOR_BGR2HSV)
            imgBinAmarillo = binAmarillo (hsv0)
            #binarizar imagen hsv en un rango y extraer contornos
            if col=='Rojo':
                imgBin = binRojo(hsv)
                cnt,hie = cv2.findContours(imgBin.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            elif col=='Verde':
                imgBin = binVerde(hsv)
                cnt,hie = cv2.findContours(imgBin.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            elif col=='Azul':
                imgBin = binAzul(hsv)
                cnt,hie = cv2.findContours(imgBin.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            else:
                col="Amarillo"
                boolean=False
                imgBin = binAmarillo(hsv)
                cnt=[]
            cnt0,hie = cv2.findContours(imgBinAmarillo.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            for contour in cnt:
                area = cv2.contourArea(contour)
                if(cv2.contourArea(contour)>10): #Se cambia el valor segun la distancia a la cual se quiere empezar ver el cubo
                    cv2.drawContours(imgBin, [contour], -1, 255, -1)
                    
                    moments = cv2.moments(contour)
                    cx = int(moments['m10']/moments['m00'])
                    cy = int(moments['m01']/moments['m00'])
                    cv2.circle(imgBGR, (cx, cy), 1, (255,0,0), 1)
                        
                    if boolean==False:
                        if cond==True:
                            cx2=cx
                            cond=False
                     
                    
                    if boolean==True and cx2<55:
                        move_Left(clientID, M_izq, M_der, 2.7, 2.8)
                    elif boolean==True and cx2>68:
                        move_Right(clientID, M_izq, M_der, 2.7, 2.8)
                    else:
                        if(cx<50):
                            move_Right(clientID, M_izq, M_der, 0.5, 1)
                        elif (cx>70):
                            move_Left(clientID, M_izq, M_der, 0.5, 1)
                        else:
                            if (cy>=71):
                                move_Up(clientID, M_izq, M_der, 2.8)
                            else:
                                stop_Motors(clientID, M_izq, M_der)
                                figura=figName(contour)
                                if figura=='':
                                    move_Up(clientID, M_izq, M_der, 0.1)
                                else:
                                    posicion=findPosicionObjeto(clientID, figura, col)
                                    lista.append(posicion)
                                    boolean=True
                                    cond=True
                                    print(col)
                                    print(figura)
                                    print(lista)
            
            #para mantenerse centrado en la pista
            if col=="Amarillo":
                for c in cnt0:
                    #area = cv2.contourArea(contour)
                    if(cv2.contourArea(c)>10): #Se cambia el valor segun la distancia a la cual se quiere empezar ver el cubo
                        x,y,w,h=cv2.boundingRect(c)
                        cv2.rectangle(imgBGR, (x,y), (x+w, y+h), (0, 0, 255), 2)
                    
                        moments = cv2.moments(c)
                        cx0 = int(moments['m10']/moments['m00'])
                        cy0 = int(moments['m01']/moments['m00'])
                        cv2.circle(imgBGR, (cx0, cy0), 1, (255,0,0), 1)

                        if(cx0<55):
                            move_Left(clientID, M_izq, M_der, 2, 3.5)
                        elif (cx0>65):
                            move_Right(clientID, M_izq, M_der, 2, 3.5)
                        else:
                            move_Up(clientID, M_izq, M_der, 5)

            #para esquivar los cubos
            if figura=="Cuadrado" and col!="Amarillo":
                if 0<cx2<55 :
                    move_Left(clientID, M_izq, M_der, 0.8, 2.8)
                elif cx2>65:
                    move_Right(clientID, M_izq, M_der, 0.8, 2.8)
            else:
                figura=""

            #para hacer que el carro se detenga al final
            if  getPosiciones(clientID, esfera)[1][1]<=(getPosiciones(clientID, brazo)[1][1]+0.2):
                stop_Motors(clientID, M_izq, M_der)
                time.sleep(1)
                
            #mostrar frame y salir con "ESC"
            cv2.imshow('Image', imgBin)
            cv2.imshow('ImageBin', imgBinAmarillo)

            
        cv2.destroyAllWindows()
        stop_Motors(clientID, M_izq, M_der)
        closeCon()
    


main()
