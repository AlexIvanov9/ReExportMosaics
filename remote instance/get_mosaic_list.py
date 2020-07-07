import sys
import subprocess
import pathlib,os

# @ALEXL: set this to the python.exe for a python install on the system
# which has the improc module installed on it
IMPROC_PYTHON_EXE_PATH = "C:/Users/administrator/Anaconda3/envs/improc/python.exe"
#IMPROC_PYTHON_EXE_PATH = "/opt/conda/bin/python"

def get_mosaic_list(flight_id):
    path_to_this_script = pathlib.Path(__file__).resolve()
    path_to_this_script = os.path.realpath(__file__)
    print(type(path_to_this_script))
    output = subprocess.check_output([IMPROC_PYTHON_EXE_PATH, path_to_this_script, str(flight_id)], universal_newlines=True)
    print (output)
    #mosaic_ids = [ int(line) for line in output.strip().split('\n') ]
    #return mosaic_ids
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("\tpython get_mosaic_list.py FLIGHT_ID")
    
    # First command line argument is the flight_id
    flight_id = sys.argv[1]
    print(flight_id)
    try:
        import improc
    except Exception as e:
        print(e)
    
    """
    import improc
    for mosaic_id in improc.dbops.spatial.get_mosaic_list(flight_id):
        print(mosaic_id)
    
    try:
        import improc
    except Exception as e:
        print(e)
    
    import improc
        for mosaic_id in improc.dbops.spatial.get_mosaic_list(flight_id):
            print(mosaic_id)
    for mosaic_id in improc.dbops.spatial.get_mosaic_list(flight_id):
        print(mosaic_id)
    """
