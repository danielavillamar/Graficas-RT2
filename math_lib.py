### Normaliza un vector.
def normalize(v):
    length = pow(((v[0])**2 +(v[1])**2 +(v[2])**2 ),0.5)
    return length

### Devuelve una copia normalizada del vector v.
def normalized(v):
    temp= []
    for i in range (len(v)):
        norm = v[i]/ normalize(v)
        temp.append(norm)
    return temp

### Calcula el producto escalar de dos vectores.
def dot(a,b):
    dotproduct =0
    for a,b in zip(a,b):
        dotproduct = dotproduct + a * b
    return dotproduct

### Calcula la diferencia de dos vectores.
def subtract(a, b):
    result = [a[i] - b[i] for i in range(min(len(a), len(b)))]
    return result

### Calcula la suma de dos vectores.
def add (a, b):
    result = [a[i] + b[i] for i in range(min(len(a), len(b)))]
    return result

### Calcula el producto de dos matrices.
def multiply(A,B):
    temp =[]
    for i in range(A):
        for j in range (B):
            mul = A[i] * B [j]
            temp.append(mul)
    return temp

### Calcula la suma de tres vectores.
def addx3 (a, b, c):
    result = [a[i] + b[i] + c[i] for i in range(min(len(a), len(b),  len(c)))]
    return result