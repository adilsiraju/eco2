from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from django.db import models  # Explicitly import models from django.db
from django.db.models import Sum, Count
from investments.models import Investment
from initiatives.models import Initiative, Category
from .models import Profile
from django.db.models.functions import TruncMonth
import json
from django.core.serializers.json import DjangoJSONEncoder
from investments.portfolio_analyzer import PortfolioAnalyzer
from django.db.models.functions import Coalesce
from django.db.models import DecimalField
from collections import defaultdict

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    investments = user.investments.all().select_related('initiative')
    
    # Calculate total invested amount
    total_invested = investments.aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']
    
    # Calculate total impact metrics using stored fields with explicit FloatField
    total_impact = investments.aggregate(
        carbon=Coalesce(Sum('carbon_impact'), 0, output_field=models.FloatField()),
        energy=Coalesce(Sum('energy_impact'), 0, output_field=models.FloatField()),
        water=Coalesce(Sum('water_impact'), 0, output_field=models.FloatField())
    )
    total_impact = {k: round(v) for k, v in total_impact.items()}
    
    # Initialize category impact dictionary
    impact_by_category = defaultdict(lambda: {'carbon': 0, 'energy': 0, 'water': 0})
    
    # Group investments by initiative
    grouped_investments = {}
    for investment in investments:
        initiative_id = investment.initiative.id
        if initiative_id not in grouped_investments:
            grouped_investments[initiative_id] = {
                'initiative': investment.initiative,
                'total_amount': 0,
                'last_investment_date': investment.created_at,
                'impact_metrics': {'carbon': 0, 'energy': 0, 'water': 0}
            }
        grouped_investments[initiative_id]['total_amount'] += investment.amount
        grouped_investments[initiative_id]['impact_metrics']['carbon'] += investment.carbon_impact
        grouped_investments[initiative_id]['impact_metrics']['energy'] += investment.energy_impact
        grouped_investments[initiative_id]['impact_metrics']['water'] += investment.water_impact
        
        # Add to category impact
        for category_name in [cat.name for cat in investment.initiative.categories.all()]:
            impact_by_category[category_name]['carbon'] += investment.carbon_impact
            impact_by_category[category_name]['energy'] += investment.energy_impact
            impact_by_category[category_name]['water'] += investment.water_impact
    
    # Round category impacts
    for category in impact_by_category:
        impact_by_category[category] = {k: round(v) for k, v in impact_by_category[category].items()}
    
    # Get recent investments
    recent_investments = sorted(
        grouped_investments.values(),
        key=lambda x: x['last_investment_date'],
        reverse=True
    )[:5]
    for investment_data in recent_investments:
        investment_data['impact_metrics'] = {k: round(v) for k, v in investment_data['impact_metrics'].items()}

    # Get investment distribution by category
    category_distribution = investments.values('initiative__categories__name').annotate(total=Sum('amount')).order_by('-total')
    
    # Get monthly investment trends
    monthly_trends = investments.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('amount')).order_by('month')
    
    # Portfolio analysis
    try:
        analyzer = PortfolioAnalyzer()
        portfolio_analysis = analyzer.get_diversification_recommendations(user)
        portfolio_analysis['category_distribution'] = {k: float(v) for k, v in portfolio_analysis['category_distribution'].items()}
        portfolio_analysis['technology_distribution'] = {k: float(v) for k, v in portfolio_analysis['technology_distribution'].items()}
        portfolio_recommendations = portfolio_analysis['recommendations']
    except Exception as e:
        portfolio_analysis = {'category_distribution': {}, 'technology_distribution': {}, 'recommendations': []}
        portfolio_recommendations = []
        print(f"Portfolio analysis error: {str(e)}")

    context = {
        'user': user,
        'total_invested': total_invested,
        'total_impact': total_impact,
        'recent_investments': recent_investments,
        'category_distribution': category_distribution,
        'monthly_trends': monthly_trends,
        'impact_by_category': dict(impact_by_category),
        'portfolio_analysis': json.dumps(portfolio_analysis, cls=DjangoJSONEncoder),
        'portfolio_recommendations': portfolio_recommendations,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'users/profile.html', context)

@login_required
def user_initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    user_investments = request.user.investments.filter(initiative=initiative)
    
    # Calculate total invested amount and impact with explicit FloatField
    totals = user_investments.aggregate(
        total_invested=Coalesce(Sum('amount'), 0, output_field=DecimalField()),
        carbon=Coalesce(Sum('carbon_impact'), 0, output_field=models.FloatField()),
        energy=Coalesce(Sum('energy_impact'), 0, output_field=models.FloatField()),
        water=Coalesce(Sum('water_impact'), 0, output_field=models.FloatField())
    )
    total_invested = totals['total_invested']
    impact_metrics = {
        'carbon': round(totals['carbon']),
        'energy': round(totals['energy']),
        'water': round(totals['water'])
    }
    
    # Get investment history
    investment_history = user_investments.order_by('-created_at')
    
    context = {
        'initiative': initiative,
        'total_invested': total_invested,
        'impact_metrics': impact_metrics,
        'investment_history': investment_history,
        'total_investors': initiative.investments.values('user').distinct().count(),
    }
    return render(request, 'users/user_initiative_detail.html', context)