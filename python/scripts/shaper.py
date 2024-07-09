import os
import csv
import sys
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from python.BenchMesh import BenchMesh

def plotResults(ax, xRefinements, y_P0, y_P1, y_cellCenters, errPrefix, fit=False, log=True):
    # Estimate for H size
    hSize = np.array(xRefinements)

    if fit:
        # Fitted
        popt, pcov = curve_fit(BenchMesh.fitFunction, hSize, np.array(y_P0))
        # popt2, pcov2 = curve_fit(BenchMesh.fitFunction, hSize, np.array(y_P1))
        ax.plot(hSize, BenchMesh.fitFunction(hSize, *popt), color='#f28513', label=r'{} interpolated to cells | $h^{{{}}}$'.format(errPrefix , f'{popt[1]:.2f}'))
        # ax.plot(hSize, BenchMesh.fitFunction(hSize, *popt2), color='#005668', label=r'{} interpolated to points | $h^{{{}}}$'.format(errPrefix , f'{popt2[1]:.2f}'))

        ## Point plot
        ax.plot(hSize, y_P0, 'p', color='#df912c')
        # ax.plot(hSize, y_P1, 'p', color='#5b7a8e')

        ### For now Cell Centers does not yield good enough result, commenting curves
        # popt3, pcov2 = curve_fit(BenchMesh.fitFunction, hSize, np.array(y_cellCenters))
        # ax.plot(hSize, BenchMesh.fitFunction(hSize, *popt3), color='#088743', label=r'{} with cell centers | $h^{{{}}}$'.format(errPrefix , f'{popt3[1]:.2f}'))
        # ax.plot(hSize, y_cellCenters, 'p', color='#81987a')

    else:
        ## Point plot
        ax.plot(hSize, y_P0, color='#f28513', label=f'{errPrefix} interpolated to cells')
        # ax.plot(hSize, y_P1, color='#005668', label=f'{errPrefix} interpolated to points')
        ax.plot(hSize, y_P0, 'p', color='#df912c')
        # ax.plot(hSize, y_P1, 'p', color='#5b7a8e')
        # ax.plot(hSize, y_cellCenters, color='#088743', label=f'{errPrefix} with cell centers')
        # ax.plot(hSize, y_cellCenters, 'p', color='#81987a')

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
    ax.set_yticks(y_P0)
    ax.set_xticklabels([f'{x:.2e}' for x in hSize], rotation=45)
    ax.set_yticklabels([f'{y:.2e}' for y in (y_P0)])
    ax.tick_params(axis='both', which='major', labelsize=7)

def dumpData(path, x, y1, y2, y3):
    # Dump data to CSV
    rows = []
    fieldnames = ['Hsize', 'L2_P0', 'L2_P1', 'L2_CellCenters']
    for i in range(len(x)):
        rows.append([x[i], y1[i], y2[i], y3[i]])

    with open(f'{path}Tools/BenchMesh/out/dump_data.csv', 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        writer.writerows(rows)

def main():
    np.finfo(np.dtype("float32"))
    np.finfo(np.dtype("float64"))
    cwd = "/home/nrechati/CEA/Thesis/"
    bench = BenchMesh(cwd + "Tools/BenchMesh",
                      cwd + "App",
                      cwd + "Tools/BenchMesh/parameters.json")

    results = []
    xRefinements = []
    if len(sys.argv) != 2:
        refinementNb = -1
    else:
        refinementNb = int(sys.argv[1])
    # Loop on mesh refinement
    pretty = "╔╗ ┌─┐┌┐┌┌─┐┬ ┬╔╦╗┌─┐┌─┐┬ ┬\n╠╩╗├┤ ││││  ├─┤║║║├┤ └─┐├─┤\n╚═╝└─┘┘└┘└─┘┴ ┴╩ ╩└─┘└─┘┴ ┴"
    print(f'{pretty}')

    # Set dimension then launch
    if refinementNb != -1:
        print(f'\n[BENCH]\tLaunching benchmark tool for {refinementNb} iterations')
        # try :
        for i in range(refinementNb):
            print(f'[BENCH]\tLaunching iteration {i+1}')
            bench.createShape()
            bench.createMesh(index=i)
            bench.runTRUSTPlugin(index=i)
            bench.cleanupTRUST(index=i)
            if bench.dimension == 2 and bench.geometry == 'tri' :
                results.append(bench.postProcessResults(index=i))
                xRefinements.append(bench.hSize)
                os.system("echo -n '\033[29A'")
                os.system("echo -n '\033[J'")
            print(f'[BENCH]\t Iteration {i+1} completed with success')
        # except Exception as e:
            # print(f'[ERROR]\t Iteration {i+1} had an error while running. See logs')
            # exit(1)

    else :
        meshes = [f'{bench.dir}/out/Test/mesh_h1.med',
                f'{bench.dir}/out/Test/mesh_h2.med',
                f'{bench.dir}/out/Test/mesh_h3.med',
                f'{bench.dir}/out/Test/mesh_h4.med']
        print(f'\n[BENCH]\tLaunching benchmark tool for {len(meshes)} iterations')
        try :
            for i, mesh in enumerate(meshes):
                print(f'[BENCH]\tLaunching {i}th mesh {mesh}')
                bench.loadMesh(mesh)
                bench.runTRUSTPlugin(index=i)
                bench.cleanupTRUST(index=i)
                results.append(bench.postProcessResults(index=i))
                xRefinements.append(bench.hSize)
                os.system("echo -n '\033[26A'")
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
    L1_P0 = [el["L1_P0"] for el in results]
    L1_P1 = [el["L1_P1"] for el in results]
    L1_CellCenters = [el["L1_CellCenters"] for el in results]
    L2_P0 = [el["L2_P0"] for el in results]
    L2_P1 = [el["L2_P1"] for el in results]
    L2_CellCenters = [el["L2_CellCenters"] for el in results]
    Linf_P0 = [el["Linf_P0"] for el in results]
    Linf_P1 = [el["Linf_P1"] for el in results]
    Linf_CellCenters = [el["Linf_CellCenters"] for el in results]

    # Dump
    dumpData(cwd, xRefinements, L2_P0, L2_P1, L2_CellCenters)

    # Print
    print(f'\n[RESULT] Results for {refinementNb} iterations')
    print(f'[RESULT] All work is done, check out dump_data.csv for raw data behind the curves')

    # Plot
    matplotlib.rcParams['figure.figsize'] = 20,8
    fig, axs = plt.subplots(1, 3)
    test = [0.0093012, 0.00263972, 0.000674624, 0.000296721, 0.000168755]

    plotResults(axs[0], xRefinements, L1_P0, L1_P1, L1_CellCenters, "$L_1$", fit=True)
    plotResults(axs[1], xRefinements, test, L2_P1, L2_CellCenters, "$L_2$", fit=True)
    plotResults(axs[2], xRefinements, Linf_P0, Linf_P1, Linf_CellCenters, "$L_\infty$", fit=True)
    plt.savefig(f'{cwd}Tools/BenchMesh/out/figure.png')
    plt.show()

if __name__ == "__main__":
    main()
