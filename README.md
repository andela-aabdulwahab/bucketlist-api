[![Build Status](https://travis-ci.org/andela-aabdulwahab/bucketlist-api.svg?branch=develop)](https://travis-ci.org/andela-aabdulwahab/bucketlist-api)
[![Coverage Status](https://coveralls.io/repos/github/andela-aabdulwahab/bucketlist-api/badge.svg?branch=develop)](https://coveralls.io/github/andela-aabdulwahab/bucketlist-api?branch=develop)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/andela-aabdulwahab/bucketlist-api/badges/quality-score.png?b=develop)](https://scrutinizer-ci.com/g/andela-aabdulwahab/bucketlist-api/?branch=develop)
[![PyPI](https://img.shields.io/pypi/pyversions/Django.svg?maxAge=2592000)]()
## Bucketlist Application API
Application for managing bucketlist, with API as interface

### Introduction

Bucketlist Application API is an application for creating and managing a bucketlist, with available API to perform the actions. Built with [flask-restful](http://flask-restful-cn.readthedocs.io/en/0.3.4/), it implements token Based Authentication for the API and only methods to register and login are accessible to unauthenticated users. Data is exchanged as JSON.

### Set up

 Application works for both Python 2.7 and 3.*
```sh
 $ git clone git@github.com:andela-aabdulwahab/bucketlist-api.git
 $ cd bucketlist_api
 ```

After cloning, create a virtual environment and install the requirements. For Linux and Mac users:

 ```sh
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements
 ```
 If you are on Windows, then use the following commands instead:

 ```sh
$ virtualenv venv
$ venv\Scripts\activate
(venv) $ pip install -r requirements.txt
```

### Installation

* Make migrations by running the following commands.<br>
      - `python manage.py db init` to create the database  for the app.
      - `python manage.py db migrate` to create necessary tables in the database.
      - `python manage.py db upgrade` to apply migrated changes

### Running

      To run the server use the following command:
```python runserver.py``` to get the app running

### Running Tests
Run ```python manage.py test``` to run test and check coverage

### API Documentation

 ```sh
 $ POST /v1/auth/register
 ```
Register a new user.<br>
The body must contain a JSON object that defines `username` and `password` fields.<br>
On success a status code 201 is returned. The body of the response contains a JSON object with a valid token for the new user.<br>
On failure status code 400 (bad request) is returned.<br>

 ```sh
 $ POST /v1/auth/login
 ```
Login an existing user.<br>
The body must contain a JSON object that defines `username` and `password` fields.<br>
On successful login a status code 201 is returned. The body of the response contains a JSON object with a valid token for the user.<br>
On failure status code 401 (unauthorize) is returned.<br>

 ```sh
 $ GET /help/
 ```
Get help on API usage<br>
On success a status code 200 is returned. With the body of the response containing help message


> Basic Authentication required to access all API listed below. Or status code 401 (unauthorized) is returned.

 ```sh
 $ POST /v1/bucketlists/
 ```
Create a BucketList.<br>
The body must contain  a JSON object that defines `name` field and an optional `is_public` field.
On success a status code 200 is returned. The body of the response contains a JSON object with a link to the created bucket list endpoint
On failure status code 400 (bad request) is returned.<br>

 ```sh
 $ GET /v1/bucketlists/
 ```
Get all bucketlist of the User.<br>
On success a status code 200 is returned. The body of the response contains a JSON object containing the bucket lists
On failure status code 404 (Not found) is returned.<br>

 ```sh
 $ GET /v1/bucketlists/&lt;id&gt;
 ```
Get a specific bucketlist.<br>
On success a status code 200 is returned. The body of the response contains a JSON object containing the bucket list
On failure status code 404 (Not found) is returned.<br>

 ```sh
 $ PUT /v1/bucketlists/&lt;id&gt;
 ```
Update the bucket list specified.<br>
The body must contain  a JSON object that defines the field(s) to be modified.
On success a status code 201 is returned. On failure status code 404 (Not found) is returned.<br>

 ```sh
 $ DELETE /bucketlists/&lt;id&gt;
 ```
Delete the specified bucket list.<br>
On success a status code 201 is returned. On failure status code 404 (Not found) is returned.<br>

 ```sh
 $ POST /bucketlists/&lt;id&gt;/items/
 ```
Create an item in a Bucket list.<br>
The body must contain  a JSON object that defines `name` field and an optional `done` field.
On success a status code 200 is returned. The body of the response contains a JSON object with a link to the created bucket list endpoint
On failure status code 400 (bad request) is returned.<br>

 ```sh
 - PUT /bucketlists/&lt;id&gt;/items/&lt;item_id&gt;
 ```
Update the specified item in the bucketlist<br>
The body must contain  a JSON object that defines the field(s) to be modified.
On success a status code 201 is returned. On failure status code 404 (Not found) is returned or 401(unauthorize) if bucketlist doesn't belong to the user.<br>

 ```sh
 - DELETE /bucketlists/&lt;id&gt;/items/&lt;item_id&gt;
 ```
Delete the specified item in the bucket list.<br>
On success a status code 201 is returned. On failure status code 404 (Not found) is returned or 401(unauthorize) if bucketlist doesn't belong to the user.<br>
