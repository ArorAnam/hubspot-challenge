class Partner:
    # class to keep track of person
    # contains first name, last name, email, country, and dates available
    def __init__(self, data):
        self.first = data['firstName']
        self.last = data['lastName']
        self.email = data['email']
        self.country = data['country']
        self.dates = data['availableDates']
