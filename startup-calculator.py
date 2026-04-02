#!/usr/bin/env python3
"""
McPherson Lab Startup Stage Financial Calculator

Calculates breakeven analysis for solo PI operation in startup stage.
No salary, focused on building revenue streams through newsletters, CE courses, and workshops.
"""

import math

# ============================================================================
# STARTUP STAGE CONSTANTS
# ============================================================================

# Office Costs
OFFICE_SIZE_SQ_FT = 400
OFFICE_COST_PER_SQ_FT_ANNUAL = 30
ANNUAL_OFFICE_RENT = OFFICE_SIZE_SQ_FT * OFFICE_COST_PER_SQ_FT_ANNUAL

# Startup Costs (one-time and annual recurring)
PLLC_FILING_COST = 500  # LegalZoom PLLC filing (one-time)
PLLC_ANNUAL_FEE = 300  # Annual state filing fee
GODADDY_WEBSITE_ANNUAL = 200  # Website hosting and domain
ZOOM_BUSINESS_ANNUAL = 200  # Zoom Business license annual

# Revenue Stream Pricing
NEWSLETTER_MONTHLY_PRICE = 10
NEWSLETTER_ANNUAL_PRICE = NEWSLETTER_MONTHLY_PRICE * 12
CE_COURSE_PRICE = 99  # Per course
WORKSHOP_PER_REGISTRANT = 10
WORKSHOP_ANNUAL_PASS = 60

# Revenue Stream Volumes
NUMBER_OF_NEWSLETTERS = 10
NUMBER_OF_CE_COURSES = 8
WORKSHOPS_PER_MONTH = 12
WORKSHOPS_PER_YEAR = WORKSHOPS_PER_MONTH * 12

# ============================================================================
# STARTUP STAGE CALCULATIONS
# ============================================================================

def calculate_startup_costs():
    """Calculate one-time and first-year startup costs."""
    one_time = PLLC_FILING_COST
    first_year_recurring = (
        ANNUAL_OFFICE_RENT +
        PLLC_ANNUAL_FEE +
        GODADDY_WEBSITE_ANNUAL +
        ZOOM_BUSINESS_ANNUAL
    )
    return one_time, first_year_recurring, one_time + first_year_recurring

def calculate_annual_operating_costs():
    """Calculate ongoing annual operating costs (excluding startup)."""
    return (
        ANNUAL_OFFICE_RENT +
        PLLC_ANNUAL_FEE +
        GODADDY_WEBSITE_ANNUAL +
        ZOOM_BUSINESS_ANNUAL
    )

def calculate_newsletter_revenue(subscribers_per_newsletter):
    """Calculate annual revenue from newsletters."""
    total_subscribers = subscribers_per_newsletter * NUMBER_OF_NEWSLETTERS
    annual_revenue = total_subscribers * NEWSLETTER_ANNUAL_PRICE
    return annual_revenue, total_subscribers

def calculate_ce_course_revenue(students_per_course):
    """Calculate annual revenue from CE courses."""
    total_students = students_per_course * NUMBER_OF_CE_COURSES
    annual_revenue = total_students * CE_COURSE_PRICE
    return annual_revenue, total_students

def calculate_workshop_revenue(registrants_per_workshop, annual_pass_buyers):
    """Calculate annual revenue from workshops."""
    # Per-workshop registrants
    total_workshop_registrations = registrants_per_workshop * WORKSHOPS_PER_YEAR
    per_workshop_revenue = total_workshop_registrations * WORKSHOP_PER_REGISTRANT
    
    # Annual pass buyers
    annual_pass_revenue = annual_pass_buyers * WORKSHOP_ANNUAL_PASS
    
    total_revenue = per_workshop_revenue + annual_pass_revenue
    return total_revenue, total_workshop_registrations, annual_pass_buyers

