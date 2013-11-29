votainteligente-portal-electoral
================================

[![Build Status](https://travis-ci.org/ciudadanointeligente/votainteligente-portal-electoral.png?branch=master)](https://travis-ci.org/ciudadanointeligente/votainteligente-portal-electoral)
[![Coverage Status](https://coveralls.io/repos/ciudadanointeligente/votainteligente-portal-electoral/badge.png?branch=master)](https://coveralls.io/r/ciudadanointeligente/votainteligente-portal-electoral?branch=master)

Votainteligente the electoral platform that Fundación Ciudadano Inteligente uses to transparent the electoral positions of different candidates to an election.

#Installation

VotaInteligente depends on 3 parts candideit.org, popit and write-it. You might choose to use all of them or just part. In the following document it is described how to install.

## Assumptions

This guide was made using an ubuntu 13.10 just installed.

## Requirements

Before the installation process is started a number of requirements is needed

- [virtualenv](https://pypi.python.org/pypi/virtualenv)
- [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)
- [Git](http://git-scm.com/)
- The requirements that [sorl-thumbnail has](http://sorl-thumbnail.readthedocs.org/en/latest/requirements.html)

## Installation process

* Clone votainteligente somewhere in your system.

`git clone https://github.com/ciudadanointeligente/votainteligente-portal-electoral.git`

Enter the installation directory

`cd votainteligente-portal-electoral`

* Create a virtual environment

`mkvirtualenv votainteligente`

Here you can optionally give the command the full path to the installation directory by adding -a <full_path>.
* If you didn't use the -a option you'll have to cd into the directory.

`cd votainteligente-portal-electoral`

* Install the requirements that votainteligente needs in the current virtualenvironment

`pip install -r requirements.txt`

It might take some time to get all installed

* Create the database and tables.

`python manage.py syncdb`

Update the tables with migrations

`python manage.py migrate`

## Bringing elections from candideit.org

Elections in VotaInteligente have a one-to-one relation with elections in candideit.org, so for your installation you'll first need to create an election in [candideit.org](http://candideit.org) and follow the next steps.

Specifically for this installation we are not using popit (But we'll soon be doing so).

* Create the file votainteligente/local_settings.py with the following content.

```
USE_POPIT = False

CANDIDEITORG_URL = http://candideit.org/api/v2/'

CANDIDEITORG_USERNAME = 'YOUR-CANDIDEITORG-USERNAME'

CANDIDEITORG_API_KEY = 'YOUR-CANDIDEITORG-APIKEY'

```

* Getting your elections from candideit.org into your installation.

You need to run the following command

`python manage.py update_from_candidator`

* Running VotaInteligente

`python manage.py runserver`

And hit http://localhost:8000/.

## Theming

### Previously created themes

* [votainteligente-venezuela-theme](https://github.com/ciudadanointeligente/votainteligente-venezuela-theme) is the theme for [eligetucandidato.org](http://eligetucandidato.org/)

### Creating your own custom theme

If you want to create a new theme you have to create a directory containing two different subdirectories templates and static, and copy the templates that you want to replace.

And in your project in your local_settings.py file you have to add the following

```
 STATICFILES_DIRS = (
     '/full/path/to/your/theme/static/',
 )
 TEMPLATE_DIRS = (
     '/full/path/to/your/theme/templates/',
 )
```

## Localization

If you want to help us translate votainteligente please join our project in [poeditor.com](https://poeditor.com/join/project?hash=6a3a384490bd4d69669db94c1cc22d78)

## Licensing

VotaInteligente is free and released as open source software covered by the terms of the [GNU Public License](http://www.gnu.org/licenses/gpl-3.0.html) (GPL v3)