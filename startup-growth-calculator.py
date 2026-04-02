#!/usr/bin/env python3
"""
McPherson Lab Startup Stage Growth Model Calculator

Models conservative 12-month growth trajectory for startup stage revenue streams:
- 3 SubStack newsletters (infectiousdiseases, antimicrobialresistance, humanmicrobiome) 
  starting from 0 paid subscribers with conservative growth
- 8 LearningExpressCE courses with costs and conservative enrollment growth
- 1 monthly workshop with participant growth

Calculates month-by-month revenue, costs, and breakeven achievement.
"""

import math

# ============================================================================
# STARTUP STAGE CONSTANTS
# ============================================================================

# Office Costs
OFFICE_SIZE_SQ_FT = 1000  # Updated from 400 to 1000 sq ft
OFFICE_COST_PER_SQ_FT_ANNUAL = 30
MONTHLY_OFFICE_RENT = (OFFICE_SIZE_SQ_FT * OFFICE_COST_PER_SQ_FT_ANNUAL) / 12

# Startup Costs (one-time and recurring)
PLLC_FILING_COST = 500  # LegalZoom PLLC filing (one-time, month 1)
PLLC_MONTHLY_FEE = 300 / 12  # Annual state filing fee, spread monthly
GODADDY_WEBSITE_MONTHLY = 200 / 12  # Website hosting and domain
ZOOM_BUSINESS_MONTHLY = 200 / 12  # Zoom Business license

# LearningExpressCE Costs
LEARNINGEXPRESSCE_ANNUAL_COST = 2000  # Platform annual cost (unchanged)
LEARNINGEXPRESSCE_COST_PER_REGISTRANT = 12.50  # Cost per registrant (updated from per hour)
CE_REGISTRANTS_FOR_BREAKEVEN = math.ceil(LEARNINGEXPRESSCE_ANNUAL_COST / LEARNINGEXPRESSCE_COST_PER_REGISTRANT)  # >20 registrants needed

# Revenue Stream Pricing
NEWSLETTER_MONTHLY_PRICE = 8  # Updated from 10 to 8
CE_COURSE_PRICE = 12.50  # Updated: Cost per registrant (no profit margin modeled)
WORKSHOP_PER_REGISTRANT = 10

# PI's Medium Friend Partner Program (PI only, no growth model - static)
MEDIUM_MONTHLY_PRICE = 15  # $15/month per friend
MEDIUM_ESTIMATED_READERS = 100  # Estimated 100 readers
MEDIUM_ANNUAL_REVENUE = MEDIUM_MONTHLY_PRICE * 12 * MEDIUM_ESTIMATED_READERS  # $18,000/year
MEDIUM_MONTHLY_REVENUE = MEDIUM_ANNUAL_REVENUE / 12  # $1,500/month

# Revenue Stream Configuration
NEWSLETTER_NAMES = ["infectiousdiseases", "antimicrobialresistance", "humanmicrobiome"]
NUMBER_OF_NEWSLETTERS = len(NEWSLETTER_NAMES)  # 3 newsletters
NUMBER_OF_CE_COURSES = 8
WORKSHOPS_PER_MONTH = 1  # Once monthly workshop
WORKSHOP_INITIAL_PARTICIPANTS = 30  # Starting participants in month 1
WORKSHOP_MAX_PARTICIPANTS = 300  # Maximum cap on participants

# Growth Model Parameters (Monthly Doubling Model)
MONTHLY_GROWTH_RATE = 2.0  # Doubling monthly (2x growth per month)
INITIAL_NEWSLETTER_SUBSCRIBERS = 10  # Start with 10 subscribers per newsletter
INITIAL_CE_REGISTRANTS = 1  # Start with 1 registrant per course

# USP 797 Microbiology Service Lab (NEW)
# USP 797 is the pharmaceutical compounding standard for sterile preparations
# Services include: environmental monitoring, sterility testing, endotoxin testing, media fill testing
USP797_CONTRACT_VALUE = 15000  # $15,000 per annual contract per pharmacy client
USP797_INITIAL_CLIENTS = 1  # Start with 1 client
USP797_MONTHLY_GROWTH_RATE = 2.0  # Doubling monthly (same as newsletters)

# ============================================================================
# GROWTH MODEL FUNCTIONS
# ============================================================================

