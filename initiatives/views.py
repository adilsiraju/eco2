from django.shortcuts import render, get_object_or_404
from .models import Initiative, Category

def initiative_list(request):
    category_filter = request.GET.get('category')
    initiatives = Initiative.objects.all()
    if category_filter:
        initiatives = initiatives.filter(category__name=category_filter)
    categories = Category.objects.all()
    return render(request, 'initiatives/initiative_list.html', {'initiatives': initiatives, 'categories': categories})

def initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    return render(request, 'initiatives/initiative_detail.html', {'initiative': initiative})