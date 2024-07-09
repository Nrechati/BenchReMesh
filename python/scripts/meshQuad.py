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

### Create Sketch
Sketch_1 = model.addSketch(Part_1_doc, model.defaultPlane("YOZ"))

### Create SketchLine
SketchLine_1 = Sketch_1.addLine(6.283185307179586, 4.499862507044922e-21, 0, 0)

### Create SketchProjection
SketchProjection_1 = Sketch_1.addProjection(model.selection("VERTEX", "PartSet/Origin"), False)
SketchPoint_1 = SketchProjection_1.createdFeature()
Sketch_1.setCoincident(SketchLine_1.endPoint(), SketchPoint_1.result())

### Create SketchLine
SketchLine_2 = Sketch_1.addLine(0, 0, 2.005460953678667e-23, 6.283185307179586)

### Create SketchLine
SketchLine_3 = Sketch_1.addLine(2.005460953678667e-23, 6.283185307179586, 6.283185307179586, 6.283185307179586)

### Create SketchLine
SketchLine_4 = Sketch_1.addLine(6.283185307179586, 6.283185307179586, 6.283185307179586, 4.499862507044922e-21)
Sketch_1.setCoincident(SketchLine_4.endPoint(), SketchLine_1.startPoint())
Sketch_1.setCoincident(SketchLine_1.endPoint(), SketchLine_2.startPoint())
Sketch_1.setCoincident(SketchLine_2.endPoint(), SketchLine_3.startPoint())
Sketch_1.setCoincident(SketchLine_3.endPoint(), SketchLine_4.startPoint())
Sketch_1.setPerpendicular(SketchLine_1.result(), SketchLine_2.result())
Sketch_1.setPerpendicular(SketchLine_2.result(), SketchLine_3.result())
Sketch_1.setPerpendicular(SketchLine_3.result(), SketchLine_4.result())
Sketch_1.setLength(SketchLine_2.result(), 6.283185307179586)
Sketch_1.setEqual(SketchLine_2.result(), SketchLine_3.result())

### Create SketchProjection
SketchProjection_2 = Sketch_1.addProjection(model.selection("EDGE", "PartSet/OZ"), False)
SketchLine_5 = SketchProjection_2.createdFeature()
Sketch_1.setCoincident(SketchLine_2.endPoint(), SketchLine_5.result())
model.do()

### Create Face
Face_1 = model.addFace(Part_1_doc, [model.selection("COMPOUND", "Sketch_1")])

### Create Group
Group_1 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_3")])
Group_1.setName("up")
Group_1.result().setName("up")

### Create Group
Group_2 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_4")])
Group_2.setName("right")
Group_2.result().setName("right")

### Create Group
Group_3 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_2")])
Group_3.setName("left")
Group_3.result().setName("left")

### Create Group
Group_4 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_1")])
Group_4.setName("down")
Group_4.result().setName("down")

model.end()

###
### SHAPERSTUDY component
###

model.publishToShaperStudy()
import SHAPERSTUDY
Face_1_1, up, right, left, down, = SHAPERSTUDY.shape(model.featureStringId(Face_1))
###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
Mesh_1 = smesh.Mesh(Face_1_1,'Mesh_1')
Regular_1D = Mesh_1.Segment()
Number_of_Segments_1 = Regular_1D.NumberOfSegments(15)
Quadrangle_2D = Mesh_1.Quadrangle(algo=smeshBuilder.QUADRANGLE)
up_1 = Mesh_1.GroupOnGeom(up,'up',SMESH.EDGE)
right_1 = Mesh_1.GroupOnGeom(right,'right',SMESH.EDGE)
left_1 = Mesh_1.GroupOnGeom(left,'left',SMESH.EDGE)
down_1 = Mesh_1.GroupOnGeom(down,'down',SMESH.EDGE)
isDone = Mesh_1.Compute()
[ up_1, right_1, left_1, down_1 ] = Mesh_1.GetGroups()


## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(up_1, 'up')
smesh.SetName(right_1, 'right')
smesh.SetName(left_1, 'left')
smesh.SetName(down_1, 'down')
smesh.SetName(Number_of_Segments_1, 'Number of Segments_1')

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
