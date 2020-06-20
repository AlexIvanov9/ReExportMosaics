import matplotlib.pyplot as plt
import glob,time,os

def get_path():

    files = glob.glob('{}/*.png'.format(os.path.dirname(os.path.realpath(__file__))))
    if len(files) > 0:
        if "A:\Flight" not in files[0]:
            for image in files:
                try:
                    img = plt.imread(image)
                    plt.imsave(image, img, cmap='afmhot')
                except Exception as e:
                    print(e)

if __name__ == "__main__":
    get_path()
