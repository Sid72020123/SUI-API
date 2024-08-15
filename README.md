# SUI v5.0 - The Scratch Username Index API

Indexer API for the user accounts on [Scratch](https://scratch.mit.edu/)!

This API can be used to find usernames from their IDs., get a random user, etc.

**Note: This API is slow at indexing and not all the users on Scratch have been indexed yet. This is due to limitations of the [official Scratch API](https://api.scratch.mit.edu/) which allows a maximum of 10 requests per 1 second and the limitations of the hosting provider**

**Currently, SUI has indexed over 9.0M+ (9.0 Million) users!**

![https://sui.scratchconnect.eu.org/status/](https://img.shields.io/badge/dynamic/json?color=blue&label=Total%20Users%20Indexed&query=%24.TotalUsersData.Count&url=https%3A%2F%2Fsui.scratchconnect.eu.org%2Fstatus%2F)

## Documentation

**Interactive documentation can be found at: https://sui.scratchconnect.eu.org/docs**

## Indexing Methods/Types

1. **Username Indexer**: This Indexer indexes the first 40 followers and following of all the followers of the first 100 most popular users on Scratch
2. **Studio Members Indexer**: This Indexer indexes the host, members and curators (and their first 40 following and followers) of the studios on Scratch
3. **Project Creator Indexer**: This Indexer indexes the creators (and their first 40 following and followers) of projects on Scratch starting from project ID 104
4. **Short Usernames Indexer**: This Indexer indexes the pre-generated 3-letter short usernames (and their first 40 followers and following) on Scratch
5. **Forum Post User Indexer**: This Indexer indexes the usernames from forum posts in the Scratch Forums. Because ScratchDB went down recently, this also stores the forum post data in an external database
6. **Cloud Game Username Indexer**: This Indexer indexes the usernames from the cloud data of some selected (popular cloud projects) projects pre-added to the Scratch studio: 34001844
7. **User Comments Author Indexer**: This Indexer indexes the users from top 5 comments on top 5 popular Scratch users' profiles
8. **Front Paged Project Creator Indexer**: This Indexer indexes the creators of the front-paged projects on Scratch's front page

**Out of the above indexing methods, only the `1`st, `2`nd and `3`rd indexers are primary indexers which contribute a lot to the API while the others were added just to get more and unique usernames**

## Drawbacks

1. The indexing is very slow and takes time
2. Not all the users on Scratch are indexed
3. Although this API can update the data of a frequently occurring user, some of the data stored in the server can be out-dated and this API may show the ID and username of those accounts which are deleted on Scratch

## Endpoints

### Root

URL: `GET https://sui.scratchconnect.eu.org/`

### Status

This endpoint will give the status and other information about the server like the total number of users indexed, the index or the famous user the API is currently indexing, etc.

URL: `GET https://sui.scratchconnect.eu.org/status/`

### Get ID (from username)

**Note: Use the Scratch API to get the ID of a user. Some user's data may not have been indexed… This endpoint was made just for testing…**

Now using this endpoint you can also be able to index a user, his/her following and followers! Just give the username and the “Indexing” status will be shown! This process usually takes some time.

URL: `GET https://sui.scratchconnect.eu.org/get_id/:username`

Example: https://sui.scratchconnect.eu.org/get_id/griffpatch

### Get User (from ID)

Use this endpoint to get the username of the Scratch user from a ID

URL: `GET https://sui.scratchconnect.eu.org/get_user/:id`

Example: https://sui.scratchconnect.eu.org/get_user/1882674

### Get Random Data

Get the random indexed data

URL: `https://sui.scratchconnect.eu.org/random/`

### Get Data

Use this endpoint to get the data stored in the DB

E.g. https://sui.scratchconnect.eu.org/get_data/?limit=100&offset=0

The `limit` parameter states the number of indexed data you want (max limit of 10K) and the `offset` parameter states the number of data you want to skip from the beginning. This is similar as used in the Scratch API.

## Additional Endpoints

This are some extra side-API endpoints which may/may not be useful and the maintainer can't guarantee the proper working of the endpoints:

### Search Posts

_As the ScratchDB API went down recently, I made the Forum Indexer Thread (which indexes the usernames of the people who posted in the forums) to store the post data in an external DataBase to create a simple alternative. You can use this endpoint to search for forum posts but I can't guarantee that it will always work..._

URL: `https://sui.scratchconnect.eu.org/post_search/?q=<search term>&limit=10&offset=0`

Replace the `<search term>` in the above URL with your query string. The max `limit` is 100. To get results more than 100, use the `offset` parameter.

## Libraries and Frameworks Used

**Programming Language**: _Python 3.10_
**Web framework for API**: _FastAPI_
**DataBase**: _MySQL_
**DataBase for Forum Posts**: _PostgreSQL_

Other requirements are in the `src/requirements.txt` file

## Development

Steps to run your own instance:

1. Download the source code or clone the repo in your local computer.
2. Open the `src` directory and make an `.env` file like the example file: `.env.example`. Make sure to put the correct details in the environment file. You can also edit the `Congig.py` file to make some more changes.
3. Deploy the external (not necessary) API to https://deta.space for saving history and to receive weekly updates from the directory: `sui-deta-backend`.
4. Make sure you have Python (atleast version 3.10 installed). Install the dependencies from `requirements.txt` file.
5. Run the `main.py` file using `python3 main.py`.

**Note: You can also edit the source code of the indexers to change the way the data is collected. Further, you can also stop some un-necessary thread loops like sending hourly updates, saving status history, etc. by changing some parts of the source code.**

## Screenshots

### Internal Logs

![Image](https://u.cubeupload.com/Sid72020123/Screenshotfrom202408.png)

![Image](https://u.cubeupload.com/Sid72020123/424Screenshotfrom202408.png)

### Hourly Status updates on Telegram

![Image](https://u.cubeupload.com/Sid72020123/IMG20240815135755.jpg)

### Daily Upserts Growth updates on Telegram

![Image](https://u.cubeupload.com/Sid72020123/IMG20240815135822.jpg)

![Image](https://u.cubeupload.com/Sid72020123/IMG20240815135430766.jpg)

![Image](https://u.cubeupload.com/Sid72020123/IMG20240815135433713.jpg)

### Weekly Status updates on Telegram

![Image](https://u.cubeupload.com/Sid72020123/IMG20240815135847.jpg)

## A big thanks to

1. **The Scratch Team** for the [Scratch API](https://api.scratch.mit.edu/)
2. **[@DatOneLefty on Scratch](https://scratch.mit.edu/users/DatOneLefty/)** from the [Scratch DB API](https://scratchdb.lefty.one/) (used to fetch 100 most followed users on Scratch) _As of August 2024, ScratchDB is down for an indefinite period and the API still uses the cached data received from the API a few months back..._

## Note for the Scratch Team

**If the SUI API is spamming the Scratch API then I will discontinue running it or reduce the number of requests made. Just comment me on my Scratch Profile (Account: @Sid72020123) or open an issue on Github. Currently, it makes 3-4 requests per 1 second**

### Thank You!

**Project created and maintained by [@Sid72020123 on Scratch](https://scratch.mit.edu/users/Sid72020123/)**
