from main_lib import *


list_of_sentences = [
"At least 12 people were killed in the battle last week",
"At least 12 people lost their lives in last week's fighting",
"Last week's fight took at least 12 lives",
"The fighting last week killed at least 12",
"The battle of last week killed at least 12 persons",
"At least 12 persons died in the fighting last week",
"At least 12 died in the battle last week",
"At least 12 people were killed in the fighting last week",
"During last week's fighting, at least 12 people died",
"Last week at least twelve people died in the fighting",
"Last week's fighting took the lives of twelve people"

]


# please note, the loading of bllip parser is slow;
# generation of fsm is quite quick.
# So it takes time to load main_lib, but subsequent calls are quick.


fsm = get_fsm(list_of_sentences)
# returns instance of Fsm class.


# fsm instance has following attributes:
	# start (FsmNode instance)
	# end (FsmNode instance)

# And each instance of FsmNode has following attributes:
	# nexts (dictionary with key as word labeled edge and value as the next node on that edge)
	# previouses (dictionary with key as word labeled edge and value as the previous node on that edge)

# Each instance of FsmNode is identified by unique id which can be used to indentify the node while traversing.


print fsm.start
print fsm.end
print fsm.start.nexts
print fsm.end.previouses
