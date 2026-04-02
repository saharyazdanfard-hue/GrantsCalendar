#!/usr/bin/env python3
"""
McPherson Lab - Trainee Compensation & Breakeven Calculator

This script calculates the compensation package for trainees with a base
package plus 90/10 revenue sharing model and determines the breakeven
productivity required per trainee.
"""

import math

# 2026 Contribution Limits
HSA_LIMIT_INDIVIDUAL = 4300
HSA_LIMIT_FAMILY = 8550
RETIREMENT_403B_LIMIT = 23500
ROTH_IRA_LIMIT = 7000

# Base Package Components
ANNUAL_RENT = 24000
ANNUAL_INCIDENTALS = 12000

# Revenue Sharing (NEW: 90/10 split for realistic breakeven)
LAB_REVENUE_SHARE = 0.90  # 90% to lab
TRAINEE_REVENUE_SHARE = 0.10  # 10% to trainee

# Lab Configuration
NUMBER_OF_TRAINEES = 8  # Total number of trainees (removed toxicology)

# NEW REVENUE MODEL: 15 newsletters total (8 trainee + 7 PI)
# Target: 10 monthly subscribers @ $8/month across all newsletters
SUBSTACK_SUBSCRIPTION_MONTHLY = 8  # $8/month per subscriber
SUBSTACK_SUBSCRIBERS_TARGET = 10  # Target 10 subscribers per newsletter
SUBSTACK_SUBSCRIPTION_ANNUAL = SUBSTACK_SUBSCRIPTION_MONTHLY * 12  # $96 per subscriber per year
NEWSLETTER_ANNUAL_TARGET = SUBSTACK_SUBSCRIBERS_TARGET * SUBSTACK_SUBSCRIPTION_ANNUAL  # $960 per newsletter per year
TOTAL_REVENUE_TARGET_PER_TRAINEE = NEWSLETTER_ANNUAL_TARGET  # $960 per trainee

# Trainee Newsletters (8 total - removed toxicology)
SUBSTACK_NEWSLETTERS = [
    "infectiousdiseases",
    "humanmicrobiome",
    "antimicrobialresistance",
    "structuralbiology",
    "immunology",
    "computationalbiology",
    "pharmacoepidemiology",
    "pharmacoeconomics"
]

# PI's Newsletters (7 total)
PI_NEWSLETTERS = [
    "diseaseprevention",
    "toxicology",
    "thehealthofnations",
    "scienceeducation",
    "sciencecommunication",
    "primaryeducation",
    "epidemic"
]
PI_NEWSLETTER_ANNUAL_TARGET = NEWSLETTER_ANNUAL_TARGET  # $960 per PI newsletter
PI_TOTAL_NEWSLETTER_REVENUE = len(PI_NEWSLETTERS) * PI_NEWSLETTER_ANNUAL_TARGET  # $6,720 total from 7 newsletters

# PI's Medium Friend Partner Program (unchanged)
MEDIUM_MONTHLY_PRICE = 15  # $15/month per friend
MEDIUM_ESTIMATED_READERS = 100  # Estimated 100 readers
MEDIUM_ANNUAL_REVENUE = MEDIUM_MONTHLY_PRICE * 12 * MEDIUM_ESTIMATED_READERS  # $18,000/year

# Total PI Revenue
PI_TOTAL_REVENUE = PI_TOTAL_NEWSLETTER_REVENUE + MEDIUM_ANNUAL_REVENUE  # $24,720/year

# Tax Rates (2026 estimates)
FEDERAL_TAX_BRACKETS = [
    (11925, 0.10),
    (48475, 0.12),
    (103350, 0.22),
    (197300, 0.24),
    (250525, 0.32),
    (626350, 0.35),
    (float('inf'), 0.37)
]

SOCIAL_SECURITY_RATE = 0.062
MEDICARE_RATE = 0.0145
EMPLOYER_FICA_RATE = 0.0765


def calculate_federal_tax(taxable_income):
    """Calculate federal income tax based on 2026 tax brackets for single filers."""
    tax = 0
    previous_bracket = 0
    
    for bracket_limit, rate in FEDERAL_TAX_BRACKETS:
        if taxable_income <= bracket_limit:
            tax += (taxable_income - previous_bracket) * rate
            break
        else:
            tax += (bracket_limit - previous_bracket) * rate
            previous_bracket = bracket_limit
    
    return tax


