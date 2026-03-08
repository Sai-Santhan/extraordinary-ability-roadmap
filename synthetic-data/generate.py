#!/usr/bin/env python3
"""Generate synthetic demo files for 3 immigration personas."""
import json
import os
import mailbox
import email.message
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_priya_sharma():
    """Dr. Priya Sharma - AI Researcher targeting EB-1A in 2 years.
    Strong: 25 publications, h-index 15, 3 conference PC memberships
    Weak: No awards, no media coverage, no selective memberships
    """
    persona_dir = os.path.join(BASE_DIR, "priya-sharma")

    # === CV as plain text (will be saved as .txt since we can't generate real PDF without reportlab in this script) ===
    cv_text = """DR. PRIYA SHARMA
Senior Research Scientist | Google DeepMind
priya.sharma@email.com | github.com/priyasharma-ai

EDUCATION
Ph.D. in Computer Science, Stanford University, 2020
  Dissertation: "Attention Mechanisms for Multi-Modal Reasoning"
  Advisor: Prof. James Chen
M.S. in Computer Science, IIT Bombay, 2016
B.Tech in Computer Science, IIT Bombay, 2014

CURRENT POSITION
Senior Research Scientist, Google DeepMind (2022 - present)
- Leading a team of 4 researchers on multi-modal language models
- Developed novel attention architecture adopted by 3 product teams
- Published 8 papers in top-tier venues since joining

PREVIOUS POSITIONS
Research Scientist, Google Brain (2020 - 2022)
- Core contributor to PaLM model architecture
- 5 first-author publications in NeurIPS, ICML, ACL

Research Intern, Meta AI (FAIR) (Summer 2019)
- Worked on cross-lingual transfer learning
- Paper accepted at EMNLP 2019

IMMIGRATION STATUS
H-1B visa holder
Country of birth: India

PUBLICATIONS (Selected - 25 total)
1. "ScaleFormer: Efficient Multi-Scale Attention for Language Models" - NeurIPS 2025 (Oral), Citations: 187
2. "Cross-Modal Reasoning with Sparse Attention" - ICML 2025, Citations: 124
3. "Dynamic Token Pruning for Efficient Inference" - ACL 2024, Citations: 203
4. "Multi-Modal Chain-of-Thought Prompting" - NeurIPS 2024, Citations: 312
5. "Adaptive Compute for Language Generation" - ICLR 2024, Citations: 156
6. "Hierarchical Attention Networks for Document Understanding" - ACL 2023, Citations: 289
7. "Efficient Training of Large Language Models with Mixed Precision" - ICML 2023, Citations: 198
8. "Self-Supervised Pre-training for Code Generation" - EMNLP 2023, Citations: 167
9. "Retrieval-Augmented Generation for Knowledge-Intensive Tasks" - NeurIPS 2022 (Spotlight), Citations: 445
10. "Cross-Lingual Transfer with Shared Representations" - EMNLP 2019, Citations: 234
... (15 more publications in top venues)

TOTAL CITATIONS: 4,287
H-INDEX: 15
i10-INDEX: 22

PEER REVIEW & JUDGING
- Program Committee Member, NeurIPS (2023, 2024, 2025)
- Program Committee Member, ICML (2024, 2025)
- Program Committee Member, ACL (2022, 2023, 2024, 2025)
- Reviewer, Nature Machine Intelligence (2024)
- Reviewer, JMLR (2022-present)

SPEAKING ENGAGEMENTS
- Keynote: "The Future of Multi-Modal AI" - AI Summit San Francisco (2025)
- Invited Talk: "Efficient Attention Mechanisms" - MIT CSAIL (2024)
- Tutorial: "Scaling Language Models" - NeurIPS 2024
- Panel: "Responsible AI Development" - ACM FAccT 2024

SALARY
Total compensation: $485,000/year (base + equity)

SKILLS
Python, PyTorch, JAX, TensorFlow, CUDA, Large Language Models, Multi-Modal AI, Attention Mechanisms
"""

    # Save CV as text file (simulating PDF content)
    with open(os.path.join(persona_dir, "cv.txt"), "w") as f:
        f.write(cv_text)

    # === Google Scholar Data (JSON) ===
    scholar_data = {
        "name": "Dr. Priya Sharma",
        "affiliation": "Google DeepMind",
        "h_index": 15,
        "i10_index": 22,
        "total_citations": 4287,
        "papers": [
            {"title": "ScaleFormer: Efficient Multi-Scale Attention for Language Models", "venue": "NeurIPS 2025", "year": 2025, "citations": 187, "authors": ["Priya Sharma", "Alex Kim", "James Chen"]},
            {"title": "Cross-Modal Reasoning with Sparse Attention", "venue": "ICML 2025", "year": 2025, "citations": 124, "authors": ["Priya Sharma", "Wei Li"]},
            {"title": "Dynamic Token Pruning for Efficient Inference", "venue": "ACL 2024", "year": 2024, "citations": 203, "authors": ["Priya Sharma", "Raj Patel", "Ming Zhou"]},
            {"title": "Multi-Modal Chain-of-Thought Prompting", "venue": "NeurIPS 2024", "year": 2024, "citations": 312, "authors": ["Priya Sharma", "Sarah Johnson", "David Lee"]},
            {"title": "Adaptive Compute for Language Generation", "venue": "ICLR 2024", "year": 2024, "citations": 156, "authors": ["Priya Sharma", "Tom Brown"]},
            {"title": "Hierarchical Attention Networks for Document Understanding", "venue": "ACL 2023", "year": 2023, "citations": 289, "authors": ["Priya Sharma", "Lisa Wang"]},
            {"title": "Efficient Training of Large Language Models with Mixed Precision", "venue": "ICML 2023", "year": 2023, "citations": 198, "authors": ["Priya Sharma", "Mark Davis", "Anna Lee"]},
            {"title": "Self-Supervised Pre-training for Code Generation", "venue": "EMNLP 2023", "year": 2023, "citations": 167, "authors": ["Priya Sharma", "Carlos Rodriguez"]},
            {"title": "Retrieval-Augmented Generation for Knowledge-Intensive Tasks", "venue": "NeurIPS 2022", "year": 2022, "citations": 445, "authors": ["Priya Sharma", "James Chen", "Wei Li", "Raj Patel"]},
            {"title": "Cross-Lingual Transfer with Shared Representations", "venue": "EMNLP 2019", "year": 2019, "citations": 234, "authors": ["Priya Sharma", "Pierre Dupont"]},
        ]
    }
    with open(os.path.join(persona_dir, "scholar.json"), "w") as f:
        json.dump(scholar_data, f, indent=2)

    # === Gmail MBOX (synthetic conference invites and review requests) ===
    mbox_path = os.path.join(persona_dir, "gmail.mbox")
    mbox = mailbox.mbox(mbox_path)

    emails_data = [
        {
            "subject": "Invitation to serve on NeurIPS 2025 Program Committee",
            "from": "neurips2025-pc@neurips.cc",
            "to": "priya.sharma@email.com",
            "date": "Mon, 15 Jan 2025 10:00:00 +0000",
            "body": "Dear Dr. Sharma,\n\nOn behalf of the NeurIPS 2025 organizing committee, we would like to invite you to serve as a member of the Program Committee for the 39th Conference on Neural Information Processing Systems (NeurIPS 2025).\n\nYour expertise in attention mechanisms and multi-modal AI makes you an ideal reviewer. You would be expected to review 4-6 papers.\n\nPlease confirm by February 1, 2025.\n\nBest regards,\nNeurIPS 2025 Program Chairs"
        },
        {
            "subject": "Invitation: Keynote Speaker at AI Summit San Francisco 2025",
            "from": "events@aisummit.com",
            "to": "priya.sharma@email.com",
            "date": "Wed, 05 Feb 2025 14:30:00 +0000",
            "body": "Dear Dr. Sharma,\n\nWe are honored to invite you to deliver a keynote address at the AI Summit San Francisco 2025, taking place June 15-17, 2025.\n\nYour groundbreaking work on multi-modal AI and efficient attention mechanisms has positioned you as one of the leading voices in the field. We would love for you to share your insights on \"The Future of Multi-Modal AI.\"\n\nHonorarium: $5,000\nTravel and accommodation covered.\n\nPlease let us know your availability.\n\nBest,\nAI Summit Organizing Committee"
        },
        {
            "subject": "Review Request: Nature Machine Intelligence Submission #NMI-2024-1847",
            "from": "naturemi@nature.com",
            "to": "priya.sharma@email.com",
            "date": "Fri, 20 Sep 2024 09:15:00 +0000",
            "body": "Dear Dr. Sharma,\n\nI am writing to ask whether you would be willing to review a manuscript that has been submitted to Nature Machine Intelligence.\n\nTitle: \"Emergent Reasoning Capabilities in Scaled Language Models\"\n\nGiven your published expertise in language model architectures and reasoning, your review would be highly valuable.\n\nPlease respond within 5 days.\n\nBest regards,\nDr. Emily Roberts\nAssociate Editor, Nature Machine Intelligence"
        },
        {
            "subject": "ICML 2024 Paper Decision: Accept",
            "from": "icml2024@icml.cc",
            "to": "priya.sharma@email.com",
            "date": "Tue, 12 Mar 2024 16:00:00 +0000",
            "body": "Dear Dr. Sharma,\n\nWe are pleased to inform you that your paper \"Adaptive Compute for Language Generation\" has been accepted to ICML 2024.\n\nReviewer scores: 8, 7, 8 (Strong Accept, Accept, Strong Accept)\n\nThe camera-ready deadline is April 15, 2024.\n\nCongratulations!\nICML 2024 Program Chairs"
        },
        {
            "subject": "Invitation to NeurIPS 2024 Tutorial on Scaling Language Models",
            "from": "tutorials@neurips.cc",
            "to": "priya.sharma@email.com",
            "date": "Mon, 08 Jul 2024 11:00:00 +0000",
            "body": "Dear Dr. Sharma,\n\nThe NeurIPS 2024 Tutorial Committee is pleased to accept your tutorial proposal \"Scaling Language Models: From Architecture to Deployment.\"\n\nYour tutorial is scheduled for the first day of the conference. Please prepare a 3-hour presentation.\n\nBest regards,\nNeurIPS 2024 Tutorial Chairs"
        },
    ]

    for ed in emails_data:
        msg = email.message.EmailMessage()
        msg["Subject"] = ed["subject"]
        msg["From"] = ed["from"]
        msg["To"] = ed["to"]
        msg["Date"] = ed["date"]
        msg.set_content(ed["body"])
        mbox.add(msg)

    mbox.close()

    # === Calendar ICS (speaking engagements) ===
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Synthetic Data Generator//EN
BEGIN:VEVENT
SUMMARY:Keynote: The Future of Multi-Modal AI - AI Summit SF
DTSTART:20250615T090000Z
DTEND:20250615T100000Z
LOCATION:Moscone Center, San Francisco, CA
DESCRIPTION:Keynote address at AI Summit San Francisco 2025. Topic: The Future of Multi-Modal AI.
END:VEVENT
BEGIN:VEVENT
SUMMARY:Invited Talk: Efficient Attention Mechanisms - MIT CSAIL
DTSTART:20241015T140000Z
DTEND:20241015T153000Z
LOCATION:MIT Stata Center, Cambridge, MA
DESCRIPTION:Invited research talk at MIT CSAIL. Presenting recent work on efficient attention mechanisms for large language models.
END:VEVENT
BEGIN:VEVENT
SUMMARY:Tutorial: Scaling Language Models - NeurIPS 2024
DTSTART:20241209T090000Z
DTEND:20241209T120000Z
LOCATION:Vancouver Convention Centre, Vancouver, BC
DESCRIPTION:3-hour tutorial at NeurIPS 2024 on scaling language models from architecture to deployment.
END:VEVENT
BEGIN:VEVENT
SUMMARY:Panel: Responsible AI Development - ACM FAccT 2024
DTSTART:20240604T110000Z
DTEND:20240604T123000Z
LOCATION:Rio de Janeiro, Brazil
DESCRIPTION:Panel discussion on responsible AI development practices at ACM Conference on Fairness, Accountability, and Transparency.
END:VEVENT
BEGIN:VEVENT
SUMMARY:NeurIPS 2025 PC Meeting
DTSTART:20250715T100000Z
DTEND:20250715T160000Z
LOCATION:Virtual
DESCRIPTION:Program Committee meeting for NeurIPS 2025. Discuss borderline papers and final decisions.
END:VEVENT
END:VCALENDAR"""

    with open(os.path.join(persona_dir, "calendar.ics"), "w") as f:
        f.write(ics_content)

    print("Generated: Priya Sharma (AI Researcher, EB-1A)")


def generate_marco_chen():
    """Marco Chen - Senior SWE targeting EB-2 NIW in 3 years.
    Strong: 500+ GitHub stars, 3 patents, critical role at FAANG
    Weak: No publications, no judging, limited visibility
    """
    persona_dir = os.path.join(BASE_DIR, "marco-chen")

    # CV
    cv_text = """MARCO CHEN
