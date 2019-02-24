How to set up from scratch:
1. check if you have pip installed by doing `pip --version`
2. Get pip if you don't. (almost always comes with Mac by default)
3. `pip install virtualenv`
4. make sure you are at cs121p3/
5. `. bin/activate` -- you have activated virtualenv and this will protect the rest of your environment.
6. `pip install -r requirements.txt`
7. I think you should be good at this point. If you run into any issues, let me know.


To start your local server (in app/):
`python routes.py`


To make a change in the css >> cs121p3/app/static/css/static.css
To make a change in the nav or footer >> cs121p3/app/templates/base.html
To make a change in the home page >> cs121p3/app/templates/home.html
To make a change to the form >> cs121p3/app/forms.py
To make a change in the results page >> cs121p3/app/templates/results.html
To make a change in the main search engine code >> cs121p3/app/project3.py
To make a change in the startup and "API" >> cs121p3/app/routes.py


To leave virtualenv:
`deactivate`
