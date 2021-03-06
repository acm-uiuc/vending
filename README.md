
ACM Vending
===========

## About ##

The ACM Vending Interface was written as a Yahoo! HackU project in 2010 under
the name "Machine-Controlled, Generic, Expandable Interface for Vending and
Amusement Appliances" (McGeivaa). After losing the HackU competition, but
winning an unrelated prize (the added-at-the-last-minute "White Hat" award), the
API was renamed to something more appropriate and pronounceable and some things
were cleaned up to make it more accessible.

[http://acm.uiuc.edu/lug/vending/](http://acm.uiuc.edu/lug/vending/)

## Authors ##

ACM Vending was written by:

+ Kevin Lange <lange7@illinois.edu>
+ Sean Nicolay <nicolay2@illinois.edu>
+ Dylan Nugent <nugent5@illinois.edu>
+ Robby Schiele <schiele1@illinois.edu>

## Installation ##

ACM Vending requires PML, a GPLv2 Python HTML templating engine. We have not
provided this in the public release of ACM Vending as ACM Vending is released
under the NCSA License as a University of Illinois RSO project. Sorry.

You can get PML [here](http://codingrecipes.com/pml-a-python-template-engine).

### Application ###

As ACM Vending is an API, you will need to make an application out of it. A very
simple default setup looks like this:

    from vending import Db, Gui, Serial, Web, Vending
    class Caffeine(Vending.Vending):
    def start(self):
        Vending.Environment.tool = self
        self.serial = Serial.Serial()
        self.db = Db.MySQLBackend()
        self.web = Web.Server()
        self.gui = Gui.GraphicalInterface()
        Vending.Vending.start(self)
    Caffeine().start()

### Theme ###

You can redefine or extend the included modules as much as you want.
Additionally, you will also need a theme set:

    www/
        main.html
        gui/
            cancel.html
            cantafford.html
            confirm.html
            empty.html
            main.html
            user.html

Default examples of these are provided from the Caffeine project.

## Configuration ##

Beyond the application and theme level, you will need to configure your
application with a `machine.conf`. A sample machine.conf is provided under
`machine.conf.example`. `machine.conf` lists the operable settings for your
specific vending implementation, like the passwords for your databases and the
commands to send to the machine itself, and the responses to expect.

Note that we can't cover all possible configurations here. ACM Vending was
designed to work well with Caffeine, and uses its basic structure. If your
machine is significantly different in what it expects on its serial line,
you will need to edit `Serial.py` and possible `Vending.py`. If your database is
sufficiently different, you will most definitely need to modify `Db.py`.

The format for the config file is:

    option: value

... where `value` is in Python syntax. Note that this value is `eval`d, so
always make sure that your configuration is "safe".

## API ##

The ACM Vending API seeks to provide a concise, but expandable, library for
communicating with vending machines. The layout of the default library modules
looks like this:

    vending/
        Db.py             Database library (only MySQLBackend as of now)
        Gui.py            GUI library (only Qt with a web frontend)
        Serial.py         Serial interface (runs on a separate thread)
        Vending.py        The base class and logging
        Web.py            Web server (for GUI, web frontend, and initial telnet)

You are free to edit these library modules as much as you want, but we recommend
that you extend them as your own set of classes instead.
