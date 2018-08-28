# pyLoreBot
Simple Discord bot that allows Discord users to search Destiny 1 grimoire cards and Destiny 2 lore written in Python.

The project builds off the [destiny-manifest-manager](https://github.com/dad2cl3/destiny-manifest-manager) repository.

The lore search can be initiated in Discord by typing the command "!lore".

Web applications can also leverage the API backend minus the Discord bot initiator "!lore".

### Backend
The search functionality is supported by an AWS Lambda function written in Python sitting behind AWS API Gateway. The manifest data is stored in PostgreSQL.

    Bot <-> AWS API Gateway <-> AWS Lambda <-> PostgreSQL

### Search Capabilities

Right now, the search is performed within the PostgreSQL database using native [full-text search functionality](https://www.postgresql.org/docs/current/static/textsearch.html). The bot supports searching based on all words provided and the default behavior for the bot is to replace uninterrupted whitespace between words with the *AND* operator "&".

For example:

    !lore whisper of the worm produces 'whisper & of & the & worm'

The bot supports search keywords "AND", "NOT", and "OR" along with their corresponding operators "&", "!", and "|". Operator precedence using parentheses is also supported.

For example:

    !lore ikora and (eris or asher) produces 'ikora&(eris|asher)'
    !lore ikora & (eris | asher) also produces 'ikora&(eris|asher)'

The bot scrubs the search string using the following rules

    1. Remove leading/trailing spaces
        Example: " eris " becomes "eris"
        
    2. Remove punctuation "#$%'*+,-./:;<=>?@[\]^_`{}~
        Example: "</eris>" becomes "eris"
        
    3. Remove closing and opening parentheses that are touching or only separated by whitespace
        Example: "(eris and ikora) (cayde and zavala)" becomes "eris&ikora&cayde&zavala"
        
    4. Remove redundant spaces
        Example: "eris  morn" becomes "eris morn"
        
    5. Replace the words "and", "not", and "or" with operators "&", "!", and "|", respectively
        Example: "eris and morn" becomes "eris & morn"
        
    6. Replace single space between words with "&"
        Example "eris morn" becomes "eris & morn"
        
    7. Replace single space around operators "&", "!", and "|" with the operator itself
        Example "asher & ! ikora" becomes "asher&!ikora"
        
    8. Replace NOT operator "!" not preceded by AND operator "&" or OR operator "|" with "&!"
        Example: "eris and ikora not zavala" becomes "eris&ikora&!zavala"
        
    9. Replace illegal operator combinations "&|" and "|&" with "&" and "|", respectively
        Example: "eris and or ikora" becomes "eris&ikora"
        Example: "eris or and ikora" becomes "eris|ikora"
        
    10. Replace redundant operators other than parentheses with single operator
        Example: "&&&&" becomes "&"
        
    11. Remove all parentheses if number of opening and closing parentheses doesn't match
        Example: "(eris and ikora" becomes "eris&ikora"

# Database Search
### Grimoire
Lore in the original Destiny game was mostly contained within grimoire cards and available within the Destiny manifest. Grimoire cards in the manifest are comprised of three key fields: *cardName*, *cardIntro*, and *cardDescription*. The three fields, along with a single space separator, are concatenated together prior to creating the lexemes.

```postgresql
    to_tsvector('english',
	  (json->>'cardName')::TEXT || ' ' ||
	  COALESCE((json->>'cardIntro')::TEXT, '') || ' ' ||
	  (json->>'cardDescription')::TEXT
	)
```

The *COALESCE* function is necessary because not all grimoire cards have a value for *cardIntro*.

### Lore
Grimoire cards were not brought forward to Destiny 2. Lore in Destiny 2 is mostly tied to inventory items that guardians can obtain within the game. Like grimoire cards, the lore is available within the Destiny 2 manifest. The lore is comprised of three key fields: *name*, *subtitle*, and *description*. As with grimoire, the three fields, along with a single space separator, are concatenated together prior to creating the lexemes.

```postgresql
  to_tsvector('english',
    (dld.json->'displayProperties'->>'description')::TEXT || ' ' ||
    (dld.json->>'subtitle')::TEXT || ' ' ||
    (dld.json->'displayProperties'->>'name')::TEXT
  )
```

### Database Function
The database function requires two parameters: *p_lore_type* and *p_lore_search*. *p_lore_type can be either "grimoire" or "inventory". *p_lore_search* contains the scrubbed search string. The database response utilizes the function *JSONB_BUILD_OBJECT* to return each row in the query as a JSON object. Lastly, all results are returned as a set of data type RECORD. Troubleshooting can be accomplished using the following SQL query:

```postgresql
SELECT * FROM manifest.fn_search_lore('grimoire', 'eris&morn') AS t1(lore_entry JSONB);
```

# Discord
### Scrubbing
The original Destiny manifest data for grimoire cards contain HTML markup that the bot scrubs. The lore data is being scrubbed inside the AWS Lambda function. The function reads the key-value pairs in the grimoire_cleanup.json file and loops through those key-value pairs to perform a simple string replacement.
### Limitations

Discord limits the length of messages to 6000 characters. As a result, the bot will not return a response for results that exceed the limit. A future release will address the limitation.

Discord also limits the amount of text within a field in a RichEmbed to 1024 characters. Results that exceed the limit will be broken into separate fields within the Discord message. 

### Responses

A normal response in Discord will appears as follows:

![alt text](https://github.com/dad2cl3/pyLoreBot/blob/master/doc/normalresponse.png "Normal Response")

An empty response in Discord will appear as follows:

![alt text](https://github.com/dad2cl3/pyLoreBot/blob/master/doc/emptyresponse.png "Empty Response")

