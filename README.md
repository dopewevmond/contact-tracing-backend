# Contact Tracing App
### Rest API backend for a Contact Tracing App built with Flask and Flask-Restful

Prerequisites:
- Must have Python 3 and pip installed on your computer
- Must be familiar with command line/terminal

To get started (on Windows),
- Create a virtual environment with `virtualenv <name-of-virtual-environment`. If you don't have virtualenv installed, you can install it by running `pip install virtualenv` in a terminal.
- On Windows and in the root directory of this project, run `.\<name-of-virtual-environment>\Scripts\activate` to activate the virtual environment. You should see `(<name-of-virtual-environment>)` in your terminal now.
- Run `pip install -r requirements.txt` to install all the dependencies for this project.
- Run `flask db upgrade` to create all the database tables for this project.
- Create a `.env` file in the root directory and add the following environment variables.
    - `FLASK_ENV=development`
    - `FLASK_APP=setup.py`
- Run `flask run` in a terminal to start the project.
- Happy coding!!!