Staff Software Engineer | Meta (formerly Facebook)
marco.chen@email.com | github.com/marcochen

EDUCATION
M.S. in Computer Science, Carnegie Mellon University, 2018
B.S. in Computer Science, Tsinghua University, 2016

CURRENT POSITION
Staff Software Engineer, Meta (2021 - present)
- Tech lead for distributed systems infrastructure serving 3 billion users
- Designed and implemented real-time data pipeline processing 50TB/day
- Led migration of legacy monolith to microservices, reducing latency by 40%
- Mentoring 6 engineers; promoted 2 to senior level
- Critical role in Meta's messaging infrastructure team

PREVIOUS POSITIONS
Senior Software Engineer, Google (2018 - 2021)
- Core team member on Google Cloud Pub/Sub
- Implemented exactly-once delivery semantics, serving 10,000+ enterprise customers
- 2 patents on distributed message ordering algorithms

Software Engineer, Alibaba Cloud (2016 - 2018)
- Built stream processing engine handling 1M events/second
- 1 patent on adaptive load balancing for cloud environments

IMMIGRATION STATUS
H-1B visa holder
Country of birth: China

PATENTS
1. "Method for Guaranteed Message Ordering in Distributed Pub/Sub Systems" - US Patent 11,234,567 (2020)
2. "Adaptive Partitioning for Fault-Tolerant Message Delivery" - US Patent 11,345,678 (2021)
3. "Dynamic Load Balancing in Multi-Tenant Cloud Environments" - US Patent 11,456,789 (2019)

