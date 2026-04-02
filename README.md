# Personal Calendar

A comprehensive personal calendar management system that aggregates events from multiple sources and presents them in an interactive web interface.

## Features

- 📅 **Interactive Calendar View**: Powered by FullCalendar for an intuitive browsing experience
- 🎯 **Multi-source Support**: Aggregate events from various calendar sources
- 📋 **Agenda Panel**: See today's events and upcoming tasks at a glance
- 🏷️ **Event Categorization**: Organize events by type (work, personal, reminders, etc.)
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🔄 **Automated Sync**: Keep your calendar up-to-date with automatic data synchronization

## Quick Start

### File Structure

```
calendar/
├── index.qmd          # Main calendar UI (Quarto document)
├── _quarto.yml        # Quarto project configuration
├── styles.css         # Custom styling
└── sync_calendar.py   # Data synchronization script
```

### Setup

1. **Configure your calendar sources** in `sync_calendar.py`
2. **Run the sync script** to populate calendar data:
   ```bash
   python calendar/sync_calendar.py
   ```
3. **Build and view** the calendar:
   ```bash
   quarto render calendar/index.qmd
   ```

### Configuration

Edit `calendar/sync_calendar.py` to:
- Add your calendar sources (Google Calendar, Outlook, ICS files, etc.)
- Define event categories and colors
- Set update frequency and data transformations

## Event Format

Events are stored as JavaScript objects with the following structure:

```javascript
{
  id: "event-unique-id",
  title: "Event Title",
  start: "2026-04-02T10:00:00",
  end: "2026-04-02T11:00:00",
  category: "work",
  description: "Event details",
  url: "https://example.com"
}
```

## Development

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

### Building

Build the calendar for deployment:
```bash
quarto render calendar/index.qmd
```

The output will be in `calendar/_site/`.
   - Base package breakdown ($70,800 value)
   - Tax-advantaged savings maximization
   - 90/10 revenue sharing model
   - Example scenarios

2. **[Breakeven Analysis](breakeven-analysis.md)**
   - Employer base costs per trainee ($103,186)
   - True breakeven with revenue sharing ($114,651 total revenue)
   - Revenue stream scenarios
   - Growth projections and KPIs

### 🧮 Tools

3. **[Calculator Script](calculator.py)**
   - Python script for automated calculations
   - Calculates required gross salary to fund base package
   - Models revenue sharing scenarios
   - Breakeven analysis with different performance levels

## Quick Start

### Run the Calculator

```bash
python3 calculator.py
```

This will output:
- Base package breakdown and required gross salary
- Employer base costs per trainee
- Breakeven revenue with 50/50 sharing
- Multiple performance scenarios (conservative, breakeven, high performance)

## Key Findings

### Base Package: $70,800

| Component | Annual Amount |
|-----------|---------------|
| HSA Contribution | $4,300 |
| 403(b) Contribution | $23,500 |
| Roth IRA Contribution | $7,000 |
| Rent Allowance | $24,000 |
| Incidentals | $12,000 |
| **Total** | **$70,800** |

### Required Gross Salary

To fund the base package after taxes and deductions: **$84,706**

### Employer Base Costs

- **Total Annual Base Cost per Trainee**: $103,186
  - Gross salary: $84,706
  - Employer FICA: $6,480
  - Benefits admin: $1,000
  - Indirect costs: $11,000 (space, equipment, training, etc.)

### Breakeven with Revenue Sharing

**Total Revenue Required**: $114,651 per trainee

With 90/10 sharing:
- Lab receives 90% = $103,186 (covers base costs)
- Trainee receives 10% = $11,465

**Trainee Total Compensation at Breakeven**: $82,265
- Base package: $70,800
- Revenue share: $11,465

### Revenue Scenarios

#### NEW MODEL: 9 Trainees + PI with Newsletter Revenue

**Per Trainee (at $200k total revenue):**
- Newsletter revenue: $200,000 (requires 1,667 subscribers @ $10/mo)
- **Total revenue**: $200,000
- Lab's 90% share: $180,000
- **Trainee total comp**: $90,800 ($70,800 base + $20,000 share)
- **Lab net**: $76,814 per trainee (profitable!)

