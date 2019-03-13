from Connection import Connection;

class State:

    def __init__(self, stateID):
      self.stateID = stateID;

      connection = Connection();
      #get CreatedTime, User, ProjectName for the state and add to graph view
      statedetailsql = """SELECT DISTINCT timeCreated, userId, stateID, projectID, projectName
                        FROM edges
                        WHERE stateID = %s
                        ORDER BY timeCreated"""
      statedetailresult = connection.run_sql(statedetailsql, (self.stateID,));
      connection.close_cursor();

      self.timeCreated = statedetailresult[0]['timeCreated'];
      self.userID = statedetailresult[0]['userId'];
      self.projectName = statedetailresult[0]['projectName'];
      self.projectID = statedetailresult[0]['projectID'];

      return;


###############################################################################################################################

    def get_edges(self):
        edges = ();

        connection = Connection();
        #get the edges for the state and add to edges list
        stateedgessql = """SELECT fromID, toID
                           FROM edges
                           WHERE stateID = %s
                           ORDER BY timeCreated"""
        stateedgesresult = connection.run_sql(stateedgessql, (self.stateID,));
        connection.close_cursor();

        for i in range(0,len(stateedgesresult)):
            fromNode = stateedgesresult[i]['fromID'];
            toNode = stateedgesresult[i]['toID'];
            # cater for edges that return from the DB as empty / incomplete. All edges should connect 2 nodes exactly. If either / both are empty, it is not a valid edge
            #avoid adding to the list to avoid the graph adding empty nodes
            if fromNode != '' and toNode != '':
                edge = (fromNode, toNode);
                edges = edges + ((edge),);

        return edges;

###############################################################################################################################

    def get_nodes(self):
        nodes = {};

        connection = Connection();
        #for each node for the state, get all its properties and add to nodes list
        statenodessql = """SELECT DISTINCT nodeID, nodeName, nodeX, nodeY FROM nodes
                                  WHERE stateID = %s ORDER BY timeCreated"""
        stateedgesresult = connection.run_sql(statenodessql, (self.stateID,));
        connection.close_cursor();

        for i in range(0,len(stateedgesresult)):
            properties = {};
            node = stateedgesresult[i]['nodeID'];
            if node != '':
                properties['pos'] = (int(float(stateedgesresult[i]['nodeX'])),int(float(stateedgesresult[i]['nodeY'])));
                properties['labels'] = stateedgesresult[i]['nodeName'];
                nodes[node] = properties;

        return nodes;

###############################################################################################################################

    def get_paths(self):
        pathssql = "SELECT ID FROM samlogs.directedgraphs WHERE stateID = %s"

        connection = Connection();
        pathsresult = connection.run_sql(pathssql, (self.stateID,))
        connection.close_cursor();

        return pathsresult;
