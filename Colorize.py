import matplotlib.pyplot as plt
import glob

files = glob.glob('./*.png')
if len(files) > 0:
    if "A:\Flight" not in files[0]:
        for image in files:
            try:
                img = plt.imread(image)
                plt.imsave(image, img, cmap='afmhot')
            except Exception as e:
                print(e)