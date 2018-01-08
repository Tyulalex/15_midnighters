import requests
import pytz
import urllib.parse
import time
import datetime
import logging
import yaml
from json.decoder import JSONDecodeError


def load_config():
    with open('config.yaml', 'r') as config_file:
        return yaml.load(config_file)


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger


def send_ok_request(url, attempts=3):
    sleep_time_between_attempts_sec = 30
    response = requests.get(url, verify=False)
    if not response.ok and attempts > 0:
        time.sleep(sleep_time_between_attempts_sec)
        attempt = attempts - 1
        send_ok_request(url, attempts=attempt)
    elif not response.ok:
        get_logger().error(
            "status of requests {} not ok, but {}".format(
                response.url, response.status_code))
        get_logger().warning(
            "skipping this"
        )
    else:
        return response


def fetch_json_data(url):
    try:
        response = send_ok_request(url, attempts=1)
        return response.json()
    except JSONDecodeError:
        return None


def load_attempts():
    source_url = load_config()['source_url']
    pages = fetch_json_data(source_url)['number_of_pages']
    if not pages:
        return None
    for page in range(pages):
        request_url = '{}{}'.format(
            source_url, urllib.parse.urlencode(
                {'page': page + 1}))
        records = fetch_json_data(request_url)["records"]
        for record in records:
            yield record


def get_midnighters():
    midnighters_list = []
    midnight_dt = datetime.time(0, 0, 0)
    morning_dt = datetime.time(7, 0, 0)
    attempts_generator = load_attempts()
    for attempt in attempts_generator:
        local_timezone = pytz.timezone(attempt["timezone"])
        utc_dt = pytz.utc.localize(
            datetime.datetime.utcfromtimestamp(attempt["timestamp"]))
        local_dt = utc_dt.astimezone(local_timezone)
        if midnight_dt <= local_dt.time() <= morning_dt:
            midnighters_list.append(attempt["username"])
    return midnighters_list

if __name__ == '__main__':
    midnighters = get_midnighters()
    print("midnighters are {}".format(midnighters))
