
**Herramientas**
===============

* Python como lenguaje de programación
* Bibliotecas estándar de Python:
 + `socket` para la comunicación entre procesos
 + `threading` para la ejecución concurrente de tareas
 + `json` para la serialización y deserialización de datos
 + `time` para la gestión del tiempo y la sincronización
 + `random` para la generación de números aleatorios
* Un archivo de configuración (`config.py`) que contiene parámetros como el número de procesos, el tiempo de espera para la elección de líder y el intervalo de envío de heartbeats

**Algoritmos**
==============

* **Elección de líder**: el algoritmo de elección de líder se utiliza para determinar qué proceso será el líder en un sistema distribuido. En este caso, se utiliza un algoritmo de elección de líder basado en el algoritmo de Bully, que se describe a continuación.
* **Comunicación entre procesos**: se utiliza la biblioteca `socket` para establecer conexiones entre procesos y enviar mensajes entre ellos.
* **Gestión de mensajes**: se utiliza un sistema de gestión de mensajes para manejar los mensajes que se envían entre procesos.

**Elección de líder**
--------------------

* **Algoritmo de Bully**: el algoritmo de Bully es un algoritmo de elección de líder que se utiliza en sistemas distribuidos. El algoritmo funciona de la siguiente manera:
 1. Cada proceso que se inicia envía un mensaje de elección a todos los procesos con un ID más alto.
 2. Si un proceso recibe un mensaje de elección, responde con un mensaje de ack.
 3. Si un proceso no recibe un mensaje de ack dentro de un tiempo determinado, se convierte en el líder.
 4. El líder envía mensajes de heartbeat a todos los procesos para indicar que sigue vivo.
 5. Si un proceso no recibe un mensaje de heartbeat dentro de un tiempo determinado, inicia una nueva elección de líder.

**Funcionamiento del programa**
=============================

* **Iniciación de procesos**: cada proceso se inicia y envía un mensaje de elección a todos los procesos con un ID más alto.
* **Elección de líder**: se selecciona un líder según el algoritmo de Bully.
* **Envío de mensajes**: los procesos envían mensajes entre sí utilizando la biblioteca `socket`.
* **Gestión de mensajes**: se utiliza un sistema de gestión de mensajes para manejar los mensajes que se envían entre procesos.
* **Envío de heartbeats**: el líder envía mensajes de heartbeat a todos los procesos para indicar que sigue vivo.
* **Detección de fallos**: si un proceso no recibe un mensaje de heartbeat dentro de un tiempo determinado, inicia una nueva elección de líder.


**Algoritmos alternativos**
=============================

### 1. Algoritmo de Elección de Líder por Token Ring

Este algoritmo utiliza un token que se pasa entre los procesos en un orden circular. El proceso que posee el token es el líder.

**Pseudocódigo**
```markdown
INICIO
  si soy el proceso inicial
    crea un token y envíalo al siguiente proceso
  fin si

  mientras true
    si recibo el token
      soy el líder
      envía mensajes de heartbeat a todos los procesos
      envía el token al siguiente proceso después de un tiempo determinado
    fin si
  fin mientras
FIN
```

### 2. Algoritmo de Elección de Líder por Árbol de Cobertura

Este algoritmo utiliza un árbol de cobertura para elegir al líder. Cada proceso envía un mensaje a sus vecinos y el proceso que recibe más mensajes es el líder.

**Pseudocódigo**
```markdown
INICIO
  envía un mensaje a todos tus vecinos
  inicializa un contador de mensajes recibidos

  mientras true
    si recibo un mensaje
      incrementa el contador de mensajes recibidos
    fin si

    si soy el proceso con más mensajes recibidos
      soy el líder
      envía mensajes de heartbeat a todos los procesos
    fin si
  fin mientras
FIN
```

### 3. Algoritmo de Elección de Líder por Algoritmo de Raft

Este algoritmo utiliza un algoritmo de consenso distribuido para elegir al líder. Cada proceso vota por un líder y el proceso que recibe más votos es el líder.

**Pseudocódigo**
```markdown
INICIO
  inicializa un contador de votos

  mientras true
    si soy el proceso inicial
      envía un mensaje de votación a todos los procesos
    fin si

    si recibo un mensaje de votación
      vota por el proceso que envió el mensaje
      envía un mensaje de votación a todos los procesos
    fin si

    si soy el proceso con más votos
      soy el líder
      envía mensajes de heartbeat a todos los procesos
    fin si
  fin mientras
FIN
```