def calculate_base_package_value():
    """Calculate the total value of the base package."""
    total_savings = HSA_LIMIT_INDIVIDUAL + RETIREMENT_403B_LIMIT + ROTH_IRA_LIMIT
    return total_savings + ANNUAL_RENT + ANNUAL_INCIDENTALS


def calculate_required_gross_salary():
    """
    Calculate the gross salary required to fund the base package.
    
    The gross salary must cover:
    - Pre-tax deductions (HSA + 403b)
    - Taxes (Federal + FICA)
    - Post-tax Roth IRA
    - Net amount for rent and incidentals
    """
    # Target net amount needed after all deductions and taxes
    target_net = ANNUAL_RENT + ANNUAL_INCIDENTALS + ROTH_IRA_LIMIT
    
    # Iterate to find the gross salary that yields the target net
    # Starting estimate
    gross_salary = 84000
    
    for _ in range(10):  # Iterate to converge
        pre_tax = HSA_LIMIT_INDIVIDUAL + RETIREMENT_403B_LIMIT
        taxable = gross_salary - pre_tax
        federal_tax = calculate_federal_tax(taxable)
        fica = gross_salary * (SOCIAL_SECURITY_RATE + MEDICARE_RATE)
        net = gross_salary - pre_tax - federal_tax - fica
        
        if abs(net - target_net) < 100:  # Close enough
            break
        
        # Adjust gross salary
        gross_salary += (target_net - net) * 1.4  # Factor to account for marginal tax
    
    return gross_salary


def calculate_compensation_package():
    """
    Calculate the compensation package for a trainee.
    
    Returns:
        Dictionary with compensation breakdown
    """
    base_package_value = calculate_base_package_value()
    gross_salary = calculate_required_gross_salary()
    
    # Pre-tax deductions
    hsa_contribution = HSA_LIMIT_INDIVIDUAL
    retirement_403b = RETIREMENT_403B_LIMIT
    pre_tax_deductions = hsa_contribution + retirement_403b
    taxable_income = gross_salary - pre_tax_deductions
    
    # Calculate taxes
    federal_tax = calculate_federal_tax(taxable_income)
    social_security_tax = gross_salary * SOCIAL_SECURITY_RATE
    medicare_tax = gross_salary * MEDICARE_RATE
    total_fica = social_security_tax + medicare_tax
    
    # Net pay calculation
    net_pay = gross_salary - pre_tax_deductions - federal_tax - total_fica
    
    # After Roth IRA (post-tax)
    after_roth = net_pay - ROTH_IRA_LIMIT
    
    return {
        'gross_salary': gross_salary,
        'hsa_contribution': hsa_contribution,
        '403b_contribution': retirement_403b,
        'roth_ira_contribution': ROTH_IRA_LIMIT,
        'total_savings': hsa_contribution + retirement_403b + ROTH_IRA_LIMIT,
        'annual_rent': ANNUAL_RENT,
        'annual_incidentals': ANNUAL_INCIDENTALS,
        'base_package_value': base_package_value,
        'pre_tax_deductions': pre_tax_deductions,
        'taxable_income': taxable_income,
        'federal_tax': federal_tax,
        'social_security_tax': social_security_tax,
        'medicare_tax': medicare_tax,
        'total_fica': total_fica,
        'net_pay': net_pay,
        'after_roth_ira': after_roth,
        'available_for_rent_incidentals': after_roth
    }


def calculate_employer_costs():
    """
    Calculate total employer costs per trainee.
    
    Returns:
        Dictionary with cost breakdown
    """
    gross_salary = calculate_required_gross_salary()
    employer_fica = gross_salary * EMPLOYER_FICA_RATE
    benefits_admin = 1000  # Estimated
    
    # Indirect costs
    office_space = 3000
    equipment_supplies = 2000
    software_tools = 1500
    training_dev = 1500
    insurance = 1000
    admin_overhead = 2000
    
    total_indirect = (office_space + equipment_supplies + software_tools + 
                     training_dev + insurance + admin_overhead)
    
    total_cost = gross_salary + employer_fica + benefits_admin + total_indirect
    
    return {
        'gross_salary': gross_salary,
        'employer_fica': employer_fica,
        'benefits_admin': benefits_admin,
        'office_space': office_space,
        'equipment_supplies': equipment_supplies,
        'software_tools': software_tools,
        'training_dev': training_dev,
        'insurance': insurance,
        'admin_overhead': admin_overhead,
        'total_indirect': total_indirect,
        'total_annual_cost': total_cost
    }


