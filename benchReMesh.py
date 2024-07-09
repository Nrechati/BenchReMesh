import os
import csv
import sys
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from python.Bench import Bench

def plotResults(ax, xRefinements, values, errPrefix, fit=False, log=True):
	# Estimate for H size
	hSize = np.array(xRefinements)

	if fit:
		# Fitted
		popt, pcov = curve_fit(Bench.fitFunction, hSize, np.array(values))
		ax.plot(hSize, Bench.fitFunction(hSize, *popt), color='#f28513', label=r'{} interpolated to cells | $h^{{{}}}$'.format(errPrefix , f'{popt[1]:.2f}'))
		ax.plot(hSize, values, 'p', color='#df912c')
	else:
		## Point plot
		ax.plot(hSize, values, color='#f28513', label=f'{errPrefix} interpolated to cells')
		ax.plot(hSize, values, 'p', color='#df912c')

	# Plot config
	if log == True:
		ax.set_yscale('log')
		ax.set_xscale('log')
	ax.set_xlabel(r'$h_{{{}}}$'.format('size'), fontsize=15)
	ax.set_ylabel(f'{errPrefix} error', fontsize=15)
	ax.set_title(f'{errPrefix} error convergence', fontsize=20)
	ax.legend(fontsize="12", loc ="upper left")
	ax.grid(True, linestyle='--')

	# Setting ticks
	ax.set_xticks(hSize)
	ax.set_yticks(values)
	ax.set_xticklabels([f'{x:.2e}' for x in hSize], rotation=45)
	ax.set_yticklabels([f'{values:.2e}' for values in (values)])
	ax.tick_params(axis='both', which='major', labelsize=7)

def dumpData(path, x, y_L1, y_L2, y_Linf):
	# Dump data to CSV
	rows = []
	fieldnames = ['Hsize', 'L1', 'L2', 'Linf']
	for i in range(len(x)):
		rows.append([x[i], y_L1[i], y_L2[i], y_Linf[i]])

	with open(f'{path}/out/dump_data.csv', 'w+', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(fieldnames)
		writer.writerows(rows)

def main():
	np.finfo(np.dtype("float32"))
	np.finfo(np.dtype("float64"))
	rootDir = "/home/nrechati/CEA/Thesis"
	cwd = f'{rootDir}/Tools/BenchReMesh'
	bench = Bench(cwd,
				  rootDir + "/App",
				  cwd + "/parameters.json")

	results = []
	xRefinements = []
	if len(sys.argv) != 2 or int(sys.argv[1]) < 3:
		print(f'\n[USAGE]\tNeeded a refinement number. python benchReMesh.py [refinementNb]. Must be > 2')
		exit(1)
	else:
		refinementNb = int(sys.argv[1])
	# Loop on mesh refinement
	pretty = "╔╗ ┌─┐┌┐┌┌─┐┬ ┬╔╦╗┌─┐┌─┐┬ ┬\n╠╩╗├┤ ││││  ├─┤║║║├┤ └─┐├─┤\n╚═╝└─┘┘└┘└─┘┴ ┴╩ ╩└─┘└─┘┴ ┴"
	print(f'{pretty}')

	# Set dimension then launch
	try :
		for i in range(refinementNb):
			print(f'[BENCH]\tLaunching iteration {i+1}')
			bench.createShape()
			bench.createMesh(index=i)
			bench.runTRUSTPlugin(index=i)
			bench.cleanupTRUST(index=i)
			if bench.dimension == 2 and bench.geometry == 'tri' :
				bench.postProcessResults(index=i)
				results.append(bench.results)
				xRefinements.append(bench.hSize)
				os.system("echo -n '\033[29A'")
				os.system("echo -n '\033[J'")
			print(f'[BENCH]\t Iteration {i+1} completed with success')
	except Exception as e:
		print(f'[ERROR]\t Iteration {i+1} had an error while running. See logs')
		exit(1)

	# quad/3D exit
	if bench.geometry != 'tri' or bench.dimension == 3 :
		print(f'[RESULT] All work is done. Currently there is no post-processing for 3D or Quads')
		exit(0)

	# Results
	L1 = [el["L1"] for el in results]
	L2 = [el["L2"] for el in results]
	Linf = [el["Linf"] for el in results]

	# Dump
	dumpData(cwd, xRefinements, L1, L2, Linf)

	# Print
	print(f'\n[RESULT] Results for {refinementNb} iterations')
	print(f'[RESULT] All work is done, check out dump_data.csv for raw data behind the curves')

	# Plot
	matplotlib.rcParams['figure.figsize'] = 20,8
	fig, axs = plt.subplots(1, 3)
	plotResults(axs[0], xRefinements, L1, "$L_1$", fit=True)
	plotResults(axs[1], xRefinements, L2, "$L_2$", fit=True)
	plotResults(axs[2], xRefinements, Linf, "$L_\infty$", fit=True)
	plt.savefig(f'{bench.dir}/out/figure.png')
	plt.show()

if __name__ == "__main__":
	main()
