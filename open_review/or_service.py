import openreview

class OpenReviewService:
  def __init__(self):
    self.client = openreview.Client(baseurl = 'https://dev.openreview.net', username = 'OpenReview.net', password = 'OpenReview_dev')

  def store_venue(self, venue):
    self.client.post_venue(venue)

  def get_venue(self, ids=None, id=None, invitations=None):
    return self.client.get_venues(ids=ids, id=id, invitations=invitations)
