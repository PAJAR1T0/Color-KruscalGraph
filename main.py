import signal
import string
import sys

import matplotlib.pyplot as plt
import networkx as nx


class GraphClass:
    """
    Flujo general:
    1. Pregunta cuántos nodos tendrá el grafo.
    2. Pregunta si los nodos se nombran como letras o números.
    3. Pide las conexiones de cada nodo.
    4. Genera la lista de aristas sin repetirlas.
    5. Pregunta si el grafo tiene pesos.
    6. Calcula coloración y, si hay pesos, Kruskal.
    7. Muestra un menú para graficar el grafo normal, coloreado o Kruskal.
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

    def handleExitSignal(self, signalNumber, currentFrame):
        """
        Maneja Ctrl+C.

        Esta función se registra con signal.signal dentro del constructor.
        Permite cerrar el programa con un mensaje más limpio en lugar de mostrar
        el traceback
        """
        print("\n [*] Programa finalizado con Ctrl+C. Gracias por usar el sistema de grafos.")
        sys.exit(0)

    def getNodesNames(self, nodesNumber):
        """
        Genera los nombres de los nodos según el formato elegido por el usuario.

        Alfabético: A, B, C...
        Numérico: 1, 2, 3...

        Todos los nombres se manejan como strings para que el resto del programa
        pueda comparar nodos sin mezclar tipos int y str.
        """
        while (True):
            print(" [*] Selecciona el tipo de nombramiento de nodos:\n 1) Alfabético: A, B, C...\n 2) Numérico: 1, 2, 3...")
            answer = input(" --> ").strip()

            match answer:
                case "1":
                    return list(string.ascii_uppercase[:nodesNumber])
                case "2":
                    return [str(number) for number in range(1, nodesNumber + 1)]
                case _:
                    print(" [!] Valor incorrecto ingresado, intentalo nuevamente")

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

    def __init__(self):
        """
        Constructor de la clase.

        Aquí se inicializan todos los datos principales del grafo y se dispara
        el menú principal al final.
        """
        signal.signal(signal.SIGINT, self.handleExitSignal)

        nodesNumber = self.askPositiveInteger(" [*] Ingresa la cantidad de nodos a operar: \n --> ")

        self.NodesNames = self.getNodesNames(nodesNumber)
        self.NodesEdgesArray = self.getNodesEdgesArray()
        self.Edges = self.getEdges()

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
        3. Garfo Kruskal + tabla de pesos usados.
        4. Todas las visualizaciones anteriores.
        """
        while (True):
            print(" [*] Selecciona la opcion a representar:\n 1) Grafo Normal\n 2) Grafo de color\n 3) Grafo Kruscal\n 4) Todos")
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
                    self.drawGraph()
                case 2:
                    self.drawGraph("Grafo de Color", nodeColors=self.NodesColored)
                    self.drawColorTable()
                case 3:
                    self.ensureKruscalData()
                    self.drawGraph("Grafo de Kruscal", edges=self.KruscalEdgesArray)
                    self.drawKruscalTable()
                case 4:
                    self.ensureKruscalData()
                    self.drawGraph()
                    self.drawGraph("Grafo de Color", nodeColors=self.NodesColored)
                    self.drawColorTable()
                    self.drawGraph("Grafo de Kruscal", edges=self.KruscalEdgesArray)
                    self.drawKruscalTable()
                case _:
                    print(" [!] Valor incorrecto ingresado, intentalo nuevamente")
                    return

            # Se llama al final para mantener abiertas todas las ventanas generadas.
            plt.show()

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
                nodeEdge = nodeEdge.strip().upper()

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
        Convierte NodesEdgesArray en una lista de aristas sin duplicados.

        Como el grafo es no dirigido, A-B y B-A representan la misma arista.
        Por eso antes de agregar una arista se revisa si su versión inversa ya existe.
        """
        edges = []

        for nodeData in self.NodesEdgesArray:
            originNode = nodeData["Node"]

            for destinationNode in nodeData["List"]:
                edge = [originNode, destinationNode]
                reversedEdge = [destinationNode, originNode]

                if (reversedEdge not in edges):
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

    def getNodeLabels(self):
        """
        Crea las etiquetas de los nodos para el dibujo.

        Cada nodo se dibuja con su nombre y con su número de conexiones.
        Ejemplo:
        A
        Edges: 3
        """
        nodeLabels = {}

        for nodeData in self.NodesEdgesArray:
            nodeName = nodeData["Node"]
            nodeLabels[nodeName] = f"{nodeName}\nEdges: {nodeData['EdgesCount']}"

        return nodeLabels

    def getEdgeLabels(self, edges=None):
        """
        Crea las etiquetas de pesos para las aristas.

        Si edges es None, se retornan todos los pesos del grafo original.
        Si edges trae una lista de aristas, solo se retornan los pesos de esas aristas.
        Esto permite que Kruskal muestre únicamente los pesos usados en su árbol.
        """
        edgeLabels = {}

        if (not self.haveWeights):
            return edgeLabels

        for edgeData in self.EdgesWeights:
            edgeTuple = tuple(edgeData["Edge"])
            reversedEdge = [edgeTuple[1], edgeTuple[0]]

            if (edges is None or list(edgeTuple) in edges or reversedEdge in edges):
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
        graph = nx.Graph()

        if (edges is None):
            graph.add_edges_from(self.Edges)
        else:
            graph.add_edges_from(edges)

        nodeLabels = self.getNodeLabels()
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
                nodeData["EdgesCount"],
                nodeColor,
            ])

            cellColors.append([
                "white",
                "white",
                "white",
            ])

        table = ax.table(
            cellText=tableData,
            colLabels=["Nodo", "Vertices", "Color"],
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