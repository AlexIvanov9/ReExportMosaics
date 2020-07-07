try:
    import improc
except Exception as e:
    print (e)
import sys
import os,re
import time

flight = sys.argv[1]
field = sys.argv[2]
camera = sys.argv[3]



block = ''
if type(field).__name__ != 'int':
    block = ''.join(re.findall(r'[^\W\d]', field))
    field = ''.join(re.findall(r'[\d]', field))
    
print(flight, field,camera,block)

def downsync(flight,field,block,camera):
    try:
        
        improc.qc.syncer.downsync_mosaic(flight, int(field), mosaic_block_letter=block, camera = camera)
    except Exception as e:
        print (e)
    return

up = downsync(flight,field,block,camera)


"""
cmd = 'C:/Users/administrator/Anaconda3/envs/improc/python "C:/Program Files/Agisoft/PhotoScan Pro/python/Scripts/downsync.py" {} {} {}'.format(flight_id,field_id,camera)
print(cmd)
result = os.system(cmd)

"""
