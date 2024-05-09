import os
from re import sub
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
debug = 0

class MyProblem(Problem):
    def __init__(self,work_dir,opt_input,nx,ny,xl,xu):
        super().__init__(n_var=nx,
                         n_obj=ny,
                         n_ieq_constr=1,
                         xl=xl,
                         xu=xu)
        self.evaluation_counter = 0
        self.work_dir = work_dir
        self.opt_input = opt_input

    def _evaluate(self, x, out):
        #print("shape of x = ",x.shape)
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.run_external_program, x[i],i) for i in range(len(x))]
            results = [future.result() for future in futures]
        #print(results)
        # Assign the results to the output
        out["F"] = list(np.array(results).T)[:2]
        out["G"] = list(np.array(results).T)[2]
        out["id"] = list(np.array(results).T)[-1]
        #print("out = ",out)

    def run_external_program(self, solution,idx):
        # Unique folder for the solution
        
        folder_name = f"eval/{idx}"
        os.makedirs(folder_name, exist_ok=True)

        full_dir = os.path.join(self.work_dir, folder_name)
        #print(full_dir)
        Gen_Inputs_files(solution, full_dir,self.opt_input)
        
        Run_Sims.Run_Generator(full_dir,"gen.in")
        Run_Sims.Run_Astra(full_dir,"run.in",iParallel=0)
        y1 = Read_Result.Read_output('run','Xemit',full_dir)
        y2 = Read_Result.Read_output('run','Zemit',full_dir)
        g1 = Read_Result.Read_output('run','LandF',full_dir)
        #print("y1 = ",y1)
        #print("y2 = ",y2)
        return y1,y2,g1,idx



def Gen_Para_Space(fn):
    xl = []
    xu = []
    opt_input = Read_JSON.read_json_file(fn)
    # The struture has a fixed depth of 4
    key1s = list(opt_input.keys())
    #print(key1s)
    for key1 in key1s:
        #print(key1)
        # Then go into the second lv of keys
        key2s = list(opt_input[key1].keys())
        #print(key2s)
        for key2 in key2s:
            #print(key2s)
            #print(opt_input[key1][key2])
            # Then go into the third lv of keys for real parameters we'd like to optimize
            key3s = list(opt_input[key1][key2].keys())
            # Now we need to extract the lower and upper bounds of each parameter and put them all in one 1d array
            # At this level the values are list of dictionarie with only on element
            for key3 in key3s:
                key4s = list(opt_input[key1][key2][key3][0].keys())
                #print(key4s)
                for key4 in key4s:
                    xl.append(opt_input[key1][key2][key3][0][key4][0])
                    xu.append(opt_input[key1][key2][key3][0][key4][1])
    return xl, xu,opt_input
def Gen_x(path):
    home = os.getcwd()
    os.chdir(path)
    xl,xu,opt_input = Gen_Para_Space('Opt_input.json')
    return xl,xu,opt_input

def find_key(key,string,n):
    # find the n-th occurance of the key in the string
    idx = -1
    for i in range(n):
        idx = string.find(key,idx+1)
    return idx

def Gen_Inputs_files(x,path,opt_input):
    home = os.getcwd()
    #print(home)
    os.makedirs(path, exist_ok=True)
    ###############################################################
    # Create the input files for the generator
    # Get the input template for the a example file, first try to open the file then read the whole context
    input_text_gen = ''
    try:
        f = open('Generator_input_template.txt', 'r')
        input_text_gen = f.read()
        f.close()
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    #print(input_text_gen)
    
    # generate the input text from the template and xl and xu
    # find out how many parameters are for the generator
    # replace the parameters in the template with the values in xl and xu
    n_gen = 0
    for i in list(opt_input['Generator']["INPUT"].keys()):
         idx = 0                
         #print(i)
         for j in list(opt_input['Generator']["INPUT"][i][0].keys()):
                # if the key is "1", find the first occurance of the key in the template   
                #print(j)                 
                # find the j-th occurance of the key in the template
                idx = find_key(i,input_text_gen,int(j))
                #print(idx)
                idx_end = input_text_gen.find(',',idx+1)
                sub_string_to_replace = input_text_gen[idx:idx_end]
                #print(sub_string_to_replace)

                tmp = input_text_gen.split(sub_string_to_replace,1)
                #print(tmp)
                input_text_gen = tmp[0] + i + ' = ' + str(x[n_gen]) +tmp[1]
                #print(input_text_gen)
                n_gen += 1
                #print("n_gen = ",n_gen)
    ###############################################################
    # Create the input files for the astra
    input_text_Astra = ''
    try:
        f = open('Astra_input_template.txt', 'r')
        input_text_Astra = f.read()
        f.close()
        # Input for astra has four layers of keys
        for i in list(opt_input['Astra'].keys()):
            idx = 0                
            #print(i)
            for j in list(opt_input['Astra'][i].keys()):
                #print(j)
                for k in list(opt_input['Astra'][i][j][0].keys()):
                    #print(k)
                    # find the k-th occurance of the key in the template
                    idx = find_key(j,input_text_Astra,int(k))
                    #print(idx)
                    idx_end = input_text_Astra.find(',',idx+1)
                    sub_string_to_replace = input_text_Astra[idx:idx_end]
                    if i == "SOLENOID" and j == "S_pos":
                        tmp = input_text_Astra.split(sub_string_to_replace,1)
                        print(sub_string_to_replace)
                        #print(tmp)
                        input_text_Astra = tmp[0] + j + '(' + str(k) + ')' + ' = ' + str(x[n_gen]) +tmp[1]
                        idx = find_key("S_pos(2)",input_text_Astra,1)
                        #print(idx)
                        idx_end = input_text_Astra.find(',',idx+1)
                        sub_string_to_replace = input_text_Astra[idx:idx_end]
                        tmp = input_text_Astra.split(sub_string_to_replace,1)
                        input_text_Astra = tmp[0] + "S_pos(2)" + ' = ' + str(-x[n_gen]) +tmp[1]
                    else:
                        tmp = input_text_Astra.split(sub_string_to_replace,1)
                        #print(tmp)
                        input_text_Astra = tmp[0] + j + '(' + str(k) + ')' + ' = ' + str(x[n_gen]) +tmp[1]
                        
                    #print(input_text_Astra)
                    n_gen += 1
                    #print("n_gen = ",n_gen)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    
    # try to open the "gen.in" file and write the input text into it    
    os.chdir(path)
    try:
        f = open('gen.in', 'w')
        f.write(input_text_gen)
        f.close()
        f = open('run.in','w')
        f.write(input_text_Astra)
        f.close()
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    os.chdir(home)

if debug == True:
    print("Debug mode is on.")
    work_dir = os.getcwd()+'/Unit_Test'
    os.chdir(work_dir)

    fn_opt_input = os.path.join(work_dir,'Opt_input.json')
    xl,xu,opt_input = Gen_Para_Space(fn_opt_input)
    print(xl)
    print(xu)
    
    y = np.zeros(2)
    #Gen_Inputs_files(x, work_dir,opt_input)
    problem = MyProblem(work_dir,opt_input,len(xl),len(y),xl,xu)
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
    
    X = res.X
    F = res.F
    print(X)
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
                f.write(str(X[i][j]) + ' ')
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
