import shutil,fnmatch,glob,os,json,re
import subprocess,time
try:
    import dirfuncs
    import PhotoScan
    from psutils import get_project_filename
    import basesettings
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
        scr = os.path.join('C:\Program Files\Agisoft\PhotoScan Pro\python\Scripts\mosaic_reexport.py')
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



def find_images(flight_id, field_id, camera):
    """
    get list of images for photoscan project
    """
    data_dir = dirfuncs.get_data_dir(flight_id, camera,
                                     mosaic_input_stage=None)
    
    imu_dir = dirfuncs.get_imu_dir(flight_id, field_id, camera)
    imupath = imu_dir + basesettings.get_setting(camera, "logs", "imu")
    if os.path.exists(imupath):
        
        expected_images, likely_turns = dirfuncs.get_expected_images(
            flight_id, field_id, camera)
        available_images = dirfuncs.get_available_images(flight_id, field_id,
                                                         camera)
    image_filenames = []
    for im in expected_images:
        if im in available_images:
            image_filenames.append(data_dir + im)
    if not image_filenames:
        print("Images for this project not available in {}".format(data_dir))
        return None
    return image_filenames, likely_turns




def disable_alternate_photos(project=None, n=2):
    """
    Disables every other photo in loaded project.

    Parameters
    ----------
    project : PhotoScan project instance
    """

    if project is None:
        project = PhotoScan.app.document
    chunk = project.chunk
    c = 0
    for i in chunk.cameras:
        if c % n != 0:
            i.enabled = False
        c += 1





def add_images_to_project(flight_id, field_id, camera,project,
                          master_channel=-1, alt_cameras=None,
                          use_turns=False):
    """
    Given a list of filenames of images, loads the images into a photoscan
    project.

    Parameters
    ----------
    image_filenames : list
        Full paths to images to load in project

    likely_turns : list
        Boolean values corresponding to image_filenames which indicate whether
        the image has been classified as a turn, extra pass, late pass etc.
    project : instance of PhotoScan.app.document

    master_channel : int (opt)
        Default is -1, which is PhotoScan default. Corresponds to band in
        image to use as channel for alignment.

    alt_cameras : int (opt)
        If set, will enable only every nth image. E.g. alt_cameras=2 keeps
        every other image, alt_cameras=3 keeps every third image, etc.

    use_turns : boolean (opt)
        Default is False, if True will not disable images classified as turn,
        late, or belonging to a duplicate pass in the PhotoScan project.

    Returns
    -------
    project : instance of PhotoScan.app.document
        Same project passed in, but now with images.

    Notes
    -----
    Only takes a "fresh" project. If there is already a chunk, an exception
    will be raised.
    """
    
    #project = PhotoScan.app.document
    image_filenames, likely_turns = find_images(flight_id, field_id, camera)
    
    if len(project.chunks) > 0:
        project.remove(project.chunks)

    chunk = project.addChunk()
    chunk.label = "Chunk 1"
    chunk.addPhotos(image_filenames)
    if "1.4" in PhotoScan.app.version:
        chunk.master_channel = master_channel
    else:
        chunk.primary_channel = master_channel


    if not use_turns:
        disabled_images = [image for (image, turn) in zip(image_filenames,
                                                          likely_turns) if turn]
        disabled_images = [os.path.basename(x) for x in disabled_images]
        for i in [x for x in project.chunk.cameras if x.label in disabled_images]:
            i.enabled = False
        print("Disabling {} cameras".format(len(disabled_images)))

    if alt_cameras is not None:
        disable_alternate_photos(project, alt_cameras)

    return project







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
    
    #delete_old_projects(os.environ["TMP"])
    pathExport = os.path.join(os.environ["TMP"] + "Projects")
    if not os.path.exists(pathExport):
        os.makedirs(pathExport)
    
    pathExport = os.path.join(pathExport, os.path.basename(project)[:-4] + 'v1.psz')
    return pathExport 



