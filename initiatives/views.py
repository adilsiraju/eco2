from django.shortcuts import redirect, render, get_object_or_404
from .models import Initiative, Category
from investments.models import Investment
from django.db.models import Q, ExpressionWrapper, F, Sum, FloatField, DecimalField, Count
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce, Cast
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import InitiativeForm
from django.urls import reverse

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
    
    # Calculate impact for ₹1000
    total_carbon = 0
    for initiative in initiatives:
        mock_investment = Investment(amount=1000, initiative=initiative)
        impact = mock_investment.calculate_impact()  # Hypothetical calculation
        initiative.impact_for_1000 = {k: round(v) for k, v in impact.items()}
        total_carbon += initiative.impact_for_1000['carbon']
    
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
    
    # Calculate impact for ₹1000
    mock_investment = Investment(amount=1000, initiative=initiative)
    impact_metrics = mock_investment.calculate_impact()
    impact_metrics = {k: round(v) for k, v in impact_metrics.items()}
    
    # Get recent investments
    recent_investments = initiative.investments.all().order_by('-created_at')[:5]
    
    # Get similar initiatives
    similar_initiatives = Initiative.objects.filter(
        categories__in=initiative.categories.all()
    ).exclude(pk=initiative.pk).distinct()[:3]
    
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
            
            # Simplified impact calculation (unchanged)
            base_carbon_reduction = 1000  # kg CO2 per 100,000 INR
            base_energy_savings = 5000    # kWh per 100,000 INR
            base_water_savings = 10000    # liters per 100,000 INR
            
            initiative.carbon_reduction_per_investment = base_carbon_reduction / 100
            initiative.energy_savings_per_investment = base_energy_savings / 100
            initiative.water_savings_per_investment = base_water_savings / 100
            
            goal_amount_float = float(initiative.goal_amount)
            initiative.carbon_impact = (goal_amount_float / 100000) * base_carbon_reduction
            initiative.energy_impact = (goal_amount_float / 100000) * base_energy_savings
            initiative.water_impact = (goal_amount_float / 100000) * base_water_savings
            
            initiative.current_amount = 0
            initiative.status = 'active'
            initiative.risk_level = 'medium'
            initiative.roi_estimate = 12.0
            
            initiative.save()
            form.save_m2m()
            messages.success(request, 'Initiative created successfully!')
            return redirect('initiative_detail', pk=initiative.pk)
    else:
        form = InitiativeForm()
    return render(request, 'initiatives/create_initiative.html', {'form': form})