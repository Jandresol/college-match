# college-match
<a name="readme-top"></a>

  <h3 align="center">College Match Design Doc</h3>



<!-- ABOUT THE PROJECT -->
## About The Project

This is a CS50 final project made in collaboration with Jasmine Andresol and Matteo Diaz.

College Match is a website aimed at prospective college students searching for what college to apply to. Users can create their profile, take the quiz, and discover what colleges await them! The matching algorithm compares the user's preferences with a database of 2,000+ colleges across the country to find the best match!


### Built With

- Flask
- Bootstrap
- SQL
- HTML/CSS
- Javascript
  
<p align="right">(<a href="#readme-top">back to top</a>)</p>


## File Tree
COLLEGE-MATCH <br />
| - __pycache__ <br />
| - flask_session <br />
| - static <br />
| - templates <br />
| | - base.html <br />
| | - confirm_retake.html <br />
| | - landing.html <br />
| | - layout.html <br / >
| | - login.html <br />
| | - register.html <br />
| | - results.html <br />
| | - settings.html <br />
| | - step_1.html <br />
| | - step_2.html <br />
| | - step_3.html <br />
| | - step_4.html <br />
| | - step_5.html <br />
| | - step_6.html <br />
| | - step_7.html <br />
| | - step_8.html <br />
| | - survey.html <br />
| | - waiting.html <br />
| | - survey_completed.html <br />
| - app.py <br />
| - helpers.py <br />
| - college_data.csv <br />
| - constants.py <br />
| - match.py <br />
| - users.db <br />
| - README.py<br />


## templates
This folder holds the HTML templates that are used in the app.py flask file

### base.html
This is the standard template extended to all steps in the survey

### landing.html
This HTML file is the landing page.

### layout.html
This is the HTML template extended to all pages in the website

### login.html
This is the HTML template for the login page

### register.html
This is the HTML template for the registration page

### results.html
This renders the results table

### settings.html
This is the HTML file that renders the settings page

### step.html
These HTML files are the web pages for the survey

### survey.html
This HTML file is the start of the survey page.

### waiting.html
This HTML file is the page for when a user hasn't taken a survey yet.

### survey_completed.html
This is the page that appears when the survey is complete

## app.py
This flask file manages the redirection between pages and renders the HTML. It also handles the login and registration and the functionality of outputting the survey results.

## helpers.py
This file holds two functions crucial for the login and registration

## match.py
This file holds the crucial functions for the matching algorithm 

## college_data.csv
This is the csv file that contains the list of 2000+ file gathered from the IPEDS database

## users.db
This SQL database stores the users as well as their results from the college matching survey
