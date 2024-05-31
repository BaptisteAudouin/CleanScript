
"""
File: cleanScript_code.py
Version: v005
Author: Baptiste Audouin
baptiste.audouin.vfx@gmail.com
Date: April 2024
Description: Removes unnecessary nodes from a Nuke script. It gives the user 3 difference addition of type of nodes to remove ( Sources - reads, sticky notes, ... -, disabled nodes, and viewers)
"""
import nukescripts
import nuke
import webbrowser



class cleanScriptPanel( nukescripts.PythonPanel):
    def __init__( self ):
        nukescripts.PythonPanel.__init__( self, 'CleanScript','cleanScript.unique_ID', scrollable=False)

        #CREATE KNOBS

        self.text01 = nuke.Text_Knob("","","<b>Choose what you want to remove:</b>")
        #tick boxes
        self.viewers = nuke.Boolean_Knob('viewers', 'Viewers?', True)
        self.viewers.setFlag(nuke.STARTLINE)
        self.disabled = nuke.Boolean_Knob('disabled', 'Disabled Nodes?', True)
        self.disabled.setFlag(nuke.STARTLINE)
        self.reads = nuke.Boolean_Knob('reads', 'Reads?', False)
        self.reads.setFlag(nuke.STARTLINE)
        self.readInfo = nuke.Text_Knob("", "","<i><font color='grey'>( All type of Reads and All Cameras)</font></i>")
        self.readInfo.clearFlag(nuke.STARTLINE)
        self.backdrops = nuke.Boolean_Knob('backdrops', 'Empty Backdrops?', False)
        self.backdrops.setFlag(nuke.STARTLINE)
        self.stickynotes = nuke.Boolean_Knob('stickynotes', 'Sticky Notes?', True)
        self.stickynotes.setFlag(nuke.STARTLINE)
        self.revealLinks = nuke.Boolean_Knob('revealLinks', 'Reveal hidden links?', True)
        self.revealLinks.setFlag(nuke.STARTLINE)
        self.revealLinksInfo = nuke.Text_Knob("", "", "<i><font color='grey'><i><font color='grey'>( Bypasses STAMPS</font></i>)</font></i>")
        self.revealLinksInfo.clearFlag(nuke.STARTLINE)

        self.divider01 = nuke.Text_Knob("")

        self.text02 = nuke.Text_Knob("","","<b>Important:</b>")
        self.Info = nuke.Text_Knob("","","The bottom of every <i> useful </i>  branche<br><u>needs to be connected to a <b><font color='Yellow'>Write node</font></b></u><br> to be considered <i>useful<i/>.")

        self.divider02 = nuke.Text_Knob(" ", " ", " ")

        self.tutorial = nuke.PyScript_Knob('How it works?', 'tutorial', 'webbrowser.open("https://themilkyway.atlassian.net/wiki/spaces/Knowledge/pages/117473297/Top+bar+Milk+menu")')
        self.tutorial.setFlag(nuke.STARTLINE)

        self.divider03 = nuke.Text_Knob("")

        self.author = nuke.Text_Knob("author","","<i><font color='grey'>CleanScript v4.0 2024 baptiste-audouin.com</font></i><br>")

        self.okButton = nuke.PyScript_Knob('Clean', 'clean', 'cleanScriptTEST.cleanScript()')
        self.okButton.setFlag(nuke.STARTLINE)
        self.cancelButton = nuke.PyScript_Knob('Cancel', 'cancel', '')
        

        #ADD KNOBS

        

        self.addKnob(self.text01)

        self.addKnob( self.viewers)
        self.addKnob( self.disabled)
        self.addKnob( self.reads)
        self.addKnob(self.readInfo)
        self.addKnob( self.backdrops)
        self.addKnob( self.stickynotes)
        self.addKnob( self.revealLinks)
        self.addKnob(self.revealLinksInfo)

        self.addKnob(self.divider01)

        self.addKnob(self.text02)
        self.addKnob(self.Info)
        self.addKnob(self.divider02)

        self.addKnob(self.tutorial)
        self.addKnob(self.divider03)
        self.addKnob(self.author)

        
        self.addKnob(self.okButton)
        self.addKnob(self.cancelButton)