OPEN SOURCE CONTRIBUTIONS
- github.com/marcochen/fastqueue - High-performance message queue library (847 stars, 120 forks)
- github.com/marcochen/distrib-tools - Distributed systems testing toolkit (312 stars)
- Contributor to Apache Kafka (15 merged PRs)
- Contributor to etcd (8 merged PRs)

GITHUB METRICS
Total stars: 1,200+
Contributions last year: 847
Pull request reviews: 200+

SPEAKING
- "Building Reliable Distributed Systems at Scale" - Meta Internal Tech Talk (2024)
- "Exactly-Once Semantics in Practice" - Strange Loop 2023

SALARY
Total compensation: $520,000/year (base + equity + bonus)
"""

    with open(os.path.join(persona_dir, "cv.txt"), "w") as f:
        f.write(cv_text)

    # GitHub data
    github_data = {
        "username": "marcochen",
        "name": "Marco Chen",
        "company": "Meta",
        "followers": 1245,
        "total_stars": 1200,
        "contributions_last_year": 847,
        "pr_reviews": 203,
        "repositories": [
            {"name": "fastqueue", "description": "High-performance message queue library for distributed systems", "stars": 847, "forks": 120, "language": "Rust", "topics": ["distributed-systems", "message-queue", "high-performance"]},
            {"name": "distrib-tools", "description": "Testing toolkit for distributed systems", "stars": 312, "forks": 45, "language": "Go", "topics": ["distributed-systems", "testing", "chaos-engineering"]},
            {"name": "partition-sim", "description": "Network partition simulator for testing fault tolerance", "stars": 41, "forks": 8, "language": "Python", "topics": ["testing", "distributed-systems"]},
        ],
        "contributions_to": [
            {"repo": "apache/kafka", "prs_merged": 15},
            {"repo": "etcd-io/etcd", "prs_merged": 8},
        ]
    }
    with open(os.path.join(persona_dir, "github.json"), "w") as f:
        json.dump(github_data, f, indent=2)

    # LinkedIn PDF (simulated as text)
    linkedin_text = """Marco Chen
