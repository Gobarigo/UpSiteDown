# UpSiteDown
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

UpSiteDown is a script that checks if a web page is up or down, and optionally takes a screenshot of the page.

## How it works

### Usage

Please see the inline help for details:
```
python3 check_links.py -h
```

### Input

The input file must be a csv file with quoted strings, for instance:
```
"string1","string2","http://fqdn.com"
```
The minimal csv would be:
```
"http://fqdn.com"
```

When you run the script you will have to specify:
1. which file to process (`sites.txt`)
2. the position of the url in the csv (in the first example it would be 3, in the second it would be 1)
3. optionally, the csv field delimiter (by default it is the comma character)

### Output

The output will be a csv file name exactly the same as the input, but suffixed by `_CHECKED`.

The output will contain the same information as the input, but the following columns will be added by default:
- the web page status (UP/DOWN, considered UP is http response code is lower than 400)
- `http_code`: the http response code
- `elapsed`: the elapsed time
- `datetime`: the timestamp of the request

You can chose to add/remove or re-order any of these columns by setting `--fields` when you run the script.

Please note that the output file is appended at each execution. This has a main advantage: you can re-run the script on the same
input files many times. You are then able to compare statuses and execution times at different times. 

### Examples

#### Simple example 

Considering an input file `sites.txt` (see the file provided).
The simplest way to run the script is the following: 
```
python3 check_links.py sites.txt --csv_link_position 1
```
=>
```
"http://google.com","UP","200","0:00:00.107449","2020-04-19 13:55:07.912898"
"http://microsoft.com","UP","200","0:00:00.093168","2020-04-19 13:55:08.277377"
"http://apple.com","UP","200","0:00:00.027584","2020-04-19 13:55:08.530473"
```

By default the "HEAD" http method HEAD is used to check for the web page status.
This optimizes resources as much as possible. You can modify this behavior by setting the parameter
`--http_method` (HEAD, GET and POST are currently supported). 

#### Specifying fields

No other field than the status:
```
python3 check_links.py sites.txt --csv_link_position 1 --fields ""
```
=>
```
"http://google.com","UP"
"http://microsoft.com","UP"
"http://apple.com","UP"
```

Only the status and the http response code:
```
python3 check_links.py sites.txt --csv_link_position 1 --fields http_code
```
=>
```
"http://google.com","UP","200"
"http://microsoft.com","UP","200"
"http://apple.com","UP","200"
```

#### Specifying the request proxy

By default, no proxy is used. You can chose to specify one by setting two parameters: `--proxy` and `--proxy_type`.

One usage would be for instance if you want to use this script on the Tor network. You would probably specify something like this:
```
python3 check_links.py input.csv --csv_link_position 1 --proxy "localhost:9050" --proxy_type socks5
```

#### Screenshots

If you specify `--take_screenshot True` at runtime, the script will create a "screenshots" directory, and for each website checked
it will run a second request and store a screenshot of it. A unique id is appended to the csv line that will refer to the name of the png file created.

This feature is likely to double the execution time of the whole script.

