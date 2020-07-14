# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

from open_review.or_service import OpenReviewService

or_service = OpenReviewService()


def index(request):
    return HttpResponse("Hello, world. You're at the venues index.")


def list_venues(request):
    # venues_list = [{'id':1},{'id':2},{'id':3}]
    conf_venues = or_service.get_venue(invitations=['Venue/-/Conference/Series'])
    workshop_venues = or_service.get_venue(invitations=['Venue/-/Workshop/Series'])
    conf_venues = [v for v in conf_venues if 'id' in v and v['id'] is not None and v['id'] is not '']
    workshop_venues = [v for v in workshop_venues if 'id' in v and v['id'] is not None and v['id'] is not '']
    return render(request, 'venues/venue_list.html', {'conf_venues': conf_venues, 'workshop_venues': workshop_venues})


def venue(request, venue_id=None):
    print(venue_id)
    venue = or_service.get_venue(id=venue_id)[0]
    occurrences = or_service.get_venue(invitations=['Venue/-/Conference/Occurrence'])
    occurrences.extend(or_service.get_venue(invitations=['Venue/-/Workshop/Occurrence']))
    occurrences = [o for o in occurrences if venue_id in o['content']['parents']]
    parents = None
    if 'parents' in venue['content']:
        parents = venue['content']['parents']

    return render(request, 'venues/venue_series.html',
                  {'venues_list': occurrences, 'venue_series': venue, 'parents': parents})
