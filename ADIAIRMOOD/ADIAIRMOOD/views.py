from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>SALUT c'est la page index ADIAIRMOOD</h1>")