def calculate_breakeven_with_revenue_sharing(base_costs):
    """
    Calculate breakeven scenarios with 90/10 revenue sharing model.
    
    NEW MODEL (8 trainees + PI):
    - Each trainee assigned 1 newsletter (out of 8 total)
    - Each newsletter targets 10 subscribers @ $8/month = $960/year
    - Total per trainee: $960/year
    - With 90/10 split: Lab gets $864 per trainee (insufficient to cover $103k costs)
    - PI has 7 newsletters + Medium Friend Partner Program
    - Total: 15 monetized newsletters (8 trainee + 7 PI)
    
    Args:
        base_costs: Total annual base costs per trainee (~$103k)
    
    Returns:
        Dictionary with breakeven scenarios
    """
    # With 90/10 revenue sharing, lab needs to generate enough revenue
    # so that its 90% share covers base costs
    breakeven_revenue = base_costs / LAB_REVENUE_SHARE  # ~$115k
    
    # Current target: Newsletter only = $960 per trainee
    # With 90/10 split: Lab gets $864 (far below $103k costs - requires additional subscribers)
    
    result = {
        'base_costs': base_costs,
        'breakeven_total_revenue': breakeven_revenue,
        'lab_share_at_breakeven': base_costs,
        'trainee_share_at_breakeven': breakeven_revenue * TRAINEE_REVENUE_SHARE,
        'subscribers_needed_for_breakeven': math.ceil(breakeven_revenue / SUBSTACK_SUBSCRIPTION_ANNUAL),
        'number_of_trainees': NUMBER_OF_TRAINEES,
        'breakeven_scenario': {
            'description': 'Breakeven with newsletter-only revenue model (8 trainees)',
            'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
            'newsletter_subscribers_current': SUBSTACK_SUBSCRIBERS_TARGET,
            'newsletter_subscribers_needed_for_breakeven': math.ceil(breakeven_revenue / SUBSTACK_SUBSCRIPTION_ANNUAL),
            'newsletter_revenue': NEWSLETTER_ANNUAL_TARGET,
            'total_revenue': NEWSLETTER_ANNUAL_TARGET,
        },
        'assignment_matrix': {
            'description': f'Assignment of 8 trainees to 8 newsletters (10 subscribers @ ${SUBSTACK_SUBSCRIPTION_MONTHLY}/mo each)',
            'trainee_1': {
                'newsletter': 'infectiousdiseases',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            },
            'trainee_2': {
                'newsletter': 'humanmicrobiome',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            },
            'trainee_3': {
                'newsletter': 'antimicrobialresistance',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            },
            'trainee_4': {
                'newsletter': 'structuralbiology',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            },
            'trainee_5': {
                'newsletter': 'immunology',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            },
            'trainee_6': {
                'newsletter': 'computationalbiology',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            },
            'trainee_7': {
                'newsletter': 'pharmacoepidemiology',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            },
            'trainee_8': {
                'newsletter': 'pharmacoeconomics',
                'newsletter_target': NEWSLETTER_ANNUAL_TARGET,
                'total_revenue': NEWSLETTER_ANNUAL_TARGET
            }
        },
        'pi_revenue_streams': {
            'newsletters': {
                'count': len(PI_NEWSLETTERS),
                'names': PI_NEWSLETTERS,
                'revenue_per_newsletter': PI_NEWSLETTER_ANNUAL_TARGET,
                'total_newsletter_revenue': PI_TOTAL_NEWSLETTER_REVENUE,
                'lab_share': PI_TOTAL_NEWSLETTER_REVENUE * LAB_REVENUE_SHARE,
            },
            'medium_friend_partner': {
                'name': 'Medium Friend Partner Program',
                'monthly_price': MEDIUM_MONTHLY_PRICE,
                'estimated_readers': MEDIUM_ESTIMATED_READERS,
                'annual_revenue': MEDIUM_ANNUAL_REVENUE,
                'lab_share': MEDIUM_ANNUAL_REVENUE * LAB_REVENUE_SHARE,
            },
            'total_pi_revenue': PI_TOTAL_REVENUE,
            'total_pi_lab_share': PI_TOTAL_REVENUE * LAB_REVENUE_SHARE,
            'note': 'No salary or breakeven analysis needed for PI revenue streams'
        }
    }
    
    # Calculate metrics for breakeven scenario
    scen = result['breakeven_scenario']
    scen['lab_share'] = scen['total_revenue'] * LAB_REVENUE_SHARE
    scen['trainee_revenue_share'] = scen['total_revenue'] * TRAINEE_REVENUE_SHARE
    scen['lab_net'] = scen['lab_share'] - base_costs
    scen['trainee_total_comp'] = calculate_base_package_value() + scen['trainee_revenue_share']
    
    # Calculate metrics for each trainee in assignment matrix
    for trainee_key in ['trainee_1', 'trainee_2', 'trainee_3', 'trainee_4', 
                        'trainee_5', 'trainee_6', 'trainee_7', 'trainee_8']:
        trainee = result['assignment_matrix'][trainee_key]
        trainee['lab_share'] = trainee['total_revenue'] * LAB_REVENUE_SHARE
        trainee['trainee_revenue_share'] = trainee['total_revenue'] * TRAINEE_REVENUE_SHARE
        trainee['lab_net'] = trainee['lab_share'] - base_costs
        trainee['trainee_total_comp'] = calculate_base_package_value() + trainee['trainee_revenue_share']
    
    return result


