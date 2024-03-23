from django.shortcuts import render, redirect
from grupo.models import Grupo

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.user.is_coord:
            grupos = Grupo.objects.filter(ciclo=request.user.ciclo)
            print("...............",grupos)
            return render(request, 'index.html', {'grupos': grupos})
        else:
            return render(request, 'index.html')
    return render(request, 'index.html')

def c403(request):
    return render(request, '403.html')

def c404(request):
    return render(request, '404.html')