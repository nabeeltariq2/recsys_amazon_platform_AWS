
# recsys_amazon
## A recommender systems platform for running online user experiments. Key features and integrations are as follows:

## Features
The base platform is based in Flask-Python. MYSQL integrations are handled through SQLAlchemy.
The algorithms are sourced from the surprise library(). Metrics available in MYSQL database.
Bootstrap template is used for rendering html pages
The Facebook Planout platform is used to randomize algorithm runs for each instance(). Metrics available in MYSQL database.
Advanced Tracking metrics eg user clicks, time on webpages also integrated and available in MYSQL database
Currently amazon datasets are used, but any ratings dataset can be easily incorporated

The platform has been created specifically to be easy to understand, modify and deploy for research purpose. I've deployed it on AWS Elastic Beanstalk for my research

### To install and run a test server:
Create a virtual environment (python 2.7)
install packages in requirements.txt
create database model - python model.py
add data - python seed.py (based on your data)
run app - python application.py

### Citations necessary for any usage of this platform.
