#!/usr/bin/env python3

import csv
import uuid
import os
import sys, traceback
import requests


class APIScrollLimit(Exception):
    pass

class APIReqLimit(Exception):
    pass

def request(category, location, api_key, i, search_limit=50):

    if search_limit*i > 999:
        raise APIScrollLimit

    url = "https://api.yelp.com/v3/businesses/search"
    params = {
		# "term": term.replace(" ", "+"),
		"location": location.replace(" ", "+"),
        "categories": category,
		"limit": search_limit,
        "offset": search_limit*i
	}
    headers = {
        "Authorization": "Bearer {}".format(api_key)
    }
    res = requests.get(url, headers=headers, params=params)

    if res:
        return res.json().get("businesses", None)
    elif res.status_code == 429:
        print("Response >>>", end="")
        print(res.text)
        raise APIReqLimit
    else:
        print("Request to API failed: {}".format(res.status_code))
        raise Exception

def scrape(category, location, api_key, dedup):
    fields = ["search term", "id", "alias", "name", "rating", "review_count",
    "price", "phone", "categories", "latitude", "longitude", "display_address",
    "city", "state", "zip_code", "url"]
    items = []

    print("Category: ", end="")
    print(category)
    print("In the following location: ", end="")
    print(location)

    loop = True
    i = 0
    req_count = 0

    while loop:
        try:
            data = request(category, location, api_key, i)
            req_count += 1

            print("Items returned from API >>> ", end="")
            print(len(data))

            if data and len(data) > 0:
                for d in data:
                    if d["id"] in dedup:
                        continue

                    categories = []
                    for c in d["categories"]:
                        categories.append(c["title"])

                    item = [
                        "all",
                        d["id"],
                        d["alias"],
                        d["name"],
                        d.get("rating", ""),
                        d.get("review_count", ""),
                        d.get("price", ""),
                        d.get("phone", ""),
                        ",".join(categories),
                        d["coordinates"]["latitude"],
                        d["coordinates"]["longitude"],
                        " ".join(d["location"]["display_address"]),
                        d["location"]["city"], d["location"]["state"],
                        d["location"]["zip_code"],
                        d["url"]]
                    items.append(item)
                    dedup.add(d["id"])

                i += 1
            else:
                loop = False

            print("Unique items found >>> ", end="")
            print(len(dedup))
        except APIScrollLimit:
            loop = False
        except APIReqLimit:
            raise APIReqLimit
        except Exception as e:
            print("Caught exception: {}".format(e))
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)
            loop = False

    path = 'data/' + uuid + '/' +  location.replace(" ", "+") + '/'

    if not os.path.exists(path):
        os.makedirs(path)

    filename = category + ".csv"

    with open(os.path.join(path, filename), 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        # csv_writer.writerow(fields)
        csv_writer.writerows(items)

    return req_count


if __name__ == '__main__':
    api_key = os.getenv("API_KEY", None)

    if api_key is None:
        print("No API Key found, stopping ...")
    else:
        uuid = str(uuid.uuid1().int)[:6]

        print("Enter category alias >>> ", end="")
        category = input()
        # path = 'data/'
        # filename = "categories.csv"
        # categories = []
        # with open(os.path.join(path, filename), 'r') as csv_file:
        #     csv_reader = csv.reader(csv_file, delimiter=',')
        #     for row in csv_reader:
        #         categories.append(row[0])
        
        print("Enter locations >>> ", end="")
        locations = input().split()

        print("Scraping the following Yelp category.")
        print("Category: ", end="")
        print(category)
        print("In the following locations: ", end="")
        print(locations)

        req_count = 0
        dedup = set()

        for location in locations:
            for category in categories:
                try:
                    req_count += scrape(category, location, api_key, dedup)
                except APIReqLimit:
                    print("Caught APIReqLimit exception; exiting")
                    raise APIReqLimit
                finally:
                    print("Request count >>> ", end="")
                    print(req_count)