Staff Software Engineer at Meta

San Francisco Bay Area

Experience

Staff Software Engineer
Meta
Jan 2021 - Present (5 years)
San Francisco, California
- Tech lead for distributed systems infrastructure
- Designed real-time data pipeline processing 50TB/day
- Led microservices migration reducing latency by 40%
- Critical role in messaging infrastructure serving 3B users

Senior Software Engineer
Google
Aug 2018 - Dec 2020 (2 years 5 months)
Mountain View, California
- Core team on Google Cloud Pub/Sub
- Implemented exactly-once delivery semantics
- 2 patents on distributed message ordering

Software Engineer
Alibaba Cloud
Jul 2016 - Jul 2018 (2 years)
Hangzhou, China
- Built stream processing engine (1M events/sec)
- 1 patent on adaptive load balancing

Education

Carnegie Mellon University
M.S., Computer Science, 2018

Tsinghua University
B.S., Computer Science, 2016

Skills
Distributed Systems, Rust, Go, Python, Kafka, Kubernetes, System Design, Cloud Infrastructure

Recommendations

"Marco is one of the most talented distributed systems engineers I've worked with. His design for our pub/sub exactly-once delivery system was elegant and battle-tested at massive scale." - Sarah Kim, Engineering Director at Google

"Marco's technical leadership on our messaging infrastructure has been exceptional. He architected solutions that serve billions of users with remarkable reliability." - David Park, VP of Engineering at Meta
"""
    with open(os.path.join(persona_dir, "linkedin.txt"), "w") as f:
        f.write(linkedin_text)

    print("Generated: Marco Chen (Staff SWE, NIW)")


def generate_amara_okafor():
    """Amara Okafor - Tech Founder targeting EB-1A in 1 year.
    Strong: TechCrunch coverage, YC alum, 5 conference talks, high compensation
    Weak: No scholarly publications, limited judging
    """
    persona_dir = os.path.join(BASE_DIR, "amara-okafor")

    # CV
    cv_text = """AMARA OKAFOR
