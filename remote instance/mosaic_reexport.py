# -*- coding: utf-8 -*-

import PhotoScan
import os
import time
import mosaic
import json

def batch_export_ortho():
    """
    run this function if there is list 
    
    """
    global path_to_project
    
    for path in path_to_project:
        export_filename = os.path.basename(path['ProjectPath']).replace('.psz','.tif')
        export_path = os.path.join(export_folder,export_filename)
        try:
            project = PhotoScan.app.document
            project.open(path['ProjectPath'])
            
            dx, dy = mosaic.get_resolution(path['Flight_id'], path['Field'], path['Camera'])
            
            if dx is not None and dy is not None:
                status = project.activeChunk.exportOrthophoto(
            export_path, format="tif", color_correction=False, blending='average', dx=dx, dy=dy,
            projection=project.activeChunk.projection)
            else:
                status = project.activeChunk.exportOrthophoto(export_path, format="tif", color_correction=False, blending='average',projection=project.activeChunk.projection)
        except Exception as e:
            print(e)
    if status is True:
        print("Perfect")
        app = PhotoScan.Application()
        app.quit()
    

def export_ortho():
    global path_to_project
    print(path_to_project['ProjectPath'])
    export_filename = os.path.basename(path_to_project['ProjectPath']).replace('.psz','.tif')
    export_path = os.path.join(export_folder,export_filename)
    try:
        project = PhotoScan.app.document
        project.open(path_to_project['ProjectPath'])
        dx, dy = mosaic.get_resolution(path_to_project['Flight_id'], path_to_project['Field'], path_to_project['Camera'])
        if dx is not None and dy is not None:
                status = project.activeChunk.exportOrthophoto(export_path, format="tif", 
                                                              color_correction=False, blending='average', dx=dx, dy=dy,
                                                              projection=project.activeChunk.projection)
        else:
            status = project.activeChunk.exportOrthophoto(export_path, format="tif", color_correction=False, blending='average',
                                                          projection=project.activeChunk.projection)
        if status is True:
            app = PhotoScan.Application()
            app.quit()
    except Exception as e:
        print(e)
        
    return

def open_project():
    global path_to_project
    path_to_project = path_to_project['ProjectPath']
    try:
        project = PhotoScan.app.document
        project.open(path_to_project)
    except Exception as e:
        print(e)
        
    return


def check_lines(txt_file):
    """
    check txt file for count of project
    if there are more then 1 path - need batch proccess it
    """
    
    lines = len(get_name_from_txt (txt_file))
    if lines > 1:
        return True
    else:
        return False


def get_name_from_txt (txtpath):
    """
    take path project from txt file
    file prokect should be save in Photoscan 1.3
    """
    f= open(txtpath,"r")
    contents = json.load(f)
    #f.close       
    return contents


def get_export_folder(exportpath,flight_id):
    """
    check if there is path to export folder
    """
    ef = 'D:\Flight {}\mosaic'.format(flight_id)
    if check_txt(exportpath):
        try:
            f= open(exportpath,"r")
            ep = f.read()
            f.close
            if not os.path.exists(ep):
                os.makedirs(ep)
            return ep
        except Exception as e:
            print(e)
    else:
        if not os.path.exists(ef):
            os.makedirs(ef)
        return ef

def check_txt(txtpath):
    """
    Check if txt file is available and was created pass 12 seconds
    
    Parameters
    ----------
    txtpath - str 
        path to txt folder
    
    Returns
    -------
    
    True or False if there is no such file
    
    
    """
    if not os.path.isfile(txtpath) :
        return False
    nowTime = time.time()
    ageTime = nowTime - 20
    fileTime = os.path.getmtime(txtpath)
    if fileTime > ageTime:
        return True
    return False
    
#projectpath = "ProjectPath.txt"
"""
check if file was create late than 20 sec if yes pass if no run project
"""
projectpath = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Agisoft\PhotoScan Pro\scripts\ProjectPath.txt'))
exportpath = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Agisoft\PhotoScan Pro\scripts\mosaicexport.txt'))
if check_txt(projectpath):
    
    global export_folder
    flight_id = get_name_from_txt (projectpath)[0]['Flight_id']
    export_folder = get_export_folder(exportpath,flight_id)
    
    global path_to_project
    if check_lines(projectpath):
        path_to_project = get_name_from_txt (projectpath)
        lexport = "Export orthophoto/batch export"  
        PhotoScan.app.addMenuItem(lexport, batch_export_ortho)
        
        
    else:
        path_to_project = get_name_from_txt (projectpath)[0]
        lexport = "Export orthophoto/Export mosaic{} ".format(os.path.basename(path_to_project['ProjectPath'][:-4]))    
        PhotoScan.app.addMenuItem(lexport, export_ortho)
        label = "Export orthophoto/ Open {}".format(os.path.basename(path_to_project['ProjectPath'][:-4]))
        PhotoScan.app.addMenuItem(label, open_project)
    
    
