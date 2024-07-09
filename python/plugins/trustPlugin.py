import sys
import json

from trustutils import run

def loadJSON(paramJSON):
	try:
		with open(paramJSON, 'r') as file:
			data = json.load(file)
		return data
	except FileNotFoundError:
		print(f"Error: The file '{paramJSON}' was not found.")
		sys.exit(1)
	except json.JSONDecodeError:
		print(f"Error: The file '{paramJSON}' is not a valid JSON file.")
		sys.exit(1)

def runTRUST(path, params):
	run.BUILD_DIRECTORY = f'{path}/out/tmp'
	dimension = params['DIMENSION']
	boundary = params['BOUNDARY']
	dataFile = f'../template/template{dimension}D{"_neumann" if boundary == 2 else ""}.data'
	run.addCaseFromTemplate(dataFile, "", params, targetData=f'{params["MEDFileName"][:-4]}.data')
	run.runCases()

def main(path, paramJSON):
	paramDict = loadJSON(paramJSON)
	runTRUST(path, paramDict)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python trustPlugin.py <path_to_json_params>")
		sys.exit(1)

	cwd = sys.argv[1]
	paramJSON = sys.argv[2]
	main(cwd, paramJSON)