CEO & Co-Founder | DataBridge AI
amara@databridge.ai | linkedin.com/in/amaraokafor

EDUCATION
M.S. in Data Science, Columbia University, 2020
B.Sc. in Computer Science, University of Lagos, 2018

CURRENT POSITION
CEO & Co-Founder, DataBridge AI (2021 - present)
- Founded AI-powered data integration platform for healthcare
- Y Combinator W22 batch ($500K investment + $2M seed round)
- 45 employees, $4.2M ARR, 120 enterprise customers
- Platform processes 10M+ patient records daily across 35 hospital systems
- Named to Forbes 30 Under 30 (Enterprise Technology, 2024)

PREVIOUS POSITIONS
Data Scientist, McKinsey & Company (2020 - 2021)
- Led AI/ML projects for Fortune 500 healthcare clients
- Built predictive models reducing hospital readmission rates by 23%

Research Assistant, Columbia University (2019 - 2020)
- Published 2 papers on healthcare data interoperability

IMMIGRATION STATUS
O-1 visa holder
Country of birth: Nigeria

AWARDS & RECOGNITION
- Forbes 30 Under 30 - Enterprise Technology (2024)
- TechCrunch Disrupt Startup Battlefield Finalist (2023)
- Y Combinator Top Company (W22 batch) - Selected from 16,000 applicants
- Columbia University Outstanding Graduate Award (2020)
- Google for Startups Black Founders Fund Recipient ($100K, 2022)

