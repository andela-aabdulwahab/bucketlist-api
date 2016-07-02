[![Build Status](https://travis-ci.org/andela-aabdulwahab/bucketlist-api.svg?branch=develop)](https://travis-ci.org/andela-aabdulwahab/bucketlist-api)
[![Coverage Status](https://coveralls.io/repos/github/andela-aabdulwahab/bucketlist-api/badge.svg?branch=develop)](https://coveralls.io/github/andela-aabdulwahab/bucketlist-api?branch=develop)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/andela-aabdulwahab/bucketlist-api/badges/quality-score.png?b=develop)](https://scrutinizer-ci.com/g/andela-aabdulwahab/bucketlist-api/?branch=develop)
## Bucketlist Application API
Application for managing bucketlist, with API as interface

### Introduction

Bucketlist Application API is an application for creating and managing a bucketlist, with available API to perform the actions. Built with [flask-restful](http://flask-restful-cn.readthedocs.io/en/0.3.4/), it implements token Based Authentication for the API and only methods to register and login are accessible to unauthenticated users. Data is exchanged as JSON.

Access control mapping is listed below.

<table>
 <tr>
 <th> Functionality </th>
 <th> Endpoint</th>
 <th> Public Access</th>
 </tr>
 <tr>
 <td>Logs a user in</td>
 <td>POST /v1/auth/login</td>
 <td>True</td>
 </tr>
 <tr>
  <td>Register a user</td>
  <td>POST /v1/auth/register</td>
  <td> True</td>
 </tr>

 <tr>
 <td>Create a new bucket list</td>
 <td>POST /v1/bucketlists/ </td>
 <td>False</td>
 </tr>

 <tr>
 <td>List all the created bucket lists</td>
 <td>GET /v1/bucketlists/ </td>
 <td>False</td>
 </tr>

 <tr>
 <td>Get single bucket list</td>
 <td>GET /v1/bucketlists/&lt;id&gt; </td>
 <td>False</td>
 </tr>

 <tr>
 <td>Update vthis bucket list</td>
 <td>PUT /v1/bucketlists/&lt;id&gt; </td>
 <td>False</td>
 </tr>

 <tr>
 <td>Delete this single bucket list</td>
 <td>DELETE /v1/bucketlists/&lt;id&gt; </td>
 <td>False</td>
 </tr>

 <tr>
 <td>Create new item in this bucket list</td>
 <td>POST /v1/bucketlists/&lt;id&gt;/items </td>
 <td>False</td>
 </tr>

 <tr>
 <td>Update a bucketlist item </td>
 <td>PUT /v1/bucketlists/&lt;id&gt;/items/&lt;item_id&gt; </td>
 <td>False</td>
 </tr>

 <tr>
 <td>Delete this item in this bucket list</td>
 <td>DELETE /v1/bucketlists/&lt;id&gt;/items/&lt;item_id&gt; </td>
 <td>False</td>
 </tr>
 </table>

### Set up

 Application works for both Python 2.7 and 3.*

 ```sh
$ git clone git@github.com:andela-aabdulwahab/bucketlist-api.git
$ cd bucketlist_api
$ pip install -r requirements
 ```

### Installation

* Make migrations by running the following commands.<br>
      - `python manage.py db create_db` to create the database  for the app.
      - `python manage.py db migrate` to create necessary tables in the database.
      - `python manage.py db upgrade` to apply migrated changes
* Run ```python runserver.py``` to get the app running

### Running Tests
Run ```python manage.py test``` to run test and check coverage
