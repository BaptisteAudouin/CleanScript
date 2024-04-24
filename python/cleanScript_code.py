
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
#################Script Clean##########################

def cleanScript():

    ##### -- Variable prep -- #####

    ## Selection Mode or not?
    if len(nuke.selectedNodes()) > 1:
        Selected = True
        nodes = nuke.selectedNodes()
    else:
        nodes=nuke.allNodes()
        Selected = False

    coreNode = nuke.toNode("cleanScript") ## dev mode
    #coreNode = nuke.thisNode()           ## user mode

    disableCount = 0
    badNodeCount = 0
    backdropsDeletedCount = 0
    revealedLinkCount = 0
    viewersDeletedCount = 0

    globalCount=1 ## counts every node deleted

    while globalCount>0: ## While Loop to make sure eveything is deleted
        globalCount=0

        ##### -- Deletes Disabled Nodes -- #####


        if coreNode["Disable"].value():
            for i in nodes:
                try:
                    if i["disable"].value() and not (i.Class() == "Write" and i.dependencies()):
                        disableCount+=1
                        globalCount+=1
                        nodes.remove(i)
                        nuke.delete(i)
                except:
                    pass

        #### -- Deletes Viewer inside groups -- #####

        for i in nuke.allNodes("Group"):
            for j in nuke.allNodes("Viewer", group = i):
                nuke.delete(j)


        ## Find the root Nodes  ( selection mode or Not)
        rootNodesList=[]
        for i in nodes:
                if "Write" in i.Class() and i.dependencies():
                    rootNodesList.append(i)
        if Selected:
            allDependencies = nuke.dependencies(nuke.allNodes())
            SelectedDependencies = nuke.dependencies(nodes )
            potentialRootNodes= set(nodes)-set(SelectedDependencies)

            for i in potentialRootNodes:
                if i in allDependencies:
                    rootNodesList.append(i)



        ##### -- Finds which are the un-useful nodes -- #####


        usefulNodes = []
        for i in rootNodesList:
            Dependencies=[i]
            ## CLimbs up the tree from roots nodes looking at dependencies of dependencies ... until there is no left.
            while Dependencies:
                usefulNodes.extend(nuke.dependencies( Dependencies, nuke.INPUTS | nuke.HIDDEN_INPUTS ))
                Dependencies = nuke.dependencies( Dependencies, nuke.INPUTS | nuke.HIDDEN_INPUTS )
        usefulNodes.extend(nuke.dependencies(nodes, nuke.EXPRESSIONS )) # adds expression linked nodes

        usefulNodes.extend(rootNodesList)

        badNodes = set(nodes) - set(usefulNodes)


        ##### -- Deletes unwanted nodes-- #####

        exeption = ["BackdropNode"]

        if not coreNode["stickynotes"].value():
            exeption.append("StickyNote")


        for i in badNodes:
            if i.Class() not in exeption and i != coreNode:
                if not (not coreNode["sources"].value() and i.Class() == "Read"): ## checks if sources should be deleted or not
                    if i.Class() != "Dot": ## count the nodes for display
                        badNodeCount+=1
                        globalCount += 1
                    nodes.remove(i) # proofs potential addition
                    nuke.delete(i)



        for i in usefulNodes:

            ## Reveales links
            try:
                if coreNode["revealLinks"].value() and i.knob("hide_input").value()== True:
                    if not("Stamp" in i.name() and i.knob("title")): # Stamp module protection
                        revealedLinkCount+=1
                        globalCount += 1
                        i.knob("hide_input").setValue(False)
            except:
                pass

            #Deletes viewers
            if i.Class() == "Viewer" and coreNode["viewers"]:
                viewersDeletedCount+=1
                globalCount += 1
                nodes.remove(i) # proofs potential addition
                nuke.delete(i)


        for i in nodes:
            #Deletes backdrop nodes if empty
            try:
                if i.Class()== "BackdropNode" and (not i.getNodes() or any(j.Class() == "StickyNote" for j in i.getNodes())):
                    backdropsDeletedCount+=1
                    globalCount += 1
                    nodes.remove(i)# proofs potential addition
                    nuke.delete(i)
            except:
                pass
    ## End of While Loop

    ##### -- End Message setup-- #####
    
    message =[]
    message.append((" Nodes deleted ",badNodeCount))
    message.append((" Disabled nodes deleted",disableCount))
    message.append((" Backdrops deleted",backdropsDeletedCount))
    message.append((" Revealed links",revealedLinkCount))
    message.append((" Viewers deleted", viewersDeletedCount))


    end_message=""
    for i in message:
        if i[1]>0:
            end_message+="<b><font color='Yellow'>"+str(i[1])+"</font>"+i[0]+"</b><br>"
    if end_message=="":
        nuke.message("Nothing to Clean")
    else:
        nuke.message(end_message)
