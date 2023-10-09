# NEW VERSION STILL WIP... (VERY SLOW DEVELOPMENT)

# SUI v2.6 - The Scratch Username Index API

Simple Indexer API for Scratch Usernames! This API can be used to find usernames from their IDs.

## Currently, SUI has indexed 3.0M+ (3.0 Million) users!

![https://sui.sid72020123.repl.co/status/](https://img.shields.io/badge/dynamic/json?color=blue&label=Total%20Users%20Indexed&query=%24.TotalUsersData.Count&url=https%3A%2F%2Fsui.scratchconnect.eu.org%2Fstatus%2F)

## Documentation

Interactive documentation can be found at: https://sui.sid72020123.repl.co/docs

### Root

URL: ```GET https://sui.sid72020123.repl.co/```

### Status

This endpoint will give the status and other information about the server like the total number of users indexed, etc.

URL: ```GET https://sui.sid72020123.repl.co/status/```

### Get ID (from username)
**Note: Use the Scratch API to get the ID of a user. Some user's data may not have been indexed… This endpoint was made just for testing…**

Now using this endpoint you can also be able to index a user, his/her following and followers! Just give the username and the “Indexing” status will be shown!

URL: ```GET https://sui.sid72020123.repl.co/get_id/:username```

Example: https://sui.sid72020123.repl.co/get_id/griffpatch

### Get User (from ID)

URL: ```GET https://sui.sid72020123.repl.co/get_user/:id```

Example: https://sui.sid72020123.repl.co/get_user/1882674

### Get Random Data
Get the random indexed data
URL: ```https://sui.sid72020123.repl.co/random/```

### Get Data
To get the data, use the ```/get_data``` endpoint. Eg. https://sui.sid72020123.repl.co/get_data/?limit=100&offset=0

The ```limit``` parameter states the number of indexed data you want (max limit of 10K) and the ```offset``` parameter states the number of data you want to skip from the beginning. This is similar as used in the Scratch API.

### Note for Scratch Team
If the SUI API is spamming the Scratch API then I will discontinue running it or reduce the number of requests made. Currently, it makes 3-4 requests per 1 second.

### Thank You!
