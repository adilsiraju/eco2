from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm
from django.db.models import Sum
from investments.models import Investment
from initiatives.models import Initiative, Company
from investments.models import Investment

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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

    # Aggregate company investments
    company_investments = investments.filter(company__isnull=False).values(
        'company__id', 'company__name', 'company__share_price'
    ).annotate(
        total_amount=Sum('amount'),
        total_shares=Sum('shares_purchased'),
        total_carbon_reduced=Sum('carbon_reduced'),
        total_energy_saved=Sum('energy_saved'),
        total_water_conserved=Sum('water_conserved')
    ).order_by('company__id')

    # Calculate totals
    total_invested = sum(inv['total_amount'] for inv in initiative_investments) + sum(inv['total_amount'] for inv in company_investments)
    total_carbon_reduced = sum(inv['total_carbon_reduced'] for inv in initiative_investments) + sum(inv['total_carbon_reduced'] for inv in company_investments)
    total_energy_saved = sum(inv['total_energy_saved'] for inv in initiative_investments) + sum(inv['total_energy_saved'] for inv in company_investments)
    total_water_conserved = sum(inv['total_water_conserved'] for inv in initiative_investments) + sum(inv['total_water_conserved'] for inv in company_investments)
    total_holdings = initiative_investments.count() + company_investments.count()

    context = {
        'initiative_investments': initiative_investments,
        'company_investments': company_investments,
        'initiatives': Initiative.objects.all(),  # For lookup filter
        'companies': Company.objects.all(),       # For lookup filter
        'total_invested': total_invested,
        'total_carbon_reduced': total_carbon_reduced,
        'total_energy_saved': total_energy_saved,
        'total_water_conserved': total_water_conserved,
        'total_holdings': total_holdings,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user.profile)
    return render(request, 'users/profile.html', {'form': form})