def print_compensation_report(comp):
    """Print formatted compensation report."""
    print("\n" + "="*60)
    print("MCPHERSON LAB - TRAINEE COMPENSATION ANALYSIS")
    print("="*60)
    print("\n🎁 BASE PACKAGE (Guaranteed)")
    print(f"  Total Savings:")
    print(f"    HSA Contribution:         ${comp['hsa_contribution']:,.2f}")
    print(f"    403(b) Contribution:      ${comp['403b_contribution']:,.2f}")
    print(f"    Roth IRA Contribution:    ${comp['roth_ira_contribution']:,.2f}")
    print(f"    Subtotal Savings:         ${comp['total_savings']:,.2f}")
    print(f"  Living Expenses:")
    print(f"    Annual Rent Allowance:    ${comp['annual_rent']:,.2f}")
    print(f"    Annual Incidentals:       ${comp['annual_incidentals']:,.2f}")
    print(f"  {'─'*40}")
    print(f"  BASE PACKAGE VALUE:         ${comp['base_package_value']:,.2f}")
    
    print("\n💰 REQUIRED GROSS SALARY")
    print(f"  To fund the base package, the lab provides:")
    print(f"  Gross Salary:               ${comp['gross_salary']:,.2f}")
    
    print("\n📊 TAX ANALYSIS")
    print(f"  Gross Salary:               ${comp['gross_salary']:,.2f}")
    print(f"  Pre-tax Deductions:        -${comp['pre_tax_deductions']:,.2f}")
    print(f"  Taxable Income:             ${comp['taxable_income']:,.2f}")
    print(f"  Federal Tax:               -${comp['federal_tax']:,.2f}")
    print(f"  FICA Tax:                  -${comp['total_fica']:,.2f}")
    print(f"  {'─'*40}")
    print(f"  Net Pay:                    ${comp['net_pay']:,.2f}")
    print(f"  Roth IRA (post-tax):       -${comp['roth_ira_contribution']:,.2f}")
    print(f"  {'─'*40}")
    print(f"  Available for Rent+Incidentals: ${comp['available_for_rent_incidentals']:,.2f}")
    print(f"  (Target: ${ANNUAL_RENT + ANNUAL_INCIDENTALS:,.2f})")
    
    print("\n🚀 PLUS: 90/10 REVENUE SHARING")
    print(f"  Lab receives 90% of revenue (to cover costs)")
    print(f"  Trainees receive 10% of revenue they generate")
    print(f"  Example: Generate $200k → Lab gets $180k, Trainee gets $20k + base package")