panel = cleanScriptPanel()



def cleanScript():

    ##### -- Variable prep -- #####

    ## Selection Mode or not?
    if len(nuke.selectedNodes()) > 1:
        Selected = True
        nodes = nuke.selectedNodes()
    else:
        nodes=nuke.allNodes()
        Selected = False

    #coreNode = nuke.toNode("cleanScript") ## dev mode
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


        if panel.disabled.value():
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
            ## Climbs up the tree from roots nodes looking at dependencies of dependencies ... until there is no left.
            while Dependencies:
                usefulNodes.extend(nuke.dependencies( Dependencies, nuke.INPUTS | nuke.HIDDEN_INPUTS ))
                Dependencies = nuke.dependencies( Dependencies, nuke.INPUTS | nuke.HIDDEN_INPUTS )
        usefulNodes.extend(nuke.dependencies(nodes, nuke.EXPRESSIONS )) # adds expression linked nodes



            ## Expression linked node expection ( keep the tree up the node) ## THIS LIST IS TO ADJUSTED DEPENDING ON PRODUCTION

        usefulNodes_exceptionList = ["TM_LensInfo"]
        usefulNodes_exception=[]
        for a in usefulNodes_exceptionList:
            for i in usefulNodes:
                if a in i.name():
                    Dependencies = [i]
                    while Dependencies:
                        usefulNodes_exception.extend(nuke.dependencies(Dependencies, nuke.INPUTS | nuke.HIDDEN_INPUTS))
                        Dependencies = nuke.dependencies(Dependencies, nuke.INPUTS | nuke.HIDDEN_INPUTS)
                    usefulNodes_exception.extend(nuke.dependencies(nodes, nuke.EXPRESSIONS))  # adds expression linked nodes
            usefulNodes.extend(usefulNodes_exception)



        usefulNodes.extend(rootNodesList)

        badNodes = set(nodes) - set(usefulNodes)




        ##### -- Deletes unwanted nodes-- #####

        exeption = ["BackdropNode"]

        if not panel.stickynotes.value():  # Deletes StickyNote
            exeption.append("StickyNote")

        if not panel.viewers.value():  # Deletes viewers
            exeption.append("Viewer")


        for i in badNodes:
            if i.Class() not in exeption:
                if not (not panel.reads.value() and ("Read" in i.Class() or "Camera" in i.Class())):  ## checks if sources should be deleted or not ## Will find every type of reads and every type of Camera
                    if i.Class() != "Dot":  ## count the nodes for display
                        badNodeCount += 1
                        globalCount += 1
                    if i.Class() == "Viewer" :
                        viewersDeletedCount += 1
                    nodes.remove(i)  # proofs potential addition
                    nuke.delete(i)

        for i in usefulNodes:

            ## Reveales links
            try:
                if panel.revealLinks.value() and i.knob("hide_input").value()== True:
                    if not("Stamp" in i.name() and i.knob("title")): # Stamp module protection
                        revealedLinkCount+=1
                        globalCount += 1
                        i.knob("hide_input").setValue(False)
            except:
                pass



        if panel.backdrops.value():   #Deletes backdrop nodes if empty
            for i in nodes:
                try:
                    if i.Class()== "BackdropNode" and (not i.getNodes() or any(j.Class() == "StickyNote" for j in i.getNodes())):
                        backdropsDeletedCount+=1
                        globalCount += 1
                        nodes.remove(i)# proofs potential addition
                        nuke.delete(i)
                except:
                    pass


        for i in nuke.dependencies(usefulNodes, nuke.EXPRESSIONS):
            if not any(j in i.name() for j in usefulNodes_exceptionList):
                for k in range(i.inputs()): i.setInput(k, None)

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



def runCleanScriptPane():
    return panel.showModalDialog()
