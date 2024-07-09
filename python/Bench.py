import os
import sys
import math
import json
import shutil
import subprocess
import pandas as pd

import salome
import SHAPERSTUDY
import SMESH
import pvsimple

from pvsimple import *
from pathlib import Path
from salome.shaper import model
from salome.smesh import smeshBuilder

class Bench:
	"""The PEGASERunner class provide tool to run PEGASE cosimulation through SIGE"""

	_instance = None

	#MISC
	dir = None
	appDir = None
	targetMed = None
	paramsJSON = None
	params = {}
	dimension = 2
	geometry = 'tri'
	boundary = 1

	#SHAPER
	shape = None
	up = None
	down = None
	left = None
	right = None
	front = None
	back = None

	# SALOME
	hSize = None
	nbElem = None
	surfaceLen = None
	area = None
	meshSizeTarget = None
	meshName_prefix = None
	medFile = None

	# TRUST
	f_m = None
	phi_m = None
	upBC = None
	downBC = None
	leftBC = None
	rightBC = None
	frontBC = None
	backBC = None
	results = None

	def __new__(cls, path, appDir, params):
		"""Create an instance of the Bench class - Singleton pattern"""

		if cls._instance is None:
			cls._instance = super(Bench, cls).__new__(cls)
			cls.dir = path
			cls.appDir = appDir
			cls.paramsJSON = params
			cls.loadParams()
			sys.path.insert(0, cls.dir)
		return cls._instance

	@classmethod
	def fitFunction(cls, x, a, b):
		return a*(x**b)

	@classmethod
	def loadParams(cls):
		# Open and read JSON param file
		try:
			with open(cls.paramsJSON, 'r') as file:
				cls.params = json.load(file)
		except FileNotFoundError:
			print(f"Error: The file '{cls.paramsJSON}' was not found.")
			sys.exit(1)
		except json.JSONDecodeError:
			print(f"Error: The file '{cls.paramsJSON}' is not a valid JSON file.")
			sys.exit(1)

		# Fill class with params
		cls.surfaceLen = cls.params["surfaceLen"]
		cls.meshSizeTarget = cls.params["meshSizeTarget"]
		cls.meshName_prefix = cls.params["meshName_prefix"]
		cls.dimension = cls.params["dimension"]
		cls.boundary = cls.params["boundary"]
		cls.geometry = cls.params["geometry"]
		cls.postProcessFormat = cls.params["postProcessFormat"]
		cls.f_m = cls.params["f_m"]
		cls.phi_m = cls.params["phi_m"]
		cls.upBC = cls.params["upBC"]
		cls.downBC = cls.params["downBC"]
		cls.leftBC = cls.params["leftBC"]
		cls.rightBC = cls.params["rightBC"]

	@classmethod
	def createShape(cls):
		cls.createShape2D()

	@classmethod
	def createShape2D(cls):
		print(f'\t[SHAPE]\t- Creating 2D CAO shape')
		model.begin()
		partSet = model.moduleDocument()

		# Part and Sketch
		Part_1 = model.addPart(partSet)
		Part_1_doc = Part_1.document()
		Sketch_1 = model.addSketch(Part_1_doc, model.defaultPlane("YOZ"))
		SketchLine_1 = Sketch_1.addLine(6.283185307179586, 4.499862507044922e-21, 0, 0)
		SketchProjection_1 = Sketch_1.addProjection(model.selection("VERTEX", "PartSet/Origin"), False)
		SketchPoint_1 = SketchProjection_1.createdFeature()
		Sketch_1.setCoincident(SketchLine_1.endPoint(), SketchPoint_1.result())

		### Create SketchLine
		SketchLine_2 = Sketch_1.addLine(0, 0, 2.005460953678667e-23, 6.283185307179586)
		SketchLine_3 = Sketch_1.addLine(2.005460953678667e-23, 6.283185307179586, 6.283185307179586, 6.283185307179586)
		SketchLine_4 = Sketch_1.addLine(6.283185307179586, 6.283185307179586, 6.283185307179586, 4.499862507044922e-21)
		Sketch_1.setCoincident(SketchLine_4.endPoint(), SketchLine_1.startPoint())
		Sketch_1.setCoincident(SketchLine_1.endPoint(), SketchLine_2.startPoint())
		Sketch_1.setCoincident(SketchLine_2.endPoint(), SketchLine_3.startPoint())
		Sketch_1.setCoincident(SketchLine_3.endPoint(), SketchLine_4.startPoint())
		Sketch_1.setPerpendicular(SketchLine_1.result(), SketchLine_2.result())
		Sketch_1.setPerpendicular(SketchLine_2.result(), SketchLine_3.result())
		Sketch_1.setPerpendicular(SketchLine_3.result(), SketchLine_4.result())
		Sketch_1.setLength(SketchLine_2.result(), str(cls.surfaceLen))
		Sketch_1.setEqual(SketchLine_2.result(), SketchLine_3.result())
		### Create SketchProjection
		SketchProjection_2 = Sketch_1.addProjection(model.selection("EDGE", "PartSet/OZ"), False)
		SketchLine_5 = SketchProjection_2.createdFeature()
		Sketch_1.setCoincident(SketchLine_2.endPoint(), SketchLine_5.result())
		model.do()

		### Create Face
		Face_1 = model.addFace(Part_1_doc, [model.selection("COMPOUND", "Sketch_1")])
		### Create Groups
		Group_1 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_3")])
		Group_1.setName("up")
		Group_1.result().setName("up")
		Group_2 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_4")])
		Group_2.setName("right")
		Group_2.result().setName("right")
		Group_3 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_2")])
		Group_3.setName("left")
		Group_3.result().setName("left")
		Group_4 = model.addGroup(Part_1_doc, "Edges", [model.selection("EDGE", "Face_1_1/Modified_Edge&Sketch_1/SketchLine_1")])
		Group_4.setName("down")
		Group_4.result().setName("down")

		model.end()
		model.publishToShaperStudy()
		cls.shape, cls.up, cls.right, cls.left, cls.down, = SHAPERSTUDY.shape(model.featureStringId(Face_1))

	@classmethod
	def createMesh(cls, index):
		if cls.dimension == 2:
			if cls.geometry == 'tri':
				cls.createMesh2D_tri(index)
			elif cls.geometry == 'quad':
				cls.createMesh2D_quad(index)
		elif cls.dimension == 3:
			cls.createMesh3D(index)

	@classmethod
	def createMesh2D_tri(cls, index=1):
		print(f'\t[MESH]\t- Creating mesh ...')
		# Set Size
		if index > 0:
			targetSize = cls.meshSizeTarget / (2 * index)
		else:
			targetSize = cls.meshSizeTarget
		print(f'\t[MESH]\t- Current iteration : {index + 1} || Current size parameter : {targetSize}')

		# Do SMESH
		smesh = smeshBuilder.New()
		Mesh_1 = smesh.Mesh(cls.shape, f'{cls.meshName_prefix}{index + 1}')
		GMSH_2D = Mesh_1.Triangle(algo=smeshBuilder.GMSH_2D)
		Gmsh_Parameters = GMSH_2D.Parameters()
		Gmsh_Parameters.Set2DAlgo( 2 )
		Gmsh_Parameters.SetMinSize( targetSize )
		Gmsh_Parameters.SetMaxSize( targetSize )
		Gmsh_Parameters.SetIs2d( 1 )
		up_1 = Mesh_1.GroupOnGeom(cls.up,'up',SMESH.EDGE)
		right_1 = Mesh_1.GroupOnGeom(cls.right,'right',SMESH.EDGE)
		left_1 = Mesh_1.GroupOnGeom(cls.left,'left',SMESH.EDGE)
		down_1 = Mesh_1.GroupOnGeom(cls.down,'down',SMESH.EDGE)
		isDone = Mesh_1.Compute()
		[ up_1, right_1, left_1, down_1 ] = Mesh_1.GetGroups()
		smesh.SetName(Mesh_1, f'{cls.meshName_prefix}{index + 1}')
		cls.targetMed = f'{cls.dir}/out/meshing/{cls.meshName_prefix}{index + 1}.med'
		try:
			Mesh_1.ExportMED( cls.targetMed, 0, 41, 1, Mesh_1, 1, [], '',-1, 1 )
			pass
		except:
			print('ExportPartToMED() failed. Invalid file name?')

		## Set names of Mesh objects
		smesh.SetName(GMSH_2D.GetAlgorithm(), 'GMSH_2D')
		smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
		smesh.SetName(up_1, 'up')
		smesh.SetName(right_1, 'right')
		smesh.SetName(left_1, 'left')
		smesh.SetName(down_1, 'down')
		smesh.SetName(Gmsh_Parameters, 'Gmsh Parameters')

		if salome.sg.hasDesktop():
			salome.sg.updateObjBrowser()

		meshElementCount = Mesh_1.NbElements()
		print(f'\t[MESH]\t- Current mesh elements count is : {meshElementCount}')
		cls.medFile = f'{cls.meshName_prefix}{index + 1}.med'
		cls.nbElem = meshElementCount
		return meshElementCount

	@classmethod
	def createTRUSTParamsJSON(cls, index, dimension=2):
		# Create dict and fill
		params = {
					"DIMENSION" : str(cls.dimension),
					"BOUNDARY" : cls.boundary,
					"FORMAT" : cls.postProcessFormat,
					"MEDFileName" : cls.medFile,
					"F_M" : cls.f_m ,
					"RIGHT_BC" : cls.rightBC ,
					"LEFT_BC" : cls.leftBC ,
					"UP_BC" : cls.upBC ,
					"DOWN_BC" : cls.downBC
				}

		# Create JSON with params for TRUST
		targetJSON = f'{cls.dir}/out/json/{cls.meshName_prefix}{index + 1}.json'
		try:
			with open(targetJSON, 'w') as file:
				json.dump(params, file, indent=4)
				return targetJSON
		except IOError:
			print(f"Error: Could not write to file '{targetJSON}'.")
			sys.exit(1)

	@classmethod
	def cleanupTRUST(cls, index=1):
		# Set and create directories
		filePrefix = f'{cls.meshName_prefix}{index + 1}'
		tmpDir = f'{cls.dir}/out/tmp'
		outDir = f'{cls.dir}/out/data/{filePrefix}'
		os.makedirs(outDir, exist_ok=True)

		# Move .data and .lata and clean the rest
		for file in os.listdir(tmpDir):
			shutil.move(os.path.join(tmpDir, file), os.path.join(outDir, file))
		# Cleanup tmp
		[os.remove(os.path.join(tmpDir, file)) for file in os.listdir(tmpDir)]

	@classmethod
	def runTRUSTPlugin(cls, index=1):
		print(f'\t[RUN]\t- Preparing to launch TRUST simulation on mesh')
		paramsJSON = cls.createTRUSTParamsJSON(index)
		try:
			print(f'\t[RUN]\t- Launching TRUST simulation ...')
			command = f'source {cls.appDir}/TRUST/env_TRUST.sh && python python/plugins/trustPlugin.py {cls.dir} {paramsJSON}'
			subprocess.run(command, shell=True, check=True, executable='/bin/bash', stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as e:
			raise
		print(f'\t[RUN]\t- Simulation of iteration {index + 1} complete')

	@classmethod
	def getCellRangeData(cls, obj, field):
		array = obj.GetCellData().GetArray(field)
		rangeValues = array.GetRange()
		return rangeValues

	@classmethod
	def getPointRangeData(cls, obj, field):
		array = obj.GetPointData().GetArray(field)
		rangeValues = array.GetRange()
		return rangeValues

	@classmethod
	def getBlockData(cls, obj):
		dataBlock = obj.GetBlock(0).GetBlock(0)
		return dataBlock

	@classmethod
	def postProcessResults(cls,index=1):
		if cls.postProcessFormat == "lata":
			cls.postProcessLATA(index)
		elif cls.postProcessFormat == "med":
			cls.postProcessMED(index)

	@classmethod
	def postProcessMED(cls,index=1):
		pass

	@classmethod
	def postProcessLATA(cls,index=1):
		pvsimple.ShowParaviewView()
		pvsimple._DisableFirstRenderCameraReset()

		# Load file
		print(f'\t[POST]\t- Loading file to post processing tool')

		resultFile = None
		lataFile = f'{cls.meshName_prefix}{index + 1}/{cls.meshName_prefix}{index + 1}.lata'
		resultFile = VisItLataReader(registrationName=lataFile, FileName=f'{cls.dir}/out/data/{lataFile}')
		animationScene1 = GetAnimationScene()
		timeKeeper1 = GetTimeKeeper()
		animationScene1.UpdateAnimationUsingDataTimeSteps()

		# Phi_sol
		RenameProxy(resultFile, 'sources', 'Phi_sol')
		RenameSource('Phi_sol', resultFile)
		if cls.postProcessFormat == "lata":
			resultFile.CellArrays = ['TEMPERATURE_ELEM_dom']
		renderView1 = GetActiveViewOrCreate('RenderView')
		renderView1.Update()
		animationScene1.GoToLast()

		###############
		#  Cell Size  #
		###############
		SetActiveSource(resultFile)

		# Compute Phi_m (manufactured)
		print(f'\t[POST]\t- Compute manufactured solution values on domain')
		calculator1 = Calculator(registrationName='Calculator1', Input=resultFile)
		SetActiveSource(calculator1)
		RenameProxy(calculator1, 'sources', 'Phi_m')
		RenameSource('Phi_m', calculator1)
		calculator1.ResultArrayName = 'Phi_m'
		calculator1.Function = cls.phi_m.replace("x", "coordsX").replace("y", "coordsY")
		calculator1.ReplaceInvalidResults = 0

		# Interpolate Phi_m to cells
		pointDatatoCellData1 = PointDatatoCellData(registrationName='PointDatatoCellData1', Input=calculator1)
		RenameProxy(pointDatatoCellData1, 'sources', 'Phi_m_cells')
		RenameSource('Phi_m_cells', pointDatatoCellData1)
		pointDatatoCellData1Display = Show(pointDatatoCellData1, renderView1, 'UnstructuredGridRepresentation')
		SetActiveSource(calculator1)

		# Compute sum of edge length per cell
		SetActiveSource(calculator1)
		mergeBlocks1 = MergeBlocks(registrationName='MergeBlocks1', Input=calculator1)
		materialLibrary1 = GetMaterialLibrary()
		programmableFilter1 = ProgrammableFilter(registrationName='ProgrammableFilter1', Input=mergeBlocks1)
		programmableFilter1.OutputDataSetType = 'vtkUnstructuredGrid'
		programmableFilter1.Script = """import vtkmodules.all as vtk
import numpy as np
import math

pdi = self.GetInput()
pdo = self.GetOutput()
newData = vtk.vtkDoubleArray()
newData.SetName("HSize")  # Changed the array name
numCells = pdi.GetNumberOfCells()
for i in range(numCells):
	cell = pdi.GetCell(i)
	nb_edges = cell.GetNumberOfPoints()
	pts = [ np.array(pdi.GetPoint(cell.GetPointId(i))) for i in range(nb_edges) ]
	cellEdgeLength = 0
	for j in range(len(pts)):
		if j == (len(pts) - 1):
			cellEdgeLength += math.sqrt(((pts[j][0] - pts[0][0]) ** 2) + ((pts[j][1] - pts[0][1]) ** 2))
		else:
			cellEdgeLength += math.sqrt(((pts[j][0] - pts[j+1][0]) ** 2) + ((pts[j][1] - pts[j+1][1]) ** 2))
	newData.InsertNextValue(cellEdgeLength / nb_edges)

pdo.GetCellData().AddArray(newData)"""
		programmableFilter1Display = Show(programmableFilter1, renderView1, 'UnstructuredGridRepresentation')
		programmableFilter1Display.Representation = 'Surface'
		programmableFilter1Display.RescaleTransferFunctionToDataRange(False, True)

		rawEdgeData = servermanager.Fetch(programmableFilter1)
		hSizeMAX = rawEdgeData.GetCellData().GetArray("HSize").GetRange()[1]  # Taking min value
		hSizeMIN = rawEdgeData.GetCellData().GetArray("HSize").GetRange()[0]  # Taking min value
		cls.hSize = hSizeMAX
		print(f'Current hSize = {cls.hSize} || iter = {index}')

		# Value spreadsheet
		spreadSheetView1 = CreateView('SpreadSheetView')
		spreadSheetView1.ColumnToSort = ''
		spreadSheetView1.BlockSize = 1024
		spreadSheetView1.Update()

		# rawAreaData = servermanager.Fetch(integrateVariables1)
		# cls.area = cls.getCellRangeData(rawAreaData, "Area")[0]
		cls.area = 39.4784176043574344

		##########
		# Get P0 #
		##########
		# (Phi_m - Phi_sol) on Cells (P0)
		SetActiveSource(pointDatatoCellData1)
		calculator1_3_1 = Calculator(registrationName='Calculator1_3_1', Input=pointDatatoCellData1)
		animationScene1.UpdateAnimationUsingDataTimeSteps()
		animationScene1.GoToLast()
		calculator1_3_1.ResultArrayName = 'E_cells'
		calculator1_3_1.Function = 'abs(Phi_m-TEMPERATURE_ELEM_dom)'
		SetActiveSource(calculator1_3_1)
		# Sum values
		integrateVariables1_2 = IntegrateVariables(registrationName='IntegrateVariables1_2', Input=calculator1_3_1)

		# (Phi_m - Phi_sol)^2 on Cells (P0)
		calculator1_3 = Calculator(registrationName='Calculator1', Input=pointDatatoCellData1)
		RenameProxy(calculator1_3, 'sources', 'E_sq_cells')
		RenameSource('E_sq_cells', calculator1_3)
		calculator1_3.ResultArrayName = 'E_sq_cells'
		calculator1_3.Function = '(Phi_m-TEMPERATURE_ELEM_dom)^2'
		calculator1_3Display = Show(calculator1_3, spreadSheetView1, 'SpreadSheetRepresentation')
		spreadSheetView1.Update()

		# Integrated (Phi_m - Phi_sol)^2 on Cells (P0)
		integrateVariables1_1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=calculator1_3)
		RenameProxy(integrateVariables1_1, 'sources', 'integrated_e_sq_cells')
		RenameSource('integrated_e_sq_cells', integrateVariables1_1)
		integrateVariables1_1Display = Show(integrateVariables1_1, spreadSheetView1, 'SpreadSheetRepresentation')
		spreadSheetView1.Update()
		integrateVariables1_1Display.Assembly = ''
		spreadSheetView1.FieldAssociation = 'Cell Data'

		# Compute L2 : sqrt((Phi_m - Phi_sol)^2) / (square_len^2) on Cells (P0)
		calculator1_4 = Calculator(registrationName='Calculator1', Input=integrateVariables1_1)
		RenameProxy(calculator1_4, 'sources', 'L2')
		RenameSource('L2', calculator1_4)
		calculator1_4.Function = f'sqrt(E_sq_cells)/({cls.area})'
		calculator1_4Display = Show(calculator1_4, spreadSheetView1, 'SpreadSheetRepresentation')
		Hide(integrateVariables1_1, spreadSheetView1)
		spreadSheetView1.Update()
		calculator1_4Display.Assembly = ''
		calculator1_4.ResultArrayName = 'L2'
		spreadSheetView1.Update()


		# Compute L1 results
		print(f'\t[POST]\t- Computing L1 Error')
		errSumData = servermanager.Fetch(integrateVariables1_2)
		L1 = errSumData.GetCellData().GetArray("E_cells").GetRange()[0]

		# Compute L2 results
		print(f'\t[POST]\t- Computing L2 Error')
		calcData_L2 = servermanager.Fetch(calculator1_4)
		L2 = cls.getCellRangeData(calcData_L2, "L2")[0]

		# Compute Linf results
		print(f'\t[POST]\t- Computing Linf Error')
		errRawData = servermanager.Fetch(calculator1_3_1)
		Linf = cls.getCellRangeData(cls.getBlockData(errRawData),"E_cells")[1]

		# Store and send results
		results = {
			"L1" : L1,
			"L2" : L2,
			"Linf" : Linf,
		}
		# Store to instance
		cls.results = results
