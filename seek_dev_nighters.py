import requests
import pytz
import datetime


def load_attempts():
    source_url = "https://devman.org/api/challenges/solution_attempts/"
    page = 1
    while True:
        response = requests.get(source_url, data={"page": page}).json()
        max_page = response["number_of_pages"]
        records = response["records"]
        for record in records:
            yield record
        page += 1
        if page > max_page:
            break


def is_user_a_midnighter(record, date_range):
    local_timezone = pytz.timezone(record["timezone"])
    utc_dt = pytz.utc.localize(
        datetime.datetime.utcfromtimestamp(record["timestamp"]))
    local_dt = utc_dt.astimezone(local_timezone)
    if date_range[0] <= local_dt.time() <= date_range[1]:
        return True

if __name__ == '__main__':
    midnight_dt = datetime.time(0, 0, 0)
    morning_dt = datetime.time(7, 0, 0)
    records = load_attempts()
    midnighters = set()
    for record in records:
        if is_user_a_midnighter(record, [midnight_dt, morning_dt]):
            midnighters.add(record["username"])
    print("Users that made commits in time range "
          "between {} and {} are:\n{}".format(midnight_dt,
                                              morning_dt,
                                              "\n".join(midnighters)))
