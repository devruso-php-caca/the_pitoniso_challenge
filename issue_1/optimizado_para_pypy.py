import os, mmap
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

FILE = "./measurements.txt"
NP = os.cpu_count() # Número de cores (incluye smt)

def consumer(start_pos, end_pos):
    # Vamos a leer el archivo en modo binario y vamos a tratar todo como bytes y
    # no como texto / unicode (utf-8) porque decodificar bytes a utf-8 es
    # carisimo y no está el paiton para menearlo.
    f = open(FILE, "rb")

    # mmapear un archivo con offset distinto a 0 requiere alinearlo al tamaño de
    # la pagina del kernel... Explicado para frontenders:
    # Supongamos que start_pos era 68. No podemos situarnos directamente ahí
    # porque el offset de mmap necesita un multiplo del tamaño de página del
    # kernel. En mi caso (en mi maquina), el tamaño de página es de 16, así que
    # me muevo a 64 (la dirección mas cercana a 68, multiplo de 16).
    mem_align = (start_pos // mmap.PAGESIZE) * mmap.PAGESIZE

    offset = start_pos - mem_align
    length = end_pos - start_pos + offset
    fm = mmap.mmap(f.fileno(), length=length, access=mmap.ACCESS_READ, offset=mem_align)

    # Ya que estamos mmapeando archivos, hay un truco para optimizar la lectura.
    # Podemos advertirle al kernel que vamos a leer el archivo de manera
    # secuencial y, por lo tanto, puede asumir que puede ir leyendo cosas a las
    # que todavía no hemos llegado para ahorrar tiempo.
    # ... todo esto si MacOS no fuese una gran putisima 💩, claro. *sigh*
    # Tim Apple dimisión!!
    fm.madvise(mmap.MADV_SEQUENTIAL, 0, length)
    fm.madvise(mmap.MADV_WILLNEED, 0, length)

    # ... y como hemos retrocedido hacía atras, ahora tenemos que compensar con
    # la diferencia entre lo que hemos retrocedido y la posición donde realmente
    # deberíamos estar
    fm.seek(offset)

    # Vamos a guardar los resultados en un diccionario donde el key va a ser el
    # churro binario y el valor va a ser un array de 4 números, representando el
    # mínimo, el máximo, la media (agregado) y el número de veces que aparece,
    # (para poder sacar la media).
    # ¿Y por que no un diccionario para el valor? Porque la complejidad de
    # acceso a un diccionario es avg O(1), mientras que el de un array es
    # siempre O(1). Y porque ocupa menos memoria.
    result = defaultdict(lambda: [0, 0, 0, 0])

    # Podría parecer que la manera mas óptima de iterar sobre las líneas del
    # archivo es con un iterador, pero un bucle infinito es mas óptimo porque
    # va a generar una estructura de instrucciones con 0 comprobaciones
    # adicionales.
    #for line in iter(fm.readline, b""):

    # Micro-optimización: cada vez que accedemos a atributo o metodo de un
    # objeto usando ".", Paiton tiene que acceder a una tabla de hashmap para
    # encontrarlo. Si nos guardamos una referencia a la función "readline()",
    # podemos ahorrarnos unos cuantos ciclos de CPU por cada iteración.
    _r = fm.readline
    while True:
        #chunk = fm.readline()
        chunk = _r()

        # Micro-optimización: dado que estoy optimizando este código para PyPy y
        # no para CPython, puedo aprovecharme del hecho de que aquí acceder a
        # posiciones aleatorios de bytes es más rápido que generar 2 churros de
        # bytes distintos...
        sep = chunk.find(b";")

        try:
            # ... y también me puedo aprovechar del hecho de que parsear un int
            # es más rápido que parsear un float (al revés que en CPython).
            # Y para parsear el int lo que voy a hacer es leer todo desde la
            # posición del separador (";") hasta el final - 3 caracteres, y lo
            # voy a concatenar a los penúltimos 2 caracteres.
            # Básicamente, en el string "LaCiudad;-46.8\n" (aquí tengo "\n" al
            # final del churro de bytes) leo "-46" por un lado y "8" por otro.
            # Voy a parsearlo como int y al final del todo, cuando esté
            # imprimiendo los resultados, dividiré entre 10.
            v = int(chunk[sep+1:-3] + chunk[-2:-1], 10)
        except Exception:
            break

        # En cualquier caso, NO vamos a convertir el churro de bytes en string.
        # Eso es carisimo, no nos lo podemos permitir. Vamos a trabajar con
        # bytes en vez de con strings. Igualmente, ¿quien necesita strings? Los
        # strings estan sobrevalorados.

        # No nos hace falta comprobar si "station" está en el diccionario porque
        # estamos usando un defaultdict, eso nos asegura que va a estar.
        _s = result[chunk[0:sep]]


        # Micro-optimización: en vez de hacer algo así:
        #_s[0] = min(v, _s[0]) # min
        #_s[1] = max(v, _s[1]) # max
        # podemos usar nuestro propio código. min() y max() van a hacer 3
        # comparaciones (cada uno), mientras que el nuestro va a hacer 3 en
        # total. ¿Podríamos mover esto a una nueva función? Pues claro. Pero al
        # dejarlo aquí nos ahorramos el *tremendo* overhead que supone llamar
        # una nueva función.
        #if _s[0] > _s[1]:
        #    _max = _s[0]
        #    _min = _s[1]
        #else:
        #    _max = _s[1]
        #    _min = _s[0]
        #if v > _max:
        #    _max = v
        #if v < _min:
        #    _min = v

        # Micro-optimización: ¿Podríamos mover cada assign a una nueva línea?
        #_s[0] = _min # min
        #_s[1] = _max # max
        #_s[2] = _s[2] + v # avg
        #_s[3] = _s[3] + 1 #count
        # Pues claro. Y nos quedaría la hostia de cuki. Pero aquí hemos venido
        # a raspar cada ciclo de CPU que podemos, así que vamos a meter todo en
        # 1 línea para que el interprete haga los 4 assign en menos operaciones.
        #_s[0], _s[1], _s[2], _s[3] = _min, _max, _s[2] + v, _s[3] + 1

        # Micro-optimización: Ok... podemos hacer todo lo anterior, pero podemos
        # optimizarlo todavía mas: Podemos no asignar los nuevos valores de min
        # y max en cada iteración, sino asignar solo los que han cambiado.
        # "bah... eso ahorra 1 if/else y 2 if, eso no es na..."
        # Te recuerdo, querido lector, que estamos en medio de un bucle que va a
        # procesar ~(1 billón / NP) líneas. Cada instrucción que nos ahorremos
        # va a agregar decenas de miles de ciclos a la ejecución.
        if v < _s[0]:
            _s[0] = v
        elif v > _s[1]:
            _s[1] = v
        _s[2], _s[3] = _s[2] + v, _s[3] + 1

    # Paiton cerrará esto por nosotros
    #fm.close()
    #f.close()

    # Vamos a devolver un array de arrays. Y cada array va a tener el nombre de
    # la ciudad, el min, el max y el avg. Y vamos a ordenarlos porque así cada
    # proceso se encargará de ordenar ~(1 billón / NP) elementos, distribuyendo
    # así el trabajo.
    return [[k, v[0], v[1], v[2] / v[3]] for k, v in sorted(result.items())]
    # station^ min^  max^  avg^

def main():
    # Lo que queremos hacer es distribuir el trabajo entre todos los cores de
    # tal manera para que ninguno se quede sin trabajo. Leemos el tamaño del
    # archivo, lo dividimos entre NP y eso nos da el tamaño (aproximado*) de
    # datos que le daremos a cada proceso.
    file_size = os.path.getsize(FILE)
    chunk_size_per_thread = file_size // NP

    f = open(FILE, "rb")
    fm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)

    workers = []
    start_pos = 0
    ppe = ProcessPoolExecutor()
    for i in range(NP):
        # *aproximado - si le diesemos a todos los procesos el mismo bloque de
        # datos, muy probablemente a alguno de los procesos le daríamos un
        # bloque de datos que no termina en "\n", sino que termina en medio de
        # los datos. Y eso provocaría que perdamos datos...
        # Lo que queremos hacer es ajustar el tamaño con unos bytes más, para
        # llegar al "\n" mas cercano.
        if i == NP - 1:
            end_pos = file_size
        else:
            end_pos = (fm.find(b"\n", (i + 1) * chunk_size_per_thread) + 1)
        workers.append(ppe.submit(consumer, start_pos, end_pos))
        start_pos = end_pos

    # Paiton cerrará esto por nosotros
    #fm.close()
    #f.close()

    # Sabemos que results está ordenado, así que podemos optimizar el acceso a
    # los datos...
    output = []
    for result in zip(*[w.result() for w in workers]):
        # Llegó el momento... vamos a pagar el coste de convertir bytes a utf-8.
        # Pero lo pagamos solo 1 vez por cada ciudad, no 1 billón de veces.
        station = result[0][0].decode("utf-8")

        # ... usando map para que el interprete optimice esta sección.
        mins, maxs, avgs = zip(*map(lambda v: (v[1], v[2], v[3]), result))

        output.append(f"{station}={0.1*min(mins):.1f}/{0.1*(sum(avgs) / len(avgs)):.1f}/{0.1*max(maxs):.1f}")
    print(f"{{{', '.join(output)}}}")

if __name__ == "__main__":
    main()