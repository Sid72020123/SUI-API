# SUI - The Scratch Username Index API

Simple Indexer API for Scratch Usernames! This API can be used to find usernames from their IDs.

## Currently, SUI has indexed 1.4M+ (1.4 Million) users!

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

### All Data
The all data endpoint is removed because the people may spam it and make the server unresponsive.

### Note for Scratch Team
If the SUI API is spamming the Scratch API then I will discontinue running it or reduce the number of requests made. Currently, it makes 1 request per 1 second.

### Thank You!
