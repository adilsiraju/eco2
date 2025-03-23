from django.shortcuts import render, get_object_or_404
from .models import Initiative, Category, Company

def initiative_list(request):
    category_name = request.GET.get('category')
    if category_name:
        initiatives = Initiative.objects.filter(category__name=category_name, status='active')
    else:
        initiatives = Initiative.objects.filter(status='active')
    categories = Category.objects.all()
    return render(request, 'initiatives/initiative_list.html', {'initiatives': initiatives, 'categories': categories})

def initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    return render(request, 'initiatives/initiative_detail.html', {'initiative': initiative})

def company_list(request):
    category_name = request.GET.get('category')
    if category_name:
        companies = Company.objects.filter(category__name=category_name, status='active')
    else:
        companies = Company.objects.filter(status='active')
    categories = Category.objects.all()
    return render(request, 'initiatives/company_list.html', {'companies': companies, 'categories': categories})

def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    return render(request, 'initiatives/company_detail.html', {'company': company})