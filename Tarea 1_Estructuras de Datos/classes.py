
"""------------------------------------------------------------------------------------------------------------------------------
Tarea 1: Estructuras de Datos (Python)
Efraín Martínez Garza (A01280601)
------------------------------------------------------------------------------------------------------------------------------
Descripción: Implementación de tres estrucutras de datos básicas (stack, queue y table) en Python.
------------------------------------------------------------------------------------------------------------------------------"""

""" Implementación de una pila (stack) 
LIFO (Last In, First Out)
----------------------------------------------------------------------------------------------------------------------------"""

class Stack:

    # Constructor
    def __init__(self):
        self.elementos = []

    # Métodos
    # ---------------------------------------------------------------------------

    # push: Inserta un elemento encima de la pila.
    def push(self, elemento):
        self.elementos.append(elemento)

    # pop: Elimina el elemento en el tope de la pila y lo devuelve.
    def pop(self):
        if not self.is_empty():
            return self.elementos.pop()
        return None  
    
    # size: Regresa el tamaño de la pila (número de elementos).
    def size(self):
        return len(self.elementos)
    
    # is_empty: Devuelve "verdadero" si la pila está vacía, y falso si no lo está.
    def is_empty(self):
        """Devuelve True si el stack está vacío"""
        return len(self.elementos) == 0

    # top: Devuelve el elemento que está en el tope de la pila.
    def top(self):
        if not self.is_empty():
            return self.elementos[-1]
        return None
    
    # bottom: Regresa el valor del elemento ubicado al fondo de la pila.
    def bottom(self):
        if len(self.elementos) != 0:
            return self.elementos[0]
        return None
    
    # print: Imprime los elementos contenidos en la pila.
    def print_items(self):
        if len(self.elementos) == 0:
            print("Pila vacía")
        else:
            for elemento in self.elementos:
                print(elemento, end = " ")


""" Implementación de una fila (Queue) 
FIFO (first In, First Out)
----------------------------------------------------------------------------------------------------------------------------"""

class Queue:

    # Constructor
    def __init__(self):
        self.elementos = []

     # Métodos
    # ---------------------------------------------------------------------------

    # enqueue: Agrega un elemento al final de la fila.
    def enqueue(self, elemento):
        self.elementos.append(elemento)

    # dequeue: Elimina el primer elemento de la fila y lo devuelve.
    def dequeue(self):
        if self.is_empty() == False:
            return self.elementos.pop(0)
        return None
    
    # size: Devuelve el número de elementos contenidos en la fila.
    def size(self):
        return len(self.elementos)
    
    # is_empty: Regresa "verdadero" si la fila está vacía, y "falso" si tiene algún elemento.
    def is_empty(self):
        return len(self.elementos) == 0
    
    # front: Regresa el valor contenido en la primera posición de la fila.
    def front(self):
        if len(self.elementos) != 0:
            return self.elementos[0]
        return None
    
    # last: Regresa el valor de la última posición en la fila.
    def last(self):
        if len(self.elementos) != 0:
            return self.elementos[-1]
        return None
    
    # print: Imprime los elementos contenidos en la fila.
    def print_items(self):
        if len(self.elementos) == 0:
            print("Fila vacía")
        else:
            for elemento in self.elementos:
                print(elemento, end = " ")
                