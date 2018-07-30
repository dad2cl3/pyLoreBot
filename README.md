# pyLoreBot
Simple Discord bot that allows Discord users to search Destiny 1 grimoire cards and Destiny 2 lore.

The project builds off the [destiny-manifest-manager](https://github.com/dad2cl3/destiny-manifest-manager) repository.

The lore search can be initiated in Discord by typing the command !lore.

The backend is also written such that a web application can also search the data through the same API that is used from within the Discord bot.

Right now, the search is performed within the PostgreSQL database using built-in full-text search functionality. The bot only supports searching based on all words provided.