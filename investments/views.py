from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from initiatives.models import Initiative, Company
from .models import Investment
from .impact_calculator import ImpactCalculator
from decimal import Decimal

impact_calculator = ImpactCalculator()

@login_required
def invest_initiative(request, initiative_id):
    initiative = get_object_or_404(Initiative, pk=initiative_id)
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        carbon_reduced, energy_saved, water_conserved = impact_calculator.predict_impact(
            investment_amount=amount,
            category_name=initiative.categories.first().name,
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
    return render(request, 'investments/invest.html', {'initiative': initiative, 'type': 'initiative'})

@login_required
def invest_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == 'POST':
        shares = int(request.POST.get('shares'))
        amount = shares * float(company.share_price)
        if shares > company.shares_remaining:
            return render(request, 'investments/invest.html', {
                'company': company,
                'type': 'company',
                'error': f"Only {company.shares_remaining} shares remaining."
            })
        carbon_reduced, energy_saved, water_conserved = impact_calculator.predict_impact(
            investment_amount=amount,
            category_name=company.categories.first().name,
            project_duration_months=company.duration_months,
            project_scale=company.company_scale,
            location=company.location
        )
        investment = Investment(
            user=request.user,
            company=company,
            amount=amount,
            shares_purchased=shares,
            carbon_reduced=carbon_reduced,
            energy_saved=energy_saved,
            water_conserved=water_conserved
        )
        investment.save()
        company.shares_sold += shares
        if company.shares_remaining == 0:
            company.status = 'funded'
        company.save()
        profile = request.user.profile
        profile.carbon_reduced += carbon_reduced
        profile.energy_saved += energy_saved
        profile.water_conserved += water_conserved
        profile.save()
        return redirect('company_detail', pk=company.id)
    return render(request, 'investments/invest.html', {'company': company, 'type': 'company'})