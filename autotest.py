import pexpect
import sys

POSICIONAMIENTO_ESPERADO = ['(?i)[M,m].dico', '(?i)[A,a]rtillero', '(?i)[F,f]rancotirador', '(?i)[I,i]nteligencia']
ACCIONES_INICIALES_ESPERADAS = ['[0-9]{1} {0,}: {0,}[M,m]over.*[M,m].dico',
                                '[0-9]{1} {0,}: {0,}[M,m]over.*[A,a]rtillero',
                                '[0-9]{1} {0,}: {0,}[D,d]isparar {1,}[E,e][N,n] {1,}.rea.*([A,a]rtillero)',
                                '[0-9]{1} {0,}: {0,}[M,m]over.*[F,f]rancotirador',
                                '[0-9]{1} {0,}: {0,}[D,d]isparar {1,}[A,a] {1,}[U,u][N,n][A,a] {1,}[C,c]elda.*([F,f]rancotirador)',
                                '[0-9]{1} {0,}: {0,}[M,m]over.*[I,i]nteligencia',
                                '[0-9]{1} {0,}: {0,}[R,r,]evelar.*[I,i]nteligencia']
ACCIONES_INICIALES_INDICES = ["1", "2", "3", "4", "5", "6", "7"]
ACCIONES_INICIALES_INDICE_MOVIMIENTO = ["1", "2", "4", "6"]
ACCIONES_INICIALES_INDICE_DISPAROS = [2, 4]
ACCIONES_INICIALES_INDICE_INTELIGENCIA = 6

FALLO_CELDA_INCORRECTA = ['(?i)[U,u][P,p][S,s].*[I,i][N,n][C,c][O,o][R,r][R,r][E,e][C,c][T,t][A,a,O,o].*\n']
FALLO_CELDA_OCUPADA = ['(?i)[U,u][P,p][S,s].*[O,o][C,c][U,u][P,p][A,a][D,d][A,a].*\n']
PETICION_CELDA_MOVER = ['(?i)[C,c][E,e][L,l][D,d][A,a].*[M,m][O,o][V,v][E,e][R,r]']
MENSAJE_NINGUN_PERSONAJE_HERIDO = "(?i)[N,n]ing.n {1,}[P,p]ersonaje {1,}[H,h]a {1,}[S,s]ido {1,}[H,h]erido"
MENSAJE_NINGUN_PERSONAJE_REVELADO = "(?i)[N,n]ing.n {1,}[P,p]ersonaje {1,}[H,h]a {1,}[S,s]ido {1,}[R,r]evelado"
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

class TestGame():
    child = None

    def __init__(self, child):
        self.child = child
        self.child.logfile_read = sys.stdout
        sys.stdout.flush()
        self.child.expect(INTRO)
        self.child.sendline()
        sys.stdout.flush()


    def salta_doble_intro(self):
        self.child.expect(INTRO)
        self.child.sendline()
        sys.stdout.flush()

        self.child.expect(INTRO)
        self.child.sendline()
        sys.stdout.flush()

    def prueba_posicionamiento_jugadores(self):
        for j in JUGADORES:
            for w in POSICIONAMIENTO_ESPERADO:
                i = self.child.expect(POSICIONAMIENTO_ESPERADO)
                self.child.sendline(POSICIONES_POR_JUGADOR[j][i])
            self.salta_doble_intro()

    def prueba_movimientos(self):
        # Movimientos Incorrectos de los dos jugadores para todos los personajes
        # Para avanzar hay que meter uno correcto. Se chequean movimientos OK
        # (No hay cambio de turno, esperamos "Ups ... valor de celda incorrecto")
        personaje = 0
        for indice in ACCIONES_INICIALES_INDICE_MOVIMIENTO:
            for j in JUGADORES:
                # Jugador j
                i = self.child.expect(ACCIONES_INICIALES_ESPERADAS)
                self.child.sendline(ACCIONES_INICIALES_INDICE_MOVIMIENTO[i+personaje])
                siguiente_movimiento_correcto = 0
                for i in range(0, len(MOVIMIENTOS_INCORRECTOS_JUGADOR)):
                    # Esperamos que pida movimiento
                    self.child.expect(PETICION_CELDA_MOVER)
                    # Mandamos la celda errónea
                    self.child.sendline(MOVIMIENTOS_INCORRECTOS_JUGADOR[i])
                    # Esperamos fallo celda incorrecta
                    self.child.expect(FALLO_CELDA_INCORRECTA)
                # Movimientos A Celda ocupada
                self.child.expect(PETICION_CELDA_MOVER)
                # Mandamos movimiento a la celda ocupada
                self.child.sendline(POSICIONES_POR_JUGADOR[j][personaje])
                self.child.expect(FALLO_CELDA_OCUPADA)

                # Finalmente movemos a una celda correcta
                self.child.sendline(MOVIMIENTOS_JUGADORES[j][personaje])

                self.salta_doble_intro()
            personaje += 1

    def get_re_index(self):
        return self.child.match.group().split(':', 1)[0].strip()

    def prueba_disparos_fallidos(self):
        # Estado Inicial J1: [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]
        # Estado Final J1:   [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]
        # Estado Inicial J2: [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
        # Estado Final J2:   [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
        # Disparos Incorrectos de los dos jugadores para el francotirador
        # Se chequea informe y resultado acción
        for i in ACCIONES_INICIALES_INDICE_DISPAROS:
            for j in JUGADORES:
                # Envio de opcion (disparo artillero/disparo francotirador)
                self.child.expect(ACCIONES_INICIALES_ESPERADAS[i])
                self.child.sendline(str(self.get_re_index()))
                # Nos pide donde disparar, enviamos celda vacia (cualquiera fila A)
                self.child.sendline("A1")
                # Esperamos mensaje "Ningún personaje ha sido herido"
                self.child.expect(MENSAJE_NINGUN_PERSONAJE_HERIDO)
                self.salta_doble_intro()

    def prueba_inteligencia_fallida(self):
        # Estado Inicial J1: [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]
        # Estado Final J1:   [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]
        # Estado Inicial J2: [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
        # Estado Final J2:   [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
        # Chequeo incorrecto de reporte de inteligencia
        # Se chequea informe y resultado acción
        for j in JUGADORES:
            # Envio de opcion (disparo artillero/disparo francotirador)
            self.child.expect(ACCIONES_INICIALES_ESPERADAS[ACCIONES_INICIALES_INDICE_INTELIGENCIA])
            self.child.sendline(str(self.get_re_index()))
            # Nos pide donde mirar, miramos celda vacia con alrededores vacios (cualquiera celda en fila A)
            self.child.sendline("A2")
            # Esperamos mensaje "Ningún personaje ha sido avistado"
            self.child.expect(MENSAJE_NINGUN_PERSONAJE_REVELADO)
            self.salta_doble_intro()

def main():
    # TODO: set executable configurable
    child = pexpect.spawnu('python ./jugar.py', timeout=1)

    test_game = TestGame(child)

    test_game.prueba_posicionamiento_jugadores()
    test_game.prueba_movimientos()

    # ACCIONES CON CELDAS ERRÓNEAS
    # ACCIONES
    # Estado Inicial J1: [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]
    # Estado Final J1:   [MC1(1/1), AC2(2/2), FC3(3/3), IC4(2/2)]
    # Estado Inicial J2: [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
    # Estado Final J2:   [MD1(1/1), AD2(2/2), FD3(3/3), ID4(2/2)]
    test_game.prueba_disparos_fallidos()
    test_game.prueba_inteligencia_fallida()

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
