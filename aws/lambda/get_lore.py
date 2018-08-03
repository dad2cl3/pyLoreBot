import os, pg8000, re, string


def build_search_string(raw_string):
    # remove leading/trailing whitespace
    raw_string = raw_string.strip()
    # remove any punctuation
    #raw_string = raw_string.translate(raw_string.maketrans('', '', string.punctuation))
    raw_string = raw_string.translate(raw_string.maketrans('', '', '"#$%\'*+,-./:;<=>?@[\]^_`{}~'))
    # Remove )(
    bad_parens = re.compile('\)\s*\(')
    raw_string = re.sub(bad_parens, ' ', raw_string)
    # remove redundant spaces
    raw_string = re.sub('\s\s+', ' ', raw_string)

    # replace keywords 'and', 'not', and 'or' with '&', '!' and '|'
    keywords = [
        {
            'old': 'and',
            'new': '&'
        },
        {
            'old': 'not',
            'new': '!'
        },
        {
            'old': 'or',
            'new': '|'
        }
    ]
    print(raw_string)
    for keyword in keywords:
        keyword_sub = re.compile('\s{0}\s'.format(keyword['old']))

        # must maintain whitespace for successive searches within the loop
        raw_string = re.sub(keyword_sub, ' {0} '.format(keyword['new']), raw_string)
        print(raw_string)

    # replace single space between words with &
    single_space = re.compile('([a-zA-Z0-9])\s([a-zA-Z0-9])')
    raw_string = re.sub(single_space, '\\1&\\2', raw_string)
    print('Remove single space between words with & - {0}'.format(raw_string))

    # replace single space around operators with operator
    allowed_punc = ['(', ')', '&', '!', '|']

    for punc in allowed_punc:
        punc_sub = re.compile('\s*\{0}\s*'.format(punc))
        raw_string = re.sub(punc_sub, punc, raw_string)

    print('Replace single space around operators with operators - {0}'.format(raw_string))
    #raw_string = raw_string.replace(' and ', '&').replace(' or ', '|').replace(' & ', '&').replace(' | ', '|')

    # Look for ! not preceded by & or | and replace with &!
    invalid_not = re.compile('([a-zA-Z0-9])!')
    raw_string = re.sub(invalid_not, '\\1&!', raw_string)

    # Look for combinations &| or |&
    bad_combo = re.compile('&\|([&\|!]{1,})')
    raw_string = re.sub(bad_combo, '&', raw_string)
    print('Removing "&|" combination - {0}'.format(raw_string))

    bad_combo = re.compile('\|&([&\|!]{1,})')
    raw_string = re.sub(bad_combo, '|', raw_string)
    print('Removing "|&" combination - {0}'.format(raw_string))

    # Look for redundant operators other than parentheses
    allowed_punc = ['&', '!', '\|']

    for punc in allowed_punc:
        punc_sub = re.compile('{0}'.format(punc) + '{1,}')
        raw_string = re.sub(punc_sub, punc.replace('\\', ''), raw_string)

    # Look for mismatched ( and )
    open_parens = raw_string.count('(')
    close_parens = raw_string.count(')')

    if open_parens != close_parens:
        print('{0} - {1}'.format(open_parens, close_parens))
        # strip out all parentheses instead of trying to figure out matching
        raw_string = raw_string.replace('(', '').replace(')', '')

    print(raw_string)
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

    #return lore_search