# pyLoreBot
Simple Discord bot that allows Discord users to search Destiny 1 grimoire cards and Destiny 2 lore.

The project builds off the [destiny-manifest-manager](https://github.com/dad2cl3/destiny-manifest-manager) repository.

The lore search can be initiated in Discord by typing the command !lore.

The backend is also written such that a web application can search the data through the same API that is used from within the Discord bot.

**Search Capabilities**

Right now, the search is performed within the PostgreSQL database using built-in full-text search functionality. The bot supports searching based on all words provided.

For example:

    !lore whisper of the worm produces 'whisper & of & the & worm'

Also, the bot supports search keywords "AND", "NOT", and "OR" along with their corresponding operators "&", "!", and "|". "OR" or "|" and "NOT" or !, and operator precedence using parentheses.

For example:

    !lore ikora and (eris or asher) produces 'ikora&(eris|asher)'
    !lore ikora & (eris | asher) also produces 'ikora&(eris|asher)'

The bot also scrubs the search string using the following rules

    1. Remove leading/trailing spaces
    2. Remove punctuation "#$%'*+,-./:;<=>?@[\]^_`{}~
    3. Remove closing and opening parentheses that are touching or only separated by whitespace
    4. Remove redundant spaces
    5. Replace the words "and", "not", and "or" with operators "&", "!", and "|", respectively
    6. Replace single space between words with "&"
    7. Replace single space around operators "&", "!", and "|" with the operator itself
    8. Replace NOT operator "!" not preceded by AND operator "&" or OR operator "|" with "&!"
    9. Replace illegal operator combinations "&|" and "|&" with "&" and "|", respectively
    10. Replace redundant operators other than parentheses with single operator
    11. Remove all parentheses if number of opening and closing parentheses doesn't match

Discord limits the length of messages to 6000 characters. As a result, the bot will not return a response for results that exceed the limit. A future release will address the limitation.

Discord also limits the amount of text within a field in a RichEmbed to 1024 characters. Results that exceed the limit will be broken into separate fields within the Discord message. 

A normal response in Discord will appears as follows:

![alt text](https://github.com/dad2cl3/pyLoreBot/blob/master/doc/normalresponse.png "Normal Response")

An empty response in Discord will appear as follows:

![alt text](https://github.com/dad2cl3/pyLoreBot/blob/master/doc/emptyresponse.png "Empty Response")