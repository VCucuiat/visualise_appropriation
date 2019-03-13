#todo: check that now that I've added the uniqueID autoincrement to the directepaths table in MYSQL, my procedure still works in the code here adding records to that table
#todo: for each directed_path added, also add progressing_path_ID

import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import unravel_index
from State import State
from Project import Project
from Behaviour import Behaviour
from Path import Path

project = Project('bfe3a0c8-90d9-4c80-9286-2c452e22939f');
project_folder = "samia_caralldirections_14112017";
project_behaviour = "car";
states = project.get_states();
states_with_paths = project.get_states_with_paths();

###############################################################################################################################

def draw_graph(i,j):
    try:
        # initialise states - previous and curent
        previous_state = State(states[i]['stateID']);
        current_state = State(states[j]['stateID']);

        # get the edges from previous & current states
        previous_edges = previous_state.get_edges();
        current_edges = current_state.get_edges();

        # get the nodes from previous & current states
        previous_nodes = previous_state.get_nodes();
        current_nodes = current_state.get_nodes();

        # get added, removed or changed nodes by manipulating them as sets
        previous_nodes_set = set(previous_nodes);
        current_nodes_set = set(current_nodes);
        intersect_nodes_set = current_nodes_set.intersection(previous_nodes_set);
        added_nodes_set = current_nodes_set - intersect_nodes_set;
        removed_nodes_set = previous_nodes_set - intersect_nodes_set;
        changed_nodes_set = set(o for o in intersect_nodes_set if previous_nodes[o] != current_nodes[o]);

        # set newly added nodes color property as red, removed color property as grey, changed color property as yellow, unchanged as black
        for o in removed_nodes_set:
            # the removed nodes will only exist in the previous nodes collection. So add only the removed nodes to the list of current nodes and show in grey
            current_nodes[o] = previous_nodes[o];
            current_nodes[o]['color'] = '#d3d3d3';
        for o in intersect_nodes_set:
            current_nodes[o]['color'] = '#0c101c';
        for o in added_nodes_set:
            current_nodes[o]['color'] = '#d9534f';
        for o in changed_nodes_set:
            current_nodes[o]['color'] = '#ffbb00';

        # get added or removed edges
        previous_edges_set = set(previous_edges);
        current_edges_set = set(current_edges);
        intersect_edges_set = current_edges_set.intersection(previous_edges_set);
        added_edges_set = current_edges_set - intersect_edges_set;
        removed_edges_set = previous_edges_set - intersect_edges_set;

        # start putting the graph together
        G = nx.DiGraph();
        # add the nodes and edges to the graph.
        G.add_nodes_from(current_nodes);
        G.add_edges_from(current_edges);
        # set the nodes attributes - position, color and labels
        nx.set_node_attributes(G, current_nodes);

        # generate the individual directed paths through the graph in the current state & commit to the DB
        state_behaviour = Behaviour(current_state.projectID, current_state.stateID, project_behaviour, G);
        state_behaviour.generatestatepaths();

        # export labels into its separate dictionary - even if the labels are set as graph node attributes, it appears according to documentation
        #that they need to be explicitly exported into its own dictionary. I could have not set_node_attributes above and created the individual
        #attributes separately, but set_node_attributes is a nice way of manipulating the dictionary that I set up in the get_nodes() function against the State
        #and then invoking get_node_attributes is an easy way to separate it out. So instead of returning 3 separate dictionaries from my State class,
        #(which would probably require me to run 3 separate DB queries and 3 separate functions)
        #I return 1 dictionary of dictionaries, and use set_node_attributes and get_node_attributes to split accordingly as the graph drawing functions require it
        labeldict = nx.get_node_attributes(G,'labels');

        # same as the label dictionary, I export the color dictionary. The color needs to be a list for the drawing functions, so I then proceed to add the
        #color to the list. This seems bad as you loose the explicit association to the node that the dictionary provides, but that's whath the drawing
        #graph function needs, so I obey.
        nodecolordict = nx.get_node_attributes(G,'color');
        nodecolorlist = [];
        for key, value in nodecolordict.items():
            nodecolorlist.append(value);

        # same as the label & color dictionary, I export the position dictionary into pos_node
        pos_node = nx.get_node_attributes(G,'pos');

        # by default the labels are shown with their center of the node, horizontally, which sometimes makes them difficult to read. change the labels' positions
        #to be offset by -30 & -20 respectively in relative to their respective nodes and save into pos_label
        pos_label = {}
        for p in pos_node:
            xOffSet = -5
            yOffSet = 0
            pos_label[p] = (pos_node[p][0]+xOffSet,pos_node[p][1]+yOffSet)

        # now draw the nodes, with their position and respective color
        nx.draw_networkx_nodes(G, pos = pos_node, node_color = nodecolorlist, font_size = 10, node_size = 150)
        # now draw the labels, with their position offset as saved earlier in pos_label, and also rotate slightly to look better
        labelDescr = nx.draw_networkx_labels(G, pos = pos_label, labels=labeldict, with_labels=True)
        for n,t in labelDescr.items():
            finDegree = 70
            t.set_rotation(finDegree)

        # now draw the edges, setting the color in three separate calls
        #it's easier doing this, as we don't have any changed edges, only added or removed, which already exist in mutually exclusive sets.
        #besides, it's harder to manipulate the edges as sets than it is with the nodes which as lists, to then keep a parallel ordered list of edge colors
        #similar to what was done for the nodes. 3 calls for the edges removes the need to merge the edges into one collection, as well as the need for a
        #separate, parallel list of colors which don't have a direct reference to the node/edge they belong apart from sequence number.
        nx.draw_networkx_edges(G, pos = pos_node, edgelist=intersect_edges_set, edge_color='#0c101c', arrows=True)
        nx.draw_networkx_edges(G, pos = pos_node, edgelist=added_edges_set, edge_color='#d9534f', arrows=True)
        nx.draw_networkx_edges(G, pos = pos_node, edgelist=removed_edges_set, edge_color='#d3d3d3', arrows=True)

        # add title to plot to see details of state
        title = ('Created: ' + str(current_state.timeCreated) + ' , User: ' + str(current_state.userID) + ' , Project: ' + str(current_state.projectName) + ' , Count: ' + str(j + 1) + ' / ' + str(len(states)) + ' State: ' + str(states[j]['stateID']))
        plt.title(title);
        # save the plot as a png
        path = "C:\work\graphs\Code_Clubs\\" + project_folder + "\\" + str(j + 1) + ".png";
        plt.savefig(path, bbox_inches='tight');
        plt.clf();

        #show the plot as maximised - relevant only in the graph are displayed on screen.
        #mng = plt.get_current_fig_manager()
        #mng.window.showMaximized()
        # show the plot if you want it displayed on screen - by default, don't show on screen, just save as png in the project folder
        #plt.show()

    except:
        f = open("C:\work\graphs\log\\" + project_folder + ".txt","w")
        traceback.print_exc()
        print("Previous State: " + str(previous_state.stateID), file=f);
        print("Current State: " + str(current_state.stateID), file=f);
        f.write("Previous Edges: "); print(previous_edges, file=f);
        f.write("Current Edges: "); print(current_edges, file=f);
        f.write("Previous Nodes: "); print(previous_nodes, file=f);
        f.write("Current Nodes: "); print(current_nodes, file=f);

        f.close()

