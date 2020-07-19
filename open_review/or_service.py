from database.transformed_venue_home import TransformedVenueHome


class OpenReviewService:
    def __init__(self):
        # self.client = openreview.Client(baseurl='https://dev.openreview.net', username='OpenReview.net',
        #                                 password='OpenReview_dev')
        database = 'dev'
        self.venue_home = TransformedVenueHome(database)

    def store_venue(self, venue):
        self.store_venue(venue)
        # self.client.post_venue(venue)

    def get_venue(self, ids=None, id=None, invitation=None):
        criteria = {}
        if id is not None:
            criteria['venueid'] = id
        if invitation is not None:
            criteria['invitation'] = invitation
        return self.venue_home.get_venue(criteria)
        # return self.client.get_venues(ids=ids, id=id, invitations=invitations)
