# SUI v1.3 - The Scratch Username Index API

Simple Indexer API for Scratch Usernames! This API can be used to find usernames from their IDs.

## Currently, SUI has indexed 1.4M+ (1.4 Million) users!

![https://sui.sid72020123.repl.co/status/](https://img.shields.io/badge/dynamic/json?color=blue&label=Total%20Users%20Indexed&query=%24.TotalUsers&url=https%3A%2F%2Fsui.sid72020123.repl.co%2Fstatus%2F)

## Documentation

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

### All Data
The all data endpoint is removed because the people may spam it and make the server unresponsive.
You can still download the data from ```data``` folder in this repository!

### Note for Scratch Team
If the SUI API is spamming the Scratch API then I will discontinue running it or reduce the number of requests made. Currently, it makes 1 request per 1 second.

### Thank You!
