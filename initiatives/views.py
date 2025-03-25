from django.shortcuts import render, get_object_or_404
from .models import Initiative, Category
from investments.models import Investment
from django.db.models import Q, ExpressionWrapper, F, Sum, FloatField, DecimalField
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce, Cast
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import InitiativeForm
from django.urls import reverse
from django.http import HttpResponseRedirect

def initiative_list(request):
    initiatives = Initiative.objects.all()
    categories = Category.objects.all()

    # Filter by category
    category = request.GET.get('category')
    if category:
        initiatives = initiatives.filter(categories__name=category)

    # Filter by status
    status = request.GET.get('status')
    if status:
        initiatives = initiatives.filter(status=status)

    # Filter by search
    search = request.GET.get('search')
    if search:
        initiatives = initiatives.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )

    # Sort initiatives
    sort = request.GET.get('sort', 'newest')
    if sort == 'newest':
        initiatives = initiatives.order_by('-created_at')
    elif sort == 'progress':
        initiatives = initiatives.annotate(
            progress=ExpressionWrapper(
                Cast('current_amount', FloatField()) * 100.0 / Cast('goal_amount', FloatField()),
                output_field=FloatField()
            )
        ).order_by('-progress')
    elif sort == 'amount':
        initiatives = initiatives.order_by('-current_amount')

    # Calculate totals for hero section
    active_initiatives = initiatives.filter(status='active')
    total_initiatives = active_initiatives.count()
    total_investors = Investment.objects.values('user').distinct().count()
    total_invested = initiatives.aggregate(
        total=Coalesce(Sum('current_amount'), 0, output_field=DecimalField())
    )['total']
    total_carbon = initiatives.aggregate(
        total=Coalesce(Sum('carbon_impact'), 0, output_field=FloatField())
    )['total']
    total_energy = initiatives.aggregate(
        total=Coalesce(Sum('energy_impact'), 0, output_field=FloatField())
    )['total']
    total_water = initiatives.aggregate(
        total=Coalesce(Sum('water_impact'), 0, output_field=FloatField())
    )['total']

    # Pagination
    paginator = Paginator(initiatives, 9)  # Show 9 initiatives per page
    page = request.GET.get('page')
    initiatives = paginator.get_page(page)

    context = {
        'initiatives': initiatives,
        'categories': categories,
        'total_initiatives': total_initiatives,
        'total_investors': total_investors,
        'total_invested': total_invested,
        'total_carbon': total_carbon,
        'total_energy': total_energy,
        'total_water': total_water,
    }
    return render(request, 'initiatives/initiative_list.html', context)

def initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    
    # Get recent investments
    recent_investments = Investment.objects.filter(
        initiative=initiative
    ).select_related('user').order_by('-created_at')[:5]
    
    # Get similar initiatives based on categories
    similar_initiatives = Initiative.objects.filter(
        categories__in=initiative.categories.all()
    ).exclude(id=initiative.id).distinct()[:3]

    # Calculate total investments and investors for this initiative
    total_investors = Investment.objects.filter(
        initiative=initiative
    ).values('user').distinct().count()

    # Calculate impact metrics
    impact_metrics = {
        'carbon': initiative.carbon_impact or 0,
        'energy': initiative.energy_impact or 0,
        'water': initiative.water_impact or 0,
    }

    context = {
        'initiative': initiative,
        'recent_investments': recent_investments,
        'similar_initiatives': similar_initiatives,
        'total_investors': total_investors,
        'impact_metrics': impact_metrics,
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
