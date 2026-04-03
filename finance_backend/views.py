from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to the Finance Management API!</h1>")
