import argparse
import csv
import subprocess
from multiprocessing import Pool, cpu_count

import requests
import urllib3
from datetime import datetime
from random import choice

from p_tqdm import p_map

# Optional module
has_pyqt5 = True
try:
    from screenshot import Screenshot
except ImportError:
    has_pyqt5 = False
    pass

desktop_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
    'AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
]

http_methods_supported = [
    "HEAD",
    "GET",
    "POST"
]

supported_proxy_types = [
    "http",
    "socks5"
]

supported_csv_fields = [
    "http_code",
    "elapsed",
    "datetime"
]


def print_epilog():
    epilog = "The output will be name after the input file, suffixed by _CHECKED.\n"
    epilog += "Supported http methods: \n\t"
    for f in http_methods_supported:
        epilog += " {}".format(f)
    epilog += "\n"
    epilog += "Supported proxy types: \n\t"
    for f in supported_proxy_types:
        epilog += " {}".format(f)
    epilog += "\n"
    epilog += "Supported csv fields: \n\t"
    for e in supported_csv_fields:
        epilog += " {}".format(e)
    return epilog


# noinspection PyTypeChecker
parser = argparse.ArgumentParser(epilog=print_epilog(), formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("input", type=str, help="The csv file to process")
parser.add_argument("--proxy", default=None, type=str, help="Specifies a proxy for requests (default: none)")
parser.add_argument("--proxy_type", default='http', type=str, help="Specifies the proxy type (default: http)")
parser.add_argument("--http_method", default="HEAD", type=str, help="The http method to use (default: HEAD)")
parser.add_argument("--timeout", default=30, type=int, help="The request timeout (default: 30 seconds)")
parser.add_argument("--fields", type=str, action='append',
                    help='Fields to output to csv file (default: http_code elapsed datetime)', nargs="*")
parser.add_argument("--csv_link_position", type=int, help="The position of the link in the csv file", required=True)
parser.add_argument("--csv_field_delimiter", type=str, default=",", help='Delimiter for the CSV fields (default: ",")')
parser.add_argument("--csv_noquote", default=False, type=bool, help="If the csv link field has no quoting")
parser.add_argument("--take_screenshot", default=False, type=bool, help="Runs a second request and saves a screenshot")
parser.add_argument("--mp_units", type=int, default=(cpu_count() - 1), help="Number of processing units (default: "
                                                                            "core number minus 1)")
parser.add_argument("--list_size", default=1, type=int, help="The size of lists to process in parallel (default: 1")

args = parser.parse_args()
proxy_addr = None
proxy_port = None
proxy_type = None
proxies = None
field_delim = ","
output = "{}_CHECKED".format(args.input)
http_method = args.http_method
take_screen = False


def random_headers():
    return {'User-Agent': choice(desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}


def parse_proxy(proxy):
    s = proxy.split("//")[-1].split(":")
    if len(s) >= 2:
        return True, s[0], s[1]

    return False, None, None


def check_links_and_write_to_csv(links: list):
    global field_delim
    global http_method
    global take_screen

    nb = 0
    nb_up = 0
    nb_down = 0

    with requests.Session() as s:
        s.proxies = proxies

        for i in links:
            nb += 1

            try:
                url = i[args.csv_link_position - 1]
                ret = s.request(http_method, url, headers=random_headers(), timeout=args.timeout)

                if ret.status_code < 400:
                    i.append("UP")
                    nb_up += 1
                else:
                    nb_down += 1
                    i.append("DOWN")

                if args.fields and len(args.fields) > 0:
                    for f in args.fields[0]:
                        if f in supported_csv_fields:
                            if f == 'http_code':
                                i.append(str(ret.status_code))
                            elif f == 'elapsed':
                                i.append(str(ret.elapsed))
                            elif f == 'datetime':
                                i.append(str(datetime.now()))
                else:
                    # Default mode
                    i.append(str(ret.status_code))
                    i.append(str(ret.elapsed))
                    i.append(str(datetime.now()))

                if take_screen:
                    if ret.status_code < 400:
                        # QtApplication does not like to be called outside of main, therefore I decided to completely
                        # outsource it to screenshot.py
                        try:
                            filename = ""
                            if proxy_type and proxy_addr and proxy_port:
                                filename = subprocess.check_output(["python3",
                                                                    "screenshot.py",
                                                                    "{}".format(url),
                                                                    "--proxy_type", proxy_type,
                                                                    "--proxy_addr", proxy_addr,
                                                                    "--proxy_port", proxy_port
                                                                    ],
                                                                   text=True)
                            else:
                                filename = subprocess.check_output(["python3", "screenshot.py", "{}".format(url)],
                                                                   text=True)
                            i.append(str.replace(filename, "\n", ""))
                        except:
                            i.append("error")
                    else:
                        i.append("")
            except Exception as e:
                i.append("DOWN")
                nb_down += 1

                if args.fields and len(args.fields) > 0:
                    for f in args.fields[0]:
                        if f in supported_csv_fields:
                            if f == 'http_code':
                                i.append(str(-1))
                            elif f == 'elapsed':
                                i.append(str(-1))
                            elif f == 'datetime':
                                i.append(str(datetime.now()))
                else:
                    # Default mode
                    i.append(str(-1))
                    i.append(str(-1))
                    i.append(str(datetime.now()))

                if args.take_screenshot:
                    i.append("")

            with open(output, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=field_delim, quoting=csv.QUOTE_ALL)
                csv_writer.writerow(i)

    return nb, nb_up, nb_down


def check_links():
    global proxy_addr, proxy_port, proxy_type, proxies
    global field_delim
    global http_method
    global take_screen

    start_time = datetime.now()

    # Disabling socks5 retries
    urllib3.Retry.from_int(0)
    urllib3.Timeout.from_float(float(args.timeout))

    total_link = 0
    total_up = 0
    total_down = 0

    if args.csv_field_delimiter and len(args.csv_field_delimiter) == 1:
        field_delim = args.csv_field_delimiter

    if http_method not in http_methods_supported:
        http_method = "HEAD"

    # Checks the proxy parameters
    if args.proxy is not None:
        success, h, p = parse_proxy(args.proxy)
        if success:
            proxy_addr = h
            proxy_port = p
        else:
            print("Error: proxy '{}' does not match required format \"localhost:81\"".format(args.proxy))
            return

        if args.proxy_type in supported_proxy_types:
            proxy_type = args.proxy_type
        else:
            print("Error: proxy_type '{}' does not match any of supported:".format(args.proxy_type))
            for i in supported_proxy_types:
                print("  {}".format(i))
            return

    # Builds the proxy string
    if proxy_addr and proxy_port and proxy_type:
        print("Going to start requesting using {} proxy: {}:{}".format(proxy_type, proxy_addr, proxy_port))
        if proxy_type == "socks5":
            proxy = "{}h://{}:{}".format(proxy_type, proxy_addr, proxy_port)
            proxies = {'http': proxy, 'https': proxy}
        elif proxy_type == "http":
            proxy = "{}://{}:{}".format(proxy_type, proxy_addr, proxy_port)
            proxy_secure = "{}s://{}:{}".format(proxy_type, proxy_addr, proxy_port)
            proxies = {'http': proxy, 'https': proxy_secure}

    # Handle the optional screenshot feature
    if args.take_screenshot:
        if has_pyqt5:
            take_screen = True
        else:
            print("Warning: PyQt5 dependencies are not met, you are not able to run this script with --take_screenshot")
            return

    # Browse the input csv file, store everything in an array
    input_links = []
    with open(args.input) as f:
        quoting = csv.QUOTE_ALL
        if args.csv_noquote:
            quoting = csv.QUOTE_NONE
        csv_reader = csv.reader(f, delimiter=field_delim, quoting=quoting)
        for line in csv_reader:
            input_links.append(line)

    # Customize the length of the list of links to process in parallel
    list_len = args.list_size
    links = []
    tmp_links = []
    for i in input_links:
        if list_len == 1:
            links.append([i])
        else:
            tmp_links.append(i)
            if len(tmp_links) == list_len:
                links.append(tmp_links.copy())
                tmp_links.clear()
    if len(tmp_links) > 0:
        links.append(tmp_links.copy())

    # Loop the array, write the result to output
    items = len(links)
    units = min((cpu_count() - 1), items)
    if args.mp_units and args.mp_units > 0:
        units = min(args.mp_units, items)
    print("check_links.py started with {} processing units...".format(units))

    with Pool(units) as p:
        # p_map is a wrapper for tqdm + mp (only works for Pool, not threads)
        res = p_map(check_links_and_write_to_csv, links)

        for r in res:
            total_link += r[0]
            total_up += r[1]
            total_down += r[2]

    p.join()
    p.close()

    stop_time = datetime.now()

    print("\nReport:")
    print("  Execution time: %s seconds" % (stop_time - start_time))
    print("  Execution using method: {}".format(http_method))
    print("  Total: {} sites checked".format(str(total_link)))
    print("    Up: {}".format(total_up))
    print("    Down: {}".format(total_down))
    print("  Output file is {}".format(output))


if __name__ == "__main__":
    check_links()
