import signal
import string
import sys

import matplotlib.pyplot as plt
import networkx as nx


class GraphClass:
    """
    Flujo general:
    1. Pregunta si el grafo se capturará manualmente o desde una matriz.
    2. Pregunta si los nodos se nombran como letras o números.
    3. Captura conexiones manuales o matriz binaria.
    4. Genera la lista de aristas sin repetirlas.
    5. Pregunta si el grafo tiene pesos.
    6. Calcula coloración y, si hay pesos, Kruskal.
    7. Muestra un menú para graficar el grafo normal, coloreado, Kruskal o relaciones de matriz.
    """

    # Paleta base para la coloración del grafo.
    # Si se necesitan más colores, getNextColor genera colores adicionales automáticamente.
    COLORS = [
        "#FF6B6B",  # rojo suave
        "#4ECDC4",  # turquesa
        "#D145B3",  # morado rosaseo
        "#F7DC6F",  # amarillo
        "#BB8FCE",  # morado
        "#58D68D",  # verde
        "#F5B041",  # naranja
        "#EC7063",  # coral
        "#5DADE2",  # celeste
        "#AF7AC5",  # violeta
    ]

    def __init__(self):
        """
        Constructor de la clase.

        Aquí se inicializan todos los datos principales del grafo y se dispara
        el menú principal al final.
        """
        signal.signal(signal.SIGINT, self.handleExitSignal)

        self.Matrix = []
        self.MatrixRelations = {}
        self.hasMatrix = False
        self.isDirected = False
        self.inputSource = self.getGraphInputSource()
        self.inputMode = self.getNodeNamingMode()

        if (self.inputSource == "matrix"):
            self.hasMatrix = True
            self.isDirected = True
            self.Matrix = self.getMatrix()
            self.NodesNames = self.getNodesNames(len(self.Matrix), self.inputMode)
            self.NodesEdgesArray = self.getNodesEdgesArrayFromMatrix()
            self.MatrixRelations = self.getMatrixRelations()
        else:
            nodesNumber = self.askPositiveInteger(" [*] Ingresa la cantidad de nodos a operar: \n --> ")
            self.NodesNames = self.getNodesNames(nodesNumber, self.inputMode)
            self.NodesEdgesArray = self.getNodesEdgesArray()

        self.Edges = self.getEdges()
        self.MatrixEdges = self.getMatrixEdgesWithLoops() if self.hasMatrix else []

        # haveWeights indica si ya se capturaron pesos para las aristas.
        # Se usa para saber si se deben dibujar etiquetas de pesos y si se puede ejecutar Kruskal.
        self.haveWeights = False
        self.EdgesWeights = []
        self.KruscalEdgesArray = []

        self.askForWeights()
        self.NodesColored = self.getColorGraph()

        if (self.haveWeights):
            self.KruscalEdgesArray = self.getKruscalGraph()

        self.mainMenu()

    def handleExitSignal(self, signalNumber, currentFrame):
        """
        Maneja Ctrl+C.

        Esta función se registra con signal.signal dentro del constructor.
        Permite cerrar el programa con un mensaje más limpio en lugar de mostrar
        el traceback
        """
        print("\n [*] Programa finalizado con Ctrl+C. Gracias por usar el sistema de grafos.")
        sys.exit(0)

    def getGraphInputSource(self):
        """
        Pregunta de dónde saldrá la estructura del grafo.

        Manual:
        - El usuario escribe las conexiones de cada nodo.

        Matriz:
        - El usuario captura una matriz binaria cuadrada.
        """
        while (True):
            print(" [*] Selecciona el origen del grafo:\n 1) Manual\n 2) Matriz binaria")
            answer = input(" --> ").strip()

            match answer:
                case "1":
                    return "manual"
                case "2":
                    return "matrix"
                case _:
                    print(" [!] Valor incorrecto ingresado, intentalo nuevamente")

    def getNodeNamingMode(self):
        """
        Pregunta cómo se nombrarán los nodos.

        Esta función se usa tanto para grafos manuales como para grafos creados
        desde matriz. Así una matriz puede representarse con A, B, C... o con
        1, 2, 3...
        """
        while (True):
            print(" [*] Selecciona el nombramiento de los nodos:\n 1) Alfabético: A, B, C...\n 2) Numérico: 1, 2, 3...")
            answer = input(" --> ").strip()

            match answer:
                case "1":
                    return "alphabetic"
                case "2":
                    return "numeric"
                case _:
                    print(" [!] Valor incorrecto ingresado, intentalo nuevamente")

    def getNodesNames(self, nodesNumber, inputMode):
        """
        Genera los nombres de los nodos según el modo de nombramiento elegido.

        Alfabético: A, B, C...
        Numérico: 1, 2, 3...
        """
        if (inputMode == "alphabetic"):
            return list(string.ascii_uppercase[:nodesNumber])

        return [str(number) for number in range(1, nodesNumber + 1)]

    def getNextColor(self, colorIndex):
        """
        Retorna un color para la coloración del grafo.

        Primero usa la lista COLORS. Si se agotan los colores predefinidos,
        genera colores extra usando el mapa HSV de matplotlib.
        """
        if (colorIndex < len(self.COLORS)):
            return self.COLORS[colorIndex]

        # Se usa la proporción áurea para distribuir mejor los colores generados
        # y evitar que colores consecutivos se parezcan demasiado.
        generatedColorIndex = colorIndex - len(self.COLORS)
        hue = (generatedColorIndex * 0.618033988749895) % 1
        red, green, blue = plt.cm.hsv(hue)[:3]

        return "#{:02X}{:02X}{:02X}".format(
            int(red * 255),
            int(green * 255),
            int(blue * 255),
        )

    def askPositiveInteger(self, message):
        """
        Pide un número entero positivo y repite la pregunta si la entrada no es válida.

        Evita que el programa se rompa si el usuario presiona Enter por accidente,
        escribe texto o ingresa un número menor o igual a cero.
        """
        while (True):
            answer = input(message).strip()

            if (answer == ""):
                print(" [!] No ingresaste ningún valor, intentalo nuevamente")
                continue

            try:
                number = int(answer)
            except ValueError:
                print(" [!] Debes ingresar un número entero válido")
                continue

            if (number <= 0):
                print(" [!] Debes ingresar un número mayor a cero")
                continue

            return number

    def askBinaryValue(self, message):
        """
        Pide un valor binario para la matriz.

        Solo acepta 0 o 1. Si el usuario presiona Enter, escribe texto o ingresa
        otro número, repite la pregunta.
        """
        while (True):
            answer = input(message).strip()

            if (answer == ""):
                print(" [!] No ingresaste ningún valor, intentalo nuevamente")
                continue

            try:
                value = int(answer)
            except ValueError:
                print(" [!] Debes ingresar 0 o 1")
                continue

            if (value not in [0, 1]):
                print(" [!] La matriz debe ser binaria, solo se permite 0 o 1")
                continue

            return value

    def getMatrix(self):
        """
        Captura una matriz binaria cuadrada.

        Matrix[i][j] = 1 significa que existe relación del nodo i hacia el nodo j.
        """
        matrixSize = self.askPositiveInteger(" [*] Ingresa el tamaño de la matriz cuadrada: \n --> ")
        matrix = []

        for row in range(matrixSize):
            matrix.append([])

            for col in range(matrixSize):
                value = self.askBinaryValue(f" [*] Ingresa el valor de fila {row + 1}, columna {col + 1}:\n --> ")
                matrix[row].append(value)

        return matrix

    def getNodesEdgesArrayFromMatrix(self):
        """
        Convierte self.Matrix en NodesEdgesArray para poder reutilizar el flujo del grafo.

        Nota: los valores de la diagonal se usan para analizar reflexividad.
        Los bucles se guardan aparte en MatrixEdges para dibujar el grafo original,
        pero no se agregan aquí para no afectar coloración ni Kruskal.
        """
        nodesEdgesArray = []

        for rowIndex, nodeName in enumerate(self.NodesNames):
            nodeEdges = []

            for colIndex, value in enumerate(self.Matrix[rowIndex]):
                destinationNode = self.NodesNames[colIndex]

                if (value == 1 and destinationNode != nodeName):
                    nodeEdges.append(destinationNode)

            nodesEdgesArray.append({
                "Node": nodeName,
                "List": nodeEdges,
                "EdgesCount": len(nodeEdges),
            })

        return nodesEdgesArray

    def getMatrixEdgesWithLoops(self):
        """
        Genera las aristas completas de la matriz incluyendo bucles.

        Se usa solo para dibujar el grafo original cuando la entrada fue una matriz.
        Así se pueden representar relaciones como A->A sin afectar coloración,
        Kruskal u otras funciones que trabajan mejor sin bucles.
        """
        matrixEdges = []

        for rowIndex, row in enumerate(self.Matrix):
            originNode = self.NodesNames[rowIndex]

            for colIndex, value in enumerate(row):
                if (value == 1):
                    destinationNode = self.NodesNames[colIndex]
                    matrixEdges.append([originNode, destinationNode])

        return matrixEdges

    def countLogicalEdgesByNode(self, nodeName):
        return sum(
            1
            for firstNode, secondNode in self.Edges
            if nodeName == firstNode or nodeName == secondNode
        )

    def countDirectedEdgesByNode(self, nodeName):
        return sum(
            1
            for firstNode, secondNode in self.MatrixEdges
            if nodeName == firstNode
        )

    def isMatrixReflexive(self):
        """
        Una relación es reflexiva si toda la diagonal principal contiene 1.
        """
        for index in range(len(self.Matrix)):
            if (self.Matrix[index][index] != 1):
                return False

        return True

    def getMatrixSymmetryRelations(self):
        """
        Retorna [isSymmetric, isAsymmetric].

        Simétrica: Matrix[i][j] == Matrix[j][i].
        Asimétrica: no existen i,j con Matrix[i][j] = 1 y Matrix[j][i] = 1.
        """
        isSymmetric = True
        isAsymmetric = True
        matrixSize = len(self.Matrix)

        for row in range(matrixSize):
            for col in range(matrixSize):
                if (self.Matrix[row][col] != self.Matrix[col][row]):
                    isSymmetric = False

                if (self.Matrix[row][col] == 1 and self.Matrix[col][row] == 1):
                    isAsymmetric = False

        return [isSymmetric, isAsymmetric]

    def isMatrixTransitive(self):
        """
        Una relación es transitiva si i->j y j->k implica i->k.
        """
        matrixSize = len(self.Matrix)

        for i in range(matrixSize):
            for j in range(matrixSize):
                for k in range(matrixSize):
                    if (self.Matrix[i][j] == 1 and self.Matrix[j][k] == 1 and self.Matrix[i][k] != 1):
                        return False

        return True

    def getMatrixRelations(self):
        """
        Calcula las propiedades principales de la matriz de relación.
        """
        symmetryRelations = self.getMatrixSymmetryRelations()

        return {
            "Reflexiva": self.isMatrixReflexive(),
            "Simétrica": symmetryRelations[0],
            "Asimétrica": symmetryRelations[1],
            "Transitiva": self.isMatrixTransitive(),
        }

    def getNodeOrder(self, nodeName):
        """
        Retorna la posición original del nodo dentro de self.NodesNames.

        Se usa para desempatar ordenamientos respetando el nombramiento elegido:
        - A, B, C... si el grafo es alfabético.
        - 1, 2, 3... si el grafo es numérico.
        """
        return self.NodesNames.index(nodeName)

    def getSortedNodesByEdgeCount(self):
        """
        Retorna los nodos ordenados para la coloración.

        Criterio:
        1. EdgeCount descendente.
        2. Nombre/orden del nodo ascendente si hay empate.

        Esta función solo afecta al grafo de coloración y su tabla.
        No se usa para Kruskal.
        """
        return sorted(
            self.NodesEdgesArray,
            key=lambda nodeData: (
                -nodeData["EdgesCount"],
                self.getNodeOrder(nodeData["Node"]),
            ),
        )

    def askForWeights(self):
        """
        Pregunta al usuario si el grafo tendrá pesos.

        Si responde Y, llama a getWeights para capturar y ordenar los pesos.
        Si responde N, el grafo se puede dibujar sin pesos, pero Kruskal pedirá
        los pesos si el usuario intenta usar esa opción después.
        """
        while (True):
            print(" [!] El grafo contiene pesos? [Y/N]")
            answer = input(" --> ").upper().strip()

            if (answer == "Y"):
                self.getWeights()
                return

            if (answer == "N"):
                return

            print(" [!] Valor incorrecto ingresado, intentalo nuevamente")

    def mainMenu(self):
        """
        Menú principal de visualización.

        Permite dibujar:
        1. Grafo original.
        2. Grafo coloreado + tabla de colores.
        3. Grafo Kruskal + tabla de pesos usados.
        4. Todas las visualizaciones anteriores.
        5. Relaciones de matriz (si aplica).
        """
        while (True):
            print(" [*] Selecciona la opcion a representar:\n 1) Grafo Normal\n 2) Grafo de color\n 3) Grafo Kruscal\n 4) Todos\n 5) Relaciones de matriz")
            answer = input(" --> ").strip()

            if (answer == ""):
                print(" [!] No ingresaste ninguna opción, intentalo nuevamente")
                continue

            try:
                answer = int(answer)
            except ValueError:
                print(" [!] Debes ingresar una opción numérica válida")
                continue

            match answer:
                case 1:
                    self.showOriginalGraph()
                case 2:
                    self.showColorGraph()
                case 3:
                    self.showKruscalGraph()
                case 4:
                    self.showAllGraphs()
                case 5:
                    self.showMatrixRelations()
                case _:
                    print(" [!] Valor incorrecto ingresado, intentalo nuevamente")
                    return

            # Se llama al final para mantener abiertas todas las ventanas generadas.
            plt.show()

    def showOriginalGraph(self):
        """
        Muestra únicamente el grafo original.
        """
        self.drawGraph()

    def showColorGraph(self):
        """
        Muestra el grafo coloreado y su tabla de colores.
        """
        self.drawGraph("Grafo de Color", nodeColors=self.NodesColored)
        self.drawColorTable()

    def showKruscalGraph(self):
        """
        Muestra el grafo de Kruskal y su tabla.
        """
        self.ensureKruscalData()
        self.drawGraph("Grafo de Kruscal", edges=self.KruscalEdgesArray)
        self.drawKruscalTable()

    def showMatrixRelations(self):
        """
        Muestra la tabla de relaciones de matriz si el grafo fue capturado por matriz.
        """
        if (self.hasMatrix):
            self.drawMatrixRelationsTable()
        else:
            print(" [!] Esta opción solo está disponible si el grafo fue creado desde una matriz")

    def showAllGraphs(self):
        """
        Muestra todas las visualizaciones disponibles.
        """
        self.showOriginalGraph()
        self.showColorGraph()
        self.showKruscalGraph()

        if (self.hasMatrix):
            self.drawMatrixRelationsTable()
    
    def drawMatrixRelationsTable(self):
        """
        Dibuja una tabla con las propiedades de la matriz de relación.

        Solo se usa cuando el grafo fue creado desde una matriz binaria.
        """
        fig, ax = plt.subplots(num="Relaciones de Matriz")
        ax.axis("off")

        tableData = []

        for relationName, relationValue in self.MatrixRelations.items():
            tableData.append([
                relationName,
                "Sí" if relationValue else "No",
            ])

        if (not any(self.MatrixRelations.values())):
            tableData.append([
                "Sin relaciones detectadas",
                "-",
            ])

        table = ax.table(
            cellText=tableData,
            colLabels=["Relación", "Resultado"],
            cellLoc="center",
            loc="center",
        )

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)

        for rowIndex in range(1, len(tableData) + 1):
            resultText = table[(rowIndex, 1)].get_text().get_text()

            if (resultText == "Sí"):
                table[(rowIndex, 1)].get_text().set_color("green")
                table[(rowIndex, 1)].get_text().set_fontweight("bold")
            elif (resultText == "No"):
                table[(rowIndex, 1)].get_text().set_color("red")

        plt.show(block=False)

    def ensureKruscalData(self):
        """
        Asegura que existan pesos y que Kruskal esté calculado.

        Esto permite que el usuario pueda decir inicialmente que el grafo no tiene
        pesos, pero si después selecciona Kruskal, el programa se los pide.
        """
        if (not self.haveWeights):
            self.getWeights()

        self.KruscalEdgesArray = self.getKruscalGraph()

    def getNodesEdgesArray(self):
        """
        Captura las conexiones de cada nodo.

        Retorna una lista de diccionarios con esta estructura:
        {
            "Node": "A",
            "List": ["B", "C"],
            "EdgesCount": 2
        }

        EdgesCount se usa después para la coloración y para etiquetar los nodos.
        """
        nodesEdgesArray = []

        for nodeName in self.NodesNames:
            nodeEdges = []
            tempNodeEdges = input(f" [!] Ingresa los nodos con los que conceta el nodo {nodeName} separados por comas (,)\n --> ").split(",")

            for nodeEdge in tempNodeEdges:
                # Se normaliza la entrada para evitar errores por espacios o minúsculas.
                nodeEdge = nodeEdge.strip()

                if (self.inputMode == "alphabetic"):
                    nodeEdge = nodeEdge.upper()

                # Solo se aceptan nodos válidos y se evita conectar un nodo consigo mismo.
                if (nodeEdge in self.NodesNames and nodeEdge != nodeName):
                    nodeEdges.append(nodeEdge)

            nodesEdgesArray.append({
                "Node": nodeName,
                "List": nodeEdges,
                "EdgesCount": len(nodeEdges),
            })

        return nodesEdgesArray

    def getEdges(self):
        """
        Convierte NodesEdgesArray en una lista de aristas.

        Manual:
        - Se trata como grafo no dirigido.
        - A-B y B-A cuentan como una sola arista.

        Matriz:
        - Se trata como grafo dirigido.
        - A->B y B->A cuentan como aristas diferentes.
        """
        edges = []

        for nodeData in self.NodesEdgesArray:
            originNode = nodeData["Node"]
            for destinationNode in nodeData["List"]:
                edge = [originNode, destinationNode]
                reversedEdge = [destinationNode, originNode]
                if (edge not in edges and reversedEdge not in edges):
                    edges.append(edge)
        return edges

    def getColorGraph(self):
        """
        Idea general:
        1. Ordena nodos por mayor cantidad de conexiones.
        2. Toma un nodo no coloreado y le asigna un color.
        3. Busca otros nodos no adyacentes para compartir el mismo color.
        4. Repite hasta colorear todos los nodos.
        """
        nodesColored = {}
        colorsUsed = []
        orderedNodes = self.getSortedNodesByEdgeCount()

        for nodeData in orderedNodes:
            nodeName = nodeData["Node"]

            if (nodeName in nodesColored):
                continue

            nodeColor = self.getNextColor(len(colorsUsed))
            colorsUsed.append(nodeColor)

            # excludedNodes contiene los nodos que no pueden usar este color
            # porque son adyacentes a algún nodo ya pintado con ese mismo color.
            excludedNodes = self.createUpdateExcludedNodes(nodeData["List"])
            nodesColored[nodeName] = nodeColor

            for candidateData in orderedNodes:
                candidateName = candidateData["Node"]

                if (candidateName not in excludedNodes and candidateName not in nodesColored):
                    excludedNodes = self.createUpdateExcludedNodes(candidateData["List"], excludedNodes)
                    nodesColored[candidateName] = nodeColor

        return nodesColored

    def getKruscalGraph(self):
        """
        - parents guarda a qué componente pertenece cada nodo.
        - Si dos nodos tienen el mismo parent, agregar su arista formaría ciclo.
        - Si tienen diferente parent, la arista se acepta y se fusionan componentes.
        """
        graphPath = []
        parents = {}

        # Al inicio cada nodo es su propio componente.
        for node in self.NodesNames:
            parents[node] = node

        def find(node):
            """
            Busca la raíz real de la componente del nodo.

            Esto evita errores cuando los padres quedan encadenados, por ejemplo:
            A <- K <- B. Sin find(), podrías comparar padres intermedios y aceptar ciclos.
            """
            if (parents[node] != node):
                parents[node] = find(parents[node])

            return parents[node]

        def union(firstNode, secondNode):
            """
            Une dos componentes si todavía no estaban conectadas.

            Retorna True si la arista se acepta.
            Retorna False si la arista formaría un ciclo.
            """
            firstRoot = find(firstNode)
            secondRoot = find(secondNode)

            if (firstRoot == secondRoot):
                return False

            parents[secondRoot] = firstRoot
            return True

        for edgeData in self.EdgesWeights:
            firstNode, secondNode = edgeData["Edge"]

            if (union(firstNode, secondNode)):
                graphPath.append([firstNode, secondNode])

            # Un árbol generador de n nodos tiene n - 1 aristas.
            # Cuando se alcanza ese tamaño, ya se puede terminar.
            if (len(graphPath) == len(self.NodesNames) - 1):
                break

        return graphPath

    def getWeights(self):
        """
        Captura el peso de cada arista.

        Guarda los datos con esta estructura:
        {
            "Edge": ["A", "B"],
            "Weight": 5
        }

        Al final ordena por peso ascendente y, en caso de empate, por el primer nodo.
        Ese orden es importante para Kruskal porque define qué arista empatada se revisa primero.
        """
        self.haveWeights = True
        self.EdgesWeights = []

        for edge in self.Edges:
            weight = self.askPositiveInteger(f" [!] Ingresa el peso entre el nodo {edge[0]} y el nodo {edge[1]}:\n --> ")
            self.EdgesWeights.append({"Edge": edge, "Weight": weight})

        self.EdgesWeights.sort(key=lambda edgeData: (edgeData["Weight"], edgeData["Edge"][0]))

    def createUpdateExcludedNodes(self, nodesList, excludedNodesList=None):
        """
        Agrega nodos a una lista de exclusión evitando duplicados.

        Se usa principalmente en la coloración para recordar qué nodos no pueden
        recibir el color actual.

        excludedNodesList inicia en None para evitar el problema de listas mutables
        como valor por defecto en Python.
        """
        if (excludedNodesList is None):
            excludedNodesList = []

        for edge in nodesList:
            if (edge not in excludedNodesList):
                excludedNodesList.append(edge)

        return excludedNodesList

    def getNodeLabels(self, drawAsDirected=False):
        """
        Crea las etiquetas de los nodos para el dibujo.

        En el grafo original dirigido muestra Out.
        En los demás grafos muestra Edges para mantener consistencia con coloración y Kruskal.
        """
        nodeLabels = {}

        for nodeName in self.NodesNames:
            if (drawAsDirected):
                labelName = "Out:"
                edgesCount = self.countDirectedEdgesByNode(nodeName)
            else:
                labelName = "Edges:"
                edgesCount = self.countLogicalEdgesByNode(nodeName)
            nodeLabels[nodeName] = f"{nodeName}\n{labelName} {edgesCount}"

        return nodeLabels

    def getEdgesToDraw(self, edges, drawAsDirected):
        """
        Decide qué lista de aristas se debe dibujar.

        - Si se dibuja el grafo original dirigido desde matriz, usa MatrixEdges
          para incluir bucles como A->A.
        - Si se dibuja el grafo original normal, usa Edges.
        - Si se pasa una lista específica, la respeta.
        """
        if (edges is not None):
            return edges

        if (drawAsDirected):
            return self.MatrixEdges

        return self.Edges

    def shouldShowEdgeLabel(self, edge, edges=None):
        """
        Decide si una etiqueta de peso debe mostrarse para una arista.

        Si edges es None, significa que se está dibujando el grafo completo.
        Si el grafo es dirigido, solo coincide la dirección exacta A->B.
        Si el grafo no es dirigido, A-B y B-A son equivalentes.
        """
        if (edges is None):
            return True

        reversedEdge = [edge[1], edge[0]]

        if (self.isDirected):
            return edge in edges

        return edge in edges or reversedEdge in edges

    def getEdgeLabels(self, edges=None):
        """
        Crea las etiquetas de pesos para las aristas.

        En grafos dirigidos solo coincide la arista exacta A->B.
        En grafos no dirigidos también acepta B-A como equivalente.
        """
        edgeLabels = {}

        if (not self.haveWeights):
            return edgeLabels

        for edgeData in self.EdgesWeights:
            edgeTuple = tuple(edgeData["Edge"])
            edge = list(edgeTuple)

            if (self.shouldShowEdgeLabel(edge, edges)):
                edgeLabels[edgeTuple] = edgeData["Weight"]

        return edgeLabels

    def drawGraph(self, title="Original", nodeColors="lightblue", edges=None):
        """
        Dibuja un grafo con NetworkX y Matplotlib.

        Parámetros:
        - title: título de la ventana.
        - nodeColors: puede ser "lightblue" o un diccionario {nodo: color}.
        - edges: si es None dibuja todas las aristas; si recibe lista, dibuja solo esas.

        Esta misma función se reutiliza para:
        - grafo original
        - grafo coloreado
        - grafo de Kruskal
        """
        plt.figure(title, figsize=(14, 10))

        # Solo el grafo original se dibuja como dirigido cuando viene de matriz.
        # Coloración y Kruskal se mantienen como grafos no dirigidos para no mezclar
        # la representación de relaciones con algoritmos que normalmente se trabajan sin dirección.
        drawAsDirected = self.isDirected and edges is None and title == "Original"

        if (drawAsDirected):
            graph = nx.DiGraph()
        else:
            graph = nx.Graph()

        graph.add_edges_from(self.getEdgesToDraw(edges, drawAsDirected))

        nodeLabels = self.getNodeLabels(drawAsDirected)
        edgeLabels = self.getEdgeLabels(edges)

        # Para el grafo coloreado se pasa un diccionario de colores por nodo.
        # NetworkX espera una lista de colores en el mismo orden que graph.nodes().
        if (nodeColors != "lightblue"):
            nodeColors = [nodeColors[nodeName] for nodeName in graph.nodes()]

        # spring_layout acomoda los nodos automáticamente.
        # seed fija el resultado para que no cambie el acomodo en cada ejecución.
        pos = nx.spring_layout(
            graph,
            k=3.0,
            iterations=300,
            seed=42,
            scale=4.0,
        )

        if (drawAsDirected):
            nx.draw(
                graph,
                pos,
                with_labels=False,
                node_size=2200,
                node_color=nodeColors,
                width=2.5,
                arrows=True,
                arrowsize=22,
                connectionstyle="arc3,rad=0.08",
            )
        else:
            nx.draw(
                graph,
                pos,
                with_labels=False,
                node_size=2200,
                node_color=nodeColors,
                width=2.5,
            )

        nx.draw_networkx_labels(
            graph,
            pos,
            labels=nodeLabels,
            font_size=10,
            font_weight="bold",
        )

        if (self.haveWeights):
            nx.draw_networkx_edge_labels(
                graph,
                pos,
                edge_labels=edgeLabels,
                font_size=11,
                label_pos=0.5,
            )

        plt.margins(0.25)
        plt.axis("off")
        plt.show(block=False)

    def drawColorTable(self):
        """
        Dibuja una tabla con la información de la coloración.

        Muestra:
        - nodo
        - número de conexiones
        - color asignado

        El texto de la columna Color se pinta usando el mismo color asignado al nodo.
        """
        fig, ax = plt.subplots(num="Color Table")
        ax.axis("off")

        tableData = []
        cellColors = []

        sortedNodes = self.getSortedNodesByEdgeCount()

        for nodeData in sortedNodes:
            nodeName = nodeData["Node"]
            nodeColor = self.NodesColored[nodeName]

            tableData.append([
                nodeName,
                self.countLogicalEdgesByNode(nodeName),
                nodeColor,
            ])

            cellColors.append([
                "white",
                "white",
                "white",
            ])

        table = ax.table(
            cellText=tableData,
            colLabels=["Nodo", "Edges", "Color"],
            cellLoc="center",
            loc="center",
            cellColours=cellColors,
        )

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)

        # La fila 0 es el encabezado, por eso start=1.
        for index, nodeData in enumerate(sortedNodes, start=1):
            nodeColor = self.NodesColored[nodeData["Node"]]
            table[(index, 2)].get_text().set_color(nodeColor)
            table[(index, 2)].get_text().set_fontweight("bold")

        plt.show(block=False)

    def drawKruscalTable(self):
        """
        Dibuja una tabla con las aristas seleccionadas por Kruskal.

        Como EdgesWeights ya está ordenado, la tabla sale de menor a mayor peso.
        Solo se agregan las aristas que están en self.KruscalEdgesArray.
        """
        fig, ax = plt.subplots(num="Tabla Kruskal")
        ax.axis("off")

        tableData = []

        for edgeData in self.EdgesWeights:
            edge = edgeData["Edge"]
            reversedEdge = [edge[1], edge[0]]

            if (edge in self.KruscalEdgesArray or reversedEdge in self.KruscalEdgesArray):
                tableData.append([
                    f"{edge[0]} -> {edge[1]}",
                    edgeData["Weight"],
                ])

        table = ax.table(
            cellText=tableData,
            colLabels=["Nodo -> Nodo", "Peso"],
            cellLoc="center",
            loc="center",
        )

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)

        plt.show(block=False)


# Punto de entrada del programa.
# Instanciar GraphClass dispara todo el flujo interactivo desde el constructor.
graph = GraphClass()