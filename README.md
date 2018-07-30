# pyLoreBot
Simple Discord bot that allows Discord users to search Destiny 1 grimoire cards and Destiny 2 lore.

The project builds off the [destiny-manifest-manager](https://github.com/dad2cl3/destiny-manifest-manager) repository.

The lore search can be initiated in Discord by typing the command !lore.

The backend is also written such that a web application can also search the data through the same API that is used from within the Discord bot.

Right now, the search is performed within the PostgreSQL database using built-in full-text search functionality. The bot only supports searching based on all words provided.

Discord limits the length of messages to 6000 characters. As a result, the bot will not return a response for results that exceed the limit. A future release will address the limitation.

Discord also limits the amount of text within a field in a RichEmbed to 1024 characters. Results that exceed the limit will be broken into separate fields within the Discord message. 

A normal response will appears as follows:

![alt text](https://github.com/dad2cl3/pyLoreBot/blob/master/doc/normalresponse.png "Normal Response")

An empty response will appear as follows:

![alt text](https://github.com/dad2cl3/pyLoreBot/blob/master/doc/emptyresponse.png "Empty Response")