###############################################################################################################################

def generateProjectPhotos():
    for i in range(1,len(states)):
        draw_graph(i-1, i);

###############################################################################################################################

def set_progressive_path():
    # for the first state, the progressive_path_ID is the same as the ID of the unique directed path itself
    first_state = State(states_with_paths[0]['stateID']);
    print(first_state.stateID);
    paths = first_state.get_paths();
    for i in range(0,len(paths)):
        path = Path(paths[i]['ID']);
        path.set_progressingID_same();

    # go through the rest of the states and update current state's paths progressing_path_ID based on previous state's paths progressing_path_ID
    for i in range(0,len(states_with_paths)-1):
        # initialise states - previous and curent
        current_state = State(states_with_paths[i+1]['stateID']);
        previous_state = State(states_with_paths[i]['stateID']);

        current_paths = current_state.get_paths();
        previous_paths = previous_state.get_paths();

        #get the size of the maxtrix
        rows = len(current_paths) + 1;
        columns = len(previous_paths) + 1;
        similarity_matrix = np.zeros((rows,columns));
        #PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT
        print(similarity_matrix);

        # fill up the matrix
        current_blocks_list = [];
        for k in range(0,len(current_paths)):
            path = Path(current_paths[k]['ID']);
            current_blocks_list.append(path.get_blockIDs_inpath());
            similarity_matrix[k+1][0] = path.ID;

        previous_blocks_list = [];
        for l in range(0,len(previous_paths)):
            path = Path(previous_paths[l]['ID']);
            previous_blocks_list.append(path.get_blockIDs_inpath());
            similarity_matrix[0][l+1] = path.ID;

        for u in range(0,len(current_paths)):
            for v in range(0,len(previous_paths)):
                similarity_score = 0;
                #it's not just how many blocks are in common between the 2 paths: previous & current, but how many are in common / total number of current blocks - percentage

                for x in range(1,len(current_blocks_list[u])):
                    for y in range(1,len(previous_blocks_list[v])):
                        if current_blocks_list[u][x] == previous_blocks_list[v][y]:
                            similarity_score = similarity_score + 1;
                similarity_matrix[u+1][v+1] = int((similarity_score / max(len(current_blocks_list[u])-1,len(previous_blocks_list[v])-1)) * 100);
        #PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT
        print(similarity_matrix);

        # go through the matrix and update the progressive paths accordingly
        # go from 0 to number of rows -1 (ignore the first row which containts the previous path IDs)
        for i in range(0,rows-1):
            # check if there are still columns to go through - meaning new paths to assign progressive_pathIDs to. There might be rows (paths from the previous states) more than columns (paths from the current state)
            if similarity_matrix.shape[1] > 1:
                #x = unravel_index(similarity_matrix[1:,1:].argmax(), similarity_matrix.shape);
                #x = np.where(similarity_matrix[1:,1:] == similarity_matrix[1:,1:].max())
                similarity_matrix_values = similarity_matrix[1:,1:]
                #print(similarity_matrix_values.max());
                #print(np.nanargmax(similarity_matrix_values, axis=1));
                #print(np.where(similarity_matrix_values==similarity_matrix_values.max()))
                # only calculate the maximum from the actual similarity values, not including the path IDs which could be higher in value than the similarity scores
                x = unravel_index(np.argmax(similarity_matrix_values, axis=None), similarity_matrix_values.shape);
                x = tuple(y+1 for y in x)
                print(x)
                # update the progressing path of current state with the progressing path of the old states
                current_pathID = similarity_matrix[x[0]][0];
                previous_pathID = similarity_matrix[0][x[1]];
                #PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT
                print(current_pathID);
                print(previous_pathID);

                current_path = Path(int(current_pathID));
                previous_path = Path(int(previous_pathID));
                previous_progressing_pathID = previous_path.progressing_path_ID;
                #PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT
                print(previous_progressing_pathID);
                #update the path with ID pathID with the progressing path of the
                current_path.set_progressingID(previous_progressing_pathID);
                #updatepathIDresult = connection.run_sql(updatepathIDsql, (previous_progressing_pathID, current_pathID));

                similarity_matrix = np.delete(similarity_matrix,x[0],0);
                similarity_matrix = np.delete(similarity_matrix,x[1],1);
                #PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT
                print(similarity_matrix);
            else:
                break;

        #for the remaining new paths in the matrix, update to itself
        for i in range(1,similarity_matrix.shape[0]):
            print(int(similarity_matrix[i][0]));
            path = Path(int(similarity_matrix[i][0]));
            path.set_progressingID_same();


