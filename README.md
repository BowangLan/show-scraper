# show-scraper

This is a python program for scraping and store tv show data from a website periodically, then notifies the user if his/her subscribed show has a new update, and hopefully automatically downloads the video through the magnet link.

## Current features

- get and store the latest episode updates
- can subscribe add show, print the current subscribed show, as well as the episode updates of the subscribed shows

## Usage

### Episode News

Get a list of episode news: (default item count: 10)

```
python3 run.py news
```

Specify how many episode news you want to get:

```
python3 run.py news <count>
python3 run.py news 20
```

Update episode news: (retrieve the latest episode news from the web)

```
python3 run.py update
```

### Show(s)

Get information about a show, given the show id:

```
python3 run.py show <show_id>
```

Get a list of shows stored, start from the last updated:

```
python3 run.py shows
python3 run.py shows <count>
python3 run.py shows 20
```

Search show names by keyword:

```
python3 run.py search <keyword>
```

### Subscribed Show(s)

Get a list of subscribed shows:

```
python3 run.py subscribed shows
```

Get a list of episode news:

```
python3 run.py subscribed news
```

Get a list of subscribed shows and their episode news:

```
python3 run.py subscribed
```
