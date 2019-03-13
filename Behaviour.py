import networkx as nx
from Connection import Connection

class Behaviour:

    def __init__(self, projectID, stateID, project_behaviour, projectGraph):
        self.projectID = projectID;
        self.stateID = stateID;
        self.Graph = projectGraph;
        self.behaviour_name = project_behaviour;
        self.directed_paths = [];
        self.directed_paths_labels = [];
        return;

###############################################################################################################################

    def generatePaths(self, startNode, endNodes, pathSoFar="", pathSoFarLabel =""):
        """
        Recursive function. Finds all paths through the specified
        graph from start node to end node. For cyclical paths, this stops
        at the end of the first cycle.
        """
        labeldict = nx.get_node_attributes(self.Graph,'labels');

        pathSoFar = pathSoFar + "->" + startNode
        pathSoFarLabel = pathSoFarLabel + "->" + labeldict[startNode];
        print('StartNode: '); print(startNode); print('End Nodes: '); print(endNodes);

        for node in self.Graph[startNode]:
            print('Node in self.Graph[startnode]: '); print(node);
            if node in endNodes:
                self.directed_paths.append(pathSoFar + "->" + node)
                self.directed_paths_labels.append(pathSoFarLabel + "->" + labeldict[node])
            else:
                self.generatePaths(node, endNodes, pathSoFar, pathSoFarLabel)

###############################################################################################################################

    def logdirectedpaths(self, startNode, endNodes):

        self.directed_paths = [];  self.directed_paths_labels = [];

        self.generatePaths(startNode, endNodes);

        connection = Connection();

        selectpathsql = """SELECT *
                           FROM samlogs.directedgraphs
                           WHERE projectID = %s
                           AND stateID = %s
                           AND path_id = %s"""

        insertpathsql = """INSERT INTO samlogs.directedgraphs (projectID, stateID, path_id, path_label, behaviour)
                           VALUES (%s, %s, %s, %s, %s)"""

        print('DirectedPath: '); print()
        for i in range(0,len(self.directed_paths)):
            selectpathresult = connection.run_sql(selectpathsql, (self.projectID, self.stateID, self.directed_paths[i]));
            print(selectpathresult)
            if not selectpathresult:
                insertpathresult = connection.run_sql(insertpathsql, (self.projectID, self.stateID, self.directed_paths[i], self.directed_paths_labels[i], self.behaviour_name));

        connection.close_cursor();

    #fileName = "C:\work\graphs\paths\\test.txt"
    #g = open(fileName,"a")
    #print(directed_paths_labels, file=g);
    #g.close()

###############################################################################################################################

    def generatestatepaths(self):

        # generate directed paths through the graph
        start_nodes = [x for x in self.Graph.nodes() if self.Graph.out_degree(x)>=1 and self.Graph.in_degree(x)==0]
        end_nodes = [x for x in self.Graph.nodes() if self.Graph.out_degree(x)==0 and self.Graph.in_degree(x)>=1]
        print('Start Nodes:'); print(start_nodes); print('End Nodes:'); print(end_nodes);
        for startNode in start_nodes:
            self.logdirectedpaths(startNode, end_nodes);
