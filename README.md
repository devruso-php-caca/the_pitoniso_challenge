# The Pitoniso challenge

El Pitoniso Supremo te reta a que desafíes, en una prueba de rendimiento bruto, la superioridad del Paiton con tu lenguaje de dirty peasant.

## Reglas

* El código ha de realizar algún tipo de operación, ya sea con CPU o IO. Se permite realizar operaciones de lectura / escritura con archivos. No se permite realizar peticiones a internet por la mera razón de no viciar los resultados (ver "Mediciones").
* Mi re-implementación no va a ser una traducción 1:1 de tu código. Por esa razón tu código debe tener un **input claro** (ya sea archivos, parámetros, set de datos inicial, etc...) y un **output claro** (resultado determinista). Trataré lo que ocurra entremedias como una caja negra y lo re-implementaré como me parezca mejor.
* Se permiten únicamente lenguajes interpretados (ej: Ruby, JS, PHP, Tcl, Perl). Si aun así quieres retarme con un lenguaje que compila a código nativo o IL (ej: C, C++, C#, Java, Rust, Go), te acepto el desafio, pero no te vas a llevar el premio (ver "Premios"). Si no estás seguro si tu lenguaje es interpretado o compilado, consulta [este link](https://en.wikipedia.org/wiki/List_of_programming_languages_by_type#Interpreted_languages).
* Se permite usar cualquier característica del lenguaje y librerías o paquetes externos.
* Se permite el uso de interpretes "alternativos" (ej: "Bun en vez de Node"). De la misma manera, me reservo el derecho a usar Cython o PyPy en vez de CPython.
* No quiero poner un límite al número de líneas, pero **no os flipéis**. Me reservo el derecho a descalificar desafíos extremadamente largos. Idealmente vuestro challenge estará en un único archivo y no superará 200 líneas (excluyendo set de datos).
* La duración de la ejecución se medirá con `time`, usando como referencia el `real time` (o "wall clock") y sacando el mejor tiempo de 10 ejecuciones. No se va a medir ni consumo de CPU, ni consumo de RAM, ni consumo energético, ni cualquier otra cosa. Aquí hemos venido a hablar de rendimiento bruto.
* El código debe funcionar en **Linux o Mac**.
* Se admiten tantos reintentos (*"uy haha espera que mejoro mi código a ver si así"*) como te apetezca.
* Como decía aquel vídeo de Youtube, **yo tengo muchos quereseres**, te responderé eventualmente, pero puede que no sea ni hoy ni mañana.

## Instrucciones

Abre un issue en el repo, pega el código de tu challenge junto con los datos de input que tenga (si aplica) y no te olvides de especificar:

* versión concreta del interprete a usar
* comando con el que se debe ejecutar tu código
* (opcional) el avatar que vas a querer que me ponga

## Premio

El ganador elige un avatar para el perdedor y este deberá llevarlo durante 1 semana en Tuiter.
A mayores, tanto si ganáis como si perdéis, vuestro nombre permanecerá hasta el fin del universo en la tabla pitonisa.

## Creditos y demás

Guido, si pierdo será culpa tuya, pero si gano será gracias a mis skills.
