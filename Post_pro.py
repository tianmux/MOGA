import pandas as pd
import os
import Read_JSON
import My_Problem
import Run_Sims
import Read_Result
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt

debug1 = 1
debug2 = 1

def Read_ouput(path,fn):
    # Read the output file
    if fn == "F.txt":
        columns = ['Emitx','Sigx']
        # use columns as the column names
        df = pd.read_csv(os.path.join(path,fn),names=columns,sep=',',index_col=False)
        return df
    elif fn == "X.txt":
        # read the opt input file first
        fn_opt_input = os.path.join(path,'Opt_input.json')
        opt_input = Read_JSON.read_json_file(fn_opt_input)
        columns = []
        for i in list(opt_input['Generator']["INPUT"].keys()):
            idx = 0                
            #print(i)
            for j in list(opt_input['Generator']["INPUT"][i][0].keys()):
                columns.append("Generator."+"INPUT."+i+'('+j+')')
        for i in list(opt_input['Astra'].keys()):
            idx = 0
            #print(i)
            for j in list(opt_input['Astra'][i].keys()):
                #print(j)
                for k in list(opt_input['Astra'][i][j][0].keys()):
                    columns.append("Astra."+i+"."+j+'('+k+')')
        # now read the X.txt file
        # use columns as the column names
        # all the columns are value, no index
        df = pd.read_csv(os.path.join(path,fn),names=columns,sep=',',index_col=False)
        return df
    
def Gen_Inputs_from_Pareto(path):
    home = os.getcwd()
    os.chdir(path)
    print("Path in Gen_input_from_Pareto : ",os.getcwd())
    F = Read_ouput(path,"F.txt")
    X = Read_ouput(path,"X.txt")
    # Join the two dataframes
    df = pd.concat([X,F],axis=1)
    # sort the values according to the EmitX
    df = df.sort_values(by=['Emitx'])
    # re order the index
    df = df.reset_index(drop=True)
    print(df)
    print(F)
    print(X)
    # Write the dataframe 
    df.to_csv('Pareto.csv',index=False)

    fn_opt_input = os.path.join(path,'Opt_input.json')
    opt_input = Read_JSON.read_json_file(fn_opt_input)
    # generate the input files for the generator 
    # and astra according to the Pareto front
    input_text_gen = ''
    try:
        f = open('Generator_Pareto_input_template.txt', 'r')
        input_text_gen = f.read()
        print(input_text_gen)
        f.close()
    except FileNotFoundError:
        print("File Generator_Pareto_input_template.txt not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    for i_samp in df.index:
        sub_path = os.path.join(path,"Pareto/"+str(i_samp))
        #print(sub_path)
        os.makedirs(sub_path, exist_ok=True)
        # generate the input files for the generator
        n_gen = 0
        for i in list(opt_input['Generator']["INPUT"].keys()):
            idx = 0
            #print(i)
            for j in list(opt_input['Generator']["INPUT"][i][0].keys()):
                # if the key is "1", find the first occurance of the key in the template   
                #print(j)                 
                # find the j-th occurance of the key in the template
                idx = My_Problem.find_key(i,input_text_gen,int(j))
                #print(input_text_gen)
                idx_end = input_text_gen.find(',',idx+1)
                sub_string_to_replace = input_text_gen[idx:idx_end]
                #print(sub_string_to_replace)

                tmp = input_text_gen.split(sub_string_to_replace,1)
                #print(tmp)
                input_text_gen = tmp[0] + i + ' = ' + str(df.iloc[i_samp][df.columns[n_gen]]) +tmp[1]
                n_gen += 1
                #print("n_gen = ",n_gen)
        ###############################################################
        # Create the input files for the astra
        input_text_Astra = ''
        try:
            f = open('Astra_Pareto_input_template.txt', 'r')
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
                        idx = My_Problem.find_key(j,input_text_Astra,int(k))
                        #print(idx)
                        idx_end = input_text_Astra.find(',',idx+1)
                        sub_string_to_replace = input_text_Astra[idx:idx_end]
                        if i == "SOLENOID" and j == "S_pos":
                            tmp = input_text_Astra.split(sub_string_to_replace,1)
                            input_text_Astra = tmp[0] + j + '(' + str(k) + ')' + ' = ' + str(df.iloc[i_samp][df.columns[n_gen]]) +tmp[1]
                            idx = My_Problem.find_key("S_pos(2)",input_text_Astra,1)
                            #print(idx)
                            idx_end = input_text_Astra.find(',',idx+1)
                            sub_string_to_replace = input_text_Astra[idx:idx_end]
                            tmp = input_text_Astra.split(sub_string_to_replace,1)
                            input_text_Astra = tmp[0] + "S_pos(2)" + ' = ' + str(-df.iloc[i_samp][df.columns[n_gen]]) +tmp[1]
                        else:
                            tmp = input_text_Astra.split(sub_string_to_replace,1)
                            #print(tmp)
                            input_text_Astra = tmp[0] + j + '(' + str(k) + ')' + ' = ' + str(df.iloc[i_samp][df.columns[n_gen]]) +tmp[1]
                        
                        n_gen += 1
                        #print("n_gen = ",n_gen)
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        # try to open the "gen.in" file and write the input text into it    
        try:
            f = open(sub_path+'/'+'gen.in', 'w')
            f.write(input_text_gen)
            f.close()
            f = open(sub_path+'/'+'run.in','w')
            f.write(input_text_Astra)
            f.close()
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    os.chdir(home)
    return

def Run_from_Pareto(idx,path):
    home = os.getcwd()
    pathes = []
    for i in idx:
        pathes.append(path+'/Pareto/'+str(i)+'/')
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(Run_Sims.Run_Generator, pathes[i],'gen.in') for i in range(len(pathes))]
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(Run_Sims.Run_Astra, pathes[i],'run.in',0) for i in range(len(pathes))]
    
    #for i in idx:
    #    sub_path = path+'/Pareto/'+str(i)+'/'
    #    fn_gen = 'gen.in'
    #    fn_astra = 'run.in'
    #    Run_Sims.Run_Generator(sub_path,fn_gen)
    #    Run_Sims.Run_Astra(sub_path,fn_astra,iParallel=0)
    os.chdir(home)
    return