**PI Newsletter (DiseasePrevention):**
- Revenue target: $400,000
- Lab's 90% share: $360,000
- No salary or breakeven analysis (PI-managed)

**Lab-Wide (9 trainees + PI):**
- Trainee revenue: $1,800,000 (9 × $200k)
- PI revenue: $400,000
- Total revenue: $2,200,000
- Lab's 90% share: $1,980,000
- Total trainee base costs: $928,671
- **Lab net**: $1,051,329 (47.8% profit margin)

**Breakeven is at $115k per trainee** (956 subscribers @ $10/mo)

#### Trainee Assignments

| Trainee | Newsletter | Revenue Target |
|---------|-----------|---------------|
| 1 | infectiousdiseases | $200,000 |
| 2 | humanmicrobiome | $200,000 |
| 3 | antimicrobialresistance | $200,000 |
| 4 | toxicology | $200,000 |
| 5 | structuralbiology | $200,000 |
| 6 | immunology | $200,000 |
| 7 | computationalbiology | $200,000 |
| 8 | pharmacoepidemiology | $200,000 |
| 9 | pharmacoeconomics | $200,000 |
| **PI** | **DiseasePrevention** | **$400,000** |

## Revenue Streams

### Core Revenue Model

**9 Trainees + PI → 10 Newsletters (1:1 assignment)**

Each trainee is assigned:
- **ONE Substack Newsletter** (out of 9 trainee newsletters)

**PI manages:**
- **DiseasePrevention Newsletter** ($400k target, no salary/breakeven)

**Revenue Target:**
- Each trainee newsletter must generate: **$200,000/year**
- PI newsletter target: **$400,000/year**
- **Total per trainee**: **$200,000/year**

### Newsletter Options

**Trainee Newsletters (Choose 1 per trainee):**
- infectiousdiseases
- humanmicrobiome
- antimicrobialresistance
- toxicology
- structuralbiology
- immunology
- computationalbiology
- pharmacoepidemiology
- pharmacoeconomics

**PI Newsletter:**
- DiseasePrevention ($400k target)

To reach $200k/year at $10/month subscription:
- Need approximately 1,667 subscribers per newsletter
- OR implement higher-tier pricing/sponsorships/premium tiers
- **Breakeven**: 956 subscribers @ $10/mo = $114,651/year

## Growth Strategy

### Year 1: Foundation (2-3 trainees)
- Build reputation and client base
- Target: Breakeven ($206k revenue per trainee)
- **Total Lab Revenue Target**: $412k-$618k
- **Expected Net**: Break even

### Year 2: Expansion (4-5 trainees)
- Scale successful programs
- Target: $350k revenue per trainee
- **Total Lab Revenue Target**: $1.4M-$1.75M
- **Expected Net**: $350k-$525k (25% margin)

### Year 3: Optimization (6-8 trainees)
- Maximize efficiency and profitability
- Target: $500k+ revenue per trainee
- **Total Lab Revenue Target**: $3M-$4M
- **Expected Net**: $900k-$1.4M (30% margin)

## Key Advantages of Revenue Sharing Model

1. **Aligned Incentives**: Trainees directly benefit from their productivity
2. **Risk Mitigation**: Lab's base costs are covered at breakeven revenue
3. **Unlimited Upside**: High performers can earn significantly more
4. **Guaranteed Foundation**: All trainees have essential needs covered
5. **Scalability**: Model works at any performance level

## Key Performance Indicators

### Per Trainee Metrics
- Total Revenue Generated: Target $210k+ for breakeven
- Revenue per Hour: Target $400-$600 for profitability
- Annual Billable Hours: Target 400-600 hours
- Client Retention Rate: Target 80%+
- Course Completion Rate: Target 70%+

### Lab-Wide Metrics
- Total Revenue: Minimum $206,371 per trainee for breakeven
- Lab's Net Margin: Target 20-30% after revenue sharing
- Client Acquisition Cost: Target <$500 per client
- Customer Lifetime Value: Target >$10,000

## Assumptions

