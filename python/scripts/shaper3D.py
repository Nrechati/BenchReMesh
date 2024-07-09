#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.12.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/nrechati/CEA/Thesis/Tools/BenchMesh/python')

###
### SHAPER component
###

from salome.shaper import model

model.begin()
partSet = model.moduleDocument()

### Create Part
Part_1 = model.addPart(partSet)
Part_1_doc = Part_1.document()

### Create Box
Box_1 = model.addBox(Part_1_doc, 0, 0, 0, 6.2831, 6.2831, 6.2831)

### Create Group
Group_1 = model.addGroup(Part_1_doc, "Faces", [model.selection("FACE", "Box_1_1/Top")])
Group_1.setName("top")
Group_1.result().setName("top")

### Create Group
Group_2 = model.addGroup(Part_1_doc, "Faces", [model.selection("FACE", "Box_1_1/Left")])
Group_2.setName("left")
Group_2.result().setName("left")

### Create Group
Group_3 = model.addGroup(Part_1_doc, "Faces", [model.selection("FACE", "Box_1_1/Front")])
Group_3.setName("front")
Group_3.result().setName("front")

### Create Group
Group_4 = model.addGroup(Part_1_doc, "Faces", [model.selection("FACE", "Box_1_1/Right")])
Group_4.setName("right")
Group_4.result().setName("right")

### Create Group
Group_5 = model.addGroup(Part_1_doc, "Faces", [model.selection("FACE", "Box_1_1/Back")])
Group_5.setName("back")
Group_5.result().setName("back")

### Create Group
Group_6 = model.addGroup(Part_1_doc, "Faces", [model.selection("FACE", "Box_1_1/Bottom")])
Group_6.setName("bottom")
Group_6.result().setName("bottom")

model.end()

###
### SHAPERSTUDY component
###

model.publishToShaperStudy()
import SHAPERSTUDY
Box_1_1, top, left, front, right, back, bottom, = SHAPERSTUDY.shape(model.featureStringId(Box_1))

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