def Read_from_Pareto(idx,path):
    home = os.getcwd()
    print(home)
    pathes = []
    for i in idx:
        pathes.append(path+'/Pareto/'+str(i)+'/')
    for i in range(len(pathes)):
        z,Xemit = Read_Result.Read_line('run','Xemit',pathes[i])
        z,Zemit = Read_Result.Read_line('run','Zemit',pathes[i])
        os.chdir(path+'/Pareto')
        Xemit_plot_fn = str(i)+'Xemit.png'
        Zemit_plot_fn = str(i)+'Zemit.png'
        plt.figure(figsize=(7, 5))
        plt.plot(z, Xemit)
        plt.title("Xemit")
        plt.xlabel("$z[m]$")
        plt.ylabel("$\epsilon_x [\pi mm-mrad]$")
        # save the figure
        plt.savefig(Xemit_plot_fn, dpi=200)
        plt.close()

        plt.figure(figsize=(7, 5))
        plt.plot(z, Zemit)
        plt.title("Zemit")
        plt.xlabel("$z[m]$")
        plt.ylabel("$\sigma_z$ [mm]")
        # save the figure
        plt.savefig(Zemit_plot_fn, dpi=200)
        plt.close()
        os.chdir(home)

if debug1:
    print("Debug mode 1 is on.")
    path = os.getcwd()+'/5nC/Free_Constraints/5nC_PITZ'
    fn = "F.txt"
    data = Read_ouput(path,fn)
    fn = "X.txt"
    data = Read_ouput(path,fn)
    print(data)
    Gen_Inputs_from_Pareto(path)
    print("Finished Reading data from Pareto.")
    idx_pareto = [i for i in range(len(data[data.columns[0]]))]
    Run_from_Pareto(idx_pareto,path)

if debug2:
    print("Debug mode 2 is on.")
    path = os.getcwd()+'/5nC/Free_Constraints/5nC_PITZ'
    fn = "F.txt"
    data = Read_ouput(path,fn)
    fn = "X.txt"
    data = Read_ouput(path,fn)
    idx_pareto = [i for i in range(len(data[data.columns[0]]))]
    Read_from_Pareto(idx_pareto,path)