def calculate_breakeven_scenarios():
    """Calculate different scenarios to reach breakeven."""
    annual_costs = calculate_annual_operating_costs()
    
    print("\n" + "="*80)
    print("MCPHERSON LAB - STARTUP STAGE BREAKEVEN ANALYSIS")
    print("="*80)
    
    # Startup Costs
    print("\n--- STARTUP COSTS ---")
    one_time, first_year_recurring, total_first_year = calculate_startup_costs()
    print(f"One-time costs (PLLC filing): ${one_time:,.0f}")
    print(f"First year recurring: ${first_year_recurring:,.0f}")
    print(f"Total first year costs: ${total_first_year:,.0f}")
    
    # Annual Operating Costs
    print("\n--- ANNUAL OPERATING COSTS (after year 1) ---")
    print(f"Office rent (400 sq ft @ $30/sq ft): ${ANNUAL_OFFICE_RENT:,.0f}/year")
    print(f"PLLC annual fee: ${PLLC_ANNUAL_FEE:,.0f}/year")
    print(f"GoDaddy website: ${GODADDY_WEBSITE_ANNUAL:,.0f}/year")
    print(f"Zoom Business: ${ZOOM_BUSINESS_ANNUAL:,.0f}/year")
    print(f"Total annual operating costs: ${annual_costs:,.0f}/year")
    print(f"\nBREAKEVEN TARGET: ${annual_costs:,.0f}/year")
    
    # Revenue Streams
    print("\n" + "="*80)
    print("REVENUE STREAM CONFIGURATIONS")
    print("="*80)
    
    # Scenario 1: Conservative
    print("\n--- SCENARIO 1: CONSERVATIVE ---")
    newsletter_subs_per = 50
    ce_students_per = 100
    workshop_reg_per = 30
    annual_pass = 20
    
    news_rev, news_subs = calculate_newsletter_revenue(newsletter_subs_per)
    ce_rev, ce_students = calculate_ce_course_revenue(ce_students_per)
    work_rev, work_regs, work_annual = calculate_workshop_revenue(workshop_reg_per, annual_pass)
    
    total_rev = news_rev + ce_rev + work_rev
    net = total_rev - annual_costs
    
    print(f"\nNewsletter Revenue:")
    print(f"  {newsletter_subs_per} subs/newsletter × {NUMBER_OF_NEWSLETTERS} newsletters = {news_subs} total subs")
    print(f"  Revenue: ${news_rev:,.0f}/year (${news_rev/12:,.0f}/month)")
    
    print(f"\nCE Course Revenue:")
    print(f"  {ce_students_per} students/course × {NUMBER_OF_CE_COURSES} courses = {ce_students} total students")
    print(f"  Revenue: ${ce_rev:,.0f}/year")
    
    print(f"\nWorkshop Revenue:")
    print(f"  {workshop_reg_per} registrants/workshop × {WORKSHOPS_PER_YEAR} workshops = {work_regs} registrations")
    print(f"  Per-workshop revenue: ${work_regs * WORKSHOP_PER_REGISTRANT:,.0f}")
    print(f"  {annual_pass} annual pass buyers × ${WORKSHOP_ANNUAL_PASS} = ${annual_pass * WORKSHOP_ANNUAL_PASS:,.0f}")
    print(f"  Total workshop revenue: ${work_rev:,.0f}/year")
    
    print(f"\nTOTAL REVENUE: ${total_rev:,.0f}/year")
    print(f"OPERATING COSTS: ${annual_costs:,.0f}/year")
    print(f"NET PROFIT: ${net:,.0f}/year")
    if net >= 0:
        print(f"STATUS: ✅ PROFITABLE (margin: {net/total_rev*100:.1f}%)")
    else:
        print(f"STATUS: ❌ SHORTFALL")
    
    # Scenario 2: Moderate (Breakeven Target)
    print("\n--- SCENARIO 2: MODERATE (TARGET BREAKEVEN) ---")
    newsletter_subs_per = 60
    ce_students_per = 150
    workshop_reg_per = 40
    annual_pass = 30
    
    news_rev, news_subs = calculate_newsletter_revenue(newsletter_subs_per)
    ce_rev, ce_students = calculate_ce_course_revenue(ce_students_per)
    work_rev, work_regs, work_annual = calculate_workshop_revenue(workshop_reg_per, annual_pass)
    
    total_rev = news_rev + ce_rev + work_rev
    net = total_rev - annual_costs
    
    print(f"\nNewsletter Revenue:")
    print(f"  {newsletter_subs_per} subs/newsletter × {NUMBER_OF_NEWSLETTERS} newsletters = {news_subs} total subs")
    print(f"  Revenue: ${news_rev:,.0f}/year")
    
    print(f"\nCE Course Revenue:")
    print(f"  {ce_students_per} students/course × {NUMBER_OF_CE_COURSES} courses = {ce_students} total students")
    print(f"  Revenue: ${ce_rev:,.0f}/year")
    
    print(f"\nWorkshop Revenue:")
    print(f"  {workshop_reg_per} registrants/workshop × {WORKSHOPS_PER_YEAR} workshops = {work_regs} registrations")
    print(f"  Per-workshop revenue: ${work_regs * WORKSHOP_PER_REGISTRANT:,.0f}")
    print(f"  {annual_pass} annual pass buyers × ${WORKSHOP_ANNUAL_PASS} = ${annual_pass * WORKSHOP_ANNUAL_PASS:,.0f}")
    print(f"  Total workshop revenue: ${work_rev:,.0f}/year")
    
    print(f"\nTOTAL REVENUE: ${total_rev:,.0f}/year")
    print(f"OPERATING COSTS: ${annual_costs:,.0f}/year")
    print(f"NET PROFIT: ${net:,.0f}/year")
    if net >= 0:
        print(f"STATUS: ✅ PROFITABLE (margin: {net/total_rev*100:.1f}%)")
    else:
        print(f"STATUS: ❌ SHORTFALL of ${-net:,.0f}")
    
    # Scenario 3: Growth
    print("\n--- SCENARIO 3: GROWTH ---")
    newsletter_subs_per = 100
    ce_students_per = 200
    workshop_reg_per = 50
    annual_pass = 50
    
    news_rev, news_subs = calculate_newsletter_revenue(newsletter_subs_per)
    ce_rev, ce_students = calculate_ce_course_revenue(ce_students_per)
    work_rev, work_regs, work_annual = calculate_workshop_revenue(workshop_reg_per, annual_pass)
    
    total_rev = news_rev + ce_rev + work_rev
    net = total_rev - annual_costs
    
    print(f"\nNewsletter Revenue:")
    print(f"  {newsletter_subs_per} subs/newsletter × {NUMBER_OF_NEWSLETTERS} newsletters = {news_subs} total subs")
    print(f"  Revenue: ${news_rev:,.0f}/year")
    
    print(f"\nCE Course Revenue:")
    print(f"  {ce_students_per} students/course × {NUMBER_OF_CE_COURSES} courses = {ce_students} total students")
    print(f"  Revenue: ${ce_rev:,.0f}/year")
    
    print(f"\nWorkshop Revenue:")
    print(f"  {workshop_reg_per} registrants/workshop × {WORKSHOPS_PER_YEAR} workshops = {work_regs} registrations")
    print(f"  Per-workshop revenue: ${work_regs * WORKSHOP_PER_REGISTRANT:,.0f}")
    print(f"  {annual_pass} annual pass buyers × ${WORKSHOP_ANNUAL_PASS} = ${annual_pass * WORKSHOP_ANNUAL_PASS:,.0f}")
    print(f"  Total workshop revenue: ${work_rev:,.0f}/year")
    
    print(f"\nTOTAL REVENUE: ${total_rev:,.0f}/year")
    print(f"OPERATING COSTS: ${annual_costs:,.0f}/year")
    print(f"NET PROFIT: ${net:,.0f}/year")
    if net >= 0:
        print(f"STATUS: ✅ PROFITABLE (margin: {net/total_rev*100:.1f}%)")
    else:
        print(f"STATUS: ❌ SHORTFALL")
    
    # Summary
    print("\n" + "="*80)
    print("STARTUP STAGE SUMMARY")
    print("="*80)
    print(f"\nOperating Model:")
    print(f"  - Solo operation (PI only, no salary)")
    print(f"  - Office: 400 sq ft in TMC @ $30/sq ft")
    print(f"  - {NUMBER_OF_NEWSLETTERS} monetized newsletters @ $10/month subscription")
    print(f"  - {NUMBER_OF_CE_COURSES} LearningExpressCE courses")
    print(f"  - {WORKSHOPS_PER_MONTH} workshops per month ({WORKSHOPS_PER_YEAR}/year)")
    print(f"\nAnnual Operating Costs: ${annual_costs:,.0f}")
    print(f"Breakeven Revenue Target: ${annual_costs:,.0f}/year")
    print(f"\nNote: PI has no salary in startup stage. All profits are retained for growth")
    print(f"      or can be taken as owner distributions.")
    print("="*80)

if __name__ == "__main__":
    calculate_breakeven_scenarios()
