from argparse import ArgumentParser
import os
import json


"""
    Must supply an input directory containing .txt files output by our model.
    Must supply an output JSON file.
    Must supply one of three filtering criteria used on each unique object: top
    K results, results equal to or above a certain confidence level, or all
    results where the difference between the confidence of the current and
    previous class is less than or equal to a particular value.
"""
def parseArguments():
    parser = ArgumentParser()

    parser.add_argument('-i', '--input', required=True,
            help='directory of result files to filter')
    parser.add_argument('-o', '--output', required=True,
            help='JSON file to store results in')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-k', '--K_results', type=int,
            help='filter top K results')
    group.add_argument('-c', '--confidence_cutoff', type=float,
            help='filter results with a confidence of at least C')
    group.add_argument('-s', '--confidence_spread', type=float,
            help='filter successive results with a spread less than S')

    return parser.parse_args()


def filterResults():

    # Yields class clusters grouped by unique object.
    def groupBoxes(boxes):

        def boxCoordinates(box):
            return ' '.join(box.split()[1:-1])


        def findMatchingBoxes():
            u_set = ()
            for box in list(boxes):
                if boxCoordinates(box) == u_coordinates:
                    u_set += (box.strip('\n'),)
                    del boxes[boxes.index(box)]
            groups.append(list(reversed(sorted(u_set, key=lambda x:
                x.split()[-1]))))


        unique = set([boxCoordinates(b) for b in boxes])
        groups = []
        [findMatchingBoxes() for u_coordinates in unique]

        return groups

    results = {}    # JSON data to write to file.

    # Iterate .txt files, group unique objects, then filter.
    for f in os.listdir(args.input):
        print os.listdir(args.input)
        print '\nprocessing file {}\n'.format(f)
        with open(args.input + f) as f_open:
            groups = groupBoxes(f_open.readlines())

        for i, group in enumerate(groups):
            group = groups.pop(i)
            if args.K_results:
                group = group[0:args.K_results]
            elif args.confidence_cutoff:
                g = [j for j in group if float(j.split()[-1])
                        >= args.confidence_cutoff]
                group = tuple([group[0]]) if not g else tuple(g)
            else:
                last = float('-inf')
                new_group, last = [], float('-inf')
                for g in group:
                    confidence = float(g.split()[-1])
                    if last - confidence <= args.confidence_spread:
                        new_group.append(g)
                        last = confidence
                group = tuple(new_group)
            groups.insert(i, group)

        results[f]  = [{
            'class': g.split()[0],
            'xmin': g.split()[1],
            'ymin': g.split()[2],
            'xmax': g.split()[3],  # This might need to be changed to g.split()[1] + g.split()[3]
            'ymax': g.split()[4],  # This might need to be changed to g.split()[2] + g.split()[4]
            'confidence': g.split()[5]
            } for group in groups for g in group]

    return results


if __name__ == '__main__':
    args = parseArguments()
    data = filterResults()
    json.dump(data, open(args.output, 'w'))