### Tax Calculations
- Single filing status
- 2026 federal tax brackets
- No state/local income tax (varies by location)
- Standard deduction included in tax bracket calculations

### Revenue Estimates
- Based on market research and industry standards
- May vary by region and specialization
- Conservative estimates used for breakeven analysis

### Indirect Costs
- Office/lab space: $250/month per trainee
- Equipment and supplies: Shared resources
- Software and tools: Lab licenses
- Training and development: Continuing education
- Insurance: Professional liability
- Administrative overhead: HR, accounting, etc.

## Notes

- All figures are estimates for planning purposes
- Actual results may vary based on market conditions
- Revenue sharing payments are taxable income to trainees
- **IMPORTANT**: Tax calculations assume no state/local taxes
  - State tax rates vary from 0% to 13%+
  - Actual take-home will be lower in states with income tax
- Regular review and adjustment recommended
- Consult with financial and legal professionals for implementation

---

# Startup Stage

## Overview

The **Startup Stage** represents the initial phase of McPherson Lab operations where the PI operates solo without employees or salary, focusing on establishing foundational revenue streams to validate the business model before scaling to the Operation Stage.

## Startup Calculator

Run the startup stage calculator:

```bash
python3 startup-calculator.py
```

## Key Characteristics

### Operating Model
- **Solo operation**: PI only (no trainees, no salary for PI)
- **Location**: 400 sq ft office in TMC @ $30/sq ft/year
- **Minimal overhead**: Essential tools and services only

### Startup Costs
- **One-time**: PLLC filing through LegalZoom (~$500)
- **Annual recurring**:
  - Office rent: $12,000/year (400 sq ft @ $30/sq ft)
  - PLLC annual fee: $300/year
  - GoDaddy website: $200/year
  - Zoom Business license: $200/year
- **Total first year**: $13,200
- **Annual operating costs (year 2+)**: $12,700

### Revenue Streams

**10 Monetized Substack Newsletters** @ $10/month subscription
- Target: 50-100 subscribers per newsletter initially
- Revenue potential: $60,000-$120,000/year

**8 LearningExpressCE Courses** @ $99 per student
- Target: 100-200 students per course
- Revenue potential: $79,200-$158,400/year

**12 Monthly Workshops** (144/year)
- Per-workshop: $10/registrant
- Annual pass: $60 for all workshops
- Target: 30-50 registrants per workshop
- Revenue potential: $44,400-$75,000/year

### Breakeven Analysis

**Annual Operating Costs**: $12,700

**Conservative Scenario** (Immediate profitability):
- Newsletter: 50 subs × 10 newsletters = $60,000/year
- CE Courses: 100 students × 8 courses = $79,200/year
- Workshops: 30 registrants × 144 workshops + 20 annual = $44,400/year
- **Total Revenue**: $183,600/year
- **Net Profit**: $170,900/year (93% margin)

**Moderate Scenario**:
- Newsletter: 60 subs × 10 newsletters = $72,000/year
- CE Courses: 150 students × 8 courses = $118,800/year
- Workshops: 40 registrants × 144 workshops + 30 annual = $59,400/year
- **Total Revenue**: $250,200/year
- **Net Profit**: $237,500/year (95% margin)

**Growth Scenario**:
- Newsletter: 100 subs × 10 newsletters = $120,000/year
- CE Courses: 200 students × 8 courses = $158,400/year
- Workshops: 50 registrants × 144 workshops + 50 annual = $75,000/year
- **Total Revenue**: $353,400/year
- **Net Profit**: $340,700/year (96% margin)

## Transition to Operation Stage

**When to Transition:**
- Revenue consistently exceeds $200k-$300k/year
- PI capacity maxed out (unable to handle more clients/content)
- Proven business model and market validation
- Sufficient capital to hire first trainee(s)

**Transition Requirements:**
- Hire first 2-3 trainees
- Implement compensation packages ($70.8k base per trainee)
- Scale office space and infrastructure
- Transition from 100% PI work to management + oversight

---

## Privacy

This repository contains internal business operations information for the McPherson Lab and should be kept private.

---

**Last Updated**: January 2026  
**Next Review**: Quarterly
