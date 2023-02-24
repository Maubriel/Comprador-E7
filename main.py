from python_imagesearch.imagesearch import imagesearch, imagesearcharea, region_grabber, click_image
from screeninfo import get_monitors
import tkinter as tk
import pyautogui
import time
import cv2

def screensize():
    x = -1
    y = -1
    for m in get_monitors():
        if m.is_primary:
            x = m.width
            y = m.height
            break
    return (x, y)

def localizar_tienda():
    # Toma el valor de SkyStone introducido por el usuario
    # Si no es una entrada valida, lo pone en 0 para no gastar SkyStone
    inputSS = t1.get(1.0, 'end-1c')
    skyStone = 0
    try:
        skyStone = int(inputSS)
        resto = skyStone%3
        skyStone -= resto
    except ValueError:
        skyStone = 0
    
    # Mensaje base
    l3.config(text='')
    l6.config(text='Marcadores de profecía: 0')
    l7.config(text='Marcadores de místicos: 0')

    # Detecta el tamaño del monitor
    xy = screensize()
    if xy[0] < 1 or xy[1] < 1:
        l3.config(text='No se pudo detectar el monitor')
        return
    
    # Busca el rostro de Garo y hace click en él para tener el focus en el juego
    # De no encontrarlo se cancela la operación
    garo = imagesearch('imagenes/garo_tie.png', 0.8)
    if garo[0] < 1 or garo[1] < 1:
        l3.config(text='No se encontró la tienda')
        return
    click_image('imagenes/garo_tie.png', garo, 'primary', 0.2, offset=5)
    time.sleep(0.1)

    # Se empieza a almacenar las posiciones del cursor
    # La operacion se cancela si el usuario mueve el cursor
    # Esto se checkea en distintos puntos más adelante
    global current_point
    current_point = pyautogui.position()

    # Busca las coordenadas de ciertos objetos en el juego para tenerlos de referencia
    # para establecer la zona donde se buscarán los marcadores
    im = region_grabber([0, 0, xy[0], xy[1]])
    backButton = imagesearcharea('imagenes/back_button.png', 0, 0, xy[0], xy[1], 0.8, im)
    refrButton = imagesearcharea('imagenes/refresh_button.png', 0, 0, xy[0], xy[1], 0.8, im)
    buyButton = imagesearcharea('imagenes/buy_button.png', 0, 0, xy[0], xy[1], 0.8, im)
    slideZoneX = (garo[0]+buyButton[0])/2  # Coordenada X para deslizar la tienda
    if backButton[0] < 1 or backButton[1] < 1 or refrButton[0] < 1 or refrButton[1] < 1:
        l3.config(text='No se pudo detectar los bordes del juego')
        return
    lowY = int((refrButton[1]-backButton[1])*1.125)+backButton[1]
    gameScreen = [refrButton[0], backButton[1], buyButton[0], lowY]

    # Si no hubo inconvenientes, inicia la operación
    startRefreshing(gameScreen, skyStone, refrButton, slideZoneX, buyButton[0])

