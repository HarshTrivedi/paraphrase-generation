import nltk
nltk.data.path.append('./nltk_data/')
from parse_forest_lib import *
from fsm_lib import *
import requests
from nltk import word_tokenize
from nltk.tree import MultiParentedTree
from awesome_print import ap
import copy
import re
from bllipparser import RerankingParser
import itertools
import urllib
import pydot
import os
from bllipparser.ModelFetcher import download_and_install_model


print "Loding BLLIP parse model ..."
rrp = RerankingParser.from_unified_model_dir('bllip/models/WSJ')
print "Done."

# def get_svg(data):
# 	graphs = pydot.graph_from_dot_data( data )
# 	svg_string = graphs[0].create_svg()
# 	return svg_string

def get_fsm(list_of_sentences):
	global rrp
	list_of_parsed_strings = map( lambda sentence: rrp.simple_parse(str(sentence)) , list_of_sentences)
	list_of_codified_parse_strings = map( lambda parse_string: ParseForest.codify_parse_string(parse_string) , list_of_parsed_strings)
	list_of_parse_forests = map( lambda codified_parse_string: ParseForest(codified_parse_string),  list_of_codified_parse_strings)
	# list_of_parse_forests = map( lambda codified_parse_string: ParseForest(codified_parse_string),  list_of_parsed_strings)

	merged_forest = ParseForest.merge_list_of_forests( list_of_parse_forests )
	
	aligned_paraphrases_lists = merged_forest.get_aligned_paraphrases()
	fsm = Fsm()
	for codified_parse_string in list_of_codified_parse_strings:
		fsm.load_tokens( ParseForest.get_codified_tokens(codified_parse_string) )

	for aligned_paraphrase_list in aligned_paraphrases_lists:
		for para_1, para_2 in itertools.combinations(aligned_paraphrase_list, 2):
			tokens_1 = word_tokenize( para_1 )
			tokens_2 = word_tokenize( para_2 )
			fsm.merge_parallel_tokens(tokens_1, tokens_2)

	fsm.sqeeze()
	fsm.convert_to_word_edges()

	return fsm