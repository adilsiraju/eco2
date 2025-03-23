from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from initiatives.models import Initiative
from .models import Investment
from .impact_calculator import ImpactCalculator
from decimal import Decimal


impact_calculator = ImpactCalculator()

@login_required
def invest(request, initiative_id):
    initiative = get_object_or_404(Initiative, pk=initiative_id)
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        carbon_reduced, energy_saved, water_conserved = impact_calculator.predict_impact(
            investment_amount=amount,
            category_name=initiative.category.name,
            project_duration_months=initiative.duration_months,
            project_scale=initiative.project_scale,
            location=initiative.location,
            technology_type=initiative.technology_type
        )
        investment = Investment(
            user=request.user,
            initiative=initiative,
            amount=amount,
            carbon_reduced=carbon_reduced,
            energy_saved=energy_saved,
            water_conserved=water_conserved
        )
        investment.save()
        initiative.current_amount += amount
        initiative.save()
        profile = request.user.profile
        profile.carbon_reduced += carbon_reduced
        profile.energy_saved += energy_saved
        profile.water_conserved += water_conserved
        profile.save()
        return redirect('initiative_detail', pk=initiative.id)
    return render(request, 'investments/invest.html', {'initiative': initiative})