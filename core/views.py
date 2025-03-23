from django.shortcuts import render
from initiatives.models import Initiative, Company

def landing(request):
    featured_initiatives = Initiative.objects.filter(status='active')[:3]
    featured_companies = Company.objects.filter(status='active')[:3]
    return render(request, 'core/landing.html', {
        'featured_initiatives': featured_initiatives,
        'featured_companies': featured_companies,
    })
    
def learn_more(request):
    return render(request, 'core/learn_more.html')