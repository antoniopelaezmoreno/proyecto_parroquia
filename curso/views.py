from django.shortcuts import render, redirect
from .forms import CursoForm

# Create your views here.
def crear_curso(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = CursoForm(request.POST, request.FILES)
            if form.is_valid():
                curso = form.save()
                return redirect('/')
        else:
            form = CursoForm()
        return render(request, 'crear_curso.html', {'form': form})
    else:
        return redirect('/403')
    

