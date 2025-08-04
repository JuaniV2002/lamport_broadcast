# Coreografía de mensajes

## Flujo general

```
// Secuencia de ejecución típica:
1. Usuario llama broadcast(texto)
2. broadcast() → handle_message() (que incluye deliver_messages()) → flood_message() → send_to_node()
3. Mensajes recibidos → listen_messages() → handle_message() → deliver_messages()
4. _sort_neighbor_msgs() ejecuta continuamente para procesar mensajes de vecinos
```

## broadcast(message_text)

```
FUNCIÓN broadcast(mensaje):
    // Actualizar el reloj lógico
    actualizar_reloj()
    
    // Crear un nuevo mensaje con metadatos
    nuevo_mensaje ← construir_mensaje(mensaje)
    
    // Registrar el mensaje como visto
    registrar_mensaje_visto(nuevo_mensaje)
    
    // Procesar el mensaje localmente
    manejar_mensaje(nuevo_mensaje)
    
    // Propagar el mensaje a otros nodos
    propagar_mensaje(nuevo_mensaje)
FIN FUNCIÓN
```

## handle_message(data)

```
FUNCIÓN handle_message(data):
    // Extraer información relevante del mensaje
    extraer_identificadores(data)
    
    // Verificar si el mensaje ya fue visto
    SI mensaje_ya_visto(data):
        RETORNAR
    FIN SI
    
    // Registrar el mensaje como visto
    registrar_mensaje_visto(data)
    
    // Actualizar el reloj lógico
    actualizar_reloj()
    
    // Propagar el mensaje si corresponde
    SI debe_propagarse(data):
        propagar_mensaje(data)
    FIN SI
    
    // Verificar si el mensaje es antiguo
    SI es_mensaje_antiguo(data):
        RETORNAR
    FIN SI
    
    // Clasificar el mensaje según su origen
    SI es_vecino_directo(data):
        agregar_a_cola_vecino(data)
    SINO:
        agregar_a_pendientes(data)
    FIN SI
    
    // Intentar entregar mensajes pendientes
    entregar_mensajes()
FIN FUNCIÓN
```

## flood_message(message, exlude_node=None)

```
FUNCIÓN flood_message(mensaje, nodo_a_excluir=None):
    PARA CADA vecino EN obtener_vecinos():
        SI nodo_a_excluir NO ES NULO Y vecino = nodo_a_excluir:
            CONTINUAR
        FIN SI
        enviar_a_vecino(vecino, mensaje)
    FIN PARA
FIN FUNCIÓN
```

## send_to_node(node, message)

```
FUNCIÓN send_to_node(node, message):
    // Preparar el mensaje para envío (serialización, codificación, etc.)
    datos_preparados ← preparar_datos_para_envio(message)
    
    // Intentar enviar los datos al nodo destino
    SI enviar_datos(node, datos_preparados):
        RETORNAR VERDADERO
    SINO:
        // Manejar error de envío
        manejar_error_envio(node, message)
        RETORNAR FALSO
    FIN SI
FIN FUNCIÓN
```

## is_old_msg(msg)

```
FUNCIÓN is_old_msg(msg):
    // Verificar si el mensaje ya fue procesado o está en espera
    SI mensaje_ya_entregado_o_en_espera(msg):
        RETORNAR VERDADERO
    SINO:
        RETORNAR FALSO
FIN FUNCIÓN
```

## deliver_messages()

```
FUNCIÓN deliver_messages():
    // Ordenar los mensajes pendientes según la política definida (por ejemplo, timestamp y remitente)
    ordenar_mensajes_pendientes()
    
    repetir:
        entregado ← FALSO
        
        SI hay_mensajes_pendientes():
            msg ← obtener_siguiente_mensaje_pendiente()
            
            SI mensaje_no_entregado(msg):
                // Entregar el mensaje al usuario o sistema
                entregar_mensaje(msg)
                
                // Marcar el mensaje como entregado
                registrar_entrega(msg)
                
                // Remover el mensaje de la lista de pendientes
                remover_mensaje_pendiente(msg)
                
                entregado ← VERDADERO
            FIN SI
        FIN SI
    HASTA QUE NO entregado
FIN FUNCIÓN
```