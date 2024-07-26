# Horospheres in hyperbolic right-angled Coxeter groups

## Overview
This library provides code to generate certain horospheres in hyperbolic right-angled Coxeter groups. The code generates a list of vertices whose word length is at most a chosen value $n$, as well as edges between them according to one of two formulas. In the Rips graph, vertices span an edge when they are at distance 2. In the divergence graph, vertices span an edge when they have certain close successor rays. For the chosen value $n$, the time complexity is on the order of $n*\lambda^n$, and generates a number of vertices on the order of $\lambda^n$, where $\lambda$ is the top eigenvalue of a certain matrix. See Jillson-Levitin-Saldin-Stuopis-Wang-Xue, 2024 for more information.

## Dependencies and installation
We assume the user is running Sage 10.3 and Python 3. To install, download the files `words.py`, `enhanced_automaton.py`, `rips_fsm_generator.py`, `rips_horosphere_generator.py`, `divergence_fsm_generator.py`, and `divergence_horosphere_generator.py` and move them somewhere that Python can import from.

## Usage
There is not currently an API for this project, though we hope to add one in a future commit. For now, here is a description of how to run the code. Start with the defining graph $\Gamma$ for a hyperbolic RACG. The code will not check that $\Gamma$ is free of induced squares, since this is computationally expensive. It is also assumed that $\Gamma$ has no separating cliques, and is not itself a clique. You must check these things yourself.

 Convert $\Gamma$ into two dictionaries, which we will refer to as `commutation_dict` and `order_dict`. `commutation_dict` encodes the edges of $\Gamma$. The keys are strings labeling the vertices $v$ of $\Gamma$, and their values are the set of (labels of) adjacent vertices. Note that `commutation_dict[v]` should not include `v` itself. `order_dict` encodes the shortlex order on the vertices. Each vertex should be mapped to a distinct value. `order_dict[v]<order_dict[w]` when $v$ proceeds $w$ in the shortlex order. In a future commit, we may add a tool to perform this conversion.

 Then, choose some pair of non-adjacent vertices in $\Gamma$ to generate the defining ray. The two vertex labels should be placed into a tuple, which we will refer to as `ray`. The defining ray is then an infinite alternation between `ray[0]` and `ray[1]`, starting with `ray[0]`. We will denote this ray `\gamma`.

 To generate the Rips or divergence graph on the group $W_\Gamma$ with defining ray `\gamma`, import either `rips_horosphere_generator.py` or `divergence_horosphere_generator.py`, and instantiate a `RipsHorosphereGenerator` or `DivergenceHorosphereGenerator` with parameters `(commutation_dict, order_dict, ray)`. Then select which horosphere you would like by choosing a `busemann_value` and choose the size of graph you would like ($n$ in the first paragraph), which we will call `length`. Bear in mind the exponential time complexity in the length parameter. Call the method `horosphere_as_networkx(length, busemann_value)`. The return value will be a `networkx.Graph` of the desired graph.

 ### Visualization
 Graph visualization is hard! We do not provide a visualization suite because there is not one best way to see a horosphere in general. For the paper Jillson-Levitin-Saldin-Stuopis-Wang-Xue, 2024, we exported the resulting graphs into the `graphml` format, and then plotted them using various graph visualization tools in Mathematica. You may find this to be a helpful approach. If not, there are many other Python libraries devoted to graph visualization.

## Authors
This code was written by Noah Jillson, Daniel Levitin, Pramana Saldin, and Katerina Stuopis. It builds on work of Noah Jillson, Daniel Levitin, Katerina Stuopis, Qianruixi Wang, and Kaicheng Xue. All authors contributed equally and are listed in alphabetical order.

 ## License
[MIT](https://choosealicense.com/licenses/mit/)

 ## Further notes
 We hope that the code is well-enough commented to be readable and understandable to those who have already read our paper. Inquiries should be directed to Daniel Levitin, at dlevitin (at) wisc (dot) edu.