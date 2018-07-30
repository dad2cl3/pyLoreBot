import os, pg8000, re, string


def build_search_string(raw_string):

    # remove leading/trailing whitespace
    raw_string = raw_string.strip()
    # remove any punctuation
    raw_string = raw_string.translate(raw_string.maketrans('', '', string.punctuation))
    # replace spaces with ampersands
    raw_string = re.sub('\s\s+', ' ', raw_string)
    raw_string = raw_string.replace(' ', ' & ')

    # print(raw_string)
    new_string = raw_string

    return new_string


def handler(event, context):
    lore_types = []
    print(event)

    if 'type' in event:
        lore_types.append(event['type'])
    else:
        lore_types = ['grimoire', 'inventory']

    print(lore_types)
    # get the lore search string
    lore_search = build_search_string(event['search'])

    # open database connection
    pg = pg8000.connect(
        host=os.environ['database_host'],
        port=5432,
        database=os.environ['database'],
        user=os.environ['database_user'],
        password=os.environ['database_password']
    )

    pg_cursor = pg.cursor()

    lore = {}

    for lore_type in lore_types:
        pg_cursor.execute(os.environ['sql'].format(lore_type, lore_search))
        query_results = pg_cursor.fetchall()

        results = []
        for result in query_results:
            results.append(result[0])

        if len(results) > 0:
            lore[lore_type] = results

    # close database connection
    pg.close()

    #print(lore)
    return lore