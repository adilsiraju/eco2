from django.shortcuts import render
from initiatives.models import Initiative

def landing_page(request):
    featured_initiatives = Initiative.objects.filter(status='active').order_by('-created_at')[:3]
    return render(request, 'core/landing.html', {'featured_initiatives': featured_initiatives})