def print_employer_cost_report(costs):
    """Print formatted employer cost report."""
    print("\n" + "="*60)
    print("EMPLOYER BASE COSTS PER TRAINEE")
    print("="*60)
    
    print("\n💼 DIRECT COSTS")
    print(f"  Gross Salary:               ${costs['gross_salary']:,.2f}")
    print(f"  Employer FICA:              ${costs['employer_fica']:,.2f}")
    print(f"  Benefits Admin:             ${costs['benefits_admin']:,.2f}")
    print(f"  {'─'*40}")
    print(f"  Total Direct:               ${costs['gross_salary'] + costs['employer_fica'] + costs['benefits_admin']:,.2f}")
    
    print("\n🏢 INDIRECT COSTS")
    print(f"  Office Space/Lab:           ${costs['office_space']:,.2f}")
    print(f"  Equipment/Supplies:         ${costs['equipment_supplies']:,.2f}")
    print(f"  Software/Tools:             ${costs['software_tools']:,.2f}")
    print(f"  Training & Development:     ${costs['training_dev']:,.2f}")
    print(f"  Insurance:                  ${costs['insurance']:,.2f}")
    print(f"  Admin Overhead:             ${costs['admin_overhead']:,.2f}")
    print(f"  {'─'*40}")
    print(f"  Total Indirect:             ${costs['total_indirect']:,.2f}")
    
    print(f"\n{'='*60}")
    print(f"  TOTAL ANNUAL BASE COST:     ${costs['total_annual_cost']:,.2f}")
    print(f"{'='*60}")
    print(f"  Note: This is before revenue sharing payments")


