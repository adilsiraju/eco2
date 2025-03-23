from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm
from django.db.models import Sum
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

    # Separate initiative and company investments
    initiative_investments = investments.filter(initiative__isnull=False)
    company_investments = investments.filter(company__isnull=False)

    # Calculate totals
    total_invested = sum(inv.amount for inv in investments)
    total_carbon_reduced = sum(inv.carbon_reduced for inv in investments)
    total_energy_saved = sum(inv.energy_saved for inv in investments)
    total_water_conserved = sum(inv.water_conserved for inv in investments)
    total_holdings = investments.count()

    context = {
        'initiative_investments': initiative_investments,
        'company_investments': company_investments,
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