def startRefreshing(gameScreen, skyStone, refrButton, slideZoneX, buyButtonX):

    # Función para comprar los marcadores (False)
    # Si hubo algun problema o interrupción (True), se termina la operación
    def comprar_marcador(a, b, tipo):
        time.sleep(0.2)
        # Detecta el tipo de marcador a comprar
        if tipo == 1:
            marcador = 'convenant_price.png'
        else:
            marcador = 'mystic_price.png'
        buy = [-1, -1]
        intentos = 0
        global current_point
        # Busca presionar el botón para comprar el marcador
        while buy[0] == -1:
            if current_point != pyautogui.position():
                return True
            click_image('imagenes/buy_button.png', [a,b+gameScreen[1]], 'primary', 0.2, offset=5)
            intentos += 1
            current_point = pyautogui.position()
            time.sleep(0.5)
            buy = imagesearcharea("imagenes/"+marcador, gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
            if intentos > 4:
                l3.config(text='Hubo un error al presionar un botón')
                return True
        intentos = 0
        time.sleep(0.5)
        # Botón de confirmar
        while buy[0] != -1:
            if current_point != pyautogui.position():
                return True
            click_image('imagenes/'+marcador, [buy[0]+gameScreen[0],buy[1]+gameScreen[1]], 'primary', 0.2, offset=5)
            intentos += 1
            current_point = pyautogui.position()
            time.sleep(0.5)
            buy = imagesearcharea("imagenes/"+marcador, gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
            if intentos > 4:
                l3.config(text='Hubo un error al presionar un botón')
                return True
            print('compro el maracador')
        time.sleep(0.5)
        return False

    convBM = 0
    mistBM = 0
    buyButtonY = -1
    img = cv2.imread("imagenes/convenantBM_icon.png")
    height, width, channels = img.shape # Se toma la altura del icono del marcador para apretar el boton de comprar
    global current_point

    # Loop que continua hasta que no queden Sky Stone
    while True:
        # Variables booleanas para saber si compró algún marcador
        convBuyed = False
        mistBuyed = False

        # Busca un marcador de profecia en la lista de items
        bm = imagesearcharea("imagenes/convenantBM_icon.png", gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
        if bm[0] != -1:
            buyButtonY = bm[1]+int(height/1.42)
            if(comprar_marcador(buyButtonX, buyButtonY, 1)):
                l3.config(text='Se interrumpió la compra')
                return
            convBuyed = True
        
        # Busca un marcador místico en la lista de items
        mm = imagesearcharea("imagenes/mysticBM_icon.png", gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
        if mm[0] != -1:
            buyButtonY = mm[1]+int(height/1.42)
            if(comprar_marcador(buyButtonX, buyButtonY, 2)):
                l3.config(text='Se interrumpió la compra')
                return
            mistBuyed = True

        # Si no detectó ni uno de los marcadores, desliza la lista de items para ver los que faltan
        if not(convBuyed and mistBuyed):
            if current_point != pyautogui.position():
                l3.config(text='Se interrumpió la compra')
                return
            pyautogui.moveTo(slideZoneX, gameScreen[3]-50)
            pyautogui.dragTo(slideZoneX, gameScreen[3]-450, 1, button='left')
            time.sleep(1)
            current_point = pyautogui.position()

            # Busca marcador de profecía
            if not convBuyed:
                bm2 = imagesearcharea("imagenes/convenantBM_icon.png", gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
            else:
                bm2 = [-1, -1]
            time.sleep(1)
            if bm2[0] != -1:
                buyButtonY = bm2[1]+int(height/1.42)
                if(comprar_marcador(buyButtonX, buyButtonY, 1)):
                    l3.config(text='Se interrumpió la compra')
                    return
                convBuyed = True

            # Busca marcador místico
            if not mistBuyed:
                mm2 = imagesearcharea("imagenes/mysticBM_icon.png", gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
            else:
                mm2 = [-1, -1]
            if mm2[0] != -1:
                buyButtonY = mm2[1]+int(height/1.42)
                if(comprar_marcador(buyButtonX, buyButtonY, 2)):
                    l3.config(text='Se interrumpió la compra')
                    return
                mistBuyed = True
        
        # Aumenta el conteo de los marcadores comprados
        if convBuyed:
            convBM += 5
            l6.config(text='Marcadores de profecía: '+str(convBM))
        if mistBuyed:
            mistBM += 50
            l7.config(text='Marcadores místicos: '+str(mistBM))

        # Si ya no hay SkyStone para gastar, termina el proceso
        if skyStone < 3:
            l3.config(text='Finalizó la compra')
            return
        
        time.sleep(0.5)
        confirm = [-1, -1]
        intentos = 0
        # Si aún hay SkyStone para gastar, presiona el botón de actualizar
        while confirm[0] == -1:
            if current_point != pyautogui.position():
                l3.config(text='Se interrumpió la compra')
                return
            click_image('imagenes/refresh_button.png', refrButton, 'primary', 0.2, offset=5)
            intentos += 1
            current_point = pyautogui.position()
            time.sleep(0.5)
            confirm = imagesearcharea("imagenes/confirm_button.png", gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
            if intentos > 4:
                l3.config(text='Hubo un error al presionar un botón')
                return
        confirm = [confirm[0]+gameScreen[0], confirm[1]+gameScreen[1]]
        intentos = 0
        # Si pudo presionar el botón de actualizar, busca el botón de confirmar el refresh
        while confirm[0] != -1:
            if current_point != pyautogui.position():
                l3.config(text='Se interrumpió la compra')
                return
            click_image('imagenes/confirm_button.png', confirm, 'primary', 0.2, offset=5)
            intentos += 1
            current_point = pyautogui.position()
            time.sleep(0.5)
            confirm = imagesearcharea("imagenes/confirm_button.png", gameScreen[0], gameScreen[1], gameScreen[2], gameScreen[3])
            if intentos > 4:
                l3.config(text='Hubo un error al presionar un botón')
                return
        
        # Resta el SkyStone gastado
        skyStone -= 3
        time.sleep(2)


# Prepara la UI
current_point = pyautogui.position()
ventana = tk.Tk()
ventana.title('Comprador E7')
ventana.iconbitmap('imagenes/garoIcon.ico')
ventana.configure(width=500,height=350,bg='lightgrey')
ventana.minsize(500,350)
ventana.resizable(0,0)
l1 = tk.Label(ventana, text="", background='lightgrey')
l1.pack()
l2 = tk.Label(ventana, text="Cantidad máxima de SkyStone a gastar", background='lightgrey')
l2.pack()
l4 = tk.Label(ventana, text="(por defecto no se gastará)", background='lightgrey')
l4.pack()
t1 = tk.Text(ventana, height=1, width=10, font='Cambria')
t1.pack()
l5 = tk.Label(ventana, text="", background='lightgrey')
l5.pack()
b1 = tk.Button(ventana, text='Iniciar', command=localizar_tienda)
b1.pack()
l3 = tk.Label(ventana, text="", background='lightgrey')
l3.pack()
l6 = tk.Label(ventana, text="", background='lightgrey')
l6.pack()
l7 = tk.Label(ventana, text="", background='lightgrey')
l7.pack()
ventana.mainloop()
