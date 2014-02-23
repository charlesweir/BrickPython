===========================
Introduction to BrickPython
===========================

I love the BrickPi.  It's a really powerful system, with the potential to do a lot.

This BrickPython package extends the BrickPi_python package to make it easier to program.  It introduces two things:
objects, and coroutines.

Why Objects
===========

Objects make programming easier.  Objects can be intelligent (for example, the Motor object can know its speed); they
can be easier to debug (Motor can print itself in a useful way); and they separate out concerns (you can deal with one
Motor at a time).

Why Coroutines?
===============

Creating programs to control things is difficult.  Several things can be happening at once, and the program
needs to be able to deal with all of them.

So, for example, if you had a little bot with two wheels each controlled by a motor, and with two sensors to
detect the direction, you'd want to continuously adjust the speed of each motor, look at both the sensors, and maybe
also react to keyboard input from the user.

But this makes programming rather hard.  One might want to have a nice simple function:
	runMotorAtConstantSpeedForTime( aSpeed, aTime )

But with normal Python programming model the program can only be executing one thing at a time.  So if it's executing
that function, all the other input (other motor, sensors, user) are being ignored.

Ouch!

There are two conventional approaches to this problem, both with disadvantages:

*   Event based programming: Whenever anything happens (a new motor position, a sensor change, a user keystroke etc),
	the framework makes a call into your program.   This is a very common idiom, but it's surprisingly hard to program:
	every function has to decide what to do based on the values of variables.  This leads to a style of programming called 'state
	machine programming'.  It's workable (I spent years using and teaching Syntropy, a methodology based on state machines).
	But it's not easy.

* 	Multithreading: Different activities in the program each gets their own 'thread'.  So in the example above, we might
	have a thread for each motor, each running a runMotorAtConstantSpeed function.  That gives a nicer structure to the
	program.  But there are appalling downside: communication between threads is tricky, and sharing variables or data
	between threads can be fraught with subtle and difficult-to-track down problems.

This framework uses a third option: Coroutines.   With a coroutine, you can write 'long running' functions, which
nevertheless allow other things to go on before they return.  This relies on the Python 'yield' statement, which
allows a function to go 'on hold' while other processing happens.

Strictly speaking, what this packages uses aren't true coroutines: a 'true' coroutine has its own stack, so
that if a coroutine function calls another function that calls 'yield', that would still work.
Python doesn't support that, but
we have ways around the problem.

The `Scheduler`
===============

To make our coroutines work, we need something that coordinates them, and manages the interaction with the BrickPi.  These are the classes `Scheduler` and its derived class `BrickPiWrapper`.

`Scheduler` handles coroutines, calling them regularly every 'work call' (50 times per second), and provides methods to manage them:
starting and stopping them, combining them, and supporting features such as timeouts for a coroutine.

`BrickPiWrapper` manages the BrickPi interaction, managing the `Motor` and `Sensor` objects, calling the BrickPi twice
for every work call (once before, and once after all the coroutines have run), taking data from and subsequently updating all
each `Motor` and `Sensor`.



Here's all that's required to make a motor move to a new position:


Here's what's required to create a RESTful API service from an existing database using
`sandman`::

    $ sandmanctl sqlite:////tmp/my_database.db

*That's it.* `sandman` will then do the following:

* connect to your database and introspect it's contents
* create and launch a REST API service
* create an HTML admin interface
* *open your browser to the admin interface*

That's right. Given a legacy database, `sandman` not only gives you a REST API,
it gives you a beautiful admin page and *opens your browser to the admin page*.
It truly does everything for you.

Supported Databases
-------------------

