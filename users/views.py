from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from django.db.models import Sum, Count
from investments.models import Investment
from initiatives.models import Initiative, Category
from .models import Profile
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder
from investments.portfolio_analyzer import PortfolioAnalyzer
from investments.impact_calculator import ImpactCalculator
from django.db.models.functions import Coalesce
from django.db.models import DecimalField, FloatField
from collections import defaultdict

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Profile instance only if it doesn't exist
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
    
    # Initialize impact calculator
    impact_calculator = ImpactCalculator()
    
    # Calculate total impact metrics using ImpactCalculator
    total_impact = {
        'carbon': 0,
        'energy': 0,
        'water': 0
    }
    
    # Initialize category impact dictionary
    impact_by_category = defaultdict(lambda: {'carbon': 0, 'energy': 0, 'water': 0})
    
    # Group investments by initiative and calculate total amount and impact
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
    
    # Get recent investments (based on last investment date) and calculate their impact
    recent_investments = sorted(
        grouped_investments.values(),
        key=lambda x: x['last_investment_date'],
        reverse=True
    )[:5]
    
    for investment_data in recent_investments:
        initiative = investment_data['initiative']
        total_amount = investment_data['total_amount']
        
        # Get category names for the initiative
        category_names = [cat.name for cat in initiative.categories.all()]
        
        # Calculate impact for this investment
        carbon, energy, water = impact_calculator.predict_impact(
            investment_amount=float(total_amount),
            category_names=category_names,
            project_duration_months=initiative.duration_months,
            project_scale=initiative.project_scale,
            location=initiative.location,
            technology_type=initiative.technology_type
        )
        
        # Store the impact metrics
        investment_data['impact_metrics'] = {
            'carbon': round(carbon),
            'energy': round(energy),
            'water': round(water)
        }
        
        # Add to total impact
        total_impact['carbon'] += carbon
        total_impact['energy'] += energy
        total_impact['water'] += water
        
        # Add to category impact
        for category_name in category_names:
            # Calculate impact for this category
            cat_carbon, cat_energy, cat_water = impact_calculator.predict_impact(
                investment_amount=float(total_amount),
                category_names=[category_name],  # Calculate impact for this category only
                project_duration_months=initiative.duration_months,
                project_scale=initiative.project_scale,
                location=initiative.location,
                technology_type=initiative.technology_type
            )
            
            # Add to category totals
            impact_by_category[category_name]['carbon'] += cat_carbon
            impact_by_category[category_name]['energy'] += cat_energy
            impact_by_category[category_name]['water'] += cat_water
    
    # Round the impact metrics
    total_impact = {
        'carbon': round(total_impact['carbon']),
        'energy': round(total_impact['energy']),
        'water': round(total_impact['water'])
    }
    
    # Round category impacts
    for category in impact_by_category:
        impact_by_category[category] = {
            'carbon': round(impact_by_category[category]['carbon']),
            'energy': round(impact_by_category[category]['energy']),
            'water': round(impact_by_category[category]['water'])
        }
    
    # Get investment distribution by category
    category_distribution = investments.values(
        'initiative__categories__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Get monthly investment trends
    monthly_trends = investments.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Initialize portfolio analyzer and get recommendations
    try:
        analyzer = PortfolioAnalyzer()
        portfolio_analysis = analyzer.get_diversification_recommendations(user)
        
        # Convert Decimal values to float for JSON serialization
        portfolio_analysis['category_distribution'] = {
            k: float(v) for k, v in portfolio_analysis['category_distribution'].items()
        }
        portfolio_analysis['technology_distribution'] = {
            k: float(v) for k, v in portfolio_analysis['technology_distribution'].items()
        }
        
        portfolio_recommendations = portfolio_analysis['recommendations']
    except Exception as e:
        # If there's an error in portfolio analysis, provide default values
        portfolio_analysis = {
            'category_distribution': {},
            'technology_distribution': {},
            'recommendations': []
        }
        portfolio_recommendations = []
        print(f"Portfolio analysis error: {str(e)}")  # Log the error
    
    context = {
        'user': user,
        'total_invested': total_invested,
        'total_impact': total_impact,
        'recent_investments': recent_investments,
        'category_distribution': category_distribution,
        'monthly_trends': monthly_trends,
        'impact_by_category': dict(impact_by_category),  # Convert defaultdict to regular dict
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
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile.html', context)

@login_required
def user_initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    user_investments = request.user.investments.filter(initiative=initiative)
    
    # Calculate total invested amount
    total_invested = user_investments.aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']
    
    # Initialize impact calculator
    impact_calculator = ImpactCalculator()
    
    # Get category names
    category_names = [cat.name for cat in initiative.categories.all()]
    
    # Calculate impact for total investment
    carbon, energy, water = impact_calculator.predict_impact(
        investment_amount=float(total_invested),
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