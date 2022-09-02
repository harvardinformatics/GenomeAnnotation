#############################################################################
# Python functions to help with the cactus gpu snakemake pipeline
#
# Gregg Thomas, April 2022
#############################################################################

import re

#############################################################################

def remBranchLength(treestring):
# Removes branch lengths from a tree.
	treestring = re.sub('[)][\d\w<>/.eE_:-]+', ')', treestring);
	treestring = re.sub(':[\d.eE-]+', '', treestring);
	return treestring;
    
#############################################################################

def getDesc(d_spec, d_treedict):
# This function takes a species in the current tree and the dictionary of the current tree
# returned by treeparse and finds the direct descendants of the species.
	d_list = [];
	for node in d_treedict:
		if d_treedict[node][1] == d_spec:
			d_list.append(node);

	if d_list == []:
		return [d_spec];
	else:
		return d_list;

#############################################################################

def getClade(c_spec, c_treedict):
# This function takes a species in the current tree and the dictionary of the current tree
# returned by treeparse and finds all tip labels that are descendants of the current node.
# This is done by getting the direct descendants of the current node with getDesc and then
# recursively calling itself on those descendants.

	clade = [];
	c_desc = getDesc(c_spec, c_treedict);
	for d in c_desc:
		if c_treedict[d][2] != 'tip':
			clade.append(getClade(d, c_treedict));
		else:
			clade.append(d);

	r_clade = [];
	for c in clade:
		if type(c) == list:
			for cc in c:
				r_clade.append(cc);
		else:
			r_clade.append(c);

	return r_clade;

#############################################################################

def pathToNode(query_node, target_node, tree_dict):
# Gets all nodes between provided node and root of the tree
	path_to_node = [];
	while tree_dict[query_node][1] != target_node:
		path_to_node.append(tree_dict[query_node][1]);
		query_node = tree_dict[query_node][1];
	return path_to_node;

#############################################################################

def maxDistToTip(node, tree_dict):
# This function returns a list of the nodes between the current node and the root of the tree.

	if tree_dict[node][2] == 'tip':
		return 0;

	tips_to_check = getClade(node, tree_dict);
	max_dist = -1;
	for tip in tips_to_check:
		cur_dist = len(pathToNode(tip, node, tree_dict));
		if cur_dist > max_dist:
			max_dist = cur_dist;

	return max_dist;

