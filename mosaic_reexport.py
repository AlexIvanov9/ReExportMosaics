# -*- coding: utf-8 -*-

import PhotoScan
import os
import time


def batch_export_ortho():
    """
    run this function if there is list 
    
    """
    global path_to_project
    print(path_to_project)
    for path in path_to_project:
        export_filename = os.path.basename(path).replace('.psz','.tif')
        export_path = os.path.join(export_folder,export_filename)
        try:
            project = PhotoScan.app.document
            project.open(path)
            status = project.activeChunk.exportOrthophoto(
            export_path, format="tif", color_correction=False, blending='average',
            projection=project.activeChunk.projection)
        except Exception as e:
            print(e)
    if status is True:
        print("Perfect")
        app = PhotoScan.Application()
        app.quit()

def export_ortho():
    global path_to_project
    print(path_to_project)
    export_filename = os.path.basename(path_to_project).replace('.psz','.tif')
    export_path = os.path.join(export_folder,export_filename)
    try:
        project = PhotoScan.app.document
        project.open(path_to_project)
        status = project.activeChunk.exportOrthophoto(
        export_path, format="tif", color_correction=False, blending='average',
        projection=project.activeChunk.projection)
        if status is True:
            print("Perfect")
            app = PhotoScan.Application()
            app.quit()
    except Exception as e:
        print(e)
        
    return

def open_project():
    global path_to_project
    print(path_to_project)
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
    file = open(txt_file,"r")
    lines = len(file.readlines())
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
    contents = f.read()
    f.close       
    return contents


def get_export_folder(exportpath):
    """
    check if there is path to export folder
    """
    ef = 'C:\Daily artifacts\Daily artifacts'
    if check_txt(exportpath):
        try:
            ef = get_name_from_txt (exportpath)
            return ef
        except:
            pass
    else:
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
    ageTime = nowTime - 12
    fileTime = os.path.getmtime(txtpath)
    if fileTime > ageTime:
        return True
    return False
    
#projectpath = "ProjectPath.txt"
"""
check if file was create late than 12 sec if yes pass if no run project
"""
projectpath = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Agisoft\PhotoScan Pro\scripts\ProjectPath.txt'))
exportpath = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Agisoft\PhotoScan Pro\scripts\mosaicexport.txt'))
if check_txt(projectpath):
    
    global export_folder
    export_folder = get_export_folder(exportpath)
    
    global path_to_project
    if check_lines(projectpath):
        path_to_project = get_name_from_txt (projectpath).split('\n')
        lexport = "Export orthophoto/batch export"  
        PhotoScan.app.addMenuItem(lexport, batch_export_ortho)
        
        
    else:
        path_to_project = get_name_from_txt (projectpath)
        lexport = "Export orthophoto/Export mosaic{} ".format(os.path.basename(path_to_project[:-4]))    
        PhotoScan.app.addMenuItem(lexport, export_ortho)
        label = "Export orthophoto/ Open {}".format(os.path.basename(path_to_project[:-4]))
        PhotoScan.app.addMenuItem(label, open_project)
    
    
