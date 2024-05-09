import os
import pandas as pd

def Read_output(project_name,result_type,path):
    home = os.getcwd()
    os.chdir(path)
    fn = project_name + '.' + result_type + '.001'
    y = None
    # open the file for reading
    try:
        f = open(fn, 'r')
        data = f.read()
        # extract the data based on the type of the result
        if result_type == 'Xemit':
            # extract the Xemit data
            # the last line is empty, so we take the second last line
            # The sixth element in the line is the normalized emittance.
            # split the data into lines by the newline character
            # then split the line with consecutive spaces
            y = data.split('\n')[-2].split()[5]
            #print(y)
        elif result_type == 'Zemit':
            # We need the 4th element in this case, which is the RMS length of the bunch. 
            y = data.split('\n')[-2].split()[3]
            #print(y)        
        elif result_type == 'LandF':
            # We need the 2nd element in this case, which is the total number of the particle. 
            # Initial number of particles
            y0 = data.split('\n')[0].split()[1]
            #print(y0)
            # Final number of particles
            y = data.split('\n')[-2].split()[1]
            #print(y)
            # ratio of particle losss
            y = (float(y0)-float(y))/float(y0)-0.01
            #print(y)
        f.close()

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    os.chdir(home)
    return y

def Read_line(project_name,result_type,path):
    home = os.getcwd()
    os.chdir(path)
    fn = project_name + '.' + result_type + '.001'
    y = None
    # open the file for reading
    try:
        f = open(fn, 'r')
        data = f.read()
        # extract the data based on the type of the result
        if result_type == 'Xemit':
            # extract the Xemit data
            # the last line is empty, so we take the second last line
            # The sixth element in the line is the normalized emittance.
            # split the data into lines by the newline character
            # then split the line with consecutive spaces
            columns=['z[m]','t[ns]','xav[mm]','xrms[mm]','xp[mrad]','epsXnorm[pimmmrad]','xxpavr[mrad]']
            data = pd.read_csv(fn,sep = '\s+',names=columns,index_col=False)
            z = data['z[m]']
            emitX = data['epsXnorm[pimmmrad]']
            os.chdir(home)
            return z,emitX
            
            #print(y)
        elif result_type == 'Zemit':
            columns=['z[m]','t[ns]','Ek[MeV]','zrms[mm]','dE[keV]','epsZnorm[pikeVmm]','zEpavr[keV]']
            data = pd.read_csv(fn,sep = '\s+',names=columns,index_col=False)
            z = data['z[m]']
            emitZ = data['epsZnorm[pikeVmm]']
            os.chdir(home)
            return z,emitZ  
        elif result_type == 'LandF':
            columns=['z[m]','Npar','Q[nC]','NLoss','DepositedEnergy[J]','TotEnergyExchanged[J]']
            data = pd.read_csv(fn,sep = '\s+',names=columns,index_col=False)
            z = data['z[m]']
            Npar = data['Npar']
            os.chdir(home)
            return z,Npar
        f.close()

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
