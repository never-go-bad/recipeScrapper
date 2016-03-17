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

	recipeObj = {"recipes" : items}

	json_string = json.dumps(recipeObj, indent=4)

	return HttpResponse(json_string, content_type="application/json; charset=utf-8")


def generateServingsAndTime(recipe): 
		if "servings" in recipe or "activeTime" in recipe or "totalTime":
			html = "<H1 style=\"font-family:Helvetica; font-weight: lighter; background-color: darkgray \">SERVINGS & COOKING TIME</H1><div style=\"font-family:Helvetica; font-size: 12pt\">"
			if "servings" in recipe: html += "<b>Servings:</b> %s<br/>" % recipe["servings"]
			if "activeTime" in recipe: html += "<b>Active Time:</b> %s<br/>" % recipe["activeTime"]
			if "totalTime" in recipe: html += "<b>Total Time:</b> %s<br/>" % recipe["totalTime"]
			html += "</div>"
		return html

def generateIngredients(recipe):
	html = "<br/><br/><H1 style=\"font-family:Helvetica; font-weight: lighter\">INGREDIENTS</H1><div style=\"font-family:Helvetica; font-size: 12pt\">"
	for group in recipe["ingredientGroups"]:
		if  "groupName" in group: html +="<br/><strong> %s </strong>" % group["groupName"]
		html +="<ul>"
		for ingredient in group["ingredients"]:
			html += "<li>%s</li>" % ingredient
		html += "</ul>"
	html += "</div>"
	return html

def generateSteps(recipe):
	html = "<br/><br/><H1 style=\"font-family:Helvetica; font-weight: lighter\">PREPARATION STEPS</H1><div style=\"font-family:Helvetica; font-size: 12pt\">"
	for group in recipe["preparationStepGroups"]:
		if  "groupName" in group: html +="<br/><strong> %s </strong>" % group["groupName"]
		html +="<ul>"
		for ingredient in group["steps"]:
			html += "<li>%s</li>" % ingredient
		html += "</ul>"
	html += "</div>"
	return html

@require_GET
def recipe(request, path):
	req = requests.get("http://www.epicurious.com/" + path)
	soup = BeautifulSoup(req.text, 'html.parser')

	recipe = {}
	recipe["name"] = soup.find("h1", itemprop="name").text
	rating = soup.find("span", class_="rating").text
	recipe["rating"] = float(rating[:rating.index('/')])
	recipe["wouldPrepareAgain"] = soup.find("div", class_="prepare-again-rating").span.text

	description = soup.find("div", class_="dek")
	if description is not None:
		recipe["description"] = description.text
	image = soup.find("meta", itemprop="image")
	if image is not None:
		recipe["image"] = image['content']

	servings = soup.find("dd", class_="yield")
	activeTime = soup.find("dd", class_="active-time")
	totalTime = soup.find("dd", class_="total-time")
	if servings is not None: recipe["servings"] = servings.text
	if activeTime is not None: recipe["activeTime"] = activeTime.text
	if totalTime is not None: recipe["totalTime"] = totalTime.text

	recipe["ingredientGroups"] = []	

	for ingredientGroup in soup.find_all("li", class_="ingredient-group"):
		obj = {}
		if ingredientGroup.strong is not None: obj["groupName"] = ingredientGroup.strong.text
		obj["ingredients"] =  [i.text.strip() for i in ingredientGroup.find_all("li", class_="ingredient")]
		recipe["ingredientGroups"].append(obj)

	recipe["preparationStepGroups"] = []	

	for stepGroup in soup.find_all("li", class_="preparation-group"):
		obj = {}
		if stepGroup.strong is not None: obj["groupName"] = stepGroup.strong.text
		obj["steps"] =  [i.text.strip() for i in stepGroup.find_all("li", class_="preparation-step")]
		recipe["preparationStepGroups"].append(obj)

	chefNotes = soup.find("div", class_="chef-notes-content")
	if chefNotes is not None:
		recipe["chefNotes"] = list(chefNotes.strings)

	recipe["html"]  = generateServingsAndTime(recipe) + generateIngredients(recipe) + generateSteps(recipe)

	json_string = json.dumps(recipe, indent=4)

	return HttpResponse(json_string, content_type="application/json; charset=utf-8")

