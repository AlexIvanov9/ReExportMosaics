# -*- coding: utf-8 -*-

import PhotoScan
import os
import sys
import time



def export_ortho():
    global path_to_project
    print(path_to_project)
    export_filename = os.path.basename(path_to_project).replace('.psz','.tif')
    export_path = os.path.join('C:\Daily artifacts\Daily artifacts',export_filename)
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


def get_name_from_txt (txtpath):
    """
    take path project from txt file
    file prokect should be save in Photoscan 1.3
    """
    f= open(txtpath,"r")
    contents = f.read()
    f.close       
    return contents


def check_txt(txtpath):
    if not os.path.isfile(txtpath) :
        return False
    nowTime = time.time()
    ageTime = nowTime - 12
    fileTime = os.path.getmtime(txtpath)
    if fileTime > ageTime:
        return True
    
#projectpath = "ProjectPath.txt"
"""
check if file was create late than 12 sec if yes pass if no run project
"""
projectpath = os.path.join(os.path.join(os.environ['USERPROFILE'],'AppData\Local\Agisoft\PhotoScan Pro\scripts\ProjectPath.txt'))
if check_txt(projectpath):
    global path_to_project
    path_to_project = get_name_from_txt (projectpath)
    lexport = "Export orthophoto/Export mosaic{}".format(os.path.basename(path_to_project[:-4]))
    label = "Export orthophoto/ Open {}".format(os.path.basename(path_to_project[:-4]))
    PhotoScan.app.addMenuItem(lexport, export_ortho)
    PhotoScan.app.addMenuItem(label, open_project)
