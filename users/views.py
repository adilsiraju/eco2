from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from django.db.models import Sum
from investments.models import Investment
from initiatives.models import Initiative
from .models import Profile

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Profile instance only if it doesn’t exist
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

    context = {
        'initiative_investments': initiative_investments,
        'initiatives': Initiative.objects.all(),  # For lookup filter
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