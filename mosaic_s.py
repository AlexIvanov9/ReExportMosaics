
import glob
import itertools
import shutil
import json
import os
import time
import subprocess,time
try:
    import PhotoScan
    import dirfuncs
    import basesettings
    from psutils import (PhotoscanException, get_project_filename,
                         gen_mosaic_list)

    ps_conv = {"height field": PhotoScan.HeightField,
               "arbitrary": PhotoScan.Arbitrary,
               "sparse": PhotoScan.DataSource.PointCloudData,
               "dense": PhotoScan.DataSource.DenseCloudData}

except ImportError:
    pass



def check_user_script():
    """
    check if user have mosaic script in his folder
    """
    scripfolder = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Agisoft\PhotoScan Pro\scripts'))
    scriptpath = os.path.join(scripfolder,'mosaic_reexport.py')
    if os.path.exists(scriptpath):
        try:
            os.remove(scriptpath)
        except:
            pass
    if not os.path.exists(scriptpath):
        scr = os.path.join(os.getcwd(),'python','Scripts','mosaic_reexport.py')
        shutil.copy(scr,scripfolder)
    txtpath = os.path.join(scripfolder,'ProjectPath.txt')
    return txtpath
        



def delete_old_projects(folder):
    """
    delete files that were created more than 24 hours ago
    """
    nowTime = time.time()
    ageTime = nowTime - 60*60*8 # hours to delete old files
    for path,dirs,files in os.walk(folder):
        for file in files:
            fileName = os.path.join(path,file)
            fileTime = os.path.getmtime(fileName)
            if fileTime < ageTime:
                print (fileName)
                try:
                    os.remove(fileName)
                except:
                    pass
    return

def old_project_name(project):
    """
    delete old projects and create name for new
    """
    
    pathExport = os.path.join(os.environ["TMP"] + "Projects")
    if not os.path.exists(pathExport):
        os.makedirs(pathExport)
    delete_old_projects(os.environ["TMP"])
    pathExport = os.path.join(pathExport, os.path.basename(project)[:-4] + 'v1.psz')
    return pathExport 


def path_to_txt (txtpath, projectpath):
    """
    save path to project in txt to run project from separete python script
    """
    if os.path.isfile(txtpath):
        try:
            os.remove(txtpath)
        except Exception as e:
            print (e)
            pass
    f= open(txtpath,"w+")
    f.write(projectpath)
    f.close
    return txtpath


def open_p(flight_id, field_id, camera = "jenoptik"):
    """
    Find and open Photoscan 1.3 porject

    Parameters
    ----------
    flight_id : int
    field_id : int or str
    camera : str by default jenoptik
    """
    project = get_project_filename(flight_id, field_id, camera)
    doc = PhotoScan.app.document
    doc.open(project)
    return


def save_old_v(flight_id, field_id, camera = "jenoptik"):
    
    '''
    Re-save project to 1.0 version of Photoscan, helpful when we have a seams on TR

    Parameters
    ----------
    flight_id : int
    field_id : int or str
    camera : str by default jenoptik

    Returns
    -------
    project 1.0

    '''
    project = get_project_filename(flight_id, field_id, camera)
    doc = PhotoScan.app.document
    doc.open(project)
    path = old_project_name(project)
    doc.save(path ,version = '1.0.0')
    #if save only one time it doesn't work
    doc.save(path ,version = '1.0.0')
    saveprojectname = check_user_script()
    path_to_txt(saveprojectname,path)
    subprocess.call(["C:\Program Files\Agisoft\PhotoScan Pro 1.0\PhotoScan Pro 1.0\photoscan.exe"])
    os.remove(path)
    PhotoScan.app.messageBox("Re-export was successful")
    
    
    return 


