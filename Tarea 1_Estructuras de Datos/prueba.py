
"""------------------------------------------------------------------------------------------------------------------------------
Tarea 1: Estructuras de Datos (Python)
Efraín Martínez Garza (A01280601)
------------------------------------------------------------------------------------------------------------------------------
Descripción: Programa para probar el correcto funcionamiento de las clases Stack, Queue y Dictionary.
------------------------------------------------------------------------------------------------------------------------------"""

from classes import Stack, Queue, Dictionary

# Pregunta al usuario: ¿Qué clase desea probar?

print("\n---------------------------------------------------")
print("¿Qué clase desea probar?")
print("---------------------------------------------------")
print("1. Pila (Stack)")
print("2. Fila (Queue)")
print("3. Diccionario (Dictionary)")
print("---------------------------------------------------")
respuesta = int(input("Respuesta: "))

# Prueba de la clase Stack (Pila)
if respuesta == 1:

    # Creación de una pila
    pila = Stack()

    # Pregunta al usuario: ¿Qué desea hacer con la pila?
    print("\n---------------------------------------------------")
    print("¿Qué desea hacer con la pila?")
    print("---------------------------------------------------")
    print("1. Insertar elemento (push)")
    print("2. Eliminar elemento (pop)")
    print("3. Vaciar pila (clear)")
    print("4. Ver tamaño de la pila (size)")
    print("5. Ver si la pila está vacía (is_empty)")
    print("6. Ver elemento en el tope de la pila (top)")
    print("7. Ver elemento en el fondo de la pila (bottom)")
    print("8. Imprimir los elementos de la pila (print_items)")
    print("9. Salir")
    print("---------------------------------------------------")
    respuesta = int(input("Respuesta: "))

    while respuesta != 9:
            
            # Inserción de un elemento
            if respuesta == 1:
                elemento = input("Elemento a insertar: ")
                pila.push(elemento)
                print("Elemento insertado satisfactoriamente.")
    
            # Eliminación de un elemento
            elif respuesta == 2:
                elemento = pila.pop()
                if elemento != None:
                    print("Elemento eliminado satisfactoriamente: " + elemento)
                else:
                    print("La pila está vacía.")
    
            # Vaciado de la pila
            elif respuesta == 3:
                pila.clear()
                print("Pila limpiada satisfactoriamente.")
    
            # Ver tamaño de la pila
            elif respuesta == 4:
                print("Tamaño de la pila: " + str(pila.size()))
    
            # Ver si la pila está vacía
            elif respuesta == 5:
                if pila.is_empty():
                    print("La pila está vacía.")
                else:
                    print("La pila no está vacía.")
    
            # Ver el elemento al tope de la pila
            elif respuesta == 6:
                elemento = pila.top()
                if elemento != None:
                    print("Elemento en el tope de la pila: " + elemento)
                else:
                    print("La pila está vacía.")
    
            # Ver el elemento al fondo de la pila
            elif respuesta == 7:
                elemento = pila.bottom()
                if elemento != None:
                    print("Elemento en el fondo de la pila: " + elemento)
                else:
                    print("La pila está vacía.")
    
            # Imprimir los elementos de la pila
            elif respuesta == 8:
                print("Elementos de la pila: ")
                pila.print_items()
    
            # Pregunta al usuario: ¿Qué desea hacer con la pila?
            print("\n---------------------------------------------------")
            print("¿Qué desea hacer con la pila?")
            print("---------------------------------------------------")
            respuesta = int(input("Respuesta: "))


## Parte 2: Prueba de la clase Queue (Fila)

