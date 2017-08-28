from scipy.misc import imread
import h5py
import numpy as np
import os


def image_generator(src, chunk_size=256):
    """ Generator function that yields chunks of image data as ndarrays.
        Images are flattened into numpy arrays of shape
        (width * height * channels,). Chunks have shape
        (chunk_size, array.shape[0]). SRC is the directory of the images to
        process. CHUNK_SIZE defines the row dimension of the yielded chunk. """
    imgs = sorted(os.listdir(src))
    i = 0
    while i + chunk_size < len(imgs):
        yield np.asarray([imread(src+imgs[i+j]) for j in range(chunk_size)])
        i += chunk_size
    if i < len(imgs):
        yield np.asarray([imread(src+imgs[i+j]) for j in range(len(imgs)-i)])


# Update this for your environment!
# This script expects the root directory to have `data` and `datasets`
# directories in it.
root = /home/aicg2/


# Dictionary with H5 'group' names as keys and image directory paths as values.
src_directories = {
    'aic540/train': root + 'datasets/aic540/train/images/',
    'aic540/val': root + 'datasets/aic540/val/images/',
    'aic480/train': root + 'datasets/aic480/train/images/',
    'aic480/val': root + 'datasets/aic480/val/images/',
}


# Set this to reasonable chunk size. Apparently the recommended chunk size for
# large datasets is ~1MiB which is about the size of just a single image --
# 1555200 8-bit integers is 1,555,200 bytes or 1.5MiB -- this may still be
# useful though if we down sample images to, say, 32x32 or something like that.
chunk_size=3


# Opens an H5 data file and creates multiple "groups" (datasets) inside of it
# which are matrices of flattened images.
with h5py.File(root + 'data/data.h5', 'w') as f:
    for group, src in src_directories.items():
        print "Making a dataset for group {} using files located at {}".format(group, src)
        gen = image_generator(src=src, chunk_size=chunk_size)
        chunk = next(gen)

        dset = f.create_dataset(name=group,
                    shape=(chunk.shape),
                    maxshape=(None, None, None, None),
                    chunks=(chunk.shape),
                    dtype=np.int8)

        dset[:] = chunk
        count = chunk.shape[0]
        for chunk in gen:
            dset.resize(count + chunk.shape[0], axis=0)
            dset[count:] = chunk
            count += chunk.shape[0]
