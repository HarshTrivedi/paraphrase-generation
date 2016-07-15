# Paraphrase Generation web demo

> Open sourced implementation of [this paper](http://www.isi.edu/natural-language/projects/rewrite/bopang.pdf):
**Syntax-based Alignment of Multiple Translations: Extracting Paraphrases
and Generating New Sentences** 
<br>Demo is available [here](http://paraphrase-generation-web-demo.herokuapp.com/).


### Installation

I am assuming that you have `python 2.7` and `pip` installed ! All other requirements are mentioned in `requirements.txt`

Install them as:

```
pip install -r requirements.txt
```

If you are having problem installing them this way, try to install each of the following independently. I am sure this won't be difficult.

* nltk
* pydot
* asciitree
* awesome-print
* requests
* bllipparser

Installing `bllipparser` on mac is a little mess. 
You can follow these links to help: [link1](http://stackoverflow.com/questions/24728405/error-compiling-the-bllip-parser-for-mac), [link2](https://github.com/jbjorne/TEES/issues/14), [link3](https://github.com/BLLIP/bllip-parser/issues/19).
Or else, try running it on linux/ubuntu vm : )

---

**Usage:**

`example.py` documents the basic usage.
* step 1: clone this repo: `https://github.com/HarshTrivedi/paraphrase-generation`
* step 2: go to the root directory: `cd paraphrase-generation/`
* step 3: open python terminal and rest can be done as follows:

```python
from main_lib import *

list_of_equivalent_sentences = [
"At least 12 people were killed in the battle last week",
"At least 12 people lost their lives in last week's fighting",
"Last week's fight took at least 12 lives",
"The fighting last week killed at least 12"
]

fsm = get_fsm(list_of_equivalent_sentences)
# returns instance of Fsm class.

```

Please Note:

* `fsm` instance has `start` and `end` attributes. Each of them is a `FsmNode` instance.

* And each instance of `FsmNode` has `nexts` and `previouses` attributes. Each is a dictionary with key as word labeled edge and value as the next / previous node on that edge.

* Each instance of `FsmNode` is identified by unique id which can be used to indentify the node while traversing.


---

<br><br>
In case you plan to use it in your research, please cite the above paper using:

```
@inproceedings{pang2003syntax,
  title={Syntax-based alignment of multiple translations: Extracting paraphrases and generating new sentences},
  author={Pang, Bo and Knight, Kevin and Marcu, Daniel},
  booktitle={Proceedings of the 2003 Conference of the North American Chapter of the Association for Computational Linguistics on Human Language Technology-Volume 1},
  pages={102--109},
  year={2003},
  organization={Association for Computational Linguistics}
}
```


Please Note: I am NOT any of the authors of of the paper. So, if you want you can consider to verify the implementation from [this demo app](http://paraphrase-generation-web-demo.herokuapp.com/).

In case of any problem, please contact me at: harshjtrivedi94@gmail.com

Hope you find it useful : )
