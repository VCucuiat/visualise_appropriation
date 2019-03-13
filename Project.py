from Connection import Connection;

class Project:

    def __init__(self, projectID):
        self.projectID = projectID;
        return;

###############################################################################################################################

    def get_states(self):
        statessql = """SELECT DISTINCT stateID
                                    FROM edges e
                                    WHERE projectID = %s
                                    ORDER BY timeCreated""";
        #get all the states for a project in which a graph has existed - the various changes made to the same project graph over time
        connection = Connection();
        statesresult = connection.run_sql(statessql, (self.projectID,))
        connection.close_cursor();
        return statesresult;

###############################################################################################################################

    def get_states_with_paths(self):
        statessql = """SELECT DISTINCT directedgraphs.stateID, timeCreated FROM samlogs.directedgraphs
                        JOIN samlogs.nodes ON directedgraphs.stateID = nodes.stateID
                        WHERE directedgraphs.projectID = %s
                        ORDER BY timeCreated""";
        #get all the states for a project in which a graph has existed - the various changes made to the same project graph over time
        connection = Connection();
        statesresult = connection.run_sql(statessql, (self.projectID,))
        connection.close_cursor();
        return statesresult;