def run_down_bat(flight,field,camera,sep = False, buffer = False):
    """
    create bat file for donwsync photoscan project from S3
    """
    
    #block = ''
    print(flight,field,camera)
    fieldsep = field
    if type(field).__name__ != 'int':
        #block = ''.join(re.findall(r'[^\W\d]', field))
        field = ''.join(re.findall(r'[\d]', field))
         
    batpath = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Temp','{}{}.bat'.format(flight,field)))
    bat = open(batpath,'w+')

    bat.write('pushd %TEMP% \n')
    #if block != '':
        #function = '"import improc;improc.qc.syncer.downsync_mosaic({0}, {1},camera = '.format(flight,field) + "'{}'".format(camera) + ",mosaic_block_letter = '{}'".format(block) + ')"'
    #else:
    if sep == False:
        function = '"import improc;improc.qc.syncer.downsync_mosaic({0}, {1}, camera = '.format(flight,field) + "'{}'".format(camera) + ')"'
        bat.write('C:/Users/administrator/Anaconda3/envs/improc/python -c {} \n'.format(function))
    if camera == "stack" or camera == "ids rgb" and buffer == False:
        separete = '"import improc;improc.preprocess.write_separated_log({}'.format(flight)+ " ,'{}'".format(fieldsep) + " ,camera = '{}'".format(camera) + ')"'
        bat.write('C:/Users/administrator/Anaconda3/envs/improc/python -c {}'.format(separete))
    
    elif buffer:
        separete = '"import improc;improc.preprocess.write_separated_log({}'.format(flight)+ " ,'{}'".format(fieldsep) + " ,camera = '{}'".format(camera) + ',fov_frac = {})"'.format(buffer)
        bat.write('C:/Users/administrator/Anaconda3/envs/improc/python -c {}'.format(separete))
    
    
    bat.close()
    subprocess.check_call(batpath)
    os.remove(batpath)
    return




def re_build_project(flight_id, field_id, typecam, buffer = False):
    """
    rebuild project for 1.3
    to fix 80% such artefacts as stalactide, blobls
    """
    open_p(flight_id, field_id, typecam)
    doc = PhotoScan.app.document
    if buffer != False:
        add_images_to_project(flight_id, field_id, typecam, doc)
        
    chunk = doc.chunk
    doc.chunk.point_cloud = None
    doc.chunk.model = None
    doc.chunk.orthomosaic = None
    chunk.resetRegion()
    
    
    # reset all camera
    for camera in chunk.cameras:
        camera.transform = None
        # camera.enabled = True
    # image matching and alignment
    
    chunk.matchPhotos(accuracy=PhotoScan.HighestAccuracy, generic_preselection=True,
                     reference_preselection=True, keypoint_limit=1000,tiepoint_limit=0)
    chunk.alignCameras(adaptive_fitting=False)
    aligned_photos = []
    for camera in chunk.cameras:
        if camera.transform==None:
            aligned_photos.append(camera)
    if len(aligned_photos)>0:
        chunk.alignCameras(aligned_photos,adaptive_fitting=False)
    point_cloud = PhotoScan.PointCloud
    filter = point_cloud.Filter()
    filter.init(chunk, filter.ReconstructionUncertainty)
    filter.removePoints(25)
    chunk.optimizeCameras()
    filter.removePoints(25)
    chunk.resetRegion()
    chunk.buildModel(surface=PhotoScan.HeightField, interpolation=PhotoScan.EnabledInterpolation)
    chunk.model.closeHoles()
    chunk.smoothModel(1)
    # chunk.buildOrthomosaic(surface = PhotoScan.DataSource.ModelData, blending= PhotoScan.AverageBlending)
    #chunk.crs.project(chunk.transform.matrix.mulp(chunk.region.center)) пременить к центрам снимков
    doc.save()
    
    return