#############################################################################
def treeParse(tree, debug=False):
# The treeParse function takes as input a rooted phylogenetic tree with branch lengths and returns the tree with node labels and a
# dictionary with usable info about the tree in the following format:
# node:[branch length (if present), ancestral node, node type, node label (if present)]

	tree = tree.strip();
	if tree[-1] != ";":
		tree += ";";
	# Some string handling

	nodes, bl, supports, ancs = {}, {}, {}, {};
	# Initialization of all the tracker dicts

	topology = remBranchLength(tree);

	if debug == 1:
		print("TOPOLOGY:", topology);

	##########

	nodes = {};
	for n in topology.replace("(","").replace(")","").replace(";","").split(","):
		nodes[n] = 'tip';
	# Retrieval of the tip labels

	if debug == 1:
		print("NODES:", nodes);

	##########

	new_tree = "";
	z = 0;
	numnodes = 1;
	while z < (len(tree)-1):
		new_tree += tree[z];
		if tree[z] == ")":
			node_label = "<" + str(numnodes) + ">";
			new_tree += node_label;
			nodes[node_label] = 'internal';
			numnodes += 1;
		z += 1;
	nodes[node_label] = 'root';
	rootnode = node_label;
	# This labels the original tree as new_tree and stores the nodes and their types in the nodes dict

	if debug:
		print("NEW TREE:", new_tree);
		print("TREE:", tree);
		print("NODES:", nodes);
		print("ROOTNODE:", rootnode);
	
	##########

	topo = "";
	z = 0;
	numnodes = 1;
	while z < (len(topology)-1):
		topo += topology[z];
		if topology[z] == ")":
			node_label = "<" + str(numnodes) + ">";
			topo += node_label;
			numnodes += 1;
		z += 1;
	# This labels the topology with the same internal labels

	if debug:
		print("TOPO:", topo);

	##########

	for node in nodes:
		if node + node in new_tree:
			new_tree = new_tree.replace(node + node, node);

	##########

	for node in nodes:
	# One loop through the nodes to retrieve all other info
		if debug:
			print("NODE:", node);

		if nodes[node] == 'tip':
			supports[node] = "NA";
			if node + ":" in tree:
				cur_bl = re.findall(node + ":[\d.Ee-]+", new_tree);
				cur_bl = cur_bl[0].replace(node + ":", "");
				if debug:
					print("FOUND BL:", cur_bl);
				bl[node] = cur_bl;				
			else:
				bl[node] = "NA";

		elif nodes[node] == 'internal':
			if node + node in new_tree:
				new_tree = new_tree.replace(node + node, node);

			if node + "(" in new_tree or node + "," in new_tree or node + ")" in new_tree:
				if debug:
					print("NO BL OR LABEL");
				supports[node] = "NA";
				bl[node] = "NA";

			elif node + ":" in new_tree:
				supports[node] = "NA";
				cur_bl = re.findall(node + ":[\d.Ee-]+", new_tree);
				cur_bl = cur_bl[0].replace(node + ":", "");
				if debug:
					print("FOUND BL:", cur_bl);
				bl[node] = cur_bl;								

			else:
				cur_bsl = re.findall(node + "[\d\w<>_*+.Ee/-]+:[\d.Ee-]+", new_tree);
				if cur_bsl:
				# If the pattern above is found then the node has both support and branch length
					cur_bs = cur_bsl[0].replace(node, "");
					cur_bs = cur_bs[:cur_bs.index(":")];
					cur_bl = cur_bsl[0].replace(node, "").replace(cur_bs, "").replace(":", "");
					if debug:
						print("FOUND BL AND LABEL:", cur_bl, cur_bs);
					supports[node] = cur_bs;
					bl[node] = cur_bl;
					#new_tree = new_tree.replace(cur_bs, "");
				else:
				# If it is not found then the branch only has a label
					cur_bs = re.findall(node + "[\w*+.<> -]+", new_tree);
					cur_bs = cur_bs[0].replace(node, "");
					if debug:
						print("FOUND LABEL:", cur_bs);
					supports[node] = cur_bs;
					bl[node] = "NA";
					#new_tree = new_tree.replace(cur_bs, "");

		elif nodes[node] == 'root':
			bl[node] = "NA";
			supports[node] = new_tree[new_tree.index(node)+len(node):];
			ancs[node] = "NA";
			continue;
		# Next we get the ancestral nodes. If the node is the root this is set to NA.

		##########

		anc_match = re.findall('[(),]' + node, new_tree);

		anc_match = re.findall(node, topo);
		if debug:
			print("ANC MATCH:", anc_match);

		##########

		anc_tree = new_tree[new_tree.index(anc_match[0]):][1:];
		# Ancestral labels are always to the right of the node label in the text of the tree, so we start our scan from the node label

		if debug:
			print("NODE:", node);
			print("ANC_MATCH:", anc_match);
			print("ANC_TREE:", anc_tree);

		##########
			
		cpar_count = 0;
		cpar_need = 1;

		for i in range(len(anc_tree)):
		# We find the ancestral label by finding the ) which matches the nesting of the number of ('s found
			if anc_tree[i] == "(":
				cpar_need = cpar_need + 1;
			if anc_tree[i] == ")" and cpar_need != cpar_count:
				cpar_count = cpar_count + 1;
			if anc_tree[i] == ")" and cpar_need == cpar_count:
				anc_tree = anc_tree[i+1:];
				ancs[node] = anc_tree[:anc_tree.index(">")+1];
				break;

		if debug:
			print("FOUND ANC:", ancs[node]);
			print("---");

		##########

	####################

	nofo = {};
	for node in nodes:
		nofo[node] = [bl[node], ancs[node], nodes[node], supports[node]];
	# Now we just restructure everything to the old format for legacy support

	if debug:
	# Debugging options to print things out
		print(("\ntree:\n" + tree + "\n"));
		print(("new_tree:\n" + new_tree + "\n"));
		print(("topology:\n" + topo + "\n"));
		print("nodes:");
		print(nodes);
		print()
		print("bl:");
		print(bl);
		print()
		print("supports:");
		print(supports);
		print()
		print("ancs:");
		print(ancs);
		print()
		print("-----------------------------------");
		print()
		print("nofo:");
		print(nofo);
		print()

	return nofo, topo, rootnode;

#############################################################################