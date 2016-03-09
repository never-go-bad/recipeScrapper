import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from bs4 import BeautifulSoup
import json

from .models import Greeting

# Create your views here.
def index(request):
    r = requests.get('http://httpbin.org/status/418')
    print r.text
    return HttpResponse('<pre>' + r.text + '</pre>')

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})



@require_GET
def search(request): 
	req = requests.get("http://www.epicurious.com/tools/searchresults?" + request.GET.urlencode())
	soup = BeautifulSoup(req.text, 'html.parser')
	recipes = soup.find_all("div", class_="sr_rows")

	items = []

	for recipe in recipes:
		obj = {}
		obj["name"] = recipe.div.a.string
		if recipe.a.img is not None: 
			obj["image"] = recipe.a.img.get("src")
		obj["id"] = recipe.div.a["href"]
		rating_div = recipe.find_all("div", class_="sr_ratings_box") 
		if len(rating_div) > 0 :
			rating =  rating_div[0].span.string
			obj["rating"] = float(rating[:rating.index('/')])
		items.append(obj)

	json_string = json.dumps(items, indent=4)

	return HttpResponse(json_string, content_type="application/json; charset=utf-8")

