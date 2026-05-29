# is_restaurant_open
API that takes a datetime string and returns a list of restaurant names which are open on that date at that time.

Problem Statement:

Python is preferred, but if you feel unable to complete it using python, use whatever programming language you feel most comfortable in.

Build an API with an endpoint which takes a single parameter, a datetime string, and returns a list of restaurant names which are open on that date and time. You are provided a dataset in the form of a CSV file of restaurant names and a human-readable, string-formatted list of open hours. Store this data in whatever way you think is best. Optimized solutions are great, but correct solutions are more important. Make sure whatever solution you come up with can account for restaurants with hours not included in the examples given in the CSV. Please include all tests you think are needed.
Assumptions:

    If a day of the week is not listed, the restaurant is closed on that day
    All times are local — don’t worry about timezone-awareness
    The CSV file will be well-formed, assume all names and hours are correct

Want bonus points? Here are a few things we would really like to see:

    A Dockerfile and the ability to run this in a container

## Running the program

Create and activate the virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Django development server:

```bash
python manage.py runserver
```

Query the endpoint with a timestamp:

```bash
curl "http://127.0.0.1:8000/restaurants/?datetime=2024-01-15%2012:00:00"
```

Run the test suite:

```bash
python manage.py test
```

To deactivate the virtual environment when you are done:

```bash
deactivate
```