MEDIA COVERAGE
- TechCrunch: "DataBridge AI raises $2M to fix healthcare data silos" (2023)
- Forbes: "30 Under 30: The Nigerian Founder Revolutionizing Healthcare AI" (2024)
- VentureBeat: "How DataBridge AI is solving healthcare interoperability" (2023)
- Healthcare IT News: "AI startup DataBridge connects disparate hospital systems" (2023)
- Bloomberg Technology: Interview on healthcare AI trends (2024)

SPEAKING ENGAGEMENTS
- SXSW 2025: "AI and Healthcare Data Portability"
- Web Summit 2024: "Building AI for Healthcare: Regulatory Challenges"
- TechCrunch Disrupt 2023: Startup Battlefield Presentation
- Y Combinator Demo Day W22: Pitch Presentation
- Health 2.0 Conference 2024: "Interoperability in the Age of AI"

BOARD & ADVISORY ROLES
- Advisory Board Member, Columbia University Health Informatics Program (2023-present)
- Mentor, Techstars NYC (2024-present)
- Judge, MIT Hacking Medicine Grand Hack (2024)

SALARY/COMPENSATION
Founder equity valued at $3.2M; salary $180,000/year + standard benefits
"""

    with open(os.path.join(persona_dir, "cv.txt"), "w") as f:
        f.write(cv_text)

    # LinkedIn (as text)
    linkedin_text = """Amara Okafor
CEO & Co-Founder at DataBridge AI | Y Combinator W22 | Forbes 30 Under 30

New York City Metropolitan Area

Experience

CEO & Co-Founder
DataBridge AI
Jun 2021 - Present
New York, NY
- AI-powered data integration platform for healthcare
- Y Combinator W22 ($500K + $2M seed)
- 45 employees, $4.2M ARR, 120 enterprise customers
- Processing 10M+ patient records daily

Data Scientist
McKinsey & Company
Jul 2020 - May 2021
New York, NY
- AI/ML projects for healthcare clients
- Reduced hospital readmissions by 23%

Education

Columbia University
M.S., Data Science, 2020

University of Lagos
B.Sc., Computer Science, 2018

Honors & Awards
- Forbes 30 Under 30 (2024)
- TechCrunch Disrupt Finalist (2023)
- Y Combinator W22
- Google for Startups Black Founders Fund

Skills
Machine Learning, Healthcare AI, Data Integration, Python, Leadership, Fundraising

Recommendations

"Amara is a visionary founder who combines deep technical expertise with exceptional business acumen. DataBridge AI is transforming how hospitals share data." - Michael Torres, Partner at Y Combinator