def print_breakeven_report(breakeven):
    """Print formatted breakeven analysis report."""
    print("\n" + "="*60)
    print("BREAKEVEN ANALYSIS WITH 90/10 REVENUE SHARING")
    print("="*60)
    
    print(f"\n🎯 NEW MODEL: {breakeven['number_of_trainees']} Trainees")
    print(f"  Base Costs per Trainee:     ${breakeven['base_costs']:,.2f}")
    print(f"  With 90/10 sharing, each trainee needs to generate:")
    print(f"  Required Total Revenue:     ${breakeven['breakeven_total_revenue']:,.2f}")
    print(f"    → Lab receives 90%:       ${breakeven['lab_share_at_breakeven']:,.2f}")
    print(f"    → Trainee receives 10%:   ${breakeven['trainee_share_at_breakeven']:,.2f}")
    
    print(f"\n📰 ASSIGNMENT STRUCTURE:")
    print(f"  • {NUMBER_OF_TRAINEES} Trainees → {NUMBER_OF_TRAINEES} Newsletters (1 each)")
    print(f"  • Each newsletter targets: {SUBSTACK_SUBSCRIBERS_TARGET} subscribers @ ${SUBSTACK_SUBSCRIPTION_MONTHLY}/mo")
    print(f"  • Revenue per newsletter: ${NEWSLETTER_ANNUAL_TARGET:,.0f}/year")
    print(f"  • Total per trainee: ${TOTAL_REVENUE_TARGET_PER_TRAINEE:,.0f}/year")
    print(f"  • Note: At current targets, need {breakeven['subscribers_needed_for_breakeven']} subscribers @ ${SUBSTACK_SUBSCRIPTION_MONTHLY}/mo per newsletter for breakeven")
    
    print(f"\n💼 CURRENT TARGET SCENARIO (Per Trainee)")
    scen = breakeven['breakeven_scenario']
    print(f"  Newsletter revenue target:  ${scen['newsletter_revenue']:,.2f}")
    print(f"    ({scen['newsletter_subscribers_current']} subscribers @ ${SUBSTACK_SUBSCRIPTION_MONTHLY}/mo)")
    print(f"    (Need {scen['newsletter_subscribers_needed_for_breakeven']} subscribers for breakeven)")
    print(f"  {'─'*40}")
    print(f"  Total Revenue:              ${scen['total_revenue']:,.2f}")
    print(f"  Lab's 90%:                  ${scen['lab_share']:,.2f}")
    print(f"  Lab's Net:                  ${scen['lab_net']:,.2f}")
    if scen['lab_net'] < 0:
        print(f"  ⚠️  Below breakeven by ${abs(scen['lab_net']):,.2f}")
    elif scen['lab_net'] < 5000:
        print(f"  ✓ Near breakeven (within $5k)")
    else:
        print(f"  ✅ Profitable")
    print(f"  Trainee's Total Comp:       ${scen['trainee_total_comp']:,.2f}")
    print(f"    (Base: ${calculate_base_package_value():,.2f} + Share: ${scen['trainee_revenue_share']:,.2f})")
    
    print(f"\n👥 TRAINEE ASSIGNMENTS:")
    matrix = breakeven['assignment_matrix']
    trainee_keys = ['trainee_1', 'trainee_2', 'trainee_3', 'trainee_4',
                    'trainee_5', 'trainee_6', 'trainee_7', 'trainee_8']
    for i, key in enumerate(trainee_keys, 1):
        trainee = matrix[key]
        print(f"\n  Trainee {i}:")
        print(f"    Newsletter: {trainee['newsletter']} (${trainee['newsletter_target']:,.0f}/yr)")
        print(f"    Total Revenue: ${trainee['total_revenue']:,.0f}")
        print(f"    Lab Net: ${trainee['lab_net']:,.0f}")
        print(f"    Trainee Comp: ${trainee['trainee_total_comp']:,.0f}")
    
    # Add PI Revenue Streams
    print(f"\n🎓 PI REVENUE STREAMS:")
    pi = breakeven['pi_revenue_streams']
    print(f"    {pi['newsletters']['count']} Substack Newsletters:")
    for nl in pi['newsletters']['names']:
        print(f"      • {nl}")
    print(f"      Revenue per newsletter: ${pi['newsletters']['revenue_per_newsletter']:,.0f}")
    print(f"      Total Newsletter Revenue: ${pi['newsletters']['total_newsletter_revenue']:,.0f}")
    print(f"      Lab's 90% Share: ${pi['newsletters']['lab_share']:,.0f}")
    print(f"    Medium Friend Partner Program:")
    print(f"      ${pi['medium_friend_partner']['monthly_price']}/mo × {pi['medium_friend_partner']['estimated_readers']} readers")
    print(f"      Annual Revenue: ${pi['medium_friend_partner']['annual_revenue']:,.0f}")
    print(f"      Lab's 90% Share: ${pi['medium_friend_partner']['lab_share']:,.0f}")
    print(f"    {'─'*40}")
    print(f"    Total PI Revenue: ${pi['total_pi_revenue']:,.0f}")
    print(f"    Total Lab's Share: ${pi['total_pi_lab_share']:,.0f}")
    print(f"    Note: {pi['note']}")
    
    print(f"\n📊 LAB-WIDE TOTALS ({breakeven['number_of_trainees']} trainees + PI):")
    print(f"  TOTAL NEWSLETTERS: {NUMBER_OF_TRAINEES + len(PI_NEWSLETTERS)} ({NUMBER_OF_TRAINEES} trainee + {len(PI_NEWSLETTERS)} PI)")
    total_lab_revenue = NEWSLETTER_ANNUAL_TARGET * NUMBER_OF_TRAINEES + PI_TOTAL_REVENUE
    total_lab_share = (NEWSLETTER_ANNUAL_TARGET * NUMBER_OF_TRAINEES * LAB_REVENUE_SHARE) + (PI_TOTAL_REVENUE * LAB_REVENUE_SHARE)
    total_lab_costs = breakeven['base_costs'] * NUMBER_OF_TRAINEES
    total_lab_net = total_lab_share - total_lab_costs
    print(f"  Trainee Revenue:            ${NEWSLETTER_ANNUAL_TARGET * NUMBER_OF_TRAINEES:,.0f}")
    print(f"  PI Revenue:                 ${PI_TOTAL_REVENUE:,.0f}")
    print(f"    (Newsletters: ${PI_TOTAL_NEWSLETTER_REVENUE:,.0f} + Medium: ${MEDIUM_ANNUAL_REVENUE:,.0f})")
    print(f"  Total Revenue:              ${total_lab_revenue:,.0f}")
    print(f"  Lab's 90% Share:            ${total_lab_share:,.0f}")
    print(f"  Total Base Costs:           ${total_lab_costs:,.0f}")
    print(f"  Lab's Net:                  ${total_lab_net:,.0f}")
    if total_lab_net < 0:
        print(f"  ⚠️  Lab operates at ${abs(total_lab_net):,.0f} deficit")
    else:
        margin = (total_lab_net / total_lab_revenue) * 100 if total_lab_revenue > 0 else 0
        print(f"  Lab Margin:                 {margin:.1f}%")


