import sys
import json
import MySQLdb
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('-f', '--file', help='path to json file to parse')
parser.add_argument('-u', '--databaseuser', help='username for making database connection')
parser.add_argument('-p', '--databasepassword', help='password for making database connection')
args = parser.parse_args()

input_file = args.file if args.file else 'annotations.json'
username = args.databaseuser if args.databaseuser else None
password = args.databaseuser if args.databaseuser else None


"""
    Returns a list of records from the provided JSON file INPUT_FILE
    ('annotations.json' is used by default, but an alternative path can be
    provided with the -f or --file command line argument) with all the invalid
    records (records without a populated 'regions' attribute) filtered out.
"""
def loadJSON(f=input_file):
    print('\nParsing JSON file \'{}\'...'.format(f))

    try:
        records = [json.loads(line) for line in open(f)]
    except IOError:
        if sys.version_info[0] < 3:
            return loadJSON(raw_input('\tFile \'{}\' was not found. ' \
                    'Enter a valid file: '.format(f)))
        else:
            return loadJSON(input('\tFile \'{}\' was not found. ' \
                    'Enter a valid file: '.format(f)))

    print('\t{} records in json file.\n' \
            '\tFiltering records with annotations...'.format(len(records)))

    valid_records = list(filter(lambda r: 'content' in r and
        bool(r['content']['regions']), records))

    print('\t{} valid records in json file.'.format(len(valid_records)))

    return valid_records


"""
    Returns a MySQLdb connection.
"""
def connectDB(username, password):
    print('\nConnecting to MySQL database...')
    return MySQLdb.connect(host="130.65.159.67",
            user=username, passwd=password)


"""
    Returns two dictionaries, users and images, which are mappings of usernames
    and image urls respectively to IDs. These are used to add users.id and
    images.id foreign key fields to annotation records.
"""
def getTables(db):
    print('\nCreating dictionaries \'users\' and \'images\' which map IDs to ' \
            'usernames and image urls respectively...')

    with db as cursor:
        cursor.execute("use annotate")
        cursor.execute("select username, id from users;")
        users = {u[0]: u[1] for u in cursor.fetchall()}
        cursor.execute("select url, id from images;")
        images = {i[0]: i[1] for i in cursor.fetchall()}

    return users, images


"""
    Creates new records and inserts them into the MySQL database.
"""
def populateDB(records, users, images, db):
    print('\nCreating new records and inserting them into MySQL database.')

    error_log = open('errors.log', 'w')
    test_log = open('test.log', 'w')

    """
        Iterates regions in the JSON object.
    """
    def extractAttributes(record):

        """
            Actually creates record and calls insertRecord().
        """
        def createRecord():
            try:
                attrs = {
                        'user_id': users[record['users'][0]['username']],
                        'image_id': images['/'.join(record['imageURL'].split('/')[-1:])],
                        #'image_id': 'dummy value',
                        'class': region['region_attributes']['name'],
                        'last_updated': record['updated']['$date'],
                        'shape': str(region['shape_attributes'])
                        }
                insertRecord(attrs)
            except:
                error_log.write(str(sys.exc_info()) + '\n')


        for region in record['content']['regions'].values():
            createRecord()


    """
        Actually inserts the record into the MySQL database.
    """
    def insertRecord(r):
        test_log.write(str(r) + '\n')

        # NOTE: not tested! -- uncomment this once 'images' table is populated.
        with db as cursor:
            cursor.execute("use annotate")
            cursor.execute("insert into annotations values({}, {}, {}, {}, {})"
                    .format(r['user_id'], r['image_id'], r['shape'],
                        r['class'], r['last_updated']))

    for r in records:
        extractAttributes(r)

    error_log.close()
    test_log.close()


if __name__ == '__main__':
    valid_records = loadJSON()
    db = connectDB(username, password)
    users, images = getTables(db)
    populateDB(valid_records, users, images, db)
    db.close()
