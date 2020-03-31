# Improved arXiv

This README briefly discusses design philosophy, testing, and setup.

## Overall Design Philosophy

Given the requirements of collecting and manipulating data that are at least six months old, it is clear from the start
that the web app cannot simply hit the arXiv bulk data endpoint and display data. Thus, a database is required to store
both article and author information. This app requires a frontend since it is a user-facing app. Due to the limited
and simple functionality of the app, there is no need for any fancy SPA frameworks; Django templating will suffice. With
relevant data from arXiv, then it becomes a relatively simple task to query the article and author data in our
internal database. Since the amount of articles published in the last six months and the number of authors can be
sizable, we must paginate the results on the APi level to ensure performance and responsiveness.

There are three main questions for this web app that warrant more attention and consideration:
1. How are we getting the data to begin with so that the first time an user uses the app, there is actually data to
work with?
2. How do we keep data up-to-date?
3. How do we get the most relevant articles for the topics of interests?

For the first question, we can run a management command to bootstrap data from the arXiv service. The command will
use the bulk data API to get all relevant articles (by topic) that are published within the last six months and put
the author and article information into the Author and Article table respectively. The bulk data API command supports
sorting the article results by submission date, so once the command parses an article that is outside the six-month
window, the command can stop.

Unfortunately, I did not get to implement functionality to solve the issue that arises from the second question.
However, if I had the time, I would pdate the management command so that the cutoff is dynamic, based on the last time
the management command is run, and set up a cron job for the management command to refresh the data. Depending on
frequency, this approach can help keep our internal up-to-date with some minor gaps. If we want to ensure there are no
gaps in the data, then we can make a call to the bulk data API every time an user hits one of our views, and we can
parse the data and populate new data into our database.

The third question, in my opinion, requires some trial-and-error. The topics of interests do not directly map to any
of the categories available on the site, which means we will get irrelevant results. We can either work on refining
our search query by naked eye, or perhaps build out some statistical model that help us determine which fields or
combination of fields give us the best results.

## Testing
With the time limit, I was unable to start writing unit tests fot the functionality I have implemented. If time
permitted, I would have tested rigorously. Some libraries I would use to assist testing are httpretty and factory boy
to mock out API responses and create test objects. The following are some unit test examples I would write in the tests
directory in this app.
- test the method to handle entry in the bootstrap data script
    - Test that if authors AND/OR articles are created ONLY if those entries are not already in DB.
    - Test that an Article entry has all the correct Authors associated with it.
    - Test that an Author can indeed have multiple Articles in the db.
- test that the bulk data API is called correctly, specifically regarding the pagination parameters in the url
- test that the page that contains the latest articles display the articles in descending order based on submission date
- test that said page does honor pagination
- test that the page that contains the most prolific authors display the authors in descinding order based on article
count in the last six months and the most recent published date
- test that said page honors pagination
- test that the basic article and author page display the right information based on the html text and mocked data

## Setup

1. Create virtual environment with python 3 and activate environment.
2. Install django with `pip install django`.
3. Install additional requirements with `pip install -r ../requirements.txt`.
4. Give bootstrap script that runs migrations and loads data from arXiv execution privilege wih `chmod +x ./bootstrap.sh`. Run the script.
5. Run server with `./manage.py runserver`.
