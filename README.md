# SUI v4.0 - The Scratch Username Index API

Indexer API for the user accounts on [Scratch](https://scratch.mit.edu/)!

This API can be used to find usernames from their IDs., get a random user, etc.

**Note: This API is slow at indexing and not all the users on Scratch have been indexed yet. This is due to limitations of the [official Scratch API](https://api.scratch.mit.edu/) which allows a maximum of 10 requests per 1 second and the limitations of the hosting provider**

**Currently, SUI has indexed over 6.0M+ (6.0 Million) users!**

![https://sui.scratchconnect.eu.org/status/](https://img.shields.io/badge/dynamic/json?color=blue&label=Total%20Users%20Indexed&query=%24.TotalUsersData.Count&url=https%3A%2F%2Fsui.scratchconnect.eu.org%2Fstatus%2F)

## Documentation

**Interactive documentation can be found at: https://sui.scratchconnect.eu.org/docs**

## Indexing Methods

1. **Following and Followers**: This method involves the indexing of all the followers of the top 100 most followed users on Scratch and the first 40 following and followers of the famous user's individual followers
2. **Studio Managers and Curators**: This method involves the indexing of first 40 managers and curators of the studios on Scratch
3. **Project Creator**: This method involves the indexing of the project creator and the first 40 following and followers of that creator
4. **Short Usernames**: This method involves the indexing of the short 3-letter usernames
5. **Forum Post Username**: This method involves the indexing of the person posting a post in the Scratch forums
6. **Cloud Game Usernames**: This method involves the indexing of the person playing some famous cloud-based games on Scratch by fetching the project's cloud data from the Scratch API. Only those project's cloud data is fetched which are popular on Scratch

**Out of the above indexing methods, only the ```1```st, ```2```nd and ```3```rd indexers are primary indexers which contribute a lot to the API while the others were added just to get more and unique usernames**

## Drawbacks

1. The indexing is very slow and takes time
2. Not all the users on Scratch are indexed
3. Although this API can update the data of a frequently occurring user, some of the data stored in the server can be out-dated

## Endpoints

### Root

URL: ```GET https://sui.scratchconnect.eu.org/```

### Status

This endpoint will give the status and other information about the server like the total number of users indexed, the index or the famous user the API is currently indexing, etc.

URL: ```GET https://sui.scratchconnect.eu.org/status/```

### Get ID (from username)
**Note: Use the Scratch API to get the ID of a user. Some user's data may not have been indexed… This endpoint was made just for testing…**

Now using this endpoint you can also be able to index a user, his/her following and followers! Just give the username and the “Indexing” status will be shown! This process usually takes a lot of time.

URL: ```GET https://sui.scratchconnect.eu.org/get_id/:username```

Example: https://sui.scratchconnect.eu.org/get_id/griffpatch

### Get User (from ID)

Use this endpoint to get the username of the Scratch user from a ID

URL: ```GET https://sui.scratchconnect.eu.org/get_user/:id```

Example: https://sui.scratchconnect.eu.org/get_user/1882674

### Get Random Data

Get the random indexed data

URL: ```https://sui.sid72020123.repl.co/random/```

### Get Data

To get the data, use the ```/get_data``` endpoint. 

E.g. https://sui.sid72020123.repl.co/get_data/?limit=100&offset=0

The ```limit``` parameter states the number of indexed data you want (max limit of 10K) and the ```offset``` parameter states the number of data you want to skip from the beginning. This is similar as used in the Scratch API.

## A big thanks to

1. **The Scratch Team** for the [Scratch API](https://api.scratch.mit.edu/)
2. **[@DatOneLefty on Scratch](https://scratch.mit.edu/users/DatOneLefty/)** from the [Scratch DB API](https://scratchdb.lefty.one/) (used to fetch 100 most followed users on Scratch)
3. **[MongoDB Atlas](https://www.mongodb.com/atlas/database)** for free cloud database
4. **[Deta Space](https://deta.space/)** for the amazing cloud service

## Note for the Scratch Team

**If the SUI API is spamming the Scratch API then I will discontinue running it or reduce the number of requests made. Just comment me on my Scratch Profile (Account: @Sid72020123) or open an issue on Github. Currently, it makes 3-4 requests per 1 second**

### Thank You!

**Project created and maintained by [@Sid72020123 on Scratch](https://scratch.mit.edu/users/Sid72020123/)**
