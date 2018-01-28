import requests
import pytz
from datetime import datetime


def load_attempts():
    source_url = "https://devman.org/api/challenges/solution_attempts/"
    page = 1
    while True:
        page_data = requests.get(source_url, params={"page": page}).json()
        records = page_data["records"]
        for record in records:
            yield record
        page += 1
        if page > page_data["number_of_pages"]:
            break


def is_user_a_midnighter(record, hour_range):
    timezone = pytz.timezone(record["timezone"])
    locale_datetime = datetime.fromtimestamp(record["timestamp"], timezone)
    if hour_range[0] <= locale_datetime.hour <= hour_range[1]:
        return True


if __name__ == '__main__':
    midnight_hour = 0
    morning_hour = 7
    records = load_attempts()
    midnighters = set()
    for record in records:
        if is_user_a_midnighter(record, [midnight_hour, morning_hour]):
            midnighters.add(record["username"])
    print(
        "Users that made commits in time range between {} AM and {} AM are:\n"
        "{}".format(midnight_hour, morning_hour, "\n".join(midnighters))
    )
