from .dag import OboGraph, AbstractNode, AbstractEdge


class SubGraph(OboGraph):

    """A subgraph of a provided super_graph with node contents filtered to those
    containing words from the provided keyword_list."""
    
    def __init__(self, super_graph, namespace_filter=None, allowed_relationships=None):
        self.super_graph = super_graph
        self.top_node = None
        self._mapping = None

        if self.super_graph.namespace_filter and self.super_graph.namespace_filter != namespace_filter:
            raise Exception("Unless a namespace_filter is not specified for a parent_graph, a subgraph's namespace_filter must not differ from its parent graph's namespace_filter.\nsubgraph namespace_filter = {}, supergraph namespace_filter = {}").format(namespace_filter, self.super_graph.namespace_filter)
        
        if self.super_graph.allowed_relationships and allowed_relationships and any(relationship not in self.super_graph.allowed_relationships for relationship in allowed_relationships):
            raise Exception("Unless an allowed_relationships list is not specified for a parent graph, a subgraph's allowed_relationships list must be a subset of, or exactly, its parent graph's allowed_relationships list.\nsubgraph allowed_relationships = {}, supergraph allowed_relationships = {}").format(allowed_relationships, self.super_graph.allowed_relationships)
        
        super().__init__(namespace_filter, allowed_relationships)

    @property
    def mapping(self):
        if self._modified and self.top_node:
            self._mapping = {id: self.top_node.id for id in self.id_index.keys()}
        elif not self.top_node:
            raise Exception("Mapping failed: top-node not identified.")
        return self._mapping
    

    def subnode(self, super_node):
        if super_node.id not in self.id_index:
            self.add_node(super_node)
        return self.id_index[super_node.id]

    def add_node(self, super_node):
        self._modified = True
        subgraph_node = SubGraphNode(super_node, self.allowed_relationships)
        if self.valid_node(subgraph_node):
            super().add_node(subgraph_node)

    def connect_subnodes(self):
        self._modified = True
        for subnode in self.node_list:
            subnode.child_node_set.update([self.id_index[child.id] for child in subnode.super_node.child_node_set if child.id in self.id_index])
            subnode.parent_node_set.update([self.id_index[parent.id] for parent in subnode.super_node.parent_node_set if parent.id in self.id_index])


    def extend_subgraph(self):
        graph_extension_nodes = set()
        for subleaf in self.leaves:
            start_node = self.super_graph.id_index[subleaf.id]
            end_node = self.super_graph.id_index[self.top_node.id]

            # Adds all nodes in the super_graph that are between the subgraph leaf nodes
            # and the top_node of the subgraph.
            graph_extension_nodes.update(self.nodes_between(start_node, end_node))

            # Adds all super_graph descendants of the subgraph leaf nodes.
            # Double check with Moesley if this is appropriate 
            graph_extension_nodes.update(self.super_graph.id_index[subleaf.id].descendants)
        
        for super_node in graph_extension_nodes:
            if super_node.id not in self.id_index:
                self.add_node(super_node)
        self.connect_subnodes()

    @staticmethod
    def find_top_node(subgraph, keyword_list):
        if len(subgraph.node_list) == 1:
            return subgraph.node_list[0]
        elif not subgraph.node_list:
            raise Exception("Subgraph did not seed any nodes from the supergraph! Aborting.")
        else:
            candidates = [node for node in subgraph.node_list if any(word in node.name for word in keyword_list) and node not in subgraph.leaves and not node.obsolete]
            top_node_scoring = {node: len(node.descendants) for node in candidates}
            return max(top_node_scoring, key=top_node_scoring.get)

    @staticmethod
    def from_filtered_graph(super_graph, keyword_list, namespace_filter=None, allowed_relationships=None):

        subgraph = SubGraph(super_graph, namespace_filter, allowed_relationships)

        keyword_list = [word.lower() for word in keyword_list]

        filtered_nodes = super_graph.filter_nodes(keyword_list)

        for super_node in filtered_nodes:
            subgraph.add_node(super_node)

        subgraph.connect_subnodes()

        subgraph.top_node = subgraph.find_top_node(subgraph, keyword_list)

        subgraph.extend_subgraph()

        return subgraph


class SubGraphNode(AbstractNode):

    """An instance of a node within a subgraph of an OBO ontology (super-graph)
    """
    
    def __init__(self, super_node, allowed_relationships=None):
        self.super_node = super_node
        self.edges = set()
        self.parent_node_set = set()
        self.child_node_set = set()
        self._modified = True
        self._descendants = None
        self._ancestors = None

    @property
    def id(self):
        return self.super_node.id

    @property
    def name(self):
        return self.super_node.name
    
    @property
    def definition(self):
        return self.super_node.definition

    @property
    def namespace(self):
        return self.super_node.namespace

    @property
    def obsolete(self):
        return self.super_node.obsolete

class SubGraphEdge(AbstractEdge):

    """"""

    def __init__(self, super_edge):
        self.super_edge = super_edge

    @property
    def parent_node(self):
        return self.super_edge.parent_node

    @property
    def child_node(self):
        return self.super_edge.child_node

    @property
    def relationship(self):
        return self.super_edge.relationship
    