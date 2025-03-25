from django.shortcuts import render, get_object_or_404
from .models import Initiative, Category
from investments.models import Investment
from django.db.models import Q, ExpressionWrapper, F, Sum, FloatField, DecimalField, Count
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce, Cast
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import InitiativeForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from investments.impact_calculator import ImpactCalculator

def initiative_list(request):
    initiatives = Initiative.objects.all()
    
    # Apply filters
    category = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')
    sort = request.GET.get('sort', 'newest')
    
    if category:
        initiatives = initiatives.filter(categories__name=category)
    if status:
        initiatives = initiatives.filter(status=status)
    if search:
        initiatives = initiatives.filter(title__icontains=search)
    
    # Apply sorting
    if sort == 'progress':
        initiatives = initiatives.order_by('-current_amount')
    elif sort == 'amount':
        initiatives = initiatives.order_by('-goal_amount')
    else:  # newest
        initiatives = initiatives.order_by('-created_at')
    
    # Calculate total metrics
    total_initiatives = Initiative.objects.count()
    total_investors = Initiative.objects.aggregate(total=Count('investments__user', distinct=True))['total']
    total_invested = Initiative.objects.aggregate(total=Sum('current_amount'))['total'] or 0
    
    # Initialize impact calculator
    impact_calculator = ImpactCalculator()
    
    # Calculate impact for ₹1000 for each initiative
    for initiative in initiatives:
        # Get category names
        category_names = [cat.name for cat in initiative.categories.all()]
        
        # Calculate impact for ₹1000
        carbon, energy, water = impact_calculator.predict_impact(
            investment_amount=1000,
            category_names=category_names,
            project_duration_months=initiative.duration_months,
            project_scale=initiative.project_scale,
            location=initiative.location,
            technology_type=initiative.technology_type
        )
        
        # Store the impact metrics
        initiative.impact_for_1000 = {
            'carbon': round(carbon),
            'energy': round(energy),
            'water': round(water)
        }
    
    # Calculate total carbon impact
    total_carbon = sum(initiative.impact_for_1000['carbon'] for initiative in initiatives)
    
    # Pagination
    paginator = Paginator(initiatives, 9)
    page = request.GET.get('page')
    initiatives = paginator.get_page(page)
    
    context = {
        'initiatives': initiatives,
        'categories': Category.objects.all(),
        'total_initiatives': total_initiatives,
        'total_investors': total_investors,
        'total_invested': total_invested,
        'total_carbon': total_carbon,
    }
    
    return render(request, 'initiatives/initiative_list.html', context)

def initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    
    # Initialize impact calculator
    impact_calculator = ImpactCalculator()
    
    # Get category names
    category_names = [cat.name for cat in initiative.categories.all()]
    
    # Calculate impact for ₹1000
    carbon, energy, water = impact_calculator.predict_impact(
        investment_amount=1000,
        category_names=category_names,
        project_duration_months=initiative.duration_months,
        project_scale=initiative.project_scale,
        location=initiative.location,
        technology_type=initiative.technology_type
    )
    
    # Store the impact metrics
    impact_metrics = {
        'carbon': round(carbon),
        'energy': round(energy),
        'water': round(water)
    }
    
    # Get recent investments
    recent_investments = initiative.investments.all().order_by('-created_at')[:5]
    
    # Get similar initiatives
    similar_initiatives = Initiative.objects.filter(
        categories__in=initiative.categories.all()
    ).exclude(
        pk=initiative.pk
    ).distinct()[:3]
    
    context = {
        'initiative': initiative,
        'impact_metrics': impact_metrics,
        'recent_investments': recent_investments,
        'similar_initiatives': similar_initiatives,
        'total_investors': initiative.investments.values('user').distinct().count(),
    }
    
    return render(request, 'initiatives/initiative_detail.html', context)

@login_required
def create_initiative(request):
    if request.method == 'POST':
        form = InitiativeForm(request.POST, request.FILES)
        if form.is_valid():
            initiative = form.save(commit=False)
            
            # Calculate impact values based on goal amount
            # These are example calculations - adjust based on your needs
            base_carbon_reduction = 1000  # kg CO2 per 100,000 INR
            base_energy_savings = 5000    # kWh per 100,000 INR
            base_water_savings = 10000    # liters per 100,000 INR
            
            # Calculate per-investment impact
            initiative.carbon_reduction_per_investment = base_carbon_reduction / 100
            initiative.energy_savings_per_investment = base_energy_savings / 100
            initiative.water_savings_per_investment = base_water_savings / 100
            
            # Calculate total impact based on goal amount
            goal_amount_float = float(initiative.goal_amount)
            initiative.carbon_impact = (goal_amount_float / 100000) * base_carbon_reduction
            initiative.energy_impact = (goal_amount_float / 100000) * base_energy_savings
            initiative.water_impact = (goal_amount_float / 100000) * base_water_savings
            
            # Set default values for other fields
            initiative.current_amount = 0
            initiative.status = 'active'
            initiative.risk_level = 'medium'  # Default risk level
            initiative.roi_estimate = 12.0  # Default 12% ROI estimate
            
            # Save the initiative
            initiative.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, 'Initiative created successfully!')
            return redirect('initiative_detail', pk=initiative.pk)
    else:
        form = InitiativeForm()
    
    return render(request, 'initiatives/create_initiative.html', {'form': form})
