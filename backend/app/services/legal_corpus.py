"""Immigration law corpus for RAG seeding.

Contains key USCIS policy manual excerpts, legal frameworks, and AAO decision
summaries used to ground AI assessments in actual immigration law.
"""

import logging

from app.services.vector_db import add_documents, is_seeded

logger = logging.getLogger(__name__)

# Each entry: (id, text, metadata)
# Metadata: pathway (all|eb1a|eb1b|eb1c|niw|o1), topic, source, year

LEGAL_CORPUS: list[tuple[str, str, dict]] = [
    # ──────────────────────────────────────────────
    # EB-1A: Extraordinary Ability
    # ──────────────────────────────────────────────
    (
        "eb1a-overview",
        """EB-1A Extraordinary Ability (INA § 203(b)(1)(A)):
The petitioner must demonstrate extraordinary ability in the sciences, arts, education,
business, or athletics through sustained national or international acclaim. Evidence must
show the beneficiary is one of the small percentage who have risen to the very top of
their field of endeavor. The petitioner must meet at least 3 of 10 regulatory criteria
OR provide evidence of a one-time achievement (e.g., major internationally recognized award
such as a Nobel Prize or Olympic medal).""",
        {"pathway": "eb1a", "topic": "overview", "source": "USCIS Policy Manual Vol 6 Part F", "year": "2024"},
    ),
    (
        "eb1a-kazarian",
        """Kazarian v. USCIS (596 F.3d 1115, 9th Cir. 2010) established the two-step framework
for EB-1A adjudication:
Step 1: Determine whether the evidence meets the plain language requirements of at least
3 of the 10 criteria under 8 CFR 204.5(h)(3).
Step 2: Conduct a final merits determination — review all evidence in totality to determine
whether the petitioner has demonstrated sustained national or international acclaim and is
one of the small percentage at the very top of the field.
Meeting 3 criteria alone is insufficient; the totality must support the extraordinary
ability standard. Adjudicators should not impose novel substantive or evidentiary
requirements beyond those in the regulations.""",
        {"pathway": "eb1a", "topic": "legal_framework", "source": "Kazarian v. USCIS (9th Cir. 2010)", "year": "2010"},
    ),
    (
        "eb1a-oct2024-update",
        """October 2024 USCIS Policy Update for EB-1A (effective October 7, 2024):
Key changes to criteria interpretation:
1. Awards (criterion 1): Expanded to include team awards where petitioner's contribution
is documented. Departmental or institutional awards may qualify if nationally recognized.
2. Membership (criterion 2): Professional associations must require outstanding achievements
as judged by recognized experts. Membership based on education/experience alone is insufficient.
3. Published material about the beneficiary (criterion 3): Online publications, podcasts,
and digital media now explicitly included alongside print media.
4. Judging (criterion 4): Peer review of manuscripts counts. Reviewing grant proposals or
serving on editorial boards qualifies.
5. Original contributions of major significance (criterion 5): Must show the field has
changed as a result. Patents alone are insufficient without evidence of adoption or impact.
6. Scholarly articles (criterion 6): Preprints on recognized platforms (arXiv, bioRxiv)
may count. Citation metrics provide supporting evidence of impact.
7. High salary (criterion 9): Must be high relative to others in the field, not just above
average. Geographic cost-of-living adjustments are considered.
8. Commercial success (criterion 10): Revenue figures, market impact, or commercial
licensing deals can demonstrate success in the arts.""",
        {"pathway": "eb1a", "topic": "policy_update", "source": "USCIS Policy Manual Update Oct 2024", "year": "2024"},
    ),
    (
        "eb1a-citations-guidance",
        """Scholarly Articles and Citations (EB-1A Criterion 6):
USCIS considers both the number of articles and their impact. Raw citation counts are
one factor but must be contextualized within the field. A researcher in a niche subfield
with 200 citations may be more extraordinary than one in a large field with 500 citations.
Key evidence: h-index, citation counts relative to field median, journal impact factors,
invited reviews. Self-citations should be excluded. Conference papers may count if they
are peer-reviewed and published in recognized proceedings.
AAO guidance: The petitioner should demonstrate that their scholarly work has been
recognized beyond their immediate circle of collaborators.""",
        {"pathway": "eb1a", "topic": "criteria_detail", "source": "USCIS Policy Manual + AAO decisions", "year": "2024"},
    ),
    (
        "eb1a-original-contributions",
        """Original Contributions of Major Significance (EB-1A Criterion 5):
This is often the most contested criterion. USCIS requires evidence that the contribution
has already impacted the field, not merely that it has potential. Strong evidence includes:
- Letters from independent experts explaining how the work changed their research/practice
- Citations showing other researchers built upon the work
- Industry adoption of methods, tools, or standards developed by the petitioner
- Media coverage of the contribution's impact
- Patents with evidence of licensing, commercial use, or industry adoption
A patent alone, without evidence of its significance in the field, is insufficient.
Similarly, an invitation to present at a conference does not by itself prove major
significance — the response and impact of the presentation matter more.""",
        {"pathway": "eb1a", "topic": "criteria_detail", "source": "USCIS Policy Manual + AAO decisions", "year": "2024"},
    ),
    (
        "eb1a-final-merits",
        """EB-1A Final Merits Determination (Step 2 of Kazarian):
Even after satisfying 3+ criteria, USCIS evaluates the totality of evidence. Factors include:
- Breadth of acclaim: national vs. international recognition
- Consistency of acclaim over time (sustained, not one-time)
- Comparison to peers at the top of the field
- Whether the beneficiary's entry to the US will substantially benefit prospectively
The beneficiary need not demonstrate they are THE best, but must show they are among the
small percentage at the very top. In practice, meeting 4-5 criteria strongly with corroborating
evidence typically supports a favorable final merits determination in 2025-2026.""",
        {"pathway": "eb1a", "topic": "adjudication", "source": "USCIS Policy Manual Vol 6 Part F Ch 2", "year": "2024"},
    ),

    # ──────────────────────────────────────────────
    # EB-1B: Outstanding Researchers and Professors
    # ──────────────────────────────────────────────
    (
        "eb1b-overview",
        """EB-1B Outstanding Professors and Researchers (INA § 203(b)(1)(B)):
The petitioner must demonstrate international recognition as outstanding in a specific
academic field. Requirements:
1. At least 3 years of experience in teaching or research in the academic field
2. A permanent job offer (tenured, tenure-track, or comparable permanent research position)
   from a US employer
3. The employer must have at least 3 full-time researchers and documented achievements
4. Must meet at least 2 of 6 documentary criteria under 8 CFR 204.5(i)(3)
Note: The job offer must be from a university, institution of higher education, or a
private employer with a department/division that employs at least 3 full-time researchers.""",
        {"pathway": "eb1b", "topic": "overview", "source": "USCIS Policy Manual Vol 6 Part F Ch 3", "year": "2024"},
    ),
    (
        "eb1b-criteria-detail",
        """EB-1B Documentary Criteria (8 CFR 204.5(i)(3)) — must meet 2 of 6:
1. Major prizes or awards for outstanding achievement in the academic field
2. Membership in associations requiring outstanding achievements of their members
3. Published material in professional publications written by others about the beneficiary's
   work in the academic field
4. Participation as a judge of the work of others in the same or allied academic field
   (includes peer review)
5. Original scientific or scholarly research contributions to the academic field
6. Authorship of scholarly books or articles in scholarly journals with international
   circulation in the academic field

Key distinction from EB-1A: EB-1B is limited to academia/research, requires a job offer,
and has a lower threshold (2 of 6 instead of 3 of 10). The standard is "outstanding" rather
than "extraordinary ability" — a meaningful difference in adjudication.""",
        {"pathway": "eb1b", "topic": "criteria_detail", "source": "8 CFR 204.5(i)(3)", "year": "2024"},
    ),
    (
        "eb1b-job-offer",
        """EB-1B Job Offer Requirement:
The petitioner must have a specific offer of employment from a qualifying US employer:
- University or institution of higher education for a tenured or tenure-track position
- University or institution of higher education for a permanent research position
- Private employer for a comparable permanent research position
For private employers: the department/division must employ at least 3 full-time researchers
and have documented achievements in the academic field. "Comparable" means the position is
permanent, the researcher's duties are primarily research-focused, and the position carries
the expectation of long-term employment.
Postdoctoral positions generally do NOT qualify unless they are truly permanent research positions.
Contract or term-limited positions do not satisfy the permanent job offer requirement.""",
        {"pathway": "eb1b", "topic": "requirements", "source": "USCIS Policy Manual Vol 6 Part F Ch 3", "year": "2024"},
    ),

    # ──────────────────────────────────────────────
    # EB-1C: Multinational Managers and Executives
    # ──────────────────────────────────────────────
    (
        "eb1c-overview",
        """EB-1C Multinational Managers and Executives (INA § 203(b)(1)(C)):
For multinational companies transferring managers or executives to the US. Requirements:
1. The beneficiary must have been employed outside the US for at least 1 of the 3 years
   preceding the petition in a managerial or executive capacity
2. The beneficiary must be coming to the US to work in a managerial or executive capacity
3. The petitioner (US employer) must have been doing business for at least 1 year
4. The petitioner must have a qualifying relationship with the foreign employer
   (parent, branch, subsidiary, or affiliate)
5. The foreign entity must continue to do business (or have successor interest)""",
        {"pathway": "eb1c", "topic": "overview", "source": "USCIS Policy Manual Vol 6 Part F Ch 4", "year": "2024"},
    ),
    (
        "eb1c-manager-executive",
        """EB-1C Managerial vs. Executive Capacity:
Manager: Must meet ALL of:
- Manages an organization, department, subdivision, or function
- Supervises and controls the work of other supervisory, professional, or managerial employees,
  OR manages an essential function
- Has authority to hire/fire or recommend personnel actions, OR if no direct reports, functions
  at a senior level within the organizational hierarchy
- Exercises discretion over day-to-day operations of the activity or function

Executive: Must meet ALL of:
- Directs management of the organization or a major component/function
- Establishes goals and policies of the organization, component, or function
- Exercises wide latitude in discretionary decision-making
- Receives only general supervision from higher-level executives, board of directors, or stockholders

A "function manager" manages an essential function but may not supervise staff directly.
USCIS will scrutinize whether the beneficiary truly operates at a managerial/executive level
or performs primarily operational duties.""",
        {"pathway": "eb1c", "topic": "requirements", "source": "USCIS Policy Manual + INA § 101(a)(44)", "year": "2024"},
    ),
    (
        "eb1c-qualifying-relationship",
        """EB-1C Qualifying Organizational Relationship:
The US and foreign entities must have one of these relationships:
- Parent/subsidiary: ownership or control of the other entity
- Branch: operating division of the same organization in another country
- Affiliate: both owned/controlled by the same entity, or one controls both

Key evidence:
- Articles of incorporation, bylaws, operating agreements
- Stock certificates, shareholder agreements
- Tax returns showing ownership structure
- Organizational charts demonstrating the relationship
- Evidence the foreign entity continues doing business abroad""",
        {"pathway": "eb1c", "topic": "requirements", "source": "USCIS Policy Manual Vol 6 Part F Ch 4", "year": "2024"},
    ),

    # ──────────────────────────────────────────────
    # NIW: National Interest Waiver
    # ──────────────────────────────────────────────
    (
        "niw-overview",
        """NIW National Interest Waiver (INA § 203(b)(2)(B)):
An EB-2 classification that waives the labor certification requirement when it is in the
national interest. The petitioner must first establish EB-2 eligibility (advanced degree
or exceptional ability) and then demonstrate the three Dhanasar prongs.
NIW does not require a job offer or labor certification — the beneficiary can self-petition.
This makes it attractive for researchers, entrepreneurs, and professionals who can
demonstrate their work benefits the US broadly.""",
        {"pathway": "niw", "topic": "overview", "source": "USCIS Policy Manual Vol 6 Part F Ch 5", "year": "2024"},
    ),
    (
        "niw-dhanasar",
        """Dhanasar Framework (Matter of Dhanasar, 26 I&N Dec. 884, AAO 2016):
Three-prong test for NIW. ALL three must be satisfied:

Prong 1 — Substantial Merit and National Importance:
The proposed endeavor must have substantial merit (benefit to society) and national
importance (impact beyond a local area). Fields like STEM, healthcare, education,
business/entrepreneurship, and critical infrastructure are commonly successful.
The endeavor need not have national scope — even local work can have national implications
if it advances knowledge or solves problems of national concern.

Prong 2 — Well-Positioned to Advance the Endeavor:
The petitioner must show they are well positioned to advance the proposed endeavor.
Factors: education, skills, knowledge, track record of success, future plans, progress
already made, interest from potential customers/users/investors.
A detailed business plan or research plan strengthens this prong.

Prong 3 — Balance of National Interest:
On balance, it would be beneficial to the US to waive the labor certification requirement.
The petitioner must show that the national interest would be adversely affected if the
standard labor certification process were required. Factors: urgency of the work,
unique qualifications, impact of delay caused by labor certification.""",
        {"pathway": "niw", "topic": "legal_framework", "source": "Matter of Dhanasar (AAO 2016)", "year": "2016"},
    ),
    (
        "niw-stem-guidance",
        """NIW and STEM Fields (January 2022 USCIS Policy Guidance):
USCIS issued specific guidance encouraging NIW petitions in STEM fields critical to
US competitiveness. Key points:
- STEM endeavors may warrant favorable consideration under Prong 1 (national importance)
  if they relate to areas of national concern (AI, quantum computing, biotechnology,
  semiconductors, clean energy, cybersecurity, space technology)
- Letters from government agencies, industry leaders, or research institutions describing
  the national importance of the field are particularly persuasive
- For Prong 2, publications, citations, grants, patents, and industry adoption are strong evidence
- For Prong 3, USCIS recognizes that requiring labor certification for highly specialized
  STEM roles may not serve the national interest due to acute talent shortages

Entrepreneurs can qualify by showing their startup addresses a critical STEM need,
with evidence of funding, traction, partnerships, or other validation.""",
        {"pathway": "niw", "topic": "policy_guidance", "source": "USCIS STEM NIW Guidance Jan 2022", "year": "2022"},
    ),
    (
        "niw-eb2-eligibility",
        """NIW: Establishing EB-2 Eligibility (prerequisite):
Before applying the Dhanasar framework, the petitioner must qualify for EB-2:

Option A — Advanced Degree:
- Master's degree or higher in a related field, OR
- Bachelor's degree + 5 years progressive post-baccalaureate experience
  (treated as equivalent to a master's)

Option B — Exceptional Ability:
Must meet at least 3 of 6 criteria:
1. Official academic record of degree/diploma related to the area of exceptional ability
2. Letters documenting at least 10 years of full-time experience in the occupation
3. License to practice or certification in the profession
4. Evidence of commanding a high salary or remuneration
5. Membership in professional associations
6. Recognition by peers, government, or professional organizations for achievements

Most NIW petitioners use the advanced degree route.""",
        {"pathway": "niw", "topic": "eligibility", "source": "8 CFR 204.5(k)", "year": "2024"},
    ),

    # ──────────────────────────────────────────────
    # O-1A: Extraordinary Ability (Nonimmigrant)
    # ──────────────────────────────────────────────
    (
        "o1a-overview",
        """O-1A Extraordinary Ability Visa (INA § 101(a)(15)(O)):
Nonimmigrant visa for individuals with extraordinary ability in sciences, education,
business, or athletics. Requires demonstration of sustained national or international
acclaim and recognition for achievements. Must come to the US to continue working in
the area of extraordinary ability.
Requires meeting at least 3 of 8 criteria OR evidence of a major internationally
recognized award. Also requires a US employer or agent sponsor and an advisory opinion
from a peer group or labor organization.
O-1A is a nonimmigrant (temporary) visa, unlike EB-1A which leads to permanent residence.
However, O-1A holders may simultaneously pursue green card petitions (dual intent is allowed).""",
        {"pathway": "o1", "topic": "overview", "source": "USCIS Policy Manual Vol 2 Part M", "year": "2024"},
    ),
    (
        "o1a-criteria-detail",
        """O-1A Criteria (8 CFR 214.2(o)(3)(iii)) — must meet 3 of 8:
1. Receipt of nationally or internationally recognized prizes or awards for excellence
2. Membership in associations that require outstanding achievements (as judged by experts)
3. Published material in major media or professional publications about the beneficiary
4. Participation as a judge of the work of others in the field
5. Original scientific, scholarly, or business-related contributions of major significance
6. Authorship of scholarly articles in professional journals or major media
7. Employment in a critical or essential capacity for distinguished organizations
8. Commanded or will command a high salary relative to others in the field

Key differences from EB-1A: O-1A has 8 criteria (not 10), no "leading/critical role"
or "exhibition" criteria. The "employment in critical capacity" criterion (7) is unique
to O-1A and can be very useful for professionals at prominent companies.
The evidentiary standard is the same — sustained national or international acclaim —
but in practice O-1A adjudications tend to be somewhat more favorable than EB-1A.""",
        {"pathway": "o1", "topic": "criteria_detail", "source": "8 CFR 214.2(o)(3)(iii)", "year": "2024"},
    ),
    (
        "o1a-advisory-opinion",
        """O-1A Advisory Opinion Requirement:
Every O-1A petition must include a written advisory opinion from a peer group, labor
organization, or person with expertise in the beneficiary's field. The opinion should
address the beneficiary's extraordinary ability and achievements.
If no appropriate peer group exists, USCIS may accept a letter from an expert in the field.
The advisory opinion is consultative — USCIS is not bound by it but gives it significant weight.
Common sources: IEEE (tech), ACM (computing), professional societies, university departments.""",
        {"pathway": "o1", "topic": "requirements", "source": "8 CFR 214.2(o)(5)", "year": "2024"},
    ),
    (
        "o1a-critical-capacity",
        """O-1A Critical or Essential Capacity (Criterion 7):
Employment in a critical or essential capacity for organizations with a distinguished reputation.
"Critical or essential" means the beneficiary's role was vital to the organization's goals
or operations — not merely employment at a prominent company.
Evidence should show:
- Job title and specific responsibilities
- The organization's distinguished reputation (awards, rankings, market position)
- How the beneficiary's work was indispensable — what would be lost without them
- Unique skills or expertise the beneficiary brought to the role
Senior engineering roles at FAANG/major tech companies often qualify when framed properly,
showing the petitioner led critical projects, architectures, or teams.""",
        {"pathway": "o1", "topic": "criteria_detail", "source": "USCIS Policy Manual + AAO decisions", "year": "2024"},
    ),

    # ──────────────────────────────────────────────
    # Cross-Pathway: General Guidance
    # ──────────────────────────────────────────────
    (
        "general-evidence-standards",
        """USCIS General Evidence Standards for Employment-Based Immigration:
- Preponderance of evidence standard: "more likely than not" (51%+ probability)
- Corroborating evidence strengthens claims — a single letter or document is rarely sufficient
- Expert/reference letters should be from independent experts (not collaborators or supervisors)
  whenever possible. Letters from direct collaborators carry less weight.
- Quantitative evidence (metrics, rankings, dollar figures) should be contextualized:
  "Top 5% of all researchers" is stronger than "500 citations" without field context
- USCIS may issue a Request for Evidence (RFE) — not a denial, but a request for more documentation
- Self-serving statements without corroboration are given little weight
- Quality of evidence matters more than quantity — 5 strong letters beat 20 generic ones""",
        {"pathway": "all", "topic": "evidence_standards", "source": "USCIS Policy Manual Vol 6", "year": "2024"},
    ),
    (
        "general-comparable-evidence",
        """Comparable Evidence (8 CFR 204.5(h)(4) for EB-1A; similar provisions for other categories):
If the standard criteria do not readily apply to the beneficiary's occupation, the petitioner
may submit comparable evidence. This is NOT a catch-all — the petitioner must:
1. Explain why the specific criteria are not readily applicable
2. Show that the comparable evidence is truly equivalent in significance
Example: A tech entrepreneur may not have "scholarly articles" but can show equivalent impact
through widely-adopted open-source projects, technical blog posts with millions of views,
or keynote addresses at major industry conferences.
USCIS has become more receptive to comparable evidence since the October 2024 policy update,
particularly for professionals in technology and business fields.""",
        {"pathway": "all", "topic": "evidence_standards", "source": "8 CFR 204.5(h)(4)", "year": "2024"},
    ),
    (
        "general-rfe-noid",
        """Understanding RFEs and NOIDs:
Request for Evidence (RFE): USCIS requests additional documentation. Not a denial.
The petitioner typically has 87 days to respond. Common triggers:
- Insufficient initial evidence for claimed criteria
- Unclear organizational relationship (EB-1C)
- Weak Prong 3 argument (NIW)
- Lack of independent corroboration

Notice of Intent to Deny (NOID): More serious — USCIS intends to deny but gives the
petitioner a chance to respond. Common triggers:
- Fundamental eligibility issues (e.g., EB-1B without qualifying job offer)
- Evidence appears fabricated or inconsistent
- Prior immigration violations

Both RFEs and NOIDs are addressable with additional evidence and argumentation.
A well-prepared initial petition minimizes the chance of either.""",
        {"pathway": "all", "topic": "adjudication", "source": "USCIS Policy Manual Vol 1", "year": "2024"},
    ),
    (
        "general-processing-times-2025",
        """2025-2026 Processing Context:
- Premium processing available for EB-1A, EB-1B, EB-1C, and NIW (15 business days for
  initial adjudication after premium processing request is received)
- Regular processing for employment-based I-140: varies by service center (4-12 months)
- O-1A: Premium processing available (15 business days)
- EB-1 categories are generally current for all countries (no visa bulletin backlog)
- EB-2 (NIW) may have a backlog for India and China-born applicants
- USCIS has increased denials in recent years — thorough initial filings are critical
- Multiple petitions are allowed — many applicants file both O-1A and EB-1A simultaneously""",
        {"pathway": "all", "topic": "processing", "source": "USCIS Processing Times 2025", "year": "2025"},
    ),
    (
        "general-tech-workers",
        """Guidance for Technology Professionals:
Software engineers, data scientists, ML researchers, and tech founders frequently pursue
EB-1A, O-1A, or NIW. Common strong evidence:
- GitHub contributions to widely-used open-source projects (stars, forks, downstream dependents)
- Stack Overflow reputation and impact metrics
- Patents in AI/ML, cloud computing, cybersecurity
- Publications at top conferences (NeurIPS, ICML, CVPR, ACL, KDD, SIGMOD)
- Critical role at major tech companies (FAANG, unicorn startups)
- Speaking at major conferences (re:Invent, Google I/O, WWDC, KubeCon)
- High salary relative to field (total compensation including equity)
For O-1A/EB-1A: frame open-source work as "original contributions of major significance"
with evidence of adoption (npm downloads, Docker pulls, GitHub stars vs. field baseline).
For NIW: frame STEM work as nationally important, cite government reports on talent shortages.""",
        {"pathway": "all", "topic": "field_guidance", "source": "Immigration attorney best practices", "year": "2025"},
    ),
]


def seed_corpus() -> None:
    """Seed the vector database with the legal corpus if not already seeded."""
    if is_seeded():
        logger.info("Legal corpus already seeded, skipping")
        return

    ids = [entry[0] for entry in LEGAL_CORPUS]
    texts = [entry[1] for entry in LEGAL_CORPUS]
    metadatas = [entry[2] for entry in LEGAL_CORPUS]

    add_documents(texts=texts, metadatas=metadatas, ids=ids)
    logger.info(f"Seeded legal corpus with {len(LEGAL_CORPUS)} documents")
