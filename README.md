# Contact Tracing App
A Rest API backend for a Contact Tracing App built with Flask and Flask-Restful

#### Prerequisites:
- Must have Python 3 and pip installed on your computer
- Must be familiar with command line/terminal

#### To get started
- Create a virtual environment with `virtualenv <name-of-virtual-environment`. If you don't have virtualenv installed, you can install it by running `pip install virtualenv` in a terminal.
- On Windows and in the root directory of this project, run `.\<name-of-virtual-environment>\Scripts\activate` to activate the virtual environment. You should see `(<name-of-virtual-environment>)` in your terminal now.
- Run `pip install -r requirements.txt` to install all the dependencies for this project.
- Run `flask db upgrade` to create all the database tables for this project.
- Install Elasticsearch on your local machine. [Download here](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html). You can skip this step if you're using an online/hosted installation such as those on GCP, AWS or Azure.
- This project uses the Gmail SMTP server for its email functionality. By default, Google prevents signing in from other apps. To configure your Gmail account to work with this Contact Tracing App (act as the sending Gmail address), check out this [link](https://support.google.com/accounts/answer/185833) to set up an App Password. This App Password will be set as an environment variable which the Contact Tracing App will use to Sign In.
- Create a `.env` file in the root directory and add the following environment variables.
    - `FLASK_ENV=development`
    - `FLASK_APP=setup.py`
    - `ELASTICSEARCH_URL=<elastic-search-url>`
    - `AWS_S3_BUCKET_NAME=<url-for-your-aws-bucket>`
    - `MAIL_USERNAME=<your-email-address>`
    - `MAIL_PASSWORD=<the-app-password-you-created>`

- Start your Elasticsearch server (for local installations) and make sure you have specified its url in the `ELASTICSEARCH_URL` variable in the `.env` file.
- Make sure you have correctly configured AWS cli.
- Run `flask run` in a terminal to start the project.

#### Contributing
Open to suggestions and extension of the code. To contribute
- Fork this repository
- Create a new branch
- Commit changes
- Push to the branch
- Create pull request

#### Running tests
- Open a terminal or PowerShell window
- In the root directory of this project, run `.\<name-of-virtual-environment>\Scripts\activate` to activate the virtual environment.
- Run `python -m unittest discover` to run the tests.
