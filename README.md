# Proyecto de Grafos en Python

Sistema interactivo para representación y análisis de grafos usando Python, NetworkX y Matplotlib.

El proyecto permite:

- Representar grafos visualmente.
- Colorear grafos usando una heurística greedy.
- Calcular árboles de expansión mínima usando Kruskal.
- Mostrar tablas auxiliares para análisis.
- Trabajar con nodos alfabéticos o numéricos.
- Visualizar pesos y conexiones de cada nodo.

---

# Características

## Grafo Normal

Representa el grafo original ingresado por el usuario.

Incluye:

- Nodos.
- Aristas.
- Número de conexiones por nodo.
- Pesos (si existen).

---

## Coloración de Grafos

Implementa una heurística greedy de coloración.

Características:

- Ordena nodos por mayor EdgeCount.
- Desempata usando el orden original de los nodos.
- Evita que nodos adyacentes compartan color.
- Genera colores automáticamente si se agota la paleta base.

También genera una tabla con:

| Nodo | Vertices | Color |
|------|----------|-------|

---

## Kruskal

Implementa el algoritmo de Kruskal usando Union-Find.

Características:

- Ordenamiento por peso ascendente.
- Prevención de ciclos usando `find()` y `union()`.
- Visualización del árbol de expansión mínima.
- Tabla con las aristas seleccionadas.

Tabla generada:

| Nodo -> Nodo | Peso |
|--------------|------|

---

# Tecnologías utilizadas

- Python 3.10+
- NetworkX
- Matplotlib

---

# Instalación

## 1. Clonar repositorio

```bash
git clone https://github.com/PAJAR1T0/Color-KruscalGraph.git
cd Color-KruscalGraph
```

---

## 2. Configurar dependencias

### Usando uv

```bash
uv sync
```

### Usando venv tradicional

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib networkx
```

---

# Ejecución

## Usando uv

```bash
uv run python main.py
```

## Usando venv tradicional activado

```bash
python3 main.py
```

---

# Flujo del programa

1. Ingresar cantidad de nodos.
2. Elegir nombramiento:
   - Alfabético.
   - Numérico.
3. Ingresar conexiones.
4. Definir si existen pesos.
5. Seleccionar visualización:
   - Grafo normal.
   - Grafo de color.
   - Kruskal.
   - Todas.

---

# Ejemplo de entrada

## Nodos

```text
A: B,C,D
B: A,C
C: A,B,D
D: A,C
```

## Pesos

```text
A-B = 4
A-C = 2
A-D = 7
B-C = 1
C-D = 3
```

---

# Estructuras internas

## NodesEdgesArray

```python
[
    {
        "Node": "A",
        "List": ["B", "C"],
        "EdgesCount": 2
    }
]
```

---

## EdgesWeights

```python
[
    {
        "Edge": ["A", "B"],
        "Weight": 4
    }
]
```

---

# Algoritmos implementados

## Coloración Greedy

Estrategia:

1. Ordenar nodos por EdgeCount descendente.
2. Tomar un nodo sin color.
3. Asignar color.
4. Buscar nodos no adyacentes compatibles.
5. Repetir.

---

## Kruskal + Union-Find

Estrategia:

1. Ordenar aristas por peso.
2. Recorrer aristas.
3. Usar `find()` para detectar componentes.
4. Usar `union()` para fusionarlas.
5. Rechazar ciclos.

---

# Características técnicas

- Manejo de errores de entrada.
- Soporte para Ctrl+C usando `signal`.
- Layout dinámico usando `spring_layout`.
- Tablas auxiliares con Matplotlib.
- Generación dinámica de colores.
- Código documentado para mantenimiento.