def fix_st(flight_id, field_id, typecam = "jenoptik",exportfolder = False,replace = True , buffer = False):
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
    
    if buffer != False:
        run_down_bat(flight_id, field_id, typecam ,sep = False, buffer = buffer)
        
    if exportfolder == False:
        exportfolder = r'D:\Flight {}\mosaic'.format(flight_id)
        
    field_id = check_tr_if_present(flight_id, field_id, typecam, exportfolder, replace)
    if len(field_id) == 0:
        return "All project already done"
    
    for field in field_id:
        errormesage = []
        try:
            re_build_project(flight_id, field, typecam)
        except Exception as e:
            errormesage.append(e)
            field_id = list(set(field_id) - set([field]))
    if len(field_id) == 0:
        return errormesage
    
    save_old_v(flight_id, field_id, typecam, exportfolder = exportfolder)
    return




def copyimages(flight,field,copy = True):
    
    
    chunk = PhotoScan.app.document.chunk
    ordir = os.path.dirname(chunk.cameras[1].frames[0].photo.path)
    
    if copy:
        #if exportfolder == False:
        exportfolder = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Temp',"Projects{}{}".format(flight,field)))
            #exportfolder = os.path.join(os.environ["TMP"],"Projects{}{}".format(flight,field))
        # скопировать файл
        if not os.path.exists(exportfolder):
            os.makedirs(exportfolder)
        for i in range (len(chunk.cameras)):
            scr = chunk.cameras[i].frames[0].photo.path
            shutil.copy(scr,exportfolder)
        script = r'C:\Program Files\Agisoft\PhotoScan Pro\python\Scripts\Colorize.py'
        shutil.copy(script,exportfolder)
        #quite often problem with user name change to this type
        script = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Temp',"Projects{}{}\Colorize.py".format(flight,field)))
        #script = r'{}'.format(os.path.join(exportfolder,os.path.basename(script)))
        print(script)
        cmd = 'C:\Python27\ArcGIS10.6\python.exe "{}"'.format(script)
        os.system(cmd)
        return ordir,exportfolder
    else:
       exportfolder = os.path.join(dirfuncs.guess_flight_dir(flight),'Jenoptik/Corrected')
       return ordir,exportfolder
       
   
    
def replaceimages(original,exportfolder):
    chunk = PhotoScan.app.document.chunk
    for i in range (len(chunk.cameras)):
        pathphoto = chunk.cameras[i].frames[0].photo.path
        chunk.cameras[i].frames[0].photo.path = pathphoto.replace(original, exportfolder)
    return


    
    
