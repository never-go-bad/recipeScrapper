import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.http.request import QueryDict
import json


# Create your views here.

@require_GET
def search(request): 

	queryDict = QueryDict(mutable=True)
	queryDict['q']  = request.GET['search']

	if 'pageSize' in request.GET:
		queryDict['size'] =  request.GET['pageSize']

	if 'pageNumber' in request.GET: 
		queryDict['page'] = request.GET['pageNumber']


	photoBase = "http://assets.epicurious.com/photos/%s/1:1/w_600%%2Ch_600/%s"


	response = requests.get("http://services.epicurious.com/api/search/v1/query?" + queryDict.urlencode())
	bundle = json.loads(response.text.encode('utf-8'))

	start = bundle["start"]
	numFound = bundle["numFound"]
	totalPages = bundle["totalPages"]


	recipes = []
	if start < numFound :  
		for recipe in bundle["items"] : 
			if recipe["type"] == "recipe":
				rec = {}
				rec["name"]= recipe["hed"]
				rec["id"] = recipe["url"]
				if "aggregateRating" in recipe:
					rec["rating"] = recipe["aggregateRating"]
				if "photoData" in recipe:
					rec["image"] = photoBase % (recipe["photoData"]["id"], recipe["photoData"]["filename"])
				recipes.append(rec)

	response = {}
	response["recipes"] = recipes
	response["start"] = start
	response["numFound"] = numFound
	response["totalPages"] = totalPages

	json_string = json.dumps(response, indent=4)

	# "numFound":477,"start":460,"rows":20,"totalPages":24
	# items = [{hed, type, aggregateRating, url, photoData: {}}]
	return HttpResponse(json_string, content_type="application/json; charset=utf-8")


