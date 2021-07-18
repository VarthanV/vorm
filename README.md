[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />

  <h3 align="center">vorm</h3>

  <p align="center">
    A toy ORM written in python
    <br />
    <!-- <a href="https://github.com/Varthan/vorm"><strong>Explore the docs »</strong></a> -->
    <br />
    <br />
    <!-- <a href="https://github.com/VarthanV/vorm">View Demo</a>
    · -->
    <a href="https://github.com/VarthanV/vorm/issues">Bug</a>
    ·
    <a href="https://github.com/VarthanV/vorm/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
            <li><a href="#commonly-faced-errors">Commonly faced errors</a></li>
      </ul>
    </li>
    <li><a href="#usage-and-examples">Usage and Examples</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

vorm is a toy ORM written in Python , I started it as a fun hobby project to know how ORM's work internally and to better understand it and use it efficiently in my day to day work /projects .Currently vorm supports MYSQL and PostgreSQL DB engines . Feel free to add support to other DB's as well.

Thanks for stopping here (:

### Built With

- [Python](https://www.python.org/)
- [MYSQL](https://www.mysql.com/)
- [PostgreSQL](postgresql.org)

<!-- GETTING STARTED -->

## Getting Started

## Installation

Install the package from Github

```sh
git clone  https://github.com/VarthanV/vorm.git
cd vorm
python setup.py install
```

### Commonly faced errors
If you find mysql is missing or psycopg2 is missing you can install it manually and it will work

```sh
pip install mysql-connector-python
pip install psycopg2-binary
```
<!-- USAGE EXAMPLES -->

## Usage and Examples

vorm has similiar syntax to other popular ORM's like Djang ORM and SQLalchemy , If you have familiarity with these libraries already it will not take much time for you to adopt to its syntax

## Connecting to database

We need to create a connection to a database , Currently vorm supports **PostgreSQL** and **MYSQL**

```python
from vorm.manager import ConnectionManager as db

db_settings = {
    "driver": "postgresql",
    "user": "root",
    "password": "astrongpassword",
    "host": "localhost",
    "port": 5432,
    "database": "students",
}

db.create_connection(db_settings)

```

## Creating a model class

- Each model class in vorm inherits the **Base Model** class.

- Each attribute of the model represents a field in your database.

```python
from vorm import base
from vorm import fields

class Person(base.BaseModel):

    table_name = 'person'

    first_name = fields.CharField(max_length=30)
    last_name = fields.CharField(max_length=30)
    age = fields.IntegerField(default=15)

```

`table_name` is a required attribute, Your table will be named in the database.

The above model class would create a table like this

```postgresql
CREATE TABLE person (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(30) NOT NULL,
    "last_name" VARCHAR(30) NOT NULL ,
    "age"  int DEFAULT 15 NOT NULL,
);
```

## Migration

After you define the model class ,you need to create your defined class as a table in the connected database.

```python
db.migrate(Person)
```

When this piece of code runs , The `person` table will be created in the connected database.

<!-- ROADMAP -->

## Inserting into a table

```python
person_1 = Person.objects.insert(first_name="Walter",last_name="White",age=50)

print(f"The persons name is {person.first_name} {person.last_name}")

"Walter White"
```

## Querying from a table

```python
# Get all the persons whose age is greater than 30

persons = Person.objects.where(age__gt =30)

print(len(persons))
```

The where method always returns a list of `model_class` , If no results are found it returns an empty array

## Updating a row in the table

```python
# Updates the row with the id 1 and returns the updated value

updated_person = Person.objects.update(new_data={"first_name":"Vishnu"},id=1)

print(updated_person.first_name)

"Vishnu"
```

### Deleting a row from the table

```python

# Deletes the person with the id 1

Person.objects.delete(id=1)
```

## Foreign key

```python
class Membership(base.BaseModel) :
    name = fields.CharField(max_length=100)
    person = fields.ForeignKey(Person)

person  = Person.objects.where(id=2)

membership = Person.objects.insert(name="Test membership" , person=person)

print(membership.person)  # Returns a list of the person object

```

## Roadmap

See the [open issues](https://github.com/VarthanV/vorm/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->

## Contact

Vishnu Varthan - [Twitter](https://twitter.com/vichuvb) - vishnulatha006@gmail.com

Project Link: [https://github.com/VarthanV/vorm](https://github.com/VarthanV/vorm)

<!-- ACKNOWLEDGEMENTS -->

## Acknowledgements

These repositories gave me a base idea of how a orm must be

- [Django ORM](https://github.com/django/django)
- [yann-orm](https://github.com/yannickkiki/yann-orm)
- [orm](https://github.com/gtback/orm)

## What's next 🚀 ?

- Adding support for more DB engines.
- Admin panel (Inspired by Django).
- Adding more testcases.
- SQL to vorm style code generator (CLI Tool).

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/VarthanV/vorm.svg?style=for-the-badge
[contributors-url]: https://github.com/VarthanV/vorm/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/VarthanV/vorm.svg?style=for-the-badge
[forks-url]: https://github.com/VarthanV/vorm/network/members
[stars-shield]: https://img.shields.io/github/stars/VarthanV/vorm.svg?style=for-the-badge
[stars-url]: https://github.com/VarthanV/vorm/stargazers
[issues-shield]: https://img.shields.io/github/issues/VarthanV/vorm.svg?style=for-the-badge
[issues-url]: https://github.com/VarthanV/vorm/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/vishnu-varthan-765345175/
