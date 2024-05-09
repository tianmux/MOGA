import subprocess
import os
# Run the Generator to create the initial distibution of particles
def Run_Generator(path,fn):
    home = os.getcwd()
    os.chdir(path)
    cmd = ['generator', fn]
    # make sure the command runs successfully
    try:
        sresult = subprocess.run(cmd, check=True,timeout=2,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        #print(sresult.stdout.decode('utf-8'))

    except subprocess.TimeoutExpired:
        print("The subprocess did not complete within the timeout period and was terminated.")
    except subprocess.CalledProcessError as e:
        print(f"The subprocess exited with a non-zero exit status {e.returncode}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    os.chdir(home)
# Run the Astra simulation
def Run_Astra(path,fn,iParallel=0):
    home = os.getcwd()
    os.chdir(path)
    if iParallel == 1:
        cmd = ['mpirun','PAstra',fn]
    else:
        cmd = ['Astra', fn,'> ','out']
    # make sure the command runs successfully
    try:
        sresult = subprocess.run(cmd, check=True,timeout=800,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        outfile = open('out','w')
        outfile.write(sresult.stdout.decode('utf-8'))
        outfile.close()
        #print(sresult.stdout.decode('utf-8'))
    except subprocess.TimeoutExpired:
        print("The subprocess did not complete within the timeout period and was terminated.")
    except subprocess.CalledProcessError as e:
        print(f"The subprocess exited with a non-zero exit status {e.returncode}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    os.chdir(home)

def Run_full(path_gen,fn_gen,path_astra,fn_astra,iParallel=0):
    Run_Generator(path_gen,fn_gen)
    Run_Astra(path_astra,fn_astra,iParallel=0)
    return