

import shutil,fnmatch,glob,os,json
import subprocess,time
try:
    import PhotoScan
    from psutils import get_project_filename
except ImportError:
    pass



def check_user_script():
    """
    Copy mosaic script to user folder, to run it automaticly with 1.0 Photoscan
    Create txt file with path to project
    --------------
    return path to txt file with project
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
    delete files that were created more than 6 hours ago
    ---------------------
    parameters 
    folder - str path to folder which need to clear
    """
    nowTime = time.time()
    ageTime = nowTime - 60*60*6 # hours to delete old files
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
    ---------------
    parameters 
    project - str - path to 1.3 project
    ---------------
    return
    str - path to 1.0 project on C drive
    """
    
    pathExport = os.path.join(os.environ["TMP"] + "Projects")
    if not os.path.exists(pathExport):
        os.makedirs(pathExport)
    delete_old_projects(os.environ["TMP"])
    pathExport = os.path.join(pathExport, os.path.basename(project)[:-4] + 'v1.psz')
    return pathExport 


def re_build_project(flight_id, field_id, typecam):
    """
    rebuild project for 1.3
    to fix 80% such artefacts as stalactide, blobls
    """
    
    open_p(flight_id, field_id, typecam)
    doc = PhotoScan.app.document
    chunk = doc.chunk
    # reset all camera
    for cam in chunk.cameras:
        cam.transform = None
    # image matching and alignment
    chunk.matchPhotos(accuracy=PhotoScan.HighestAccuracy, generic_preselection=True, reference_preselection=True, keypoint_limit=1000,tiepoint_limit=0)
    chunk.alignCameras(adaptive_fitting=False)
    aligned_photos = []
    for camera in chunk.cameras:
        if camera.transform==None:
            aligned_photos.append(camera)
       
    if len(aligned_photos)>0:
        chunk.alignCameras(aligned_photos,adaptive_fitting=False)
    chunk.buildModel(surface=PhotoScan.HeightField, interpolation=PhotoScan.EnabledInterpolation)
    chunk.smoothModel()
    doc.save()
    return







def fix_st(flight_id, field_id, typecam = "jenoptik",exportfolder = False):
    """
    after re-build 1.3 project
    re-save in 1.0 to avoide seams
    ------------------------------
    Parameters
    ----------
    flight_id : int
    field_id : int or str
    camera : str by default jenoptik

    Returns
    mosaic images
    """
    
    if type(field_id).__name__ == "list":
        
        for field in field_id:
            try:
                re_build_project(flight_id, field, typecam)
            except Exception as e:
                print (e)
                field_id = list(set(field_id) - set([field]))
    else:
        re_build_project(flight_id, field_id, typecam)
    
    save_old_v(flight_id, field_id, typecam, exportfolder)
    
    return
    


def path_to_txt (txtpath, projectpath):
    """
    create txt file with path to photoscan 1.0 project
    """
    f= open(txtpath,"w+")
    
    json.dump(projectpath,f)
    
    f.close
    return txtpath




def export_path_to_txt(folder,exportpath):
    """
    Parameters
    -------------------------------------
    folder - str - path to user folder to save new txt
    exportpath - str - path to folder for export mosaics
    """
    txtpath = os.path.join(folder,"mosaicexport.txt")
    f= open(txtpath,"w+")
    f.write(exportpath)
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



def get_old_version(flight_id, field_id, camera = "jenoptik"):
    """
    Parameters
    ----------
    flight_id : int
    field_id : int or str
    camera : str by default jenoptik

    Returns
    -------
    path to save project
    """
    project = get_project_filename(flight_id, field_id, camera)
    doc = PhotoScan.app.document
    doc.open(project)
    path = old_project_name(project)
    doc.save(path ,version = '1.0.0')
    #if save only one time it doesn't work
    doc.save(path ,version = '1.0.0')
    return path
    
def check_tr_if_present(exportfolder,project):
    """
    for batch export check if tr image already present
    if yes delete from list for re-save project
    
    """
    try:
        flightdircontents = glob.glob(exportfolder + '/*.tif')
    except Exception as e:
        print (e)
        return False
    
    
    for files in flightdircontents:
        if fnmatch.fnmatch(files, "*{}*".format(os.path.basename(project)[:-4])):
            return True
    return False
    
    


def save_old_v(flight_id, field_id = True, camera = "jenoptik", exportfolder = False,replace = False):
    
    """
    Re-save project to 1.0 version of Photoscan, helpful when we have a seams on TR

    Parameters
    ----------
    flight_id : int
    field_id : int or str
    camera : str by default jenoptik

    Returns
    -------
    project 1.0

    """
    txtsaveproj = check_user_script()
    
    if exportfolder:
        export_path_to_txt(os.path.dirname(txtsaveproj),exportfolder)
    else:
        exportfolder = 'C:\Daily artifacts\Daily artifacts\Flight {}'.format(flight_id)
        
    if field_id == True:
        try:
            import improc
            from improc import dbops
            field_id = improc.dbops.spatial.get_mosaic_list(flight_id)
        except Exception as e:
            print (e)
        
    
    if type(field_id).__name__ == "list":
        path = []
        # create list of pathes to delete these projects after process fill be finished
        patholdprojects = []
        for field in field_id:
            try:
                project = get_project_filename(flight_id, field, camera)
                if check_tr_if_present(exportfolder,project) == True and replace == False:
                    er = "All project already done"
                    continue
                
                old_pr = get_old_version(flight_id, field, camera)
                projectinfo = {
                        'ProjectPath': old_pr,
                        'Flight_id' : flight_id,
                        'Field': field,
                        'Camera': camera
                        }
                patholdprojects.append(old_pr)
                path.append(projectinfo)
             
            except Exception as e:
                er = e
        
        if len(path) == 0:
            return er
        
        patholdprojects = '\n'.join(patholdprojects)
    else:
        patholdprojects = get_old_version(flight_id, field_id, camera)
        path = [{'ProjectPath': patholdprojects,
                'Flight_id' : flight_id,
                'Field': field_id,
                'Camera': camera}]
        
    path_to_txt(txtsaveproj,path)
    subprocess.call(["C:\Program Files\Agisoft\PhotoScan Pro 1.0\PhotoScan Pro 1.0\photoscan.exe"])
    for pr in patholdprojects.split('\n'):
        os.remove(pr)
    PhotoScan.app.messageBox("Re-export was successful")
    
    
    return 


