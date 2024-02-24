from django.shortcuts import render

# Create your views here.
def index(request):
    user = request.user
    print(user)
    return render(request, 'index.html', {'user': user})