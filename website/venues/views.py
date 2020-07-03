# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

from open_review.or_service import OpenReviewService

or_service = OpenReviewService()

def index(request):
    return HttpResponse("Hello, world. You're at the venues index.")


def list_venues(request):
    # venues_list = [{'id':1},{'id':2},{'id':3}]
    venues = or_service.get_venue(invitations=['Venue/-/Conference/Occurrence'])
    return render(request, 'venues/venue_list.html', {'venues_list': venues})
    # return HttpResponse("List of venues present in OR")


def venue(request, venue_id):
    return HttpResponse("Details of specific venue: " % venue_id)