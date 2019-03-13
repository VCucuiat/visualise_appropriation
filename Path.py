from Connection import Connection;

class Path:
    def __init__(self, pathID):
        self.ID = pathID;

        connection = Connection();
        #get CreatedTime, User, ProjectName for the state and add to graph view
        pathdetailsql = """SELECT ID, projectID, stateID, path_id, path_label, valid, invalid_reason, behaviour, progressing_path_ID
                            FROM samlogs.directedgraphs
                            WHERE ID = %s"""
        pathdetailresult = connection.run_sql(pathdetailsql, (self.ID,));
        connection.close_cursor();

        self.projectID = pathdetailresult[0]['projectID'];
        self.stateID = pathdetailresult[0]['stateID'];
        self.path_id = pathdetailresult[0]['path_id'];
        self.path_label = pathdetailresult[0]['path_label'];
        self.valid = pathdetailresult[0]['valid'];
        self.invalid_reason = pathdetailresult[0]['invalid_reason'];
        self.behaviour = pathdetailresult[0]['behaviour'];
        self.progressing_path_ID = pathdetailresult[0]['progressing_path_ID'];

        return;

###############################################################################################################################

    def set_progressingID_same(self):
        connection = Connection();

        updatepathsql = "UPDATE samlogs.directedgraphs set progressing_path_ID = %s WHERE ID = %s"
        updatepathresult = connection.run_sql(updatepathsql, (self.ID,self.ID,));

        connection.close_cursor();
        return;

###############################################################################################################################

    def set_progressingID(self, progressing_ID):
        connection = Connection();

        updatepathsql = "UPDATE samlogs.directedgraphs set progressing_path_ID = %s WHERE ID = %s"
        updatepathresult = connection.run_sql(updatepathsql, (progressing_ID, self.ID,));

        connection.close_cursor();
        return;

###############################################################################################################################

    def get_blockIDs_inpath(self):
        blocksID = self.path_id.split('->');
        return blocksID;
