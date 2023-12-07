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
| - templates <br />
| | - base.html <br />
| | - error.html <br />
| | - results.html <br />
| | - step_1.html <br />
| | - step_2.html <br />
| | - step_3.html <br />
| | - step_4.html <br />
| | - step_5.html <br />
| | - step_6.html <br />
| | - step_7.html <br />
| | - step_8.html <br />
| | - survey.html <br />
| - app.py <br />
| - helpers.py <br />
| - college_data.csv <br />
| - constants.py <br />
| - match.py <br />
| - README.py<br />

## match.py
This file holds the crucial functions for the matching algorithm 

## helpers.py
This file holds the crucial function for running the webpage including the login and registration

## templates
This folder holds the html templates that are used in the app.py flask file

## app.py
This is a flask file that is managing the redirection between pages and rendering the HTML

## college_data.csv
This is the csv file that contains the list of 2000+ file gathered from the IPEDS database
