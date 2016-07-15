import nltk
nltk.data.path.append('./nltk_data/')
from nltk import word_tokenize
from nltk.tree import MultiParentedTree
from awesome_print import ap
import copy
import re
from bllipparser import RerankingParser
from bllipparser.ModelFetcher import download_and_install_model
import itertools
from nltk.corpus import stopwords

stop_words = stopwords.words('english')

class Node:

	def __init__(self):
		self.equivalences = None
		self.level = None
		self.label = None
		self.parent_edge = None
		self.child_edges = []


	def left_child(self):
		left_edge = filter(lambda edge: edge.side_type == "left" , self.child_edges)
		if len(left_edge) > 0:
			return left_edge[0].child_node
		else:
			return None

	def right_child(self):
		right_edge = filter(lambda edge: edge.side_type == "right" , self.child_edges)
		if len(right_edge) > 0:
			return right_edge[0].child_node
		else:
			return None

	def mid_child(self):
		mid_edge = filter(lambda edge: edge.side_type == "mid" , self.child_edges)
		if len(mid_edge) > 0:
			return mid_edge[0].child_node
		else:
			return None

	def children(self):
		children = [self.left_child(), self.mid_child(), self.right_child() ]
		children = [child for child in children if child is not None]
		return children

	def child_labels(self):
		return "-".join( map( lambda child: child.label, self.children()) )

	def all_equivalence_tokens(self):
		tokens = []
		for equivalence in self.equivalences:
			tokens.extend( equivalence.split(" ") )
		# return map(lambda token: ParseForest.id_to_word_dictionary[int(token)], tokens)
		return tokens

	def print_node_details(self):
		print("Start Node: (label) {}".format(self.label))
		print("Start Node: (level) {}".format(self.level))
		print("Equivalences:")
		print(self.equivalences)
		print("Parent Edge:")
		if self.parent_edge:
			print(self.parent_edge.merged_ids)
		else:
			print "None"
		print("Child Edges:")
		print(",".join(map(lambda edge: str(edge.merged_ids), self.child_edges)))
		print self.child_labels()
		print "\n"


class Edge:

	def __init__(self):
		self.parent_node = None
		self.child_node = None
		self.side_type = None
		self.merged_ids = []


