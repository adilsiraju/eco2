from django.shortcuts import render, redirect
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
    # Fetch user's investments
    investments = Investment.objects.filter(user=request.user)

    # Aggregate initiative investments
    initiative_investments = investments.filter(initiative__isnull=False).values(
        'initiative__id', 'initiative__title'
    ).annotate(
        total_amount=Sum('amount'),
        total_carbon_reduced=Sum('carbon_reduced'),
        total_energy_saved=Sum('energy_saved'),
        total_water_conserved=Sum('water_conserved')
    ).order_by('initiative__id')

    # Calculate totals
    total_invested = sum(inv['total_amount'] for inv in initiative_investments)
    total_carbon_reduced = sum(inv['total_carbon_reduced'] for inv in initiative_investments)
    total_energy_saved = sum(inv['total_energy_saved'] for inv in initiative_investments)
    total_water_conserved = sum(inv['total_water_conserved'] for inv in initiative_investments)
    total_holdings = initiative_investments.count()

    # Get investment distribution by category
    category_investments = investments.values(
        'initiative__categories__name'
    ).annotate(
        total_amount=Sum('amount')
    ).exclude(initiative__categories__name__isnull=True)

    # Get monthly investment trends (last 12 months)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    monthly_investments = investments.filter(
        created_at__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_amount=Sum('amount'),
        total_carbon_reduced=Sum('carbon_reduced'),
        total_energy_saved=Sum('energy_saved'),
        total_water_conserved=Sum('water_conserved')
    ).order_by('month')

    # Convert Decimal and datetime objects to JSON-serializable format
    category_investments_json = json.dumps(list(category_investments), cls=DjangoJSONEncoder)
    monthly_investments_json = json.dumps(list(monthly_investments), cls=DjangoJSONEncoder)

    context = {
        'initiative_investments': initiative_investments,
        'initiatives': Initiative.objects.all(),  # For lookup filter
        'total_invested': total_invested,
        'total_carbon_reduced': total_carbon_reduced,
        'total_energy_saved': total_energy_saved,
        'total_water_conserved': total_water_conserved,
        'total_holdings': total_holdings,
        'category_investments': category_investments_json,
        'monthly_investments': monthly_investments_json,
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