def calculate_monthly_doubling_growth(initial_value, months_elapsed, monthly_growth_rate=2.0):
    """
    Calculate value after monthly doubling growth.
    
    Args:
        initial_value: Starting value (e.g., 10 subscribers)
        months_elapsed: Number of months of growth
        monthly_growth_rate: Growth multiplier per month (2.0 = doubling monthly)
    
    Returns:
        Final value after growth
    """
    return initial_value * (monthly_growth_rate ** months_elapsed)

def calculate_monthly_costs(month, include_learningexpressce=True):
    """Calculate total costs for a given month."""
    # Base recurring costs
    monthly_cost = (
        MONTHLY_OFFICE_RENT +
        PLLC_MONTHLY_FEE +
        GODADDY_WEBSITE_MONTHLY +
        ZOOM_BUSINESS_MONTHLY
    )
    
    # Add one-time PLLC filing cost in month 1
    if month == 1:
        monthly_cost += PLLC_FILING_COST
    
    # Add LearningExpressCE annual cost in month 1
    if month == 1 and include_learningexpressce:
        monthly_cost += LEARNINGEXPRESSCE_ANNUAL_COST
    
    return monthly_cost

def calculate_newsletter_revenue_month(month):
    """
    Calculate newsletter revenue for a given month based on monthly doubling growth.
    Starts from 10 paid subscribers and doubles monthly.
    """
    months_elapsed = month - 1  # Month 1 has 0 elapsed months
    subscribers_per_newsletter = calculate_monthly_doubling_growth(
        INITIAL_NEWSLETTER_SUBSCRIBERS,
        months_elapsed,
        MONTHLY_GROWTH_RATE
    )
    
    # Round to nearest integer
    subscribers_per_newsletter = round(subscribers_per_newsletter)
    
    # Total subscribers across all newsletters
    total_subscribers = subscribers_per_newsletter * NUMBER_OF_NEWSLETTERS
    
    # Monthly revenue
    monthly_revenue = total_subscribers * NEWSLETTER_MONTHLY_PRICE
    
    return monthly_revenue, subscribers_per_newsletter, total_subscribers

def calculate_ce_revenue_month(month):
    """
    Calculate LearningExpressCE revenue and costs for a given month.
    NEW MODEL: $12.50 per registrant, $2000 annual platform fee breakeven
    Need >20 registrants per CE course for breakeven (>160 total across 8 courses)
    """
    months_elapsed = month - 1
    registrants_per_course = calculate_monthly_doubling_growth(
        INITIAL_CE_REGISTRANTS,
        months_elapsed,
        MONTHLY_GROWTH_RATE
    )
    
    # Round to nearest integer
    registrants_per_course = round(registrants_per_course)
    
    # Total registrants across all courses
    total_registrants = registrants_per_course * NUMBER_OF_CE_COURSES
    
    # Revenue at $12.50/registrant
    monthly_revenue = total_registrants * CE_COURSE_PRICE
    
    # Variable costs are the same as revenue in this breakeven model
    # Net revenue is $0 until platform fee is covered
    variable_costs = monthly_revenue  # All revenue goes to costs
    
    # Net revenue after variable costs (platform fee recovered over 12 months)
    net_revenue = 0  # Breakeven model - no profit
    
    return net_revenue, monthly_revenue, variable_costs, registrants_per_course, total_registrants

def calculate_usp797_revenue_month(month):
    """
    Calculate USP 797 Microbiology Service Lab revenue for a given month.
    USP 797 provides sterile compounding compliance testing services to pharmacies.
    Services include: environmental monitoring, sterility testing, endotoxin testing, 
    media fill testing, and personnel qualification testing.
    
    Starting with 1 client, doubling monthly.
    Contract value: $15,000 per year per client.
    """
    months_elapsed = month - 1
    total_clients = calculate_monthly_doubling_growth(
        USP797_INITIAL_CLIENTS,
        months_elapsed,
        USP797_MONTHLY_GROWTH_RATE
    )
    
    # Round to nearest integer
    total_clients = round(total_clients)
    
    # Monthly revenue (annual contract divided by 12 months)
    monthly_revenue_per_client = USP797_CONTRACT_VALUE / 12
    monthly_revenue = total_clients * monthly_revenue_per_client
    
    return monthly_revenue, total_clients