class ParseForest:

	last_unique_edge_id = 0
	last_unique_word_id = 0
	id_to_word_dictionary = {}


	@classmethod
	def tone_down_parse_tree(cls, ptree):
		for check_node in ptree.subtrees():
			if len(list(check_node)) > 2: 
				if check_node[0].label() == check_node[1].label():
					check_node[0].extend(check_node[1])
					check_node.remove(check_node[1])
				elif check_node[1].label() == check_node[2].label():
					check_node[1].extend(check_node[2])
					check_node.remove(check_node[2])
		return ptree

	@classmethod 	# class method
	def next_unique_word_id(cls, word):
		cls.last_unique_word_id += 1
		cls.id_to_word_dictionary[ cls.last_unique_word_id ] = word
		return str(cls.last_unique_word_id)

	@classmethod 	# class method
	def codify_parse_string(cls, parse_string):
		return re.sub( r'(\([\w$]+ )([\w\']+)', lambda match: match.group(1) + ParseForest.next_unique_word_id(match.group(2)) , parse_string )


	@classmethod
	def get_codified_tokens(cls, codified_parse_string):
		return map( lambda match: match[1] , re.findall( r'(\([\w$]+ )([\w\']+)', codified_parse_string ) )


	@classmethod 	# class method
	def next_unique_edge_id(cls):
		cls.last_unique_edge_id += 1
		return cls.last_unique_edge_id

	def __init__(self, parsed_string ):

		ptree = MultiParentedTree.fromstring( parsed_string  )
		ptree = ParseForest.tone_down_parse_tree(ptree)
		self.ptree = ptree
		self.root = ParseForest.build_forest( ptree )
		# ptree.draw()

	@classmethod 	# class method
	def merge_parallel_nodes(cls, node_a, node_b):
		node_a.equivalences += node_b.equivalences
		node_a.equivalences = list( set(node_a.equivalences) )
		if node_a.parent_edge:
			node_a.parent_edge.merged_ids += node_b.parent_edge.merged_ids
			node_a.parent_edge.merged_ids = list( set(node_a.parent_edge.merged_ids) )
		# for child_b in node_b.children():
		# 	child_b.parent_edge.parent_node = node_a
		# 	node_a.child_edges += [child_b.parent_edge]


	@classmethod 	# class method
	def merge_isolated_node(cls, parent_node_b, node_b ):
		parent_edge_b = node_b.parent_edge
		if parent_node_b:
			parent_edge_b.parent_node = parent_node_b
			parent_node_b.child_edges += [parent_edge_b]
		parent_edge_b.child_node = node_b

	@classmethod 	# class method
	def merge_forest(cls, parse_forest_1, parse_forest_2):

		node_a = parse_forest_1.root#()
		node_b = parse_forest_2.root#()

		merge_next_level = node_a.child_labels() == node_b.child_labels()

		ParseForest.merge_parallel_nodes( node_a, node_b)

		if not cls.check_if_permitted(node_a, node_b):
			merge_next_level = False

		if merge_next_level:
			for node_x, node_y in zip( node_a.children(), node_b.children() ):
				ParseForest.merge_parallel_nodes( node_x, node_y )
				ParseForest.merge_sub_forest(node_x, node_y)
		else:
			for node_x, node_y in zip( node_a.children(), node_b.children() ):
				ParseForest.merge_isolated_node( node_a, node_y )
		return parse_forest_1

	@classmethod
	def check_if_permitted(cls, node_a, node_b):
		node_a_left_child = node_a.left_child()
		node_a_right_child = node_a.right_child()
		node_b_left_child = node_b.left_child()
		node_b_right_child = node_b.right_child()

		if node_a_left_child is not None and node_b_right_child is not None:
			tokens_x = map( lambda x: ParseForest.id_to_word_dictionary[int(x)] , node_a.left_child().all_equivalence_tokens())
			tokens_y = map( lambda x: ParseForest.id_to_word_dictionary[int(x)] , node_b.right_child().all_equivalence_tokens())
			tokens_x = [token for token in tokens_x if token not in stop_words]
			tokens_y = [token for token in tokens_y if token not in stop_words]
			condition_1 = bool(set(tokens_x) & set(tokens_y))
		else:
			condition_1 = False
		if node_b_left_child is not None and node_a_right_child is not None:
			tokens_x = map( lambda x: ParseForest.id_to_word_dictionary[int(x)] , node_b.left_child().all_equivalence_tokens())
			tokens_y = map( lambda x: ParseForest.id_to_word_dictionary[int(x)] , node_a.right_child().all_equivalence_tokens())
			tokens_x = [token for token in tokens_x if token not in stop_words]
			tokens_y = [token for token in tokens_y if token not in stop_words]
			condition_2 = bool(set(tokens_x) & set(tokens_y))
		else: 
			condition_2 = False

		if condition_1 or condition_2:
			return False
		else:
			return True


	@classmethod 	# class method		
	def merge_sub_forest(cls, node_a, node_b):

		merge_next_level = node_a.child_labels() == node_b.child_labels()

		if not cls.check_if_permitted(node_a, node_b):
			merge_next_level = False

		if merge_next_level:
			for node_x, node_y in zip( node_a.children(), node_b.children() ):
				ParseForest.merge_parallel_nodes( node_x, node_y )
				ParseForest.merge_sub_forest(node_x, node_y)
		else:
			for node_x, node_y in zip( node_a.children(), node_b.children() ):
				ParseForest.merge_isolated_node( node_a, node_y )




	@classmethod 	# class method
	def build_sub_forest(cls, tree, parent_node, level):

		for child in tree:

			if type(child) is not str:

				is_left_child =  ( len(child.left_siblings() ) == 0 and len(child.right_siblings()) > 0 )
				is_right_child = ( len(child.right_siblings()) == 0 and len(child.left_siblings())  > 0 )
				is_mid_child =   ( len(child.right_siblings()) >  0 and len(child.left_siblings()) > 0) or ( len(child.right_siblings()) == 0 and len(child.left_siblings()) == 0)

				if is_left_child:
					side_type = "left"

				if is_right_child :
					side_type = "right"

				if is_mid_child :
					side_type = "mid"

				node = Node()
				node.level = level
				node.label = child.label()
				node.equivalences = [  " ".join(child.leaves())  ]
				edge = Edge()
				edge.parent_node = parent_node
				edge.child_node = node
				edge.merged_ids = [ ParseForest.next_unique_edge_id() ]
				node.parent_edge = edge
				parent_node.child_edges += [ edge ]
				edge.side_type = side_type
				ParseForest.build_sub_forest(child, node, level + 1)

	@classmethod 	# class method
	def build_forest(cls, tree):
		sentence = " ".join(tree.leaves())
		level = 0
		if len(tree) == 1:
			tree = tree[0]

		root_node = Node()
		root_node.equivalences = [sentence]
		root_node.level = level
		root_node.label = tree.label()
		root_node.parent_edge = None
		root_node.child_edges = []    

		ParseForest.build_sub_forest(tree, root_node, level + 1)
		return root_node

	@classmethod 	# class method
	def merge_list_of_forests(cls, list_of_forests):
		
		list_of_forests = map( lambda forest: copy.copy(forest) , list_of_forests)
		merged_forest = list_of_forests.pop()
		for forest in list_of_forests:
			merged_forest = ParseForest.merge_forest( merged_forest, forest )
		return merged_forest

	# instance method
	def print_forest(self):
		root_node = self.root

		root_node.print_node_details()		
		children = map(lambda edge: edge.child_node , root_node.child_edges )
		
		for child in children:
			self.print_sub_forest( child )


	# instance method
	def print_sub_forest(self, root_node):
		root_node.print_node_details()
		children = map(lambda edge: edge.child_node , root_node.child_edges )
		for child in children:
			self.print_sub_forest( child )

	def get_aligned_paraphrases(self):
		root_node = self.root
		list_of_equivalences = []
		for child in root_node.children():
			list_of_equivalences.append( child.equivalences )
			list_of_equivalences.extend( self.get_aligned_sub_paraphrases( child ) )
		paraphrase_list = (filter(  lambda equivalences: len(equivalences) > 1,   list_of_equivalences))
		# paraphrase_list.reverse()
		return paraphrase_list

	def get_aligned_sub_paraphrases(self, root_node):
		list_of_equivalences = []
		for child in root_node.children():
			list_of_equivalences.append( child.equivalences )
			list_of_equivalences.extend( self.get_aligned_sub_paraphrases( child ) )
		return list_of_equivalences

