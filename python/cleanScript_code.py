
"""
File: cleanScript_code.py
Version: v002
Author: Baptiste Audouin
baptiste.audouin.vfx@gmail.com
Date: April 2024
Description: Removes unnecessary nodes from a Nuke script. It gives the user 3 difference addition of type of nodes to remove ( Sources - reads, sticky notes, ... -, disabled nodes, and viewers)
"""


import nuke

#######################################################
#################Script Clean#########################
def cleanScript():
	all_dependencies=[]
	end_message="Nothing to Clean"
	#node=nuke.toNode("cleanScript") ## dev's mode
	node=nuke.thisNode()             ## user's mode

	### Selection Mode Checker #####

	if len(nuke.selectedNodes()) >1:
		Check = True
		nodes = nuke.selectedNodes()
	else:
		nodes=nuke.allNodes()
		Check = False
		
	##List of usefull Nodes ####
	exeption=["Write","BackdropNode"]
	if not node["sources"].value():
		exeption.extend(["Read", "StickyNote", "ReadGeo2", "Camera2", "Group", "BackdropNode"])





	##Delete all the Disable nodes  #####

	if node["Disable"].value():
		for i in nodes:
		    try:
		        if i["disable"].value():
		            if i.Class() =="Write" and i.dependencies():
		                None
		            else:
		                nuke.delete(i)
		                end_message="Clean!"
		                    

		        if i.Class()=="Read" and i.error():
		            nuke.delete(i)
		            end_message="Clean!"
		    except:
		        None
		        
		        
	##List of usefull alone Nodes ####

	if len(nuke.selectedNodes()) >1:
		Check = True
		nodes = nuke.selectedNodes()
	else:
		nodes=nuke.allNodes()
		Check = False
		
		


	alone_node_protection=[]

	for i in nodes:
		for j in i.dependencies():
		    all_dependencies.append(j)
	for i in nodes:
		if not i.dependencies() and i not in all_dependencies:
		    if i.Class() in exeption:
		        alone_node_protection.append(i)
		        

		    
	##Delete viewer nodes inside of groups  #####

	for i in nuke.allNodes():
		if i.Class() == "Group":
		    for j in nuke.allNodes(group = i):
		        if j.Class() == "Viewer":
		            nuke.delete(j)
		            end_message="Clean!"
		if node["viewers"].value() == True and i.Class() == "Viewer":
		    nuke.delete(i)
		    end_message="Clean!"


	## Variable prep   

	selected_nodes=nuke.selectedNodes()

	bad_nodes=[0]


	##Main code #########

	while bad_nodes: ## needs to be iterated for as long as there is bad nodes
		working_nodes=[node]
		all_nodes=[]
		bad_nodes=[]
		exLinked_nodes=[]
		
		all_nodes = nuke.allNodes()
		

		for i in all_nodes: ## check if there is expression link links - if yes, removes it from dependencies - if no, continue with normal dependencies
		    if i.dependencies(nuke.EXPRESSIONS):
		        dependencies = set(i.dependencies()) - set(i.dependencies(nuke.EXPRESSIONS))
		        for j in i.dependencies(nuke.EXPRESSIONS):
		            exLinked_nodes.append(j)
		    else: 
		        dependencies = i.dependencies()
		        
		        
		    
		    for j in dependencies: ## make a list of node in use by other nodes
		        if j not in working_nodes:
		            working_nodes.append(j)
		    if i.Class() == "Write" or i.Class() == "Viewer" or i in alone_node_protection : ## check if the "unused" node is either a Write or in the protected list - if YES count as a usefull node
		        working_nodes.append(i)

		for i in exLinked_nodes: ## add the dependencies of linked nodes to working node variable
		    for j in i.dependencies():
		        working_nodes.remove(j)
		        
		## Substract all the (selected) nodes by the nodes in use by other node to find the node that are not used anywhere
		if Check == True:
		    bad_nodes = (set(all_nodes) - set(working_nodes))- (set(all_nodes) - set(selected_nodes)) # selected Mode
		else:
		    bad_nodes = (set(all_nodes) - set(working_nodes)) ## all nodes Mode
		    
		bad_nodes = set(bad_nodes) - set(exLinked_nodes) ## makes sure expression linked nodes are not removed
		
		## delete the none usefull nodes
		if bad_nodes:
		    for i in bad_nodes:
		        nuke.delete(i)
		        end_message="Clean!"
		    
		


	if len(nuke.selectedNodes()) >1:
		nodes = nuke.selectedNodes()
	else:
		nodes=nuke.allNodes()


	for a in nodes:
		if a.Class()== "BackdropNode":
		    check = True
		    for j in a.getNodes():
		        if j.Class() != "Dot":
		            check = False
		    if check:
		        nuke.delete(a)
		        end_message="Clean!"
		        
		        
	print (end_message)
