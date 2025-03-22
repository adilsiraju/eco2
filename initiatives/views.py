from django.shortcuts import render, get_object_or_404
from .models import Initiative, Category

def initiative_list(request):
    initiatives = Initiative.objects.all()
    categories = Category.objects.all()
    return render(request, 'initiatives/initiative_list.html', {'initiatives': initiatives, 'categories': categories})

def initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    return render(request, 'initiatives/initiative_detail.html', {'initiative': initiative})