###############################################################################################################################

    # when running the code, start by drawing the very first graph in the project states
draw_graph(0,0);
    # once the first plot is shown, proceed with saving all the states as plots for that project as images into the relevant "C:\work\graphs\" folder
    #named as <StudentName><ProjectName>_<ddmmyy>
generateProjectPhotos();
set_progressive_path();

###############################################################################################################################

# navigating the states via left & right keys when the graphs are displayed on screen
#by default the graphs are not displayed on screen, just saved as pngs in the relevant project folder

# initiate the prevous_state_id as -1 and current_state_id as 0 because in the key_event method, I need to increment/decrement before I draw, otherwise
#I end up in an infinite drawing of exactly the same plot without ever getting to the increment/decrement:
#draw_graph, plt_show, key_press_event; draw_graph, plt_show, key_press_event; draw_graph, plt_show, key_press_event; etc. etc. etc.
#but this way, I increment, then I draw;
# draw_graph, plt_show, key_press_event; increment; draw_graph, plt_show, key_press_event; increment; draw_graph, plt_show, key_press_event; etc. etc. etc.
#previous_state_id = -1;
#current_state_id = 0;

#def key_event(event):
#    global current_state_id
#    global previous_state_id
#
#    event.canvas.figure.clear()
#
#    if event.key == "right":
#        if current_state_id <= len(states):
#            previous_state_id+=1;current_state_id+=1;
#            draw_graph(previous_state_id, current_state_id)
#        else:
#            draw_graph(len(states), len(states));
#    elif event.key == "left":
#        if previous_state_id > 0:
#            previous_state_id-=1;current_state_id-=1;
#            draw_graph(previous_state_id, current_state_id)
#        else:
#            draw_graph(0, 0);
#
# catch the key press events
#fig = plt.figure();
#fig.canvas.mpl_connect('key_press_event', key_event);