`sandman`, by default, supports connections to the same set of databases as
[SQLAlchemy](http://www.sqlalchemy.org). As of this writing, that includes:

* MySQL (MariaDB)
* PostgreSQL
* SQLite
* Oracle
* Microsoft SQL Server
* Firebird
* Drizzle
* Sybase
* IBM DB2
* SAP Sybase SQL Anywhere
* MonetDB

Behind the Scenes
-----------------

`sandmanctl` is really just a simple wrapper around the following::

    from sandman import app

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chinook'

    from sandman.model import activate

    activate()

    app.run()

**You don't even need to tell sandman what tables your database contains.**
Just point `sandman` at your database and let it do all the heavy lifting

Let's start our new service and make a request. While we're at it, lets make use
of `sandman`'s awesome filtering capability by specifying a filter term::

    $ python runserver.py &
    * Running on http://127.0.0.1:5000/

    > curl GET "http://localhost:5000/artists?Name=AC/DC"

and we get::

    {
        "resources": [
            {
                "ArtistId": 1,
                "Name": "AC/DC",
                "links": [
                    {
                        "rel": "self",
                        "uri": "/artists/1"
                    }
                ]
            }
        ]
    }

All of that, including filtering/searching, is automagically available from
those *five* measly lines of code.


We'll be using a subset of the Chinook test database as an example.
Create one file with the following contents (which I'll call ``runserver.py``)::

    from sandman import app, db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/jknupp/code/github_code/sandman/scripts/chinook'

    # The SQLALCHEMY_DATABASE_URI must be defined before your models.
    # Normally, this is done by importing your models, but here
    # we show them inline.

    from sandman.model import register, activate, Model

    class Artist(Model):
        __tablename__ = 'Artist'

    class Album(Model):
        __tablename__ = 'Album'

    class Playlist(Model):
        __tablename__ = 'Playlist'

    class Genre(Model):
        __tablename__ = 'Genre'

    # register can be called with an iterable or a single class
    register((Artist, Album, Playlist))
    register(Genre)
    # activate must be called *after* register
    activate()

    app.run()

Then simply run::

    python runserver.py

and try curling your new REST API service!

Of course, you don't actually need to tell sandman about your tables; it's
perfectly capable of introspecting all of them. To use introspection to make
*all* of your database tables available via the admin and REST API, simply
remove all model code and call `activate()` without ever registering a model.
To stop a browser window from automatically popping up on sandman
initialization, call `activate()` with `browser=False`.

A Quick Guide to REST APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~

Before we discuss the example code above in more detail, we should discuss some
REST API basics first. The most important concept is that of a *resource*.
Resources are sources of information, and the API is an interface to this information.
That is, resources are the actual "objects" manipulated by the API. In sandman, each
row in a database table is considered a resource.
Even though the example above is short, let's walk through it step by step.

Creating Models
---------------

A ``Model`` represents a table in your database. You control which tables to
expose in the API through the creation of classes which inherit from
:class:`sandman.model.models.Model`. The only attribute you must define in your
class is the ``__tablename__`` attribute. sandman uses this to map your
class to the corresponding database table. From there, sandman is able to divine
all other properties of your tables. Specifically, sandman creates the
following:

- an ``__endpoint__`` attribute that controls resource URIs for the class
- a ``__methods__`` attribute that determines the allowed HTTP methods for the class
- ``as_dict`` and ``from_dict`` methods that only operate on class attributes
  that correspond to database columns
- an ``update`` method that updates only the values specified (as opposed to
  ``from_dict``, which replaces all of the object's values with those passed in
  the dictionary parameter
- ``links``, ``primary_key``, and ``resource_uri`` methods that provide access
  to various attributes of the object derived from the underlying database model

Customizing Your Resources
------------------------------------------

Providing a custom endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the code above, we created 4 :class:`sandman.model.models.Model` classes that
correspond to tables in our database. If we wanted to change the endpoint for a
class (the default endpoint is simply the class's name pluralized), we would do
so by setting the ``__endpoint__`` attribute in the definition of the class::

    class Genre(Model):
        __tablename__ = 'Genre'
        __endpoint__ = 'styles'

Now we would point our browser (or ``curl``) to ``localhost:5000/styles`` to
retrieve the resources in the ``Genre`` table.

Restricting allowable methods on a resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many times, we'd like to specify that certain actions can only be carried out
against certain types of resources. If we wanted to prevent API users from
deleting any ``Genre`` resources, for example, we could specify this implicitly
by defining the ``__methods__`` attribute and leaving it out, like so::


    class Genre(Model):
        __tablename__ = 'Genre'
        __endpoint__ = 'styles'
        __methods__ = ('GET', 'POST', 'PATCH', 'PUT')

For each call into the API, the HTTP method used is validated against the
acceptable methods for that resource.

Performing custom validation on a resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifying which HTTP methods are acceptable gives rather coarse control over
how a user of the API can interact with our resources. For more granular
control, custom validation functions can be specified. To do so, simply define a
static method named ``validate_<METHOD>``, where ``<METHOD>`` is the HTTP method
the validation function should validate. To validate the ``POST`` method on
``Genres``, we would define the method ``validate_POST``, like so::


    class Genre(Model):
        __tablename__ = 'Genre'
        __endpoint__ = 'styles'
        __methods__ = ('GET', 'POST', 'PATCH', 'PUT')

        @staticmethod
        def validate_POST(self, resource=None):
            if isinstance(resource, list):
                return True

            # No classical music!
            return resource and resource.Name != 'classical'

The ``validate_POST`` method is called *after* the would-be resource is created,
trading a bit of performance for a simpler interface. Instead of needing to
inspect the incoming HTTP request directly, you can make validation decisions
based on the resource itself.

Note that the ``resource`` parameter can be either a single resource or a
collection of resources, so it's usually necessary to check which type you're
dealing with. This will likely change in a future version of sandman.

Project Layout
--------------

In a "real" project, you should divide the code into at least two files: one with the
``Model`` definitions (``models.py``) and the other with the configuration
and the ``app.run()`` call (``runserver.py``).
