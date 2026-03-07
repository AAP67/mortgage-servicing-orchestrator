"""
Sample mortgage servicing scenarios.
Synthetic but realistic data for demo purposes.
"""

SCENARIOS = {
    "Forbearance Request — Texas": {
        "borrower_name": "Maria Santos",
        "state": "TX",
        "property_type": "Single Family",
        "loan_type": "30-year Fixed (Conventional)",
        "original_amount": "$320,000",
        "current_balance": "$298,500",
        "interest_rate": "6.75%",
        "monthly_payment": "$2,076",
        "origination_date": "March 2022",
        "credit_score": "680",
        "dti_ratio": "42%",
        "payment_history": (
            "On-time payments for 24 months. "
            "Missed January and February 2026 payments. "
            "Borrower called requesting forbearance due to job loss."
        ),
        "situation": (
            "Borrower is requesting forbearance. Lost primary employment "
            "6 weeks ago. Spouse still employed part-time ($2,800/month). "
            "Has applied for unemployment benefits but not yet receiving them."
        ),
        "additional_context": (
            "Borrower has expressed anxiety about losing the home. "
            "Property estimated current value: $345,000. No other liens. "
            "Escrow balance is current."
        ),
    },
    "Refinance Inquiry — California": {
        "borrower_name": "James Chen",
        "state": "CA",
        "property_type": "Condo",
        "loan_type": "30-year Fixed (Conventional)",
        "original_amount": "$550,000",
        "current_balance": "$485,000",
        "interest_rate": "7.25%",
        "monthly_payment": "$3,753",
        "origination_date": "September 2023",
        "credit_score": "745",
        "dti_ratio": "35%",
        "payment_history": (
            "Perfect payment history — all 29 payments on time. "
            "Borrower also making additional principal payments of $200/month."
        ),
        "situation": (
            "Borrower inquiring about refinancing options. Believes rates "
            "have come down and wants to lower monthly payment. Also "
            "interested in potentially taking cash out for home improvements."
        ),
        "additional_context": (
            "Property estimated current value: $620,000. HOA dues: $450/month. "
            "Borrower recently received a promotion with 15% salary increase. "
            "No other debt besides auto loan ($18,000 remaining)."
        ),
    },
    "Escrow Shortage — Florida": {
        "borrower_name": "David & Lisa Thompson",
        "state": "FL",
        "property_type": "Single Family",
        "loan_type": "30-year Fixed (FHA)",
        "original_amount": "$280,000",
        "current_balance": "$265,000",
        "interest_rate": "5.50%",
        "monthly_payment": "$1,890 (PITI)",
        "origination_date": "June 2021",
        "credit_score": "710",
        "dti_ratio": "38%",
        "payment_history": (
            "Consistent on-time payments for 4+ years. No delinquencies ever."
        ),
        "situation": (
            "Annual escrow analysis revealed a $3,200 shortage due to property "
            "insurance premium increase (hurricane risk reassessment). New monthly "
            "payment would increase by $380/month. Borrowers are disputing the "
            "increase and requesting options."
        ),
        "additional_context": (
            "Property in coastal Florida (hurricane zone). Insurance premium "
            "increased from $2,400/yr to $6,200/yr after carrier reassessment. "
            "Borrowers are on fixed income (combined retirement + part-time "
            "work: $5,800/month). Property value: $310,000."
        ),
    },
}