def calculate_workshop_revenue_month(month):
    """
    Calculate workshop revenue for a given month.
    Once monthly workshop starting with 30 participants, doubling monthly up to max 300.
    """
    # Start with 30 participants, double each month until reaching max of 300
    participants = WORKSHOP_INITIAL_PARTICIPANTS * (2 ** (month - 1))
    participants = min(participants, WORKSHOP_MAX_PARTICIPANTS)  # Cap at 300
    
    total_participants = participants * WORKSHOPS_PER_MONTH
    monthly_revenue = total_participants * WORKSHOP_PER_REGISTRANT
    
    return monthly_revenue, participants, total_participants

def generate_12_month_projection():
    """Generate month-by-month financial projection for 12 months."""
    
    print("\n" + "="*100)
    print("MCPHERSON LAB - STARTUP STAGE 12-MONTH GROWTH PROJECTION")
    print("="*100)
    
    print("\n--- GROWTH MODEL ASSUMPTIONS ---")
    print(f"Newsletter Growth: Start with {INITIAL_NEWSLETTER_SUBSCRIBERS} subscribers per newsletter, doubling monthly")
    print(f"CE Course Growth: Start with {INITIAL_CE_REGISTRANTS} registrant per course, doubling monthly")
    print(f"USP 797 Service Lab: Start with {USP797_INITIAL_CLIENTS} client, doubling monthly at ${USP797_CONTRACT_VALUE:,.0f}/year per client")
    print(f"Workshop Attendance: Start with {WORKSHOP_INITIAL_PARTICIPANTS} participants, doubling monthly up to max {WORKSHOP_MAX_PARTICIPANTS}")
    print(f"\nRevenue Streams:")
    print(f"  - {NUMBER_OF_NEWSLETTERS} SubStack newsletters @ ${NEWSLETTER_MONTHLY_PRICE}/month")
    print(f"    Newsletters: {', '.join(NEWSLETTER_NAMES)}")
    print(f"  - {NUMBER_OF_CE_COURSES} LearningExpressCE courses @ ${CE_COURSE_PRICE}/registrant")
    print(f"  - {WORKSHOPS_PER_MONTH} workshop per month @ ${WORKSHOP_PER_REGISTRANT}/participant")
    print(f"  - USP 797 Microbiology Service Lab @ ${USP797_CONTRACT_VALUE:,.0f}/client/year")
    print(f"  - Medium Friend Partner Program: {MEDIUM_ESTIMATED_READERS} readers @ ${MEDIUM_MONTHLY_PRICE}/month (${MEDIUM_ANNUAL_REVENUE:,.0f}/year)")
    print(f"\nUSP 797 Service Lab:")
    print(f"  - Sterile compounding compliance testing for pharmacies")
    print(f"  - Services: Environmental monitoring, sterility testing, endotoxin testing,")
    print(f"    media fill testing, personnel qualification testing")
    print(f"  - Contract model: ${USP797_CONTRACT_VALUE:,.0f} annual per pharmacy client")
    print(f"\nCE Course Costs:")
    print(f"  - Annual platform fee: ${LEARNINGEXPRESSCE_ANNUAL_COST:,.0f} (month 1)")
    print(f"  - Cost per registrant: ${LEARNINGEXPRESSCE_COST_PER_REGISTRANT}/registrant")
    print(f"  - Breakeven model: Revenue matches costs (need >{CE_REGISTRANTS_FOR_BREAKEVEN} registrants for platform fee)")
    
    print("\n" + "="*100)
    print("MONTH-BY-MONTH BREAKDOWN")
    print("="*100)
    
    cumulative_revenue = 0
    cumulative_costs = 0
    cumulative_profit = 0
    breakeven_month = None
    
    monthly_data = []
    
    for month in range(1, 13):
        # Calculate revenues
        news_rev, news_subs_per, news_total_subs = calculate_newsletter_revenue_month(month)
        ce_net_rev, ce_gross_rev, ce_costs, ce_reg_per, ce_total_reg = calculate_ce_revenue_month(month)
        work_rev, work_part_per, work_total_part = calculate_workshop_revenue_month(month)
        usp797_rev, usp797_clients = calculate_usp797_revenue_month(month)
        medium_rev = MEDIUM_MONTHLY_REVENUE  # Static Medium revenue
        
        # Calculate costs
        fixed_costs = calculate_monthly_costs(month, include_learningexpressce=True)
        total_costs = fixed_costs + ce_costs  # CE variable costs already calculated
        
        # Calculate totals
        total_revenue = news_rev + ce_net_rev + work_rev + usp797_rev + medium_rev
        monthly_profit = total_revenue - fixed_costs  # CE costs already deducted from ce_net_rev
        
        cumulative_revenue += total_revenue
        cumulative_costs += fixed_costs  # Track fixed costs separately
        cumulative_profit += monthly_profit
        
        # Check for breakeven
        if breakeven_month is None and cumulative_profit >= 0:
            breakeven_month = month
        
        # Store data
        monthly_data.append({
            'month': month,
            'news_rev': news_rev,
            'news_subs_per': news_subs_per,
            'news_total_subs': news_total_subs,
            'ce_net_rev': ce_net_rev,
            'ce_gross_rev': ce_gross_rev,
            'ce_costs': ce_costs,
            'ce_reg_per': ce_reg_per,
            'ce_total_reg': ce_total_reg,
            'work_rev': work_rev,
            'work_participants': work_part_per,
            'work_total_part': work_total_part,
            'usp797_rev': usp797_rev,
            'usp797_clients': usp797_clients,
            'medium_rev': medium_rev,
            'total_revenue': total_revenue,
            'fixed_costs': fixed_costs,
            'monthly_profit': monthly_profit,
            'cumulative_revenue': cumulative_revenue,
            'cumulative_costs': cumulative_costs,
            'cumulative_profit': cumulative_profit
        })
        
        # Print month summary
        print(f"\n--- MONTH {month} ---")
        print(f"Newsletter Revenue: ${news_rev:,.0f}")
        print(f"  ({news_subs_per:,.0f} subs/newsletter × {NUMBER_OF_NEWSLETTERS} = {news_total_subs:,.0f} total subscribers)")
        print(f"CE Course Revenue (net): ${ce_net_rev:,.0f}")
        print(f"  (Gross: ${ce_gross_rev:,.0f}, Variable costs: ${ce_costs:,.0f})")
        print(f"  ({ce_reg_per:,.0f} reg/course × {NUMBER_OF_CE_COURSES} = {ce_total_reg:,.0f} total registrants)")
        print(f"Workshop Revenue: ${work_rev:,.0f}")
        print(f"  ({work_part_per} participants/workshop × {WORKSHOPS_PER_MONTH} workshops)")
        print(f"USP 797 Service Lab: ${usp797_rev:,.0f}")
        print(f"  ({usp797_clients} clients @ ${USP797_CONTRACT_VALUE:,.0f}/year)")
        print(f"Medium Friend Partner: ${medium_rev:,.0f}")
        print(f"  ({MEDIUM_ESTIMATED_READERS} readers @ ${MEDIUM_MONTHLY_PRICE}/mo)")
        print(f"Total Revenue: ${total_revenue:,.0f}")
        print(f"Fixed Costs: ${fixed_costs:,.0f}")
        print(f"Monthly Profit: ${monthly_profit:,.0f}")
        print(f"Cumulative Profit: ${cumulative_profit:,.0f}", end="")
        if cumulative_profit >= 0:
            print(" ✅ PROFITABLE")
        else:
            print(f" (Shortfall: ${-cumulative_profit:,.0f})")
    
    # Summary
    print("\n" + "="*100)
    print("12-MONTH SUMMARY")
    print("="*100)
    
    final_month_data = monthly_data[-1]
    
    print(f"\nRevenue Growth:")
    print(f"  Month 1 revenue: ${monthly_data[0]['total_revenue']:,.0f}")
    print(f"  Month 12 revenue: ${final_month_data['total_revenue']:,.0f}")
    print(f"  Growth factor: {final_month_data['total_revenue'] / monthly_data[0]['total_revenue']:.1f}x")
    
    print(f"\nNewsletter Growth:")
    print(f"  Month 1: {monthly_data[0]['news_subs_per']:,.0f} subs/newsletter ({monthly_data[0]['news_total_subs']:,.0f} total)")
    print(f"  Month 12: {final_month_data['news_subs_per']:,.0f} subs/newsletter ({final_month_data['news_total_subs']:,.0f} total)")
    print(f"  Growth: Monthly doubling from {INITIAL_NEWSLETTER_SUBSCRIBERS} initial subscribers")
    
    print(f"\nCE Course Growth:")
    print(f"  Month 1: {monthly_data[0]['ce_reg_per']:,.0f} reg/course ({monthly_data[0]['ce_total_reg']:,.0f} total)")
    print(f"  Month 12: {final_month_data['ce_reg_per']:,.0f} reg/course ({final_month_data['ce_total_reg']:,.0f} total)")
    
    print(f"\nUSP 797 Service Lab Growth:")
    print(f"  Month 1: {monthly_data[0]['usp797_clients']} client")
    print(f"  Month 12: {final_month_data['usp797_clients']} clients")
    print(f"  Contract value: ${USP797_CONTRACT_VALUE:,.0f}/client/year")
    print(f"  Final monthly revenue: ${final_month_data['usp797_rev']:,.0f}")
    print(f"  Total annual USP 797 revenue: ${sum(m['usp797_rev'] for m in monthly_data):,.0f}")
    
    print(f"\nWorkshop Performance:")
    print(f"  Month 1: {monthly_data[0]['work_participants']} participants")
    print(f"  Month 12: {final_month_data['work_participants']} participants (capped at {WORKSHOP_MAX_PARTICIPANTS})")
    print(f"  Monthly workshops: {WORKSHOPS_PER_MONTH}")
    print(f"  Final monthly revenue: ${work_rev:,.0f}")
    print(f"  Total annual workshop revenue: ${sum(m['work_rev'] for m in monthly_data):,.0f}")
    
    print(f"\nMedium Friend Partner Program:")
    print(f"  Static: {MEDIUM_ESTIMATED_READERS} readers @ ${MEDIUM_MONTHLY_PRICE}/month")
    print(f"  Monthly revenue: ${MEDIUM_MONTHLY_REVENUE:,.0f}")
    print(f"  Total annual revenue: ${MEDIUM_ANNUAL_REVENUE:,.0f}")
    
    print(f"\nFinancial Summary:")
    print(f"  Total 12-month revenue: ${cumulative_revenue:,.0f}")
    print(f"    (Newsletters: ${sum(m['news_rev'] for m in monthly_data):,.0f}, CE: ${sum(m['ce_net_rev'] for m in monthly_data):,.0f}, ")
    print(f"     Workshops: ${sum(m['work_rev'] for m in monthly_data):,.0f}, USP 797: ${sum(m['usp797_rev'] for m in monthly_data):,.0f}, Medium: ${MEDIUM_ANNUAL_REVENUE:,.0f})")
    print(f"  Total 12-month costs: ${cumulative_costs:,.0f}")
    print(f"  Total 12-month profit: ${cumulative_profit:,.0f}")
    print(f"  Overall margin: {cumulative_profit / cumulative_revenue * 100:.1f}%")
    
    if breakeven_month:
        print(f"\n✅ BREAKEVEN ACHIEVED: Month {breakeven_month}")
    else:
        print(f"\n❌ BREAKEVEN NOT ACHIEVED in 12 months")
    
    print(f"\nKey Insights:")
    print(f"  - Starting from {INITIAL_NEWSLETTER_SUBSCRIBERS} paid subscribers per newsletter, monthly doubling reaches profitability")
    print(f"  - Monthly doubling growth rate is aggressive but achievable with focused marketing")
    print(f"  - Workshop revenue grows from {WORKSHOP_INITIAL_PARTICIPANTS} to {WORKSHOP_MAX_PARTICIPANTS} participants (doubling monthly)")
    print(f"  - USP 797 service lab provides high-value contracts (${USP797_CONTRACT_VALUE:,.0f}/client/year)")
    print(f"  - USP 797 services include: environmental monitoring, sterility testing, endotoxin testing,")
    print(f"    media fill testing, and personnel qualification testing for pharmacy compliance")
    print(f"  - LearningExpressCE platform cost (${LEARNINGEXPRESSCE_ANNUAL_COST:,.0f}) recovered through registrations")
    print(f"  - No salary for PI allows all profits to compound for growth or distribution")
    
    print("="*100)
    
    return monthly_data

if __name__ == "__main__":
    generate_12_month_projection()
