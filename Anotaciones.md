
**Herramientas**
===============

* Python como lenguaje de programación
* Bibliotecas estándar de Python:
 + `socket` para la comunicación entre procesos
 + `threading` para la ejecución concurrente de tareas
 + `json` para la serialización y deserialización de datos
 + `time` para la gestión del tiempo y la sincronización
 + `random` para la generación de números aleatorios
* Un archivo de configuración (`config.py`) que contiene parámetros como el número de procesos y el mapping de dirreciones usadas.


**Algoritmo Elegido**
==============

**Reloj de Lamport**
---

La idea en que se basa tiene en cuenta un reloj lógico, el mismo constantemente va a incrementando con las diferentes acciones que realiza cada proceso, con ello se vas creando `id`'s unicos, de modo junto con un valor generado de forma pseudo-aleatoria (0-10.000), cada mensaje enviado es completemente distinguible de los demas.

**Envío/manejo de mensajes**: 
**Broadcast**: una vez armado el mensaje lo distribuye a los demás procesos (nodos) de la red.
**Recepcion de mensajes**: cada proceso se mantiene escuchando a la espera de que algún otro envíe algo nuevo.


**Algoritmos alternativos**
=============================

### 1. Algoritmo de Elección de Líder por Paxos

El algoritmo de Paxos es un protocolo de consenso distribuido que permite a un conjunto de procesos llegar a un acuerdo sobre un valor propuesto, incluso en presencia de fallos. En este caso, se utiliza Paxos para elegir un líder.

**Pseudocódigo**
```
INICIO
  Proposer:
    elige un número de propuesta único
    envía una solicitud de preparación (prepare) a la mayoría de los Acceptors

  Acceptor:
    si el número de propuesta es mayor que cualquier número de propuesta visto anteriormente
      responde con una promesa de no aceptar propuestas anteriores
      incluye el valor de la propuesta más reciente aceptada (si existe)
    fin si

  Proposer:
    si recibe promesas de la mayoría de los Acceptors
      elige un valor para la propuesta (puede ser el valor más reciente aceptado)
      envía una solicitud de aceptación (accept) a la mayoría de los Acceptors
    fin si

  Acceptor:
    si recibe una solicitud de aceptación con un número de propuesta que coincide con su promesa
      acepta la propuesta y notifica al Learner
    fin si

  Learner:
    si recibe notificaciones de aceptación de la mayoría de los Acceptors
      el valor propuesto es elegido
      el proceso que propuso el valor se convierte en el líder
      envía mensajes de heartbeat a todos los procesos
    fin si

  mientras true
    si no recibo mensajes de heartbeat del líder
      inicia una nueva ronda de Paxos para elegir un nuevo líder
    fin si
  fin mientras
FIN
```

En este algoritmo, los procesos se dividen en tres roles: Proposer, Acceptor y Learner. El Proposer propone un valor (en este caso, el liderazgo), los Acceptors aceptan o rechazan las propuestas, y los Learners aprenden el valor elegido.
 Si el líder falla, se inicia una nueva ronda de Paxos para elegir un nuevo líder.

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

    si no recibo mensajes de heartbeat del líder
      inicia una nueva ronda de elección de líder
    fin si
  fin mientras
FIN
```

### 3. Algoritmo de Elección de Líder por Algoritmo de Raft

En este algoritmo de consenso distribuido, para elegir al líder cada proceso vota por un líder y el proceso que recibe más votos es el líder.

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

    si no recibo mensajes de heartbeat del líder
      inicia una nueva ronda de votación para elegir un nuevo líder
    fin si

    si un proceso no responde a los mensajes de heartbeat
      se considera caído y se notifica a los demás procesos
    fin si
  fin mientras
FIN
```