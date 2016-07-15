 # !/usr/bin/python3

class OboGraph(object):
    """A pythonic graph of a generic Open Biomedical Ontology (OBO) directed 
    acyclic graph (DAG)"""
    def __init__(self):
        self.node_list = list()  # A list of node objects in the graph
        self.edge_list = list()  # A list of edge objects between nodes in the graph
        self.id_index = dict()  # A dictionary pointing ontology term IDs to the node object representing it in the graph
        self.vocab_index = dict()  # A dictionary pointing every unique word in the ontology to a list of terms that contain that word. CAREFUL WITH THIS ONE

    def add_node(self, node):
        self.node_list.append(node)
        self.id_index[node.id] = node
        for word in node.name+node.definition:
            try:
                self.vocab_index[word].add(node.id)
            except KeyError:
                self.vocab_index[word] = set([node.id])

    def add_edge(self, edge):
        self.edge_list.append(edge)


class GoGraph(OboGraph):
    """A Gene-Ontology-specific DAG"""
    def __init__(self, sub_ontology):
        super().__init__()
        self.sub_ontology = sub_ontology

    def add_node(self, node):
        assert node.sub_ontology  # May or may not add a contition to filter out sub-ontologies here before adding them
        super().add_node(node)

    def add_edge(self, edge):
        super().add_edge(edge) # May or may not add conditions to filter edges to nodes contained in the sub-ontology before adding.

    def connect_nodes(self):
        """Connects nodes by adding node objects to appropriate edge objects 
        and vice-versa. MUST BE CALLED AFTER BOTH NODE AND EDGE LISTS ARE
        POPULATED FROM THE DATABASE FILE"""
        pass

    
"""Can have a bunch of OBO graph objects
that inherit from the generic OboGraph
with specialized information and methods"""


class Edge(object):
    """a generic edge for an OBO node that may be extended later into a 
    subclass for ontologies like GO that are including go term extensions"""
    def __init__(self, parent_id, child_id, relationship, parent_node=None, child_node=None):
        self.parent_id = parent_id
        self.child_id = child_id
        self.relationship = relationship
        self.parent_node = parent_node
        self.child_node = child_node

    def set_parent_node(self, parent_node):
        self.parent_node = parent_node

    def set_child_node(self, child_node):
        self.child_node = child_node
"""
Can I handle the actual nodes pointers like this?
    @property
    def parent_node(self):
        return self._parent_node

    @parent_node.setter
    def parent_node(self, value):
        self._parent_node = value
SP
    @property
    def child_node(self):
        return self._child_node
    
    @child_node.setter
    def child_node(self, value):
        self._child_node = value
""" 


class AbstractNode(object):
    """Generic OBO node contaning all basic properties of a node except for 
    an edge list, which will be ontology-specific and defined in each node 
    object that inherits from this object."""
    def __init__(self):
        self.id = str()
        self.name = list()  # A list of strings (words) in the term name
        self.definition = list()  # ... in the term definition

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_definition(self, definition):
        self.definition = definition


class GoDagNode(AbstractNode):
    """Extends AbstractNode to include GO relevant information"""
    def __init__(self):
        super().__init__()
        self.edges = list()  # A list of edge object pointers in the GO graph
        self.parent_set = set()  # A set of parent (id's | node objects)? in the GO graph
        self.child_set = set()  #... child ... in the GO graph
        self.sub_ontology = str()
        self.obsolete = False

    def set_sub_ontology(self, sub_ontology):
        self.sub_ontology = sub_ontology

    def set_obsolete(self):
        self.obsolete = True

    def add_edge(self, edge):
        pass
    """need to add in methods for adding (node ids | node object 
    pointers) to the dag_parent and dag_child sets"""


class SubDagNode(AbstractNode):
    """Extends Abstract node to include GO relevent information GIVEN SUB-
    GRAPH CONSTRAINTS which deliniate a sub-DAG"""
    def __init__(self):
        super().__init__()
        self.subdag_edges = list()
        self.subdag_parent_set = set()
        self.subdag_child_set = set()
        self.dag_node = None  # Will be the node object in the overall dag, with the full edge list 
    
    def add_subdag_edge(self):
        pass

