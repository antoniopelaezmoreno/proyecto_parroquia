from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, 'index.html')

def c403(request):
    return render(request, '403.html')

def c404(request):
    return render(request, '404.html')