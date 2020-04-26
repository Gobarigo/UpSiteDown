# UpSiteDown
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

UpSiteDown is a script that checks if a web page is up or down, and optionally takes a screenshot of the page.

## How it works

### Installation

```
git clone https://github.com/Gobarigo/UpSiteDown.git
cd UpSiteDown
pip3 install -r requirements.txt
```

### Usage

Please see the inline help for details:
`python3 check_links.py -h`

### Input

The input file must be either:
* a csv file with quoted (recommended) or not strings
* a file containing only links (quoted or not)

When you run the script you will have to specify:
1. which file to process, e.g.: `sites.txt`
2. the position of the url in the csv (from 1 to n), e.g.: `--csv_link_position 1`
3. (optionally) the csv field delimiter (by default it is the comma character), e.g.: `--csv_field_delimiter ";"`
4. (optionally) specify if your csv is not quoted, e.g.: `--csv_noquote True`

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
`python3 check_links.py sites.txt --csv_link_position 1`

By default the "HEAD" http method HEAD is used to check for the web page status.
This optimizes resources as much as possible. You can modify this behavior by setting the parameter
`--http_method` (HEAD, GET and POST are currently supported). 

#### Specifying fields

No other field than the status:
`python3 check_links.py sites.txt --csv_link_position 1 --fields ""`

Only the status and the http response code:
`python3 check_links.py sites.txt --csv_link_position 1 --fields http_code`

#### Specifying the request proxy

By default, no proxy is used. You can chose to specify one by setting two parameters: `--proxy` and `--proxy_type`.

One usage would be for instance if you want to use this script on the Tor network. You would probably specify something like this:
`python3 check_links.py sites.txt --csv_link_position 1 --proxy "localhost:9050" --proxy_type socks5`

#### Screenshots

If you specify `--take_screenshot True` at runtime, the script will create a "screenshots" directory, and for each website checked
it will run a second request and store a screenshot of it. A unique id is appended to the csv line that will refer to the name of the png file created.

This feature is likely to double the execution time of the whole script.

To be able to use this feature, you need some PyQt5 additional modules that can be installed this way on Linux Debian:
```
apt-get install python3-pyqt5
apt-get install python3-pyqt5.qtwebkit
```

**Warning: be very careful when using this feature, even for testing purposes. You might end up storing screenshots of
web pages containing illegal stuff.**