def main():
    """Main function to run all calculations and print reports."""
    # Calculate compensation
    compensation = calculate_compensation_package()
    print_compensation_report(compensation)
    
    # Calculate employer costs
    employer_costs = calculate_employer_costs()
    print_employer_cost_report(employer_costs)
    
    # Calculate breakeven with revenue sharing
    breakeven = calculate_breakeven_with_revenue_sharing(employer_costs['total_annual_cost'])
    print_breakeven_report(breakeven)
    
    print("\n" + "="*60)
    print("✅ SUMMARY")
    print("="*60)
    print(f"\n  Compensation Model: Base Package + 90/10 Revenue Sharing")
    print(f"\n  Base Package Value: ${compensation['base_package_value']:,.2f}")
    print(f"    - Max out all tax-advantaged savings: ${compensation['total_savings']:,.2f}")
    print(f"    - Rent covered: ${compensation['annual_rent']:,.2f}")
    print(f"    - Incidentals: ${compensation['annual_incidentals']:,.2f}")
    print(f"\n  Lab's Base Cost per Trainee: ${employer_costs['total_annual_cost']:,.2f}")
    print(f"\n  Revenue Model ({NUMBER_OF_TRAINEES} trainees):")
    print(f"    • Each trainee: 1 newsletter")
    print(f"    • Newsletter target: ${NEWSLETTER_ANNUAL_TARGET:,.0f}/year")
    print(f"      (Requires {SUBSTACK_SUBSCRIBERS_TARGET} subscribers @ ${SUBSTACK_SUBSCRIPTION_MONTHLY}/mo)")
    print(f"    • Total per trainee: ${TOTAL_REVENUE_TARGET_PER_TRAINEE:,.0f}/year")
    print(f"\n  Breakeven Analysis:")
    print(f"    - With 90/10 split: Lab gets ${TOTAL_REVENUE_TARGET_PER_TRAINEE * LAB_REVENUE_SHARE:,.0f} per trainee")
    print(f"    - Base costs: ${employer_costs['total_annual_cost']:,.0f} per trainee")
    shortfall = employer_costs['total_annual_cost'] - TOTAL_REVENUE_TARGET_PER_TRAINEE * LAB_REVENUE_SHARE
    if shortfall > 0:
        print(f"    - Shortfall: ${shortfall:,.0f} per trainee")
        print(f"    ⚠️  Need to increase total revenue by ~${shortfall / LAB_REVENUE_SHARE:,.0f} per trainee")
    else:
        surplus = abs(shortfall)
        print(f"    - Surplus: ${surplus:,.0f} per trainee")
        print(f"    ✅ Lab profitable with ${surplus:,.0f} profit per trainee")
    print(f"\n  Trainee Compensation at ${TOTAL_REVENUE_TARGET_PER_TRAINEE:,.0f} Revenue:")
    print(f"    - Base package: ${compensation['base_package_value']:,.0f}")
    print(f"    - Revenue share (10%): ${TOTAL_REVENUE_TARGET_PER_TRAINEE * TRAINEE_REVENUE_SHARE:,.0f}")
    print(f"    - Total: ${compensation['base_package_value'] + TOTAL_REVENUE_TARGET_PER_TRAINEE * TRAINEE_REVENUE_SHARE:,.0f}")
    print(f"\n  💡 Key Insight: 90/10 split creates realistic productivity expectations.")
    print(f"     Lab needs only ~$115k per trainee to break even (vs ~$206k with 50/50).")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
