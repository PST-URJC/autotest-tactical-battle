import pexpect
import sys

POSICIONAMIENTO_ESPERADO = ['(?i)[M,m].dico', '(?i)[A,a]rtillero', '(?i)[F,f]rancotirador', '(?i)[I,i]nteligencia']
ACCIONES_INICIALES_ESPERADAS = ['(?i)[M,m]over.*[M,m].dico',
                                '(?i)[M,m]over.*[A,a]rtillero',
                                '(?i)[D,d]isparar.*[A,a]rtillero',
                                '(?i)[M,m]over.*[F,f]rancotirador',
                                '(?i)[D,d]isparar.*([F,f]rancotirador)',
                                '(?i)[M,m]over.*[I,i]nteligencia',
                                '(?i)[R,e]velar.*[I,i]nteligencia',]
ACCIONES_INICIALES_INDICE_MOVIMIENTO = ["1", "2", "4", "6"]
FALLO_CELDA_INCORRECTA = ['(?i)[U,u][P,p][S,s].*[I,i][N,n][C,c][O,o][R,r][R,r][E,e][C,c][T,t][A,a,O,o].*\n']
FALLO_CELDA_OCUPADA = ['(?i)[U,u][P,p][S,s].*[O,o][C,c][U,u][P,p][A,a][D,d][A,a].*\n']
PETICION_CELDA_MOVER = ['(?i)[C,c][E,e][L,l][D,d][A,a].*[M,m][O,o][V,v][E,e][R,r]']
INDICE_ACCIONES_ESPERADAS = ['1', '2', '3', '4']
INTRO = ['[I,i][N,n][T,t][R,r][O,o]']
JUGADORES = ["Jugador1", "Jugador2"]
POSICIONES_JUGADOR_1 = ['A1', 'A2', 'A3', 'A4']
POSICIONES_JUGADOR_2 = ['B1', 'B2', 'B3', 'B4']
MOVIMIENTOS_JUGADOR_1 = ['C1', 'C2', 'C3', 'C4']
MOVIMIENTOS_JUGADOR_2 = ['D1', 'D2', 'D3', 'D4']
MOVIMIENTOS_JUGADORES = {"Jugador1": MOVIMIENTOS_JUGADOR_1, "Jugador2": MOVIMIENTOS_JUGADOR_2}
MOVIMIENTOS_INCORRECTOS_JUGADOR = ['E1', 'D5', 'A', '3', '123', 'ABC', 'Z', '#', '']
POSICIONES_POR_JUGADOR = {"Jugador1": POSICIONES_JUGADOR_1, "Jugador2": POSICIONES_JUGADOR_2}
MOVIMIENTOS_POR_JUGADOR = {"Jugador1": MOVIMIENTOS_JUGADOR_1, "Jugador2": MOVIMIENTOS_JUGADOR_2}

def salta_doble_intro(child):
    child.expect(INTRO)
    child.sendline()
    sys.stdout.flush()

    child.expect(INTRO)
    child.sendline()
    sys.stdout.flush()

def prueba_posicionamiento_jugadores(child):
    for j in JUGADORES:
        for w in POSICIONAMIENTO_ESPERADO:
            i = child.expect(POSICIONAMIENTO_ESPERADO)
            child.sendline(POSICIONES_POR_JUGADOR[j][i])
        salta_doble_intro(child)

def prueba_movimientos(child):
    # Movimientos Incorrectos de los dos jugadores para todos los personajes
    # Para avanzar hay que meter uno correcto. Se chequean movimientos OK
    # (No hay cambio de turno, esperamos "Ups ... valor de celda incorrecto")
    personaje = 0
    for indice in ACCIONES_INICIALES_INDICE_MOVIMIENTO:
        for j in JUGADORES:
            # Jugador j
            i = child.expect(ACCIONES_INICIALES_ESPERADAS)
            child.sendline(ACCIONES_INICIALES_INDICE_MOVIMIENTO[i+personaje])
            siguiente_movimiento_correcto = 0
            for i in range(0, len(MOVIMIENTOS_INCORRECTOS_JUGADOR)):
                # Esperamos que pida movimiento
                child.expect(PETICION_CELDA_MOVER)
                # Mandamos la celda errónea
                child.sendline(MOVIMIENTOS_INCORRECTOS_JUGADOR[i])
                # Esperamos fallo celda incorrecta
                child.expect(FALLO_CELDA_INCORRECTA)
            # Movimientos A Celda ocupada
            child.expect(PETICION_CELDA_MOVER)
            # Mandamos movimiento a la celda ocupada
            child.sendline(POSICIONES_POR_JUGADOR[j][personaje])
            child.expect(FALLO_CELDA_OCUPADA)

            # Finalmente movemos a una celda correcta
            child.sendline(MOVIMIENTOS_JUGADORES[j][personaje])

            salta_doble_intro(child)
        personaje += 1

def main():
    child = pexpect.spawnu('python ./jugar.py', timeout=1)
    child.logfile_read = sys.stdout
    sys.stdout.flush()

    child.expect(INTRO)
    child.sendline()
    sys.stdout.flush()

    prueba_posicionamiento_jugadores(child)
    prueba_movimientos(child)

    # ACCIONES CON CELDAS ERRÓNEAS
    # J1: Disparo de Francotirador (Fallo)
    # Estado Inicial J2: [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
    # Estado Final J2:   [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]

    # ACCIONES
    # J1: Disparo de Francotirador (Fallo)
    # Estado Inicial J2: [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
    # Estado Final J2:   [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]

    # J2: Disparo de Artillero (Fallo)
    # Estado Inicial J1: [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]
    # Estado Final J1:   [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]

    # J1: Inteligencia (Fallo)
    # Estado Inicial J2: [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
    # Estado Final J2:   [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]

    # J1: Disparo de Francotirador (Acierto)

    # J2: Disparo de Artillero (Fallo)

    # J1: Inteligencia (Fallo)

    # J2: Curación

    # CHEQUEO ENFRIAMIENTO

    # FINAL DE PARTIDA

    child.expect(pexpect.EOF)
    child.wait()
    
if __name__ == '__main__':
    main()