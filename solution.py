from partner import Partner
from country import Country
from dateutil.parser import parse
import datetime
import json
import requests


GET_URL = 'https://candidate.hubteam.com/candidateTest/v2/partners?userKey=8ff42cf269c4279481e4784c8877'
POST_URL = 'https://candidate.hubteam.com/candidateTest/v2/results?userKey=8ff42cf269c4279481e4784c8877'


def get_data():
    r = requests.get(GET_URL)
    return r.json()


def post_data(payload):
    r = requests.post(POST_URL, data=json.dumps(payload))
    print r


def process_data(data):
    country_list = []

    # this nested dictionary maintains a relationship of
    # countries -> dictionary of dates -> set of people available at those dates
    country_dates_attendees = dict()

    # put all the relationship from the data we got into our dictionary
    for p in data['partners']:
        person = Partner(p)

        if person.country not in country_dates_attendees:
            country_dates_attendees[person.country] = dict()

        for date in person.dates:
            if date not in country_dates_attendees[person.country]:
                country_dates_attendees[person.country][date] = set()
            country_dates_attendees[person.country][date].add(person)

    for country_name, dates_attendees in country_dates_attendees.items():

        # the dates need to be in order to check for consecutive dates
        sorted_dates = sorted(dates_attendees.keys())

        # variables to keep track of the dates where attendees are maximized
        most_attendees_count = float('-inf')
        most_attendees_day = None
        most_attendees = set()

        for index in xrange(len(sorted_dates[:-1])):

            # raw string dates
            raw_curr_date = sorted_dates[index]
            raw_next_date = sorted_dates[index + 1]

            # parsed into python datetime objects for easier comparison
            curr_date = parse(raw_curr_date)
            next_date = parse(raw_next_date)

            curr_attendees = dates_attendees[raw_curr_date]
            next_attendees = dates_attendees[raw_next_date]

            # check if next date is consecutive if not skip to next
            if next_date - curr_date != datetime.timedelta(1):
                continue

            # check the number of attendees that are in both dates using set intersection
            attendees = curr_attendees & next_attendees
            attendees_count = len(attendees)

            # update the most attendees count if the count is greater
            # OR if the count is the same and the current date is earlier
            if attendees_count > most_attendees_count or \
                    (attendees_count == most_attendees_count and raw_curr_date < most_attendees_day):
                most_attendees_count = attendees_count
                most_attendees_day = raw_curr_date
                most_attendees = attendees

        # create a new country result object and add it to the country list
        country = Country()
        country.name = country_name
        if most_attendees_count > 0:
            country.start_date = most_attendees_day
        for person in most_attendees:
            country.add_attendee(person)
        country_list.append(country)

    return country_list


def get_payload(result_list):
    payload = dict()
    payload['countries'] = map(lambda result: result.get_payload(), result_list)
    return payload


def main():
    data = get_data()
    result_list = process_data(data)
    payload = get_payload(result_list)
    post_data(payload)


if __name__ == '__main__':
    main()
