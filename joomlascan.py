#!/usr/bin/env python3
import sys
import requests
import argparse
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool

dbarray = []
useragentdesktop = {
    "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Accept-Language": "it"
}
timeoutconnection = 5
swversion = "0.5beta"


def hello():
    print("-------------------------------------------")
    print("      	     Joomla Scan                  ")
    print("   Usage: python3 joomlascan.py <target>   ")
    print("    Version " + swversion + " - Database Entries " + str(len(dbarray)))
    print("         created by Andrea Draghetti       ")
    print("-------------------------------------------")


def load_component():
    with open("comptotestdb.txt", "r") as f:
        for line in f:
            dbarray.append(line.strip())


def check_url(url, path="/"):
    fullurl = url + path
    try:
        conn = requests.get(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        if conn.headers.get("content-length") and conn.headers["content-length"] != "0":
            return conn.status_code
        else:
            return 404
    except Exception:
        return None


def check_url_head_content_length(url, path="/"):
    fullurl = url + path
    try:
        conn = requests.head(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        return int(conn.headers.get("content-length", 0))
    except Exception:
        return None


def check_url_head(url, path="/"):
    fullurl = url + path
    try:
        conn = requests.head(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        return int(conn.headers.get("content-length", 0))
    except Exception:
        return 0


def check_readme(url, component):
    for fname in ["README.txt", "readme.txt", "README.md", "readme.md"]:
        for base in ["", "/administrator"]:
            path = f"{base}/components/{component}/{fname}"
            if check_url(url, "/" + path) == 200:
                print(f"\t README file found \t > {url}/{path}")


def check_license(url, component):
    for fname in ["LICENSE.txt", "license.txt"]:
        for base in ["", "/administrator"]:
            path = f"{base}/components/{component}/{fname}"
            if check_url(url, "/" + path) == 200:
                print(f"\t LICENSE file found \t > {url}/{path}")

    xmlname = f"{component[4:]}.xml"
    for base in ["", "/administrator"]:
        path = f"{base}/components/{component}/{xmlname}"
        if check_url(url, "/" + path) == 200:
            print(f"\t XML file found \t > {url}/{path}")


def check_changelog(url, component):
    for fname in ["CHANGELOG.txt", "changelog.txt"]:
        for base in ["", "/administrator"]:
            path = f"{base}/components/{component}/{fname}"
            if check_url(url, "/" + path) == 200:
                print(f"\t CHANGELOG file found \t > {url}/{path}")


def check_mainfest(url, component):
    for fname in ["MANIFEST.xml", "manifest.xml"]:
        for base in ["", "/administrator"]:
            path = f"{base}/components/{component}/{fname}"
            if check_url(url, "/" + path) == 200:
                print(f"\t MANIFEST file found \t > {url}/{path}")


def check_index(url, component):
    for fname in ["index.htm", "index.html"]:
        for base in ["", "/administrator"]:
            path = f"{base}/components/{component}/{fname}"
            if check_url_head_content_length(url, "/" + path) and check_url_head(url, "/" + path) > 1000:
                print(f"\t INDEX file descriptive found \t > {url}/{path}")


def index_of(url, path="/"):
    fullurl = url + path
    try:
        page = requests.get(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        soup = BeautifulSoup(page.text, "html.parser")
        titlepage = soup.title.string if soup.title else ""
        return "Index of /" in titlepage
    except Exception:
        return False


def scanner(component):
    global url
    found = False
    if check_url(url, "/index.php?option=" + component) == 200:
        print("Component found: " + component + f"\t > {url}/index.php?option={component}")
        found = True
    elif check_url(url, "/components/" + component + "/") == 200:
        print("Component found (inactive/protected): " + component + f"\t > {url}/index.php?option={component}")
        found = True
    elif check_url(url, "/administrator/components/" + component + "/") == 200:
        print("Component found (admin only): " + component + f"\t > {url}/index.php?option={component}")
        found = True

    if found:
        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_mainfest(url, component)
        check_index(url, component)

        for path in [f"/components/{component}/", f"/administrator/components/{component}/"]:
            if index_of(url, path):
                print(f"\t Explorable Directory \t > {url}{path}")


def main():
    global url
    parser = argparse.ArgumentParser(description="Joomla Component Scanner")
    parser.add_argument("target", help="Target Joomla site (e.g., http://example.com)")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of threads (default: 20)")
    args = parser.parse_args()

    url = args.target.rstrip("/")
    hello()
    load_component()

    with ThreadPool(processes=args.threads) as pool:
        pool.map(scanner, dbarray)


if __name__ == "__main__":
    main()