def colorize(flight_id, field_id, camera = "jenoptik",exportfolder = False, replace = False, fix = False):
    
    if replace:
        copy = False
    else:
        copy = True
        open_p(flight_id, field_id, camera)
    original,exportpath = copyimages(flight_id, field_id,copy)
    replaceimages(original,exportpath)
    
    if fix == False:
        message = "Replaced all images"
        PhotoScan.app.messageBox(message)
    if replace:
        shutil.rmtree(os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Temp',"Projects{}{}".format(flight_id,field_id))))
        doc = PhotoScan.app.document
        doc.save()
    if fix:
        fix_st(flight_id, field_id, camera, exportfolder)
    



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
    
    

def open_p(flight_id, field_id, camera = "jenoptik",openp = True):
    """
    Find and open Photoscan 1.3 porject

    Parameters
    ----------
    flight_id : int
    field_id : int or str
    camera : str by default jenoptik
    openp : bool if True will open project if False return project name 
    """
    try:
        project = get_project_filename(flight_id, field_id, camera)
        if os.path.isfile(project) == False:
            run_down_bat(flight_id, field_id, camera)
    except Exception as e:
        if type(e) == FileNotFoundError or type(e) == RuntimeError:
            run_down_bat(flight_id, field_id, camera)
            project = get_project_filename(flight_id, field_id, camera)
        if type(e) == ValueError:
            run_down_bat(flight_id, field_id, camera,sep = True)
            project = get_project_filename(flight_id, field_id, camera)
            
        
    """
        if type(e) == FileNotFoundError:
            run_down_bat(flight_id, field_id, camera)
            project = get_project_filename(flight_id, field_id, camera)
        if type(e)  == ValueError and camera == "stack" or camera == "ids rgb":
            print('First try to run \nimproc.preprocess.write_separated_log({},{},"stack") \n from Jupyter'.format(flight_id,field_id))
            print (e)
            return None
    """
        
    if openp == False:
        return project
    doc = PhotoScan.app.document
    doc.open(project)
    return project



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
    project = open_p(flight_id, field_id, camera)
    doc = PhotoScan.app.document
    path = old_project_name(project)
    doc.save(path ,version = '1.0.0')
    #if save only one time it doesn't work
    doc.save(path ,version = '1.0.0')
    return path
    



def check_tr_if_present(flight_id, field_id, camera, exportfolder,replace = True):
    """
    check if tr image already present
    if replace = True delete this image
    if yes delete from list for re-save project
    
    Parameters
    ----------
    flight_id : int
    field_id : int or str
    camera : str by default jenoptik
    exportfolder : str - folder for expot mosaic
    replace : check if mosaic image already present in folder, if True will delete
    
    Returns
    -------
    path to save project
    
    """
    
    if type(field_id).__name__ != "list":
        field_id = str(field_id).split("delimiter")
    flightdircontents = glob.glob(exportfolder + '/*.tif')
    for field in field_id:
        project = open_p(flight_id, field, camera, openp=False)
        if project == None:
            field_id = list(set(field_id) - set([field]))
            continue
            
        for file in flightdircontents:
            if fnmatch.fnmatch(file, "*{}*".format(os.path.basename(project)[:-4])):
                if replace:
                    try:
                        os.remove(file)
                        continue
                    except Exception as e:
                        continue
                        print (e)
                        
                field_id = list(set(field_id) - set([field]))
                
    return field_id
    
    
    
def downsyncpr (flight_id, field_id, camera):
    """
    downsycn data for photoscan project
    block = ''
    if type(field_id).__name__ != 'int':
        #try:
        block = ''.join(re.findall(r'[^\W\d]', field_id))
        #except Exception as e:
            #block = ''
            #print (e)
     
    #args = ['C:/Users/administrator/Anaconda3/envs/improc/python', 'C:/Program Files/Agisoft/PhotoScan Pro/python/Scripts/downsync.py',str(flight_id),str(field_id),block,camera]
    #process = subprocess.Popen(args)
    
    cmd = 'C:/Users/administrator/Anaconda3/envs/improc/python "C:/Program Files/Agisoft/PhotoScan Pro/python/Scripts/downsync.py" {} {} {}'.format(flight_id,field_id,camera)
    print(cmd)
    result = os.system(cmd)
    """
    
    return "Skip at this moment"
    
    
    
    
    


def save_old_v(flight_id, field_id, camera = 'jenoptik', exportfolder = False,replace = True):
    
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
    if exportfolder != False:
        export_path_to_txt(os.path.dirname(txtsaveproj),exportfolder)
    else:
        exportfolder = r'D:\Flight {}\mosaic'.format(flight_id)
    
    # check if precent id if and return list of id 
    e = None
    try:
        rezerv = check_tr_if_present(flight_id, field_id, camera, exportfolder , replace)
        field_id = rezerv 
    except Exception as e:
        print (e)
    if len(list(field_id)) == 0 and e == None:
        return "There is no 1.0 project to run"
    if len(field_id) == 0 and e != None:
        return e
    
    
    path = []
    # create list of pathes to delete these projects after process fill be finished
    patholdprojects = []
    failids = []
    
    for field in field_id:
        try:
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
            field_id = list(set(field_id) - set([field]))
            failids.append(field)
            er = e
        
    if len(path) == 0:
        return er
    
    path_to_txt(txtsaveproj,path)
    subprocess.call(["C:\Program Files\Agisoft\PhotoScan Pro 1.0\PhotoScan Pro 1.0\photoscan.exe"])
    for pr in patholdprojects:
        os.remove(pr)
    message = "Re-export for flight : {} , field : {} complete".format(flight_id, str(field_id))
    if len(failids) != 0:
        message = "Re-export for flight : {} , field : {} complete \n Failed export for flied {}".format(flight_id, str(field_id),str(failids))
    PhotoScan.app.messageBox(message)
    
    
    return 


