import os
import sys
import Read_JSON
import numpy as np
import Run_Sims
import Read_Result
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.problem import Problem
from concurrent.futures import ProcessPoolExecutor
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
from pymoo.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib
import My_Problem

home = os.getcwd()
work_dir = home+'/Unit_Test'
home = '/home/txin/Dropbox/My PC (DESKTOP-MIKK45R)/Documents/Work/Projects/3.LINAC_for_Plasma_Acceleration/Gun/sims/MOGA/5nC/'
work_dir = home+'5nC_1.55Cell_90Dgr'

# change the working directory to the work_dir
os.chdir(work_dir)

fn_opt_input = os.path.join(work_dir,'Opt_input.json')
xl,xu,opt_input = My_Problem.Gen_Para_Space(fn_opt_input)

y = np.zeros(2)
#Gen_Inputs_files(x, work_dir,opt_input)
problem = My_Problem.MyProblem(work_dir,opt_input,len(xl),len(y),xl,xu)
#MyProblem.evaluate(problem, x, y)
algorithm = NSGA2(
    pop_size=6,
    n_offsprings=6,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True
)
termination = get_termination("n_gen", 1)
res = minimize(problem,
            algorithm,
            termination,
            seed=1,
            save_history=True,
            verbose=True)
pop = res.pop
All_X = pop.get("X")
idxs = pop.get("id")
print(idxs)
X = res.X
F = res.F
plt.figure(figsize=(7, 5))
plt.scatter(F[:, 0], F[:, 1], s=30, facecolors='none', edgecolors='blue')
plt.title("Objective Space")
plt.xlabel("$\epsilon_x$")
plt.ylabel("$\sigma_z$")
# save the figure
plt.savefig("Objective_space.png", dpi=200)

# try to write the X corresponding to the Pareto front to a file
try:
    f = open('X.txt', 'w')
    for i in range(len(X)):
        for j in range(len(X[i])):
            f.write(str(X[i][j]) + ',')
        f.write('\n')
    f.close()
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"An error occurred: {e}")

# try to write the F corresponding to the Pareto front to a file
try:
    f = open('F.txt', 'w')
    for i in range(len(F)):
        f.write(str(F[i][0]) + ',' + str(F[i][1]) + '\n')
    f.close()
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"An error occurred: {e}")

# try to write the ID corresponding to the Pareto front to a file
try:
    f = open('ID.txt', 'w')
    for i in range(len(idxs)):
        f.write(str(idxs[i]) + '\n')
    f.close()
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"An error occurred: {e}")
os.chdir(home)