elif respuesta == 2:

    # Creación de una fila
    fila = Queue()

    # Pregunta al usuario: ¿Qué desea hacer con la fila?
    print("\n---------------------------------------------------")
    print("¿Qué desea hacer con la fila?")
    print("---------------------------------------------------")
    print("1. Insertar elemento (enqueue)")
    print("2. Eliminar elemento (dequeue)")
    print("3. Vaciar fila (clear)")
    print("4. Ver tamaño de la fila (size)")
    print("5. Ver si la fila está vacía (is_empty)")
    print("6. Ver elemento al frente de la fila (front)")
    print("7. Ver elemento al final de la fila (back)")
    print("8. Imprimir los elementos de la fila (print_items)")
    print("9. Salir")
    print("---------------------------------------------------")
    respuesta = int(input("Respuesta: "))
    
    while respuesta != 9:

        # Inserción de un elemento
        if respuesta == 1:
            elemento = input("Elemento a insertar: ")
            fila.enqueue(elemento)

        # Eliminación de un elemento
        elif respuesta == 2:
            elemento = fila.dequeue()
            if elemento != None:
                print("Elemento eliminado satisfactoriamente: " + elemento)
            else:
                print("La fila está vacía.")

        # Vaciado de la fila
        elif respuesta == 3:
            fila.clear()
            print("Fila limpiada satisfactoriamente.")
        
        # Ver tamaño de la fila
        elif respuesta == 4:
            print("Tamaño de la fila: " + str(fila.size()))

        # Ver si la fila está vacía
        elif respuesta == 5:
            if fila.is_empty():
                print("La fila está vacía.")
            else:
                print("La fila no está vacía.")
        
        # Ver el elemento al frente de la fila
        elif respuesta == 6:
            elemento = fila.front()
            if elemento != None:
                print("Elemento al frente de la fila: " + elemento)
            else:
                print("La fila está vacía.")
        
        # Ver el elemento al final de la fila
        elif respuesta == 7:
            elemento = fila.last()
            if elemento != None:
                print("Elemento al final de la fila: " + elemento)
            else:
                print("La fila está vacía.")
        
        # Imprimir los elementos de la fila
        elif respuesta == 8:
            print("Elementos de la fila: ")
            fila.print_items()

        # Pregunta al usuario: ¿Qué desea hacer con la fila?
        print("\n---------------------------------------------------")
        print("¿Qué desea hacer con la fila?")  
        print("---------------------------------------------------")
        respuesta = int(input("Respuesta: "))

## Parte 3: Prueba de la clase Dictionary (Diccionario)

elif respuesta == 3:

    # Creación de un diccionario
    diccionario = Dictionary()

    # Pregunta al usuario: ¿Qué desea hacer con el diccionario?
    print("\n---------------------------------------------------")
    print("¿Qué desea hacer con el diccionario?")
    print("---------------------------------------------------")
    print("1. Insertar clave-valor (insert)")
    print("2. Eliminar clave-valor (remove)")
    print("3. Vaciar diccionario (clear)")
    print("4. Ver tamaño del diccionario (size)")
    print("5. Ver si el diccionario está vacío (is_empty)")
    print("6. Ver valor de una clave (get)")
    print("7. Ver todas las claves (keys)")
    print("8. Ver todos los valores (values)")
    print("9. Ver todos los pares (clave-valor) (items)")
    print("10. Imprimir los elementos del diccionario (print_dict)")
    print("11. Salir")
    print("---------------------------------------------------")
    respuesta = int(input("Respuesta: "))

    while respuesta != 11:

        # Inserción de un par (clave-valor)
        if respuesta == 1:
            clave = input("Clave a insertar: ")
            valor = input("Valor a insertar: ")
            diccionario.insert(clave, valor)
            print("Par insertado satisfactoriamente.")

        # Eliminación de un par (clave-valor)
        elif respuesta == 2:
            clave = input("Clave a eliminar: ")
            if diccionario.is_empty():
                print("El diccionario está vacío.")
            else:
                diccionario.remove(clave)
                print("Par eliminado satisfactoriamente.")
        
        # Vaciado del diccionario
        elif respuesta == 3:
            diccionario.clear()
            print("Diccionario limpiado satisfactoriamente.")
        
        # Ver tamaño del diccionario
        elif respuesta == 4:
            print("Tamaño del diccionario: " + str(diccionario.size()))

        # Ver si el diccionario está vacío
        elif respuesta == 5:
            if diccionario.is_empty():
                print("El diccionario está vacío.")
            else:
                print("El diccionario no está vacío.")
        
        # Ver valor de una clave
        elif respuesta == 6:
            clave = input("Clave a buscar: ")
            valor = diccionario.get(clave)
            if valor != None:
                print("Valor de la clave " + clave + ": " + valor)
            else:
                print("La clave no existe en el diccionario.")
        
        # Ver todas las claves
        elif respuesta == 7:
            print("Claves del diccionario: ", diccionario.keys())
        
        # Ver todos los valores
        elif respuesta == 8:
            print("Valores del diccionario: ", diccionario.values())
        
        # Ver todos los pares (clave-valor)
        elif respuesta == 9:
            print("Pares (clave-valor) del diccionario: ", diccionario.items())

        # Imprimir los elementos del diccionario
        elif respuesta == 10:
            diccionario.print_dict()
        
        # Pregunta al usuario: ¿Qué desea hacer con el diccionario?
        print("\n---------------------------------------------------")
        print("¿Qué desea hacer con el diccionario?")
        print("---------------------------------------------------")
        respuesta = int(input("Respuesta: "))

# Mensaje de finalización
print("\n Fin del programa.")
