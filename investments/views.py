from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from initiatives.models import Initiative
from .models import Investment, InvestmentGoal
from .impact_calculator import ImpactCalculator
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.http import JsonResponse

# Note: Avoid global instantiation of ImpactCalculator due to potential threading issues
# We'll instantiate it within the view instead

@login_required
def invest_initiative(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount = Decimal(amount)
                if amount < initiative.min_investment:
                    messages.error(request, f'Minimum investment amount is ₹{initiative.min_investment:,}')
                elif initiative.max_investment and amount > initiative.max_investment:
                    messages.error(request, f'Maximum investment amount is ₹{initiative.max_investment:,}')
                else:
                    # Create the investment
                    investment = Investment.objects.create(
                        user=request.user,
                        initiative=initiative,
                        amount=amount
                    )
                    
                    messages.success(request, f'Successfully invested ₹{amount:,} in {initiative.title}')
                    return redirect('initiative_detail', pk=initiative.pk)
            except (ValueError, InvalidOperation):
                messages.error(request, 'Please enter a valid amount')
        # If amount is invalid or not provided, continue to GET rendering with default impact
    
    # Calculate impact metrics for the template using AI predictions
    # Use the user-provided amount if valid, otherwise default to min_investment
    try:
        amount = Decimal(request.POST.get('amount', initiative.min_investment))
        if amount < initiative.min_investment:
            amount = initiative.min_investment
        elif initiative.max_investment and amount > initiative.max_investment:
            amount = initiative.max_investment
    except (ValueError, InvalidOperation):
        amount = initiative.min_investment
    
    impact_metrics = Investment.calculate_impact_for_amount(initiative, amount)
    # impact_metrics is now a dict: {'carbon': value, 'energy': value, 'water': value}
    
    context = {
        'initiative': initiative,
        'impact_metrics': impact_metrics,
        'min_investment': initiative.min_investment,
        'max_investment': initiative.max_investment,
        'roi_estimate': initiative.roi_estimate,
        'risk_level': initiative.get_risk_label(),
        'progress_percentage': initiative.get_progress_percentage()
    }
    
    return render(request, 'investments/invest.html', context)

@login_required
def add_investment_goal(request):
    if request.method == 'POST':
        goal_type = request.POST.get('goal_type')
        target_date = request.POST.get('target_date')
        
        goal = InvestmentGoal(
            user=request.user,
            goal_type=goal_type,
            target_date=target_date
        )
        
        # Set target values based on goal type
        if goal_type == 'amount':
            goal.target_amount = Decimal(request.POST.get('target_amount'))
        elif goal_type == 'impact':
            goal.target_carbon = float(request.POST.get('target_carbon', 0))
            goal.target_energy = float(request.POST.get('target_energy', 0))
            goal.target_water = float(request.POST.get('target_water', 0))
        
        goal.save()
        messages.success(request, 'Investment goal added successfully!')
        return redirect('dashboard')
    
    return render(request, 'investments/add_goal.html')


@login_required
def impact_preview(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    try:
        amount = Decimal(request.GET.get('amount', initiative.min_investment))
        if amount < initiative.min_investment:
            amount = initiative.min_investment
        elif initiative.max_investment and amount > initiative.max_investment:
            amount = initiative.max_investment
    except (ValueError, InvalidOperation):
        amount = initiative.min_investment
    
    impact = Investment.calculate_impact_for_amount(initiative, amount)
    return JsonResponse(impact)