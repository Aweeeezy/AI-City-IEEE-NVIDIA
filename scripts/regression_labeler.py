import os
import numpy as np

def build_labels(path, mode):
    """ Creates a multi class or single class (depending on `mode`) labels file
        for each of the paths defined in the variable `paths`. """

    files = sorted(os.listdir(path))

    for i, f in enumerate(files):

        if i % 2500 == 0:
            print "Processing file {} of {}".format(i, len(files))

        vehicle_count = 0
        labels = {
            'Car': 0, 'SUV': 0, 'SmallTruck': 0, 'MediumTruck': 0,
            'LargeTruck': 0, 'Pedestrian': 0, 'Bus': 0, 'Van': 0,
            'GroupOfPeople': 0, 'Bicycle': 0, 'Motorcycle': 0,
            'TrafficSignal-Green': 0, 'TrafficSignal-Yellow': 0,
            'TrafficSignal-Red': 0
        }

        # Read label file from `path` and count individual class instances as
        # well as instances of aggregated vehicle class objects.
        with open(path+f, 'r') as f:
            lines = f.readlines()
            for l in lines:
                labels[l.split()[0]] += 1
                if l.split()[0] in vehicles:
                    vehicle_count += 1

        # Open new labels file and write either `vehicle_count` or all class
        # object counts (depending on `mode`).
        #with open('../model/labels/{}_class_labels/{}_{}_labels.txt'.format(
        with open('../labels/{}_class_labels/{}_{}_labels.txt'.format(
                mode,
                path.split('/')[-4],
                path.split('/')[-3]), 'a') as label_files:

            if mode is 'single':
                label_files.write(str(vehicle_count) + '\n')
            elif mode is 'multi':
                write_string = '{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n'
                label_files.write(write_string.format(*[l[1] for l in sorted(
                        labels.items(), key=lambda x: x[0].lower())]))


if __name__ == '__main__':

    # Training and validation labels for the aic540 and aic480 datasets.
    paths = [
        '/datasets/aic540/train/labels/', '/datasets/aic540/val/labels/',
        '/datasets/aic480/train/labels/', '/datasets/aic480/val/labels/'
    ]

    # List of object classes that are to be considered as 'vehicles' for use
    # with single class models.
    vehicles = ['Van', 'MediumTruck', 'Car', 'SmallTruck', 'SUV', 'LargeTruck', 'Bus']

    # Change this to 'multi' to count each of the 14 class objects. 'single'
    # mode aggregates the counts for each of the object classes in the
    # `vehicles` list above.
    mode = 'single'

    for path in paths:
        print "Building labels for {} in {} mode.".format(path, mode)
        build_labels(path, mode)