"Working with Amara at McKinsey, I saw her ability to translate complex ML concepts into business value. She's one of the most impressive leaders I've encountered." - Jennifer Wu, Senior Partner at McKinsey
"""
    with open(os.path.join(persona_dir, "linkedin.txt"), "w") as f:
        f.write(linkedin_text)

    # ChatGPT export
    chatgpt_export = [
        {
            "title": "EB-1A Strategy Discussion",
            "create_time": 1706745600,
            "mapping": {
                "1": {"message": {"author": {"role": "user"}, "content": {"parts": ["I'm a tech founder with an O-1 visa, and I want to transition to EB-1A. My company DataBridge AI is a Y Combinator company doing $4.2M ARR in healthcare AI. I've been featured in TechCrunch, Forbes 30 Under 30, and spoken at 5 major conferences. What are my chances?"]}}},
                "2": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["Based on what you've described, you have a strong EB-1A profile. Let me analyze against the 10 criteria:\n\n1. Awards: Forbes 30 Under 30, TechCrunch Disrupt Finalist, YC selection - these are competitive and nationally recognized.\n2. Memberships: Y Combinator is highly selective (1.5% acceptance rate).\n3. Published Material: TechCrunch, Forbes, VentureBeat articles about you and your work.\n4. Judging: MIT Hacking Medicine judge - document this.\n5. Original Contributions: DataBridge AI platform, healthcare interoperability solutions.\n6. Scholarly Articles: This is your weakest area.\n7. Exhibitions: N/A for tech.\n8. Leading Role: CEO of YC company with $4.2M ARR, 45 employees.\n9. High Salary: Equity + compensation likely in top percentile.\n10. Commercial Success: $4.2M ARR is strong evidence.\n\nYou likely meet 6-7 criteria, which is excellent. Focus on documenting everything with third-party evidence."]}}},
                "3": {"message": {"author": {"role": "user"}, "content": {"parts": ["What should I do to strengthen my case in the next 6 months?"]}}},
                "4": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["Here's a 6-month plan:\n\n1. Get recommendation letters from YC partners, industry leaders, and healthcare executives\n2. Document your advisory board role at Columbia\n3. Apply to judge more competitions (healthcare hackathons, startup competitions)\n4. Consider publishing a white paper on healthcare data interoperability\n5. Get more press coverage - pitch to Wired, Fast Company\n6. Document your company's impact metrics in detail\n7. Get salary benchmarking data showing your compensation is in the top percentile for your field"]}}}
            }
        },
        {
            "title": "Healthcare AI Conference Strategy",
            "create_time": 1709424000,
            "mapping": {
                "1": {"message": {"author": {"role": "user"}, "content": {"parts": ["I'm preparing my talk for SXSW 2025 on 'AI and Healthcare Data Portability'. Can you help me outline the key points?"]}}},
                "2": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["Great topic! Here's an outline:\n\n1. The Healthcare Data Problem: 80% of health data is unstructured, spread across incompatible systems\n2. Why Portability Matters: Patient outcomes improve 30% with integrated data\n3. AI as the Bridge: How ML models can standardize and integrate diverse data formats\n4. DataBridge AI Case Study: Your platform processing 10M+ records across 35 hospital systems\n5. Regulatory Landscape: ONC Interoperability Rules, TEFCA framework\n6. The Future: Patient-owned health records, AI-powered data portability\n\nThis positions you as a thought leader in healthcare AI interoperability."]}}}
            }
        }
    ]
    with open(os.path.join(persona_dir, "chatgpt-export.json"), "w") as f:
        json.dump(chatgpt_export, f, indent=2)

    # Media URLs
    media_urls = [
        {"title": "DataBridge AI raises $2M to fix healthcare data silos", "outlet": "TechCrunch", "url": "https://techcrunch.com/2023/synthetic/databridge-ai", "date": "2023-06-15", "about_person": True},
        {"title": "30 Under 30: The Nigerian Founder Revolutionizing Healthcare AI", "outlet": "Forbes", "url": "https://forbes.com/2024/synthetic/30under30-amara-okafor", "date": "2024-01-10", "about_person": True},
        {"title": "How DataBridge AI is solving healthcare interoperability", "outlet": "VentureBeat", "url": "https://venturebeat.com/2023/synthetic/databridge", "date": "2023-09-20", "about_person": True},
        {"title": "AI startup DataBridge connects disparate hospital systems", "outlet": "Healthcare IT News", "url": "https://healthcareitnews.com/2023/synthetic/databridge", "date": "2023-11-05", "about_person": True},
        {"title": "Interview: Healthcare AI Trends with Amara Okafor", "outlet": "Bloomberg Technology", "url": "https://bloomberg.com/2024/synthetic/healthcare-ai", "date": "2024-03-15", "about_person": True},
    ]
    with open(os.path.join(persona_dir, "media-urls.json"), "w") as f:
        json.dump(media_urls, f, indent=2)

    print("Generated: Amara Okafor (Tech Founder, EB-1A)")


if __name__ == "__main__":
    generate_priya_sharma()
    generate_marco_chen()
    generate_amara_okafor()
    print("\nAll synthetic data generated successfully!")
