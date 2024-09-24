import pygame
import random
import time
import os

# Inicializar pygame
pygame.init()

# Dimensiones de la ventana del juego (FullScreen)
ANCHO = 1920
ALTO = 1080
VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Suika Game")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)

# Frames por segundo
FPS = 60
GRAVEDAD = pygame.Vector2(0, 900)

# Tipos de frutas (niveles de frutas) y sus tamaños correspondientes
FRUTAS = [
    ('circulo1', 50),
    ('circulo2', 70),
    ('circulo3', 90),
    ('circulo4', 110),
    ('circulo5', 130),
    ('circulo6', 150),
    ('circulo7', 180),
    ('circulo8', 210)
]

PUNTAJE_FRUTAS = [1, 3, 7, 12, 19, 28, 40, 60]

# Dimensiones de la cubeta
CUBETA_ANCHO = 600
CUBETA_ALTO = 600
GROSOR_PAREDES = 20

# Posición de la cubeta, centrada en la pantalla
CUBETA_X = (ANCHO - CUBETA_ANCHO) // 2
CUBETA_Y = 400
LINEA_DE_PERDIDA_Y = CUBETA_Y

# Tiempo de espera entre tiros de frutas (en segundos)
TIEMPO_ESPERA_TIRO = 0.01
ultimo_tiro = 0

# Constantes para el temporizador y el puntaje alto
TIMER_FONT = pygame.font.SysFont(None, 48)
HIGH_SCORE_FILE = "highscore.txt"

TIEMPO_INICIO = pygame.time.get_ticks()  # Guardar el tiempo en que comenzó la partida

# Modificar la clase Fruta para incluir el atributo "soltada"
class Fruta:
    def __init__(self, tipo, x, y, tamano):
        self.tipo = tipo
        self.imagen = pygame.image.load(f"./images/fruits/{tipo}.png")
        self.imagen = pygame.transform.scale(self.imagen, (tamano, tamano))
        self.tamano = tamano
        self.radio = tamano // 2
        self.pos_actual = pygame.Vector2(x, y)
        self.pos_anterior = pygame.Vector2(x, y)
        self.aceleracion = pygame.Vector2(0, 0)
        self.soltada = False  # Inicialmente, la fruta no ha sido "soltada"

    # Método que marca la fruta como "soltada" al colisionar con algo
    def marcar_soltada(self):
        self.soltada = True

    def aplicar_fuerza(self, fuerza):
        self.aceleracion += fuerza

    def update(self, dt):
        # Integración de Verlet
        pos_siguiente = (2 * self.pos_actual) - self.pos_anterior + self.aceleracion * dt**2
        
        # Aplicar amortiguación vertical para reducir el rebote
        pos_siguiente.y = self.pos_anterior.y + (pos_siguiente.y - self.pos_anterior.y) * 0.99

        self.pos_anterior = self.pos_actual
        self.pos_actual = pos_siguiente

        # Limpiar aceleración
        self.aceleracion = pygame.Vector2(0, 0)


    def chequear_colision(self, otra_fruta):
        distancia = self.pos_actual.distance_to(otra_fruta.pos_actual)
        return distancia < (self.radio + otra_fruta.radio)

    def combinar(self, otra_fruta):
        idx = [f[0] for f in FRUTAS].index(self.tipo)
        
        # Si las frutas son de tipo circulo8, desaparecen y otorgan puntos
        if idx == len(FRUTAS) - 1:  # Si es el último tipo de fruta (circulo8)
            return None, PUNTAJE_FRUTAS[idx]  # No crear una nueva fruta, solo sumar puntos

        # Combinar en una fruta de mayor tipo
        nuevo_tipo, nuevo_tamano = FRUTAS[idx + 1]
        nueva_pos = (self.pos_actual + otra_fruta.pos_actual) / 2
        return Fruta(nuevo_tipo, nueva_pos.x, nueva_pos.y, nuevo_tamano), PUNTAJE_FRUTAS[idx]

    def dibujar(self, ventana):
        x, y = self.pos_actual
        ventana.blit(self.imagen, (x - self.radio, y - self.radio))

    def chequear_limites_cubeta(self):
        # Limitar a las paredes laterales y al piso
        if self.pos_actual.x - self.radio < CUBETA_X + GROSOR_PAREDES:
            self.pos_actual.x = CUBETA_X + GROSOR_PAREDES + self.radio
            self.pos_anterior.x = self.pos_actual.x  # Evitar que la fruta salga de nuevo por la izquierda
            self.pos_anterior.y += (self.pos_actual.y - self.pos_anterior.y) * 0.5  # Amortiguar el rebote lateral

        if self.pos_actual.x + self.radio > CUBETA_X + CUBETA_ANCHO - GROSOR_PAREDES:
            self.pos_actual.x = CUBETA_X + CUBETA_ANCHO - GROSOR_PAREDES - self.radio
            self.pos_anterior.x = self.pos_actual.x  # Evitar que la fruta salga de nuevo por la derecha
            self.pos_anterior.y += (self.pos_actual.y - self.pos_anterior.y) * 0.5  # Amortiguar el rebote lateral
            self.marcar_soltada()  # Marca la fruta como "soltada" al tocar el fondo de la cubeta

        if self.pos_actual.y + self.radio > CUBETA_Y + CUBETA_ALTO - GROSOR_PAREDES:
            self.pos_actual.y = CUBETA_Y + CUBETA_ALTO - GROSOR_PAREDES - self.radio
            self.pos_anterior.y = self.pos_actual.y  # Evitar que la fruta caiga más allá del piso
            self.marcar_soltada()  # Marca la fruta como "soltada" al tocar el fondo de la cubeta

