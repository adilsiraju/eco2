from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from initiatives.models import Initiative
from .models import Investment

@login_required
def invest(request, initiative_id):
    initiative = get_object_or_404(Initiative, pk=initiative_id)
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        investment = Investment(
            user=request.user,
            initiative=initiative,
            amount=amount,
            carbon_reduced=amount * 0.5,  # Dummy calc
            energy_saved=amount * 1.2,
            water_conserved=amount * 0.8
        )
        investment.save()
        initiative.current_amount += amount
        initiative.save()
        profile = request.user.profile
        profile.carbon_reduced += investment.carbon_reduced
        profile.energy_saved += investment.energy_saved
        profile.water_conserved += investment.water_conserved
        profile.save()
        return redirect('initiative_detail', pk=initiative.id)
    return render(request, 'investments/invest.html', {'initiative': initiative})