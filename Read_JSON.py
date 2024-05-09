# import the required module of JSON file reading
import json
import pandas as pd
from pandas import json_normalize
debug = 0

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            #print(data)
            #flattened_data = json_normalize(data)
            #print(flattened_data)
            # convert the context into a flatten dataframe for better printing
            #df = pd.DataFrame(flattened_data)
            #print(df)
            return data
    except FileNotFoundError:
        print("File not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

if debug == True:
    print("Debug mode is on.")
    # Specify the path to your JSON file
    #file_path = 'MOGA_input.json'
    file_path = 'Opt_input.json'
    # Read the JSON file
    data = read_json_file(file_path)

    if data is not None:
        print("JSON data loaded successfully!")
        # print all the keys of the columns of df
        print(data.keys())
        print(data['Generator'])
        #print(json.dumps(data["Astra"], indent=4))  
        # Access specific values, for example:
    