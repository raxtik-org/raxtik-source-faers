"""Official FDA Dosing Frequency Codes (DOSE_FREQ)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_DOSE_FREQUENCIES_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry("1X", "Once or one time", "Single dose administration", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("BID", "Twice a day", "Twice daily administration (every 12 hours)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("BIW", "Twice a week", "Twice weekly administration", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("HS", "At bedtime", "Administration at bedtime (hora somni)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("PRN", "As needed", "Administration as needed (pro re nata)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q12H", "Every 12 hours", "Administration every 12 hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q2H", "Every 2 hours", "Administration every 2 hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q3H", "Every 3 hours", "Administration every 3 hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q3W", "Every 3 weeks", "Administration every 3 weeks", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q4H", "Every 4 hours", "Administration every 4 hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q5H", "Every 5 hours", "Administration every 5 hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q6H", "Every 6 hours", "Administration every 6 hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("Q8H", "Every 8 hours", "Administration every 8 hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("QD", "Daily", "Daily administration (quaque die)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("QH", "Every hour", "Administration every hour", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("QID", "4 times a day", "Four times daily (quater in die)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("QM", "Monthly", "Monthly administration", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("QOD", "Every other day", "Every other day administration (quaque altera die)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("QOW", "Every other week", "Every other week administration", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("QW", "Every week", "Weekly administration (quaque week)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("TID", "3 times a day", "Three times daily (ter in die)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("TIW", "3 times a week", "Three times weekly administration", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("UNK", "Unknown", "Dosing frequency is unknown or unspecified", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
]