def guardar_puntaje_alto(puntaje):
    with open(HIGH_SCORE_FILE, "w") as archivo:
        archivo.write(str(puntaje))

def cargar_puntaje_alto():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as archivo:
            return int(archivo.read())
    return 0

def mostrar_menu_inicio():
    puntaje_alto = cargar_puntaje_alto()
    menu_ejecutando = True
    while menu_ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if boton_iniciar.collidepoint(mouse_x, mouse_y):
                    menu_ejecutando = False
                if boton_instrucciones.collidepoint(mouse_x, mouse_y):
                    mostrar_instrucciones()
                if boton_salir.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    exit()

        VENTANA.fill(BLANCO)
        titulo_font = pygame.font.SysFont(None, 72)
        titulo_texto = titulo_font.render("Suika Game", True, NEGRO)
        VENTANA.blit(titulo_texto, (ANCHO // 2 - titulo_texto.get_width() // 2, ALTO // 4))

        puntaje_font = pygame.font.SysFont(None, 48)
        puntaje_texto = puntaje_font.render(f"Puntaje más alto: {puntaje_alto}", True, NEGRO)
        VENTANA.blit(puntaje_texto, (ANCHO // 2 - puntaje_texto.get_width() // 2, ALTO // 2))

        boton_iniciar = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 100, 200, 50)
        pygame.draw.rect(VENTANA, VERDE, boton_iniciar)
        iniciar_texto = puntaje_font.render("Iniciar", True, NEGRO)
        VENTANA.blit(iniciar_texto, (boton_iniciar.x + 60, boton_iniciar.y + 10))

        boton_instrucciones = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 200, 200, 50)
        pygame.draw.rect(VENTANA, VERDE, boton_instrucciones)
        instrucciones_texto = puntaje_font.render("Instrucciones", True, NEGRO)
        VENTANA.blit(instrucciones_texto, (boton_instrucciones.x + 10, boton_instrucciones.y + 10))

        boton_salir = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 300, 200, 50)
        pygame.draw.rect(VENTANA, ROJO, boton_salir)
        salir_texto = puntaje_font.render("Salir", True, NEGRO)
        VENTANA.blit(salir_texto, (boton_salir.x + 60, boton_salir.y + 10))

        pygame.display.flip()

def mostrar_instrucciones():
    instrucciones_ejecutando = True
    while instrucciones_ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                instrucciones_ejecutando = False

        VENTANA.fill(BLANCO)
        instrucciones_img = pygame.image.load('./images/instructions.png')
        VENTANA.blit(instrucciones_img, (ANCHO // 2 - instrucciones_img.get_width() // 2, ALTO // 2 - instrucciones_img.get_height() // 2))

        pygame.display.flip()

def mostrar_pantalla_perdida(puntaje):
    pantalla_perdida_ejecutando = True
    while pantalla_perdida_ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if boton_reintentar.collidepoint(mouse_x, mouse_y):
                    return "reintentar"  # Indicar que se ha seleccionado "Reintentar"
                if boton_salir.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    exit()

        VENTANA.fill(BLANCO)
        perdiste_font = pygame.font.SysFont(None, 72)
        perdiste_texto = perdiste_font.render("¡Perdiste!", True, ROJO)
        VENTANA.blit(perdiste_texto, (ANCHO // 2 - perdiste_texto.get_width() // 2, ALTO // 4))

        puntaje_font = pygame.font.SysFont(None, 48)
        puntaje_texto = puntaje_font.render(f"Puntaje final: {puntaje} puntos", True, NEGRO)
        VENTANA.blit(puntaje_texto, (ANCHO // 2 - puntaje_texto.get_width() // 2, ALTO // 2))

        # Botón Reintentar
        boton_reintentar = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 + 100, 300, 50)
        pygame.draw.rect(VENTANA, VERDE, boton_reintentar)
        reintentar_texto = puntaje_font.render("Reintentar", True, NEGRO)
        VENTANA.blit(reintentar_texto, (boton_reintentar.x + 80, boton_reintentar.y + 10))

        # Botón Salir
        boton_salir = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 + 200, 300, 50)
        pygame.draw.rect(VENTANA, ROJO, boton_salir)
        salir_texto = puntaje_font.render("Salir", True, NEGRO)
        VENTANA.blit(salir_texto, (boton_salir.x + 120, boton_salir.y + 10))

        pygame.display.flip()

def mostrar_tiempo_jugado():
    tiempo_transcurrido = (pygame.time.get_ticks() - TIEMPO_INICIO) // 1000  # Convertir a segundos
    minutos = tiempo_transcurrido // 60
    segundos = tiempo_transcurrido % 60
    tiempo_texto = TIMER_FONT.render(f"Tiempo jugado: {minutos:02}:{segundos:02}", True, NEGRO)
    VENTANA.blit(tiempo_texto, (50, 50))

# Función para separar las frutas si colisionan, con menor rebote
def separar_frutas(fruta1, fruta2):
    distancia = fruta1.pos_actual.distance_to(fruta2.pos_actual)
    overlap = (fruta1.radio + fruta2.radio) - distancia
    if overlap > 0:  # Si hay solapamiento, separarlas
        direccion = (fruta1.pos_actual - fruta2.pos_actual).normalize()
        ajuste = direccion * (overlap / 6)  # Reducir el ajuste para que no reboten tanto
        fruta1.pos_actual += ajuste
        fruta2.pos_actual -= ajuste

# Función para manejar colisiones, combinar frutas del mismo tipo y apilar frutas de diferentes tipos
def manejar_colisiones(frutas, puntaje):
    combinaciones = []
    frutas_a_eliminar = []

    # Detectar colisiones
    for i in range(len(frutas)):
        for j in range(i + 1, len(frutas)):
            if frutas[i].chequear_colision(frutas[j]):
                if frutas[i].tipo == frutas[j].tipo:
                    if frutas[i].tipo == 'circulo8':
                        # Excepción para circulo8: eliminar ambos y sumar puntos
                        frutas_a_eliminar.extend([i, j])
                        puntaje += PUNTAJE_FRUTAS[-1]  # Sumar puntos por colisión de circulos 8
                        frutas[i].soltada = True  # Marcar las frutas como "soltadas" tras la colisión
                        frutas[j].soltada = True
                    else:
                        # Combinar frutas del mismo tipo
                        nueva_fruta, puntos = frutas[i].combinar(frutas[j])
                        if nueva_fruta:
                            combinaciones.append((i, j, nueva_fruta))
                        puntaje += puntos
                        frutas[i].soltada = True  # Marcar como "soltadas" tras la combinación
                        frutas[j].soltada = True
                else:
                    # Si son de diferentes tipos, simplemente separar las frutas para que no se atraviesen
                    separar_frutas(frutas[i], frutas[j])
                    frutas[i].soltada = True  # Marcar como "soltadas" tras separarse
                    frutas[j].soltada = True

    # Eliminar frutas marcadas para eliminación fuera del bucle
    for j in sorted(frutas_a_eliminar, reverse=True):
        frutas.pop(j)

    # Agregar nuevas combinaciones de frutas fuera del bucle
    for i, j, nueva_fruta in sorted(combinaciones, key=lambda x: x[1], reverse=True):
        frutas[i] = nueva_fruta
        frutas.pop(j)

    return frutas, puntaje

# Función para dibujar la cubeta
def dibujar_cubeta(ventana):
    # Dibujar la cubeta en la pantalla con las paredes visibles
    pygame.draw.rect(ventana, NEGRO, (CUBETA_X, CUBETA_Y, GROSOR_PAREDES, CUBETA_ALTO))  # Pared izquierda
    pygame.draw.rect(ventana, NEGRO, (CUBETA_X + CUBETA_ANCHO - GROSOR_PAREDES, CUBETA_Y, GROSOR_PAREDES, CUBETA_ALTO))  # Pared derecha
    pygame.draw.rect(ventana, NEGRO, (CUBETA_X, CUBETA_Y + CUBETA_ALTO - GROSOR_PAREDES, CUBETA_ANCHO, GROSOR_PAREDES))  # Piso

# Función para dibujar la línea de guía y la fruta de previsualización
def dibujar_guia(ventana, fruta_tipo, fruta_tamano, mouse_x):
    # Limitar la posición X del mouse a los bordes de la cubeta
    x = max(CUBETA_X + GROSOR_PAREDES, min(mouse_x, CUBETA_X + CUBETA_ANCHO - GROSOR_PAREDES))

    # Dibujar la línea de guía (línea horizontal sobre la cubeta)
    pygame.draw.line(ventana, NEGRO, (CUBETA_X + GROSOR_PAREDES, CUBETA_Y - 30), 
                    (CUBETA_X + CUBETA_ANCHO - GROSOR_PAREDES, CUBETA_Y - 30), 2)

    # Dibujar la previsualización de la fruta en la línea de guía
    fruta_imagen = pygame.image.load(f"./images/fruits/{fruta_tipo}.png")
    fruta_imagen = pygame.transform.scale(fruta_imagen, (fruta_tamano, fruta_tamano))
    ventana.blit(fruta_imagen, (x - fruta_tamano // 2, CUBETA_Y - fruta_tamano // 2 - 30))

# Constante para definir la altura máxima antes de perder
ALTURA_MAXIMA_PERDIDA = CUBETA_Y + GROSOR_PAREDES

# Actualizar la lógica de pérdida en el juego
def verificar_perdida(frutas):
    for fruta in frutas:
        if fruta.soltada and fruta.pos_actual.y - fruta.radio <= LINEA_DE_PERDIDA_Y:
            return True  # Si una fruta "soltada" cruza la línea, se pierde el juego
    return False

# Función para dibujar la línea que indica el límite de pérdida
def dibujar_linea_perdida(ventana):
    pygame.draw.line(ventana, (255, 0, 0, 128), 
                     (CUBETA_X + GROSOR_PAREDES, ALTURA_MAXIMA_PERDIDA), 
                     (CUBETA_X + CUBETA_ANCHO - GROSOR_PAREDES, ALTURA_MAXIMA_PERDIDA), 2)

# Inicia el tiempo justo al empezar el juego
def juego():
    frutas = []
    clock = pygame.time.Clock()
    ejecutando = True
    puntaje = 0  # Puntaje inicial
    proxima_fruta_tipo, proximo_tamano = FRUTAS[0]
    global ultimo_tiro
    
    # Reiniciar el tiempo de inicio al comenzar el juego
    tiempo_inicio = time.time()

    while ejecutando:
        dt = clock.tick(FPS) / 1000  # Delta time en segundos

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                tiempo_actual = time.time()
                if tiempo_actual - ultimo_tiro >= TIEMPO_ESPERA_TIRO:
                    x, y = pygame.mouse.get_pos()
                    x = max(CUBETA_X + GROSOR_PAREDES, min(x, CUBETA_X + CUBETA_ANCHO - GROSOR_PAREDES - proximo_tamano))
                    if y < CUBETA_Y + GROSOR_PAREDES:  # Limitar la altura para lanzar
                        nueva_fruta = Fruta(proxima_fruta_tipo, x, CUBETA_Y + GROSOR_PAREDES, proximo_tamano)
                        frutas.append(nueva_fruta)

                        # Solo seleccionar la próxima fruta entre las dos primeras
                        proxima_fruta_tipo, proximo_tamano = random.choice(FRUTAS[:2])

                        ultimo_tiro = tiempo_actual

        # Aplicar gravedad y actualizar frutas
        for fruta in frutas:
            fruta.aplicar_fuerza(GRAVEDAD)
            fruta.update(dt)
            fruta.chequear_limites_cubeta()  # Chequear si las frutas están dentro de la cubeta

        # Manejar colisiones y combinar frutas
        frutas, puntaje = manejar_colisiones(frutas, puntaje)

        # Verificar si se pierde
        if verificar_perdida(frutas):
            resultado = mostrar_pantalla_perdida(puntaje)  # Muestra la pantalla de pérdida
            if resultado == "reintentar":
                # Reiniciar variables necesarias para jugar de nuevo
                puntaje = 0
                frutas = []  # Reinicia la lista de frutas, o el estado necesario
                TIEMPO_INICIO = pygame.time.get_ticks()  # Reiniciar el temporizador
                continue  # Reiniciar el juego
            else:
                ejecutando = False  # Salir del bucle principal y cerrar el juego
            guardar_puntaje_alto(puntaje)
            mostrar_pantalla_perdida(puntaje)
            break

        # Dibujar todo
        VENTANA.fill(BLANCO)  # Limpiar la pantalla
        dibujar_cubeta(VENTANA)
        dibujar_linea_perdida(VENTANA)  # Dibujar la línea roja de límite

        # Dibujar las frutas
        for fruta in frutas:
            fruta.dibujar(VENTANA)

        # Dibujar la línea de guía y la previsualización de la próxima fruta
        mouse_x, _ = pygame.mouse.get_pos()
        dibujar_guia(VENTANA, proxima_fruta_tipo, proximo_tamano, mouse_x)

        # Mostrar el puntaje
        font = pygame.font.SysFont(None, 36)
        texto_puntaje = font.render(f"Puntaje: {puntaje}", True, NEGRO)
        VENTANA.blit(texto_puntaje, (50, 150))

        tiempo_jugado = int(time.time() - tiempo_inicio)
        mostrar_tiempo_jugado()

        pygame.display.flip()

    pygame.quit()

# Mostrar el menú de inicio y comenzar el juego
mostrar_menu_inicio()
juego()