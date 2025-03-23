from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm
from django.db.models import Sum

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
    # Calculate totals from investments
    totals = request.user.investments.aggregate(
        carbon_reduced_total=Sum('carbon_reduced'),
        energy_saved_total=Sum('energy_saved'),
        water_conserved_total=Sum('water_conserved')
    )
    
    context = {
        'user': request.user,
        'carbon_reduced_total': totals['carbon_reduced_total'] or 0,
        'energy_saved_total': totals['energy_saved_total'] or 0,
        'water_conserved_total': totals['water_conserved_total'] or 0,
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