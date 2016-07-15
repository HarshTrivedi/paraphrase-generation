import nltk
nltk.data.path.append('./nltk_data/')
from collections import Counter
from nltk import word_tokenize
from nltk.tree import MultiParentedTree
from awesome_print import ap
import copy
import re
from itertools import groupby
from parse_forest_lib import *
import itertools


class Fsm:

	def __init__(self ):
		self.start = None
		self.end = None
		self.last_unique_node_id = 0
		self.token_start_dictionary = {}
		self.token_end_dictionary = {}
		self.all_nodes = []

	# isntance method
	def get_next_unique_node_id(self):
		self.last_unique_node_id += 1
		return self.last_unique_node_id

	# instance method
	def get_node(self, id):
		nodes = self.list_nodes()
		return filter(lambda node: node.id == id, nodes)[0]

	# merge b in a's place
	def is_connected(self, node_a, node_b):
		return node_b in node_a.nexts.values() or node_a in node_b.nexts.values()


	def merge_fsm_nodes(self, fsm_node_a, fsm_node_b ):
		if fsm_node_a.id != fsm_node_b.id:
			for key, prev_node in fsm_node_b.previouses.items():
				prev_node.nexts[key] = fsm_node_a 
				fsm_node_a.previouses[key] = prev_node 
				self.token_start_dictionary[key] = prev_node
				self.token_end_dictionary[key] = fsm_node_a
			for key, next_node in fsm_node_b.nexts.items():
				fsm_node_a.nexts[key] = next_node
				next_node.previouses[key] = fsm_node_a
				self.token_start_dictionary[key] = fsm_node_a
				self.token_end_dictionary[key] = next_node
			self.all_nodes.remove(fsm_node_b)

	def print_fsm( self ):
		start = self.start
		ap("Node Id: {}".format( start.id ))
		for key, next_node in start.nexts.items():
			print("key: {}  => Node Id: {}".format(key, next_node.id ))
		print("\n")
		for key, next_node in start.nexts.items():
			ap( "From Node {} taking key {}".format(start.id, key))
			self.print_sub_fsm(next_node)

	def print_sub_fsm(self, start):
		ap("Node Id: {}".format( start.id ))
		if self.end == start:
			ap("===== Reached End ======")

		for key, next_node in start.nexts.items():
			print("key: {}  => Node Id: {}".format(key, next_node.id ))
		print("\n")
		for key, next_node in start.nexts.items():
			ap( "From Node {} taking key {}".format(start.id, key))
			self.print_sub_fsm(next_node)

	def get_graphvis_commands(self):
		start = self.start
		commands = []
		for key, next_node in start.nexts.items():
			command = "	{} -- {} [ label = \"{}\" ];".format(start.id, next_node.id, key)
			commands.append( command )
			commands.extend( self.get_graphvis_subcommands(next_node) )
		return list(set(commands))

	def get_graphvis_subcommands(self, start):
		commands = []
		for key, next_node in start.nexts.items():
			command = "	{} -- {} [ label = \"{}\" ];".format(start.id, next_node.id, key)
			commands.append( command )
			commands.extend( self.get_graphvis_subcommands(next_node) )
		return commands


	# instance method
	def load_tokens(self, tokens):

		if self.start is None:
			start_fsm_node = FsmNode(self.get_next_unique_node_id())
			self.start = start_fsm_node
			self.all_nodes.append(start_fsm_node)
		start_fsm_node = self.start 

		if self.end is None:
			end_fsm_node = FsmNode(self.get_next_unique_node_id())
			self.end = end_fsm_node
			self.all_nodes.append(end_fsm_node)
		end_fsm_node = self.end

		for token in tokens[0:(len(tokens)-1)]:
			next_fsm_node = FsmNode(self.get_next_unique_node_id())
			start_fsm_node.set_next_fsm_node(next_fsm_node, token)	
			self.token_start_dictionary[token] = start_fsm_node
			self.token_end_dictionary[token] = next_fsm_node			
			start_fsm_node = next_fsm_node
			self.all_nodes.append(next_fsm_node)

		start_fsm_node.set_next_fsm_node(end_fsm_node, tokens[-1])
		self.token_start_dictionary[tokens[-1]] = start_fsm_node
		self.token_end_dictionary[tokens[-1]] = end_fsm_node			

	# instance method
	def merge_parallel_tokens(self, tokens_1, tokens_2):
		node_x = self.token_start_dictionary[tokens_1[0]]
		node_y = self.token_start_dictionary[tokens_2[0]]
		self.merge_fsm_nodes( node_x, node_y )
		node_x = self.token_end_dictionary[tokens_1[-1]]
		node_y = self.token_end_dictionary[tokens_2[-1]]
		self.merge_fsm_nodes( node_x, node_y )

	def list_nodes(self):
		start = self.start
		nodes = [start]
		nodes.extend(start.nexts.values())
		for next_node in start.nexts.values():
			nodes.extend(self.sublist_nodes(next_node))
		all_nodes = list(set(nodes))
		self.all_nodes = all_nodes
		return list(set(nodes))

	def sublist_nodes(self, start):
		nodes = []
		nodes.extend(start.nexts.values())
		for next_node in start.nexts.values():
			nodes.extend(self.sublist_nodes(next_node))
		return nodes


	def convert_to_word_edges(self):
		self.all_nodes
		for node_x in self.all_nodes:
			for key, node_y in node_x.nexts.items():
				node_x.nexts.__delitem__(key)
				node_x.nexts[ParseForest.id_to_word_dictionary[int(key)]] = node_y
			for key, node_y in node_x.previouses.items():
				node_x.previouses[ParseForest.id_to_word_dictionary[int(key)]] = node_y



	def sqeeze(self):

		all_merges_made = set()
		merges_made = 100
		while merges_made > 0:
			merges_made = 0
			for node_x in self.all_nodes:
				word_keys = map( lambda key: ParseForest.id_to_word_dictionary[int(key)] , node_x.nexts.keys() )
				for word_key, word_key_count in Counter(word_keys).items():
					if word_key_count > 1:
						keys = filter( lambda key: ParseForest.id_to_word_dictionary[int(key)] == word_key , node_x.nexts.keys())
						nodes = map( lambda key: node_x.nexts[key], keys)
						for node_a, node_b in itertools.combinations( nodes, 2):
							if node_a.id != node_b.id:

								if not all_merges_made.__contains__( "-".join([str(node_a.id), str(node_b.id)])):
									if not self.is_connected(node_a, node_b):
										if node_b in self.all_nodes:
											self.merge_fsm_nodes(node_a, node_b)
											all_merges_made.add("-".join([str(node_a.id), str(node_b.id)]))
											all_merges_made.add("-".join([str(node_b.id), str(node_a.id)]))
											merges_made += 1
									else:
										if node_b in node_a.nexts.values():
											word_id = ParseForest.next_unique_word_id("*e*")
											node_a.nexts[word_id] = node_b
											node_b.previouses[word_id] = node_a
										else:
											word_id = ParseForest.next_unique_word_id("*e*")
											node_b.nexts[word_id] = node_a
											node_a.previouses[word_id] = node_b
										all_merges_made.add("-".join([str(node_a.id), str(node_b.id)]))

		merges_made = 100
		while merges_made > 0:
			merges_made = 0
			for node_x in self.all_nodes:
				word_keys = map( lambda key: ParseForest.id_to_word_dictionary[int(key)] , node_x.previouses.keys() )
				for word_key, word_key_count in Counter(word_keys).items():
					if word_key_count > 1:
						keys = filter( lambda key: ParseForest.id_to_word_dictionary[int(key)] == word_key , node_x.previouses.keys())
						nodes = map( lambda key: node_x.previouses[key], keys)
						for node_a, node_b in itertools.combinations( nodes, 2):
							if node_a.id != node_b.id:
								if not all_merges_made.__contains__( "-".join([str(node_a.id), str(node_b.id)])):
									if not self.is_connected(node_a, node_b):
										if node_b in self.all_nodes:
											self.merge_fsm_nodes(node_a, node_b)
											all_merges_made.add("-".join([str(node_a.id), str(node_b.id)]))
											all_merges_made.add("-".join([str(node_b.id), str(node_a.id)]))
											merges_made += 1
									else:
										if node_b in node_a.nexts.values():
											word_id = ParseForest.next_unique_word_id("*e*")
											node_a.nexts[word_id] = node_b
											node_b.previouses[word_id] = node_a
										else:
											word_id = ParseForest.next_unique_word_id("*e*")
											node_b.nexts[word_id] = node_a
											node_a.previouses[word_id] = node_b

										all_merges_made.add("-".join([str(node_a.id), str(node_b.id)]))

	def get_graphviz_code(self):
		pre = "graph finite_state_machine {\n	rankdir=LR; \n        size=\"9,9\";\n"
		# start_end_definitions = "	node [shape = doublecircle ]; 1 2;\n".format(self.start.id, self.end.id)
		# node_definition = "	node [shape = circle ];\n"
		start_end_definitions = "	node [shape = doublecircle, width=.2, fixedsize=true, label=\"\"]; 1 2;\n".format(self.start.id, self.end.id)
		node_definition = "	node [shape = circle, width=.2, fixedsize=true, label=\"\" ];\n"
		fsm_commands = (self.get_graphvis_commands())
		fsm_commands = list( set(fsm_commands) )
		transition_definitions = "\n".join( fsm_commands )
		post = "\n}"
		fsm_gv_code_snipped = pre + start_end_definitions + node_definition + transition_definitions + post
		return fsm_gv_code_snipped


class FsmNode:

	def __init__(self, id ):
		self.id = id
		self.nexts = {}
		self.previouses = {}

	# instance method
	def set_next_fsm_node(self, node, key ):
		self.nexts[key] = node
		node.previouses[key] = self

