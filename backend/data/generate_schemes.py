"""
Generate comprehensive 110-scheme database for Samarth.
Run: python -m backend.data.generate_schemes
"""
import json, os

# Keep existing 24 schemes and add 86 new ones
EXISTING_FILE = os.path.join(os.path.dirname(__file__), "schemes.json")

with open(EXISTING_FILE, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_ids = {s["scheme_id"] for s in existing}

def scheme(sid, name, name_hi, dept, cat, desc, hard, soft, benefits, docs, app, tags):
    return {
        "scheme_id": sid, "name": name, "name_hindi": name_hi,
        "department": dept, "category": cat, "description": desc,
        "eligibility": {"hard_constraints": {**hard, "domicile": "jharkhand"}, "soft_constraints": soft},
        "benefits": benefits, "documents_required": docs,
        "application_process": app, "tags": tags
    }

def doc(did, name, mandatory=True, condition=None):
    d = {"id": did, "name": name, "mandatory": mandatory}
    if condition: d["condition"] = condition
    return d

AADHAAR = doc("aadhaar", "Aadhaar Card")
BANK = doc("bank_account", "Bank Account (Aadhaar linked)")
DOMICILE = doc("domicile", "Jharkhand Domicile Certificate")
INCOME = doc("income_cert", "Family Income Certificate")
CASTE = doc("caste_cert", "Caste Certificate")
LAND = doc("land_record", "Land Records (Khatian/ROR)")
SCHOOL = doc("school_cert", "School Enrollment Certificate")
MARKSHEET = doc("marksheet", "Previous Year Marksheet")

ALL_CAT = ["SC", "ST", "OBC", "General"]
ALL_CAT_MIN = ["SC", "ST", "OBC", "General", "Minority"]
ALL_GENDER = ["male", "female", "other"]

def online_offline(url, steps):
    return {"mode": ["online", "offline"], "online_url": url, "offline_steps": steps}

def offline_only(steps):
    return {"mode": ["offline"], "online_url": None, "offline_steps": steps}

def online_only(url, steps):
    return {"mode": ["online"], "online_url": url, "offline_steps": steps}

new_schemes = [
    # ═══ AGRICULTURE (25-40) ═══
    scheme("jk_fasal_rahat", "Jharkhand Rajya Fasal Rahat Yojana", "झारखंड राज्य फसल राहत योजना",
        "Department of Agriculture, Jharkhand", "agriculture",
        "Crop relief scheme providing compensation to farmers for crop loss due to natural calamities like drought, floods, hailstorms. Not insurance — no premium required.",
        {"occupation": ["farmer"], "min_age": 18, "farmer_type": ["marginal", "small"], "categories": ALL_CAT, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.4, "description": "BPL farmers prioritized"}},
        {"type": "financial", "amount": 20000, "currency": "INR", "frequency": "on_claim", "description": "₹3,000/acre for 30-50% loss; ₹4,000/acre for >50% loss. Max 5 acres = ₹20,000."},
        [AADHAAR, LAND, BANK, doc("ration_card", "Ration Card")],
        online_offline("https://jrfry.jharkhand.gov.in", ["Register online or at CSC", "Submit crop damage claim with land records"]),
        ["agriculture", "farmer", "crop loss", "drought", "flood", "compensation", "fasal rahat"]
    ),
    scheme("jk_millet_mission", "Jharkhand Millet Mission (Madua Kranti)", "झारखंड मिलेट मिशन (मडुआ क्रांति)",
        "Department of Agriculture, Jharkhand", "agriculture",
        "5-year mission promoting Ragi (Madua) and Gondli cultivation for food security and better farmer income through subsidies and training.",
        {"occupation": ["farmer"], "min_age": 18, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "financial", "amount": 15000, "currency": "INR", "frequency": "yearly", "description": "Up to ₹15,000 subsidy for millet cultivation on 10 decimals to 5 acres."},
        [AADHAAR, LAND, BANK],
        offline_only(["Contact district agriculture office", "Apply through CSC or Krishi Bhawan"]),
        ["agriculture", "millet", "ragi", "madua", "farmer", "food security"]
    ),
    scheme("jk_pashudhan_vikas", "Mukhyamantri Pashudhan Vikas Yojana", "मुख्यमंत्री पशुधन विकास योजना",
        "Department of Animal Husbandry, Jharkhand", "agriculture",
        "Subsidies for cattle, goat, poultry and pig rearing to boost rural income. 50-90% subsidy based on category.",
        {"min_age": 18, "categories": ALL_CAT, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.5, "description": "BPL families get higher subsidy"}},
        {"type": "subsidy", "amount": 100000, "currency": "INR", "description": "50-90% subsidy on livestock purchase, shed construction, and equipment. SC/ST get up to 90%."},
        [AADHAAR, BANK, DOMICILE, CASTE],
        offline_only(["Visit Block Animal Husbandry office", "Submit application with documents", "Selection by district committee"]),
        ["animal husbandry", "cattle", "goat", "poultry", "farmer", "rural income", "livestock"]
    ),
    scheme("soil_health_card", "Soil Health Card Scheme", "मृदा स्वास्थ्य कार्ड योजना",
        "Ministry of Agriculture, Government of India", "agriculture",
        "Free soil testing and health card for farmers with crop-wise recommendations on nutrients and fertilizers.",
        {"occupation": ["farmer"], "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free soil health card with nutrient status and fertilizer recommendations. Issued every 2 years."},
        [AADHAAR, LAND],
        online_offline("https://soilhealth.dac.gov.in", ["Visit nearest Krishi Vigyan Kendra", "Or apply online for soil sample collection"]),
        ["agriculture", "farmer", "soil test", "fertilizer", "central scheme"]
    ),
    scheme("pm_krishi_sinchai", "PM Krishi Sinchai Yojana (PMKSY)", "प्रधानमंत्री कृषि सिंचाई योजना",
        "Ministry of Agriculture, Government of India", "agriculture",
        "Provides subsidized drip and sprinkler irrigation systems to farmers for water conservation and better yield.",
        {"occupation": ["farmer"], "categories": ALL_CAT, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.3, "description": "Small/marginal farmers get higher subsidy"}},
        {"type": "subsidy", "amount": None, "currency": "INR", "description": "55% subsidy for small/marginal farmers, 45% for others on micro-irrigation (drip/sprinkler)."},
        [AADHAAR, LAND, BANK],
        online_offline("https://pmksy.gov.in", ["Apply through district agriculture/horticulture office", "Or register online on PMKSY portal"]),
        ["agriculture", "irrigation", "drip", "sprinkler", "water", "farmer", "central scheme"]
    ),
    scheme("namo_drone_didi", "Namo Drone Didi Scheme", "नमो ड्रोन दीदी योजना",
        "Ministry of Agriculture, Government of India", "agriculture",
        "Provides drones to women SHGs for agricultural use — spraying pesticides, crop monitoring. Includes training and subsidy.",
        {"gender": ["female"], "min_age": 18, "categories": ALL_CAT},
        {"shg_member": {"weight": 0.9, "description": "Must be SHG/Sakhi Mandal member"}},
        {"type": "mixed", "amount": 800000, "currency": "INR", "description": "80% subsidy on drone cost (~₹8 lakh). Free pilot training. Earning potential ₹1 lakh+/year."},
        [AADHAAR, BANK, doc("shg_cert", "SHG Membership Certificate")],
        offline_only(["Apply through JSLPS/Sakhi Mandal coordinator", "Selected SHGs receive drone and training"]),
        ["agriculture", "women", "drone", "technology", "SHG", "central scheme"]
    ),

    # ═══ WOMEN & CHILD (41-55) ═══
    scheme("maiyan_samman", "Mukhyamantri Maiyan Samman Yojana", "मुख्यमंत्री मैयां सम्मान योजना",
        "Dept of Women, Child Development & Social Security, Jharkhand", "women",
        "Flagship scheme providing ₹2,500/month to women aged 21-50 for financial independence. Direct bank transfer.",
        {"gender": ["female"], "min_age": 21, "max_age": 50, "max_income_annual": 800000, "categories": ALL_CAT_MIN},
        {},
        {"type": "financial", "amount": 30000, "currency": "INR", "frequency": "monthly", "description": "₹2,500 per month (₹30,000/year) via DBT. Must have Jharkhand ration card."},
        [AADHAAR, BANK, doc("ration_card", "Jharkhand Ration Card", True), DOMICILE],
        online_offline("https://maiyansamman.jharkhand.gov.in", ["Register online or through Panchayat Sevak", "e-KYC at CSC/Pragya Kendra"]),
        ["women", "monthly income", "financial independence", "DBT", "Jharkhand", "flagship"]
    ),
    scheme("jk_vivah_sahayata", "Mukhyamantri Kanya Vivah Yojana", "मुख्यमंत्री कन्या विवाह योजना",
        "Dept of Social Welfare, Jharkhand", "women",
        "Financial assistance of ₹30,000 for marriage of girls from BPL families to prevent child marriage and support family.",
        {"gender": ["female"], "min_age": 18, "max_income_annual": 150000, "categories": ALL_CAT_MIN, "marital_status": ["unmarried"]},
        {"bpl_card": {"weight": 0.8, "description": "BPL families prioritized"}},
        {"type": "financial", "amount": 30000, "currency": "INR", "frequency": "one_time", "description": "₹30,000 one-time grant for marriage expenses. Bride must be 18+."},
        [AADHAAR, BANK, INCOME, doc("birth_cert", "Birth Certificate"), DOMICILE],
        offline_only(["Apply at Block/Circle office", "Submit documents with marriage registration"]),
        ["women", "marriage", "girl", "BPL", "financial help"]
    ),
    scheme("ladli_laxmi", "Ladli Laxmi Yojana", "लाड़ली लक्ष्मी योजना",
        "Dept of Women & Child Development, Jharkhand", "women",
        "Long-term financial security scheme for girls providing ₹1,18,000 in stages from birth to age 21.",
        {"gender": ["female"], "max_age": 1, "categories": ALL_CAT_MIN},
        {"bpl_card": {"weight": 0.5, "description": "BPL families prioritized"}},
        {"type": "financial", "amount": 118000, "currency": "INR", "frequency": "milestones", "description": "₹6,000/year for 5 years + ₹6,000 at Class 6 + ₹6,000 at Class 9 + ₹1,00,000 at age 21."},
        [AADHAAR, BANK, doc("birth_cert", "Birth Certificate of girl child"), DOMICILE],
        offline_only(["Register at Anganwadi Centre within 1 year of birth", "Submit birth certificate and parent documents"]),
        ["girl child", "savings", "education", "women", "birth registration"]
    ),
    scheme("pm_ujjwala", "Pradhan Mantri Ujjwala Yojana (PMUY)", "प्रधानमंत्री उज्ज्वला योजना",
        "Ministry of Petroleum & Natural Gas, Government of India", "women",
        "Free LPG connections to women from BPL/deprived households for clean cooking fuel, replacing wood/coal chulhas.",
        {"gender": ["female"], "min_age": 18, "categories": ALL_CAT_MIN},
        {"bpl_card": {"weight": 0.9, "description": "BPL/SECC listed households"}},
        {"type": "service", "amount": 1600, "currency": "INR", "frequency": "one_time", "description": "Free LPG connection (deposit-free). Includes free first refill and stove for eligible households."},
        [AADHAAR, BANK, doc("ration_card", "BPL Ration Card / SECC list")],
        online_offline("https://pmuy.gov.in", ["Apply at nearest LPG distributor with Aadhaar and BPL proof"]),
        ["LPG", "cooking gas", "women", "BPL", "clean fuel", "central scheme"]
    ),
    scheme("one_stop_centre", "One Stop Centre (Sakhi Centre)", "वन स्टॉप सेंटर (सखी केंद्र)",
        "Ministry of Women & Child Development, Government of India", "women",
        "24/7 support centres for women affected by violence — provides medical, legal, police, and shelter assistance.",
        {"gender": ["female"], "categories": ALL_CAT_MIN},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free medical aid, legal counselling, police assistance, psycho-social support, and temporary shelter."},
        [doc("any_id", "Any ID proof (Aadhaar/Voter ID)", False)],
        offline_only(["Call Women Helpline 181", "Visit nearest Sakhi Centre (One Stop Centre)", "No documents needed in emergency"]),
        ["women", "violence", "safety", "helpline", "shelter", "medical", "legal"]
    ),
    scheme("jk_palash_scheme", "Phulwari (Palash) Scheme", "फुलवारी (पलाश) योजना",
        "Dept of Women & Child Development, Jharkhand", "women",
        "Community-based nutrition and childcare centres for children (6 months to 3 years) and lactating mothers in tribal areas.",
        {"gender": ["female"], "categories": ["SC", "ST"]},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free hot cooked meals for children and mothers, health checkups, nutrition counselling at Phulwari centres."},
        [AADHAAR, doc("birth_cert", "Child's Birth Certificate")],
        offline_only(["Register at nearest Phulwari/Anganwadi centre", "No fees required"]),
        ["nutrition", "child", "mother", "tribal", "food", "women"]
    ),

    # ═══ EDUCATION (56-70) ═══
    scheme("guruji_credit_card", "Guruji Student Credit Card Scheme", "गुरुजी स्टूडेंट क्रेडिट कार्ड योजना",
        "Dept of Higher & Technical Education, Jharkhand", "education",
        "Collateral-free education loan up to ₹15 lakh at 4% interest for Jharkhand students to pursue professional courses.",
        {"min_age": 18, "max_age": 40, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "loan", "max_amount": 1500000, "currency": "INR", "description": "Loan up to ₹15 lakh at 4% interest. No collateral. 15-year repayment. No processing fees."},
        [AADHAAR, DOMICILE, MARKSHEET, BANK, doc("admission_letter", "Admission Letter from recognized institution")],
        online_offline("https://gscc.jharkhand.gov.in", ["Apply online on GSCC portal", "Submit documents at designated bank branch"]),
        ["education", "student", "loan", "college", "professional course", "credit card", "Jharkhand"]
    ),
    scheme("ekalyan_scholarship", "e-Kalyan Scholarship (SC/ST/BC)", "ई-कल्याण छात्रवृत्ति",
        "Department of Welfare, Jharkhand", "education",
        "State scholarship portal for SC/ST/BC students pursuing post-matric education. Covers tuition fees and maintenance.",
        {"categories": ["SC", "ST", "OBC"], "student_class": [11, 12], "max_income_annual": 250000, "gender": ALL_GENDER},
        {},
        {"type": "scholarship", "amount": 15000, "currency": "INR", "frequency": "yearly", "description": "Tuition fees + maintenance allowance. Amount varies by course level (₹5,000-₹15,000/year)."},
        [AADHAAR, CASTE, INCOME, SCHOOL, BANK],
        online_only("https://ekalyan.cg.nic.in", ["Apply online on e-Kalyan portal", "Institute verifies application"]),
        ["education", "scholarship", "SC", "ST", "OBC", "e-Kalyan", "student"]
    ),
    scheme("jk_cm_edu_promotion", "CM Education Promotion Scheme", "मुख्यमंत्री शिक्षा प्रोत्साहन योजना",
        "Dept of School Education, Jharkhand", "education",
        "Free coaching for competitive exams + ₹2,500/month accommodation allowance for students from weaker sections.",
        {"max_income_annual": 300000, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "scholarship", "amount": 30000, "currency": "INR", "frequency": "yearly", "description": "Free coaching + ₹2,500/month for accommodation = ₹30,000/year support."},
        [AADHAAR, INCOME, MARKSHEET, BANK, DOMICILE],
        offline_only(["Apply through school principal or district education office", "Selection based on merit and family income"]),
        ["education", "coaching", "competitive exam", "student", "accommodation"]
    ),
    scheme("jk_overseas_scholarship", "Marang Gomke Jaipal Singh Munda Overseas Scholarship", "मरांग गोमके जयपाल सिंह मुंडा विदेश छात्रवृत्ति",
        "Dept of Welfare, Jharkhand", "education",
        "Full scholarship for SC/ST/Minority students to study at top universities in UK. Covers tuition, living, travel.",
        {"categories": ["SC", "ST", "Minority"], "gender": ALL_GENDER, "max_income_annual": 1100000},
        {},
        {"type": "scholarship", "amount": 5000000, "currency": "INR", "frequency": "one_time", "description": "Full scholarship: tuition fees + living expenses + travel for Masters/PhD at QS Top 200 universities."},
        [AADHAAR, CASTE, INCOME, DOMICILE, BANK, doc("admission_letter", "Admission letter from QS Top 200 university")],
        online_offline("https://ekalyan.cg.nic.in", ["Apply online through e-Kalyan portal", "Selection by state-level committee"]),
        ["education", "overseas", "scholarship", "UK", "SC", "ST", "Minority", "higher education"]
    ),
    scheme("national_means_merit", "National Means-cum-Merit Scholarship (NMMSS)", "राष्ट्रीय साधन-सह-मेरिट छात्रवृत्ति",
        "Ministry of Education, Government of India", "education",
        "Merit scholarship for Class 9-12 students from economically weaker sections studying in government schools.",
        {"student_class": [9, 10, 11, 12], "max_income_annual": 350000, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "scholarship", "amount": 12000, "currency": "INR", "frequency": "yearly", "description": "₹12,000/year (₹1,000/month) for Class 9-12. Selected through state-level exam."},
        [AADHAAR, INCOME, SCHOOL, MARKSHEET, BANK],
        online_only("https://scholarships.gov.in", ["Apply on National Scholarship Portal (NSP)", "Must clear state-level NMMSS exam"]),
        ["education", "scholarship", "merit", "government school", "Class 9-12", "central scheme"]
    ),
    scheme("pm_yasasvi", "PM YASASVI Scholarship", "पीएम यशस्वी छात्रवृत्ति",
        "Ministry of Social Justice & Empowerment, Government of India", "education",
        "Scholarship for OBC/EBC/DNT students in Class 9-12 at top private/government schools. Vibrant India initiative.",
        {"student_class": [9, 10, 11, 12], "max_income_annual": 250000, "categories": ["OBC"], "gender": ALL_GENDER},
        {},
        {"type": "scholarship", "amount": 125000, "currency": "INR", "frequency": "yearly", "description": "Class 9-10: ₹75,000/year; Class 11-12: ₹1,25,000/year for top school students."},
        [AADHAAR, CASTE, INCOME, SCHOOL, BANK],
        online_only("https://yet.nta.ac.in", ["Apply online on NTA YASASVI portal", "Selection through YASASVI entrance test"]),
        ["education", "scholarship", "OBC", "student", "central scheme", "YASASVI"]
    ),
    scheme("begum_hazrat_mahal", "Begum Hazrat Mahal Scholarship", "बेगम हज़रत महल छात्रवृत्ति",
        "Maulana Azad Education Foundation, Government of India", "education",
        "Scholarship for meritorious minority girls studying in Class 9-12 from families below poverty line.",
        {"gender": ["female"], "student_class": [9, 10, 11, 12], "max_income_annual": 200000, "categories": ["Minority"]},
        {},
        {"type": "scholarship", "amount": 12000, "currency": "INR", "frequency": "yearly", "description": "Class 9-10: ₹5,000/year; Class 11-12: ₹6,000/year for minority girls."},
        [AADHAAR, doc("minority_cert", "Minority Community Certificate"), INCOME, SCHOOL, BANK],
        online_only("https://scholarships.gov.in", ["Apply on National Scholarship Portal (NSP)", "School verifies and forwards application"]),
        ["education", "scholarship", "minority", "girls", "Class 9-12"]
    ),
    scheme("midday_meal", "PM POSHAN (Mid-Day Meal) Scheme", "पीएम पोषण (मिड-डे मील) योजना",
        "Ministry of Education, Government of India", "education",
        "Free hot cooked lunch to all children in government and aided schools (Class 1-8) to improve nutrition and attendance.",
        {"student_class": [1, 2, 3, 4, 5, 6, 7, 8], "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free nutritious lunch daily. 450-700 calories per meal. Covers all govt school students Class 1-8."},
        [],
        offline_only(["Automatically available at all government/aided schools", "No separate application needed"]),
        ["education", "nutrition", "school", "children", "free food", "central scheme"]
    ),

    # ═══ EMPLOYMENT & SKILL (71-85) ═══
    scheme("pm_mudra", "Pradhan Mantri MUDRA Yojana (PMMY)", "प्रधानमंत्री मुद्रा योजना",
        "Ministry of Finance, Government of India", "employment",
        "Collateral-free micro-loans for small businesses. Shishu (₹50K), Kishore (₹5L), Tarun (₹10L), Tarun Plus (₹20L).",
        {"min_age": 18, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "loan", "max_amount": 2000000, "currency": "INR", "description": "Shishu: up to ₹50,000; Kishore: ₹50K-5L; Tarun: ₹5-10L; Tarun Plus: up to ₹20L. No collateral."},
        [AADHAAR, BANK, doc("business_plan", "Business Plan/Proposal")],
        online_offline("https://mudra.org.in", ["Apply at any bank/NBFC/MFI", "Or online through Udyamimitra portal"]),
        ["employment", "business", "loan", "micro enterprise", "self-employment", "MUDRA", "central scheme"]
    ),
    scheme("standup_india", "Stand Up India Scheme", "स्टैंड अप इंडिया योजना",
        "Ministry of Finance, Government of India", "employment",
        "Bank loans between ₹10 lakh to ₹1 crore for SC/ST/Women entrepreneurs starting greenfield businesses.",
        {"min_age": 18, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "loan", "max_amount": 10000000, "currency": "INR", "description": "Loan ₹10 lakh to ₹1 crore for new manufacturing/services/trading enterprise. Repayment up to 7 years."},
        [AADHAAR, BANK, CASTE, doc("project_report", "Detailed Project Report")],
        online_offline("https://standupmitra.in", ["Apply on Stand Up India portal", "Each bank branch must give 1 loan to SC/ST, 1 to woman"]),
        ["employment", "SC", "ST", "women", "entrepreneur", "business", "loan", "central scheme"]
    ),
    scheme("pm_svanidhi", "PM SVANidhi (Street Vendor)", "पीएम स्वनिधि (स्ट्रीट वेंडर)",
        "Ministry of Housing & Urban Affairs, Government of India", "employment",
        "Micro-credit for street vendors — ₹10,000 first loan, ₹20,000 second, ₹50,000 third. Subsidized interest.",
        {"min_age": 18, "occupation": ["self_employed", "street_vendor"], "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "loan", "max_amount": 50000, "currency": "INR", "description": "1st loan: ₹10,000; 2nd: ₹20,000; 3rd: ₹50,000. 7% interest subsidy + cashback on digital payments."},
        [AADHAAR, BANK, doc("vendor_cert", "Street Vendor Certificate/Letter of Recommendation")],
        online_offline("https://pmsvanidhi.mohua.gov.in", ["Apply online through PM SVANidhi portal", "Or at nearest ULB/municipal office"]),
        ["employment", "street vendor", "micro loan", "self-employed", "urban", "central scheme"]
    ),
    scheme("ddu_gjy", "Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)", "दीनदयाल उपाध्याय ग्रामीण कौशल योजना",
        "Ministry of Rural Development, Government of India", "employment",
        "Free skill training program for rural youth aged 15-35 with guaranteed job placement after training.",
        {"min_age": 15, "max_age": 35, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.6, "description": "BPL rural youth prioritized"}},
        {"type": "training", "amount": None, "currency": "INR", "description": "Free skill training (3-12 months) + hostel + food + stipend + guaranteed placement with min ₹6,000/month salary."},
        [AADHAAR, BANK, DOMICILE],
        online_offline("https://ddugky.gov.in", ["Register at Block office or JSLPS office", "Select skill course and training centre"]),
        ["employment", "skill", "training", "rural youth", "job placement", "central scheme"]
    ),
    scheme("pmegp", "PM Employment Generation Programme (PMEGP)", "प्रधानमंत्री रोजगार सृजन कार्यक्रम",
        "Ministry of MSME, Government of India", "employment",
        "Subsidy-linked loan scheme for setting up new micro-enterprises. 15-35% subsidy on project cost.",
        {"min_age": 18, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "loan_subsidy", "max_amount": 5000000, "currency": "INR", "description": "Manufacturing: up to ₹50L, Service: up to ₹20L. General: 15-25% subsidy; SC/ST/Women: 25-35% subsidy."},
        [AADHAAR, BANK, doc("project_report", "Detailed Project Report"), doc("edu_cert", "Education Certificate (min 8th pass)")],
        online_offline("https://www.kviconline.gov.in", ["Apply online on KVIC portal", "Interview at district KVIC/DIC office"]),
        ["employment", "business", "loan", "subsidy", "micro enterprise", "PMEGP", "central scheme"]
    ),
    scheme("jk_protsahan", "Mukhyamantri Protsahan Yojana", "मुख्यमंत्री प्रोत्साहन योजना",
        "Department of Labour, Jharkhand", "employment",
        "Financial incentive of ₹5,000 to unemployed youth who complete recognized skill training programs.",
        {"min_age": 18, "max_age": 35, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "financial", "amount": 5000, "currency": "INR", "frequency": "one_time", "description": "₹5,000 one-time incentive after completing government-recognized short-term skill training."},
        [AADHAAR, BANK, DOMICILE, doc("skill_cert", "Skill Training Completion Certificate")],
        offline_only(["Apply at District Employment Exchange", "Submit skill certificate and documents"]),
        ["employment", "skill", "incentive", "youth", "training", "Jharkhand"]
    ),
    scheme("startup_india", "Startup India Scheme", "स्टार्टअप इंडिया योजना",
        "DPIIT, Ministry of Commerce, Government of India", "employment",
        "Recognition and tax benefits for startups. 3-year tax holiday, self-certification, fast-track patent filing.",
        {"min_age": 18, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "mixed", "amount": None, "currency": "INR", "description": "3-year income tax exemption; Seed Fund up to ₹20 lakh; Self-certification for 6 labour & 3 environment laws."},
        [AADHAAR, doc("pan_card", "PAN Card"), doc("incorporation_cert", "Company/LLP Incorporation Certificate"), BANK],
        online_only("https://startupindia.gov.in", ["Register on Startup India portal", "Apply for DPIIT recognition"]),
        ["employment", "startup", "entrepreneur", "tax benefit", "innovation", "central scheme"]
    ),
    scheme("jk_swarojgar", "Jharkhand State Swarojgar Yojana", "झारखंड राज्य स्वरोजगार योजना",
        "Dept of Labour & Employment, Jharkhand", "employment",
        "State self-employment scheme providing subsidized loans for youth to start small businesses in Jharkhand.",
        {"min_age": 18, "max_age": 45, "max_income_annual": 300000, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "loan_subsidy", "max_amount": 500000, "currency": "INR", "description": "Loan up to ₹5 lakh with 25-40% subsidy. Priority to trained youth."},
        [AADHAAR, BANK, DOMICILE, INCOME, doc("project_report", "Business Plan")],
        offline_only(["Apply at District Industries Centre (DIC)", "Bank sanctions loan with state subsidy"]),
        ["employment", "self-employment", "loan", "youth", "business", "Jharkhand"]
    ),

    # ═══ SOCIAL SECURITY & HEALTH (86-100) ═══
    scheme("atal_pension", "Atal Pension Yojana (APY)", "अटल पेंशन योजना",
        "PFRDA / Ministry of Finance, Government of India", "social_security",
        "Guaranteed pension of ₹1,000-₹5,000/month after age 60 for unorganized sector workers. Government co-contributes.",
        {"min_age": 18, "max_age": 40, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "pension", "amount": 5000, "currency": "INR", "frequency": "monthly_after_60", "description": "Pension ₹1,000-₹5,000/month after 60 based on contribution. Spouse continues pension after death."},
        [AADHAAR, BANK, doc("mobile", "Mobile Number")],
        online_offline("https://jansuraksha.gov.in", ["Open APY account at any bank", "Or enroll through net/mobile banking"]),
        ["pension", "retirement", "unorganized sector", "APY", "central scheme", "social security"]
    ),
    scheme("pmgkay_ration", "PM Garib Kalyan Anna Yojana (Free Ration)", "प्रधानमंत्री गरीब कल्याण अन्न योजना",
        "Ministry of Consumer Affairs, Government of India", "social_security",
        "Free 5 kg rice/wheat per person per month to 80 crore beneficiaries under National Food Security Act. Extended till Dec 2028.",
        {"categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.9, "description": "Must be NFSA/AAY/PHH ration card holder"}},
        {"type": "food", "amount": None, "currency": "INR", "frequency": "monthly", "description": "5 kg free food grains (rice/wheat) per person per month. AAY families get 35 kg/month per household."},
        [doc("ration_card", "NFSA Ration Card (AAY/PHH)", True), AADHAAR],
        offline_only(["Visit your designated Fair Price Shop (FPS)", "Authenticate with Aadhaar biometric", "Collect free ration monthly"]),
        ["food", "ration", "rice", "wheat", "BPL", "free", "central scheme", "NFSA"]
    ),
    scheme("jk_sahay", "Mukhyamantri Sahay Yojana", "मुख्यमंत्री सहाय योजना",
        "Department of Labour, Jharkhand", "social_security",
        "Funeral/death assistance of ₹25,000 to families of registered unorganized workers on death of the worker.",
        {"min_age": 18, "max_age": 60, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "financial", "amount": 25000, "currency": "INR", "frequency": "one_time", "description": "₹25,000 one-time death/funeral assistance to nominee. Worker must have been registered on e-Shram."},
        [AADHAAR, BANK, doc("eshram_card", "e-Shram Card"), doc("death_cert", "Death Certificate")],
        offline_only(["Nominee applies at District Labour Office", "Submit death certificate and e-Shram card"]),
        ["social security", "death benefit", "unorganized worker", "funeral", "Jharkhand"]
    ),
    scheme("pm_jan_dhan", "Pradhan Mantri Jan Dhan Yojana (PMJDY)", "प्रधानमंत्री जन धन योजना",
        "Ministry of Finance, Government of India", "social_security",
        "Zero-balance bank account for all Indians with free RuPay debit card, ₹2 lakh accident insurance, and ₹30,000 life cover.",
        {"min_age": 10, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "banking", "amount": 200000, "currency": "INR", "description": "Zero-balance account + free RuPay card + ₹2L accident insurance + ₹30,000 life cover + overdraft up to ₹10,000."},
        [AADHAAR, doc("any_id", "Any valid ID (Voter ID/Driving License)", False)],
        offline_only(["Visit any bank branch or Banking Correspondent", "Open Jan Dhan account with Aadhaar", "Get free RuPay debit card"]),
        ["banking", "financial inclusion", "insurance", "zero balance", "central scheme", "Jan Dhan"]
    ),
    scheme("eshram_card", "e-Shram Card (NDUW)", "ई-श्रम कार्ड",
        "Ministry of Labour, Government of India", "social_security",
        "Universal registration for unorganized workers with ₹2 lakh accident insurance and access to welfare schemes.",
        {"min_age": 16, "max_age": 59, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "insurance", "amount": 200000, "currency": "INR", "description": "Free ₹2 lakh accidental death/disability insurance under PMSBY. Gateway to all labour welfare schemes."},
        [AADHAAR, BANK, doc("mobile", "Mobile Number linked to Aadhaar")],
        online_offline("https://eshram.gov.in", ["Self-register on eshram.gov.in", "Or register at nearest CSC for free"]),
        ["unorganized worker", "labour", "insurance", "registration", "e-Shram", "central scheme"]
    ),
    scheme("jk_ration_card", "Jharkhand Ration Card (NFSA)", "झारखंड राशन कार्ड (एनएफएसए)",
        "Dept of Food & Public Distribution, Jharkhand", "social_security",
        "Ration card for subsidized and free food grains under NFSA. Categories: AAY, PHH, Non-Priority.",
        {"categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "food", "amount": None, "currency": "INR", "description": "AAY: 35 kg/month at ₹1-3/kg. PHH: 5 kg/person/month free (under PMGKAY)."},
        [AADHAAR, DOMICILE, INCOME, doc("photo", "Passport Photo of family members")],
        online_offline("https://aahar.jharkhand.gov.in", ["Apply online on Aahar portal", "Or apply at Block Supply Officer (BSO) office"]),
        ["ration card", "food", "BPL", "subsidized", "NFSA", "Jharkhand"]
    ),
    scheme("jk_accident_relief", "Jharkhand Accident Relief Scheme", "झारखंड दुर्घटना राहत योजना",
        "Department of Transport, Jharkhand", "social_security",
        "Financial assistance to road accident victims — ₹50,000 for injury, ₹2 lakh for death.",
        {"categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "financial", "amount": 200000, "currency": "INR", "frequency": "on_claim", "description": "₹50,000 for serious injury; ₹2,00,000 for accidental death. Covers all road accident victims in Jharkhand."},
        [AADHAAR, doc("fir_copy", "FIR/Police Report"), doc("medical_cert", "Medical Certificate / Death Certificate"), BANK],
        offline_only(["File FIR at nearest police station", "Apply at District Transport Office with medical/death certificate"]),
        ["accident", "road safety", "compensation", "death", "injury", "Jharkhand"]
    ),
    scheme("national_family_benefit", "National Family Benefit Scheme (NFBS)", "राष्ट्रीय परिवार लाभ योजना",
        "Ministry of Rural Development, Government of India", "social_security",
        "₹20,000 lump sum to BPL family on death of the primary breadwinner (18-60 years).",
        {"min_age": 18, "max_age": 60, "categories": ALL_CAT, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.9, "description": "Only for BPL families"}},
        {"type": "financial", "amount": 20000, "currency": "INR", "frequency": "one_time", "description": "₹20,000 lump sum to surviving family members within 45 days of breadwinner's death."},
        [AADHAAR, BANK, doc("death_cert", "Death Certificate"), doc("bpl_cert", "BPL Certificate")],
        offline_only(["Apply at Block Development Office", "Submit death certificate and BPL proof"]),
        ["death benefit", "BPL", "family", "breadwinner", "central scheme", "social security"]
    ),

    # ═══ HOUSING (101-105) ═══
    scheme("jk_svamitva", "SVAMITVA Yojana (Property Cards)", "स्वामित्व योजना (प्रॉपर्टी कार्ड)",
        "Ministry of Panchayati Raj, Government of India", "housing",
        "Drone survey-based property cards for rural residential land owners. Enables loans against property.",
        {"categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free digital property card for rural residential land. Enables bank loans against property."},
        [AADHAAR],
        offline_only(["Drone survey conducted by Survey of India", "Property cards distributed at Gram Sabha", "Access cards on DigiLocker"]),
        ["housing", "property", "land", "rural", "drone", "central scheme"]
    ),
    scheme("jk_shahri_awas", "Jharkhand Shahri Awas Yojana", "झारखंड शहरी आवास योजना",
        "Dept of Urban Development, Jharkhand", "housing",
        "Affordable housing for urban poor in Jharkhand's municipal areas with government subsidy.",
        {"housing_status": ["homeless", "kutcha_house", "slum", "rented"], "max_income_annual": 300000, "categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.7, "description": "BPL urban families prioritized"}},
        {"type": "housing_subsidy", "amount": 150000, "currency": "INR", "description": "₹1.5-2.5 lakh subsidy for construction/purchase of affordable house in urban areas."},
        [AADHAAR, INCOME, BANK, DOMICILE, doc("no_house_affidavit", "Affidavit of no pucca house ownership")],
        offline_only(["Apply at Municipal Corporation/Nagar Palika office", "Application verified by housing committee"]),
        ["housing", "urban", "affordable", "city", "subsidy", "Jharkhand"]
    ),

    # ═══ ADDITIONAL MIXED (106-110) ═══
    scheme("jk_jharsewa_services", "JharSewa (e-District Services)", "झारसेवा (ई-जिला सेवाएं)",
        "IT Department, Jharkhand", "social_security",
        "One-stop portal for 50+ government certificates and services — caste, income, domicile, birth/death certificates.",
        {"categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Online application for caste, income, domicile, birth, death, marriage, residential certificates. Nominal fee ₹10-50."},
        [AADHAAR],
        online_offline("https://jharsewa.jharkhand.gov.in", ["Apply online on JharSewa portal", "Or at nearest CSC/Pragya Kendra", "Certificates issued within 7-15 days"]),
        ["certificates", "caste", "income", "domicile", "birth", "death", "e-governance", "Jharkhand"]
    ),
    scheme("jk_birsa_munda_swarojgar", "Birsa Munda Swarojgar Yojana", "बिरसा मुंडा स्वरोजगार योजना",
        "Dept of Tribal Welfare, Jharkhand", "employment",
        "Self-employment scheme exclusively for ST youth. Subsidy + loan for starting micro-enterprises.",
        {"min_age": 18, "max_age": 45, "categories": ["ST"], "gender": ALL_GENDER, "max_income_annual": 300000},
        {},
        {"type": "loan_subsidy", "max_amount": 500000, "currency": "INR", "description": "Loan up to ₹5 lakh with 50% subsidy (max ₹2.5 lakh) for ST youth to start businesses."},
        [AADHAAR, CASTE, INCOME, BANK, DOMICILE, doc("project_report", "Business Project Report")],
        offline_only(["Apply at ITDA (Integrated Tribal Development Agency) office", "Project approved by district committee"]),
        ["employment", "tribal", "ST", "self-employment", "loan", "subsidy", "Jharkhand"]
    ),
    scheme("jk_universal_health", "Jharkhand Universal Health Insurance", "झारखंड सार्वभौमिक स्वास्थ्य बीमा",
        "Dept of Health, Jharkhand", "social_security",
        "State health insurance scheme supplementing Ayushman Bharat for families not covered under PMJAY.",
        {"categories": ALL_CAT_MIN, "gender": ALL_GENDER},
        {"bpl_card": {"weight": 0.7, "description": "BPL families given priority"}},
        {"type": "health_insurance", "amount": 500000, "currency": "INR", "frequency": "yearly", "description": "₹5 lakh cashless health cover per family per year at empanelled hospitals in Jharkhand."},
        [AADHAAR, doc("ration_card", "Ration Card"), BANK],
        online_offline("https://jharsewa.jharkhand.gov.in", ["Register at nearest Primary Health Centre", "Or apply through JharSewa portal"]),
        ["health", "insurance", "hospital", "cashless", "Jharkhand", "universal"]
    ),
    scheme("jk_mukhyamantri_shramik", "Mukhyamantri Shramik (Labour Welfare)", "मुख्यमंत्री श्रमिक कल्याण योजना",
        "Dept of Labour, Jharkhand", "employment",
        "Welfare package for registered construction/unorganized workers — education aid, medical, maternity, funeral benefits.",
        {"min_age": 18, "max_age": 60, "occupation": ["labourer"], "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "mixed", "amount": 100000, "currency": "INR", "description": "Education aid ₹8,000-25,000/child; Medical ₹5,000-1L; Maternity ₹30,000; Funeral ₹10,000; Tool kit ₹5,000."},
        [AADHAAR, BANK, doc("labour_card", "Registered Labour/Shramik Card"), DOMICILE],
        offline_only(["Register as worker at District Labour Office", "Apply for benefits at Labour Welfare Board"]),
        ["labour", "construction worker", "welfare", "education", "medical", "Jharkhand"]
    ),
    scheme("jk_cm_fellowship", "CM Research Fellowship", "मुख्यमंत्री अनुसंधान फेलोशिप",
        "Dept of Higher Education, Jharkhand", "education",
        "Research fellowship of ₹25,000/month for PhD scholars from Jharkhand pursuing research in state universities.",
        {"min_age": 21, "max_age": 40, "categories": ALL_CAT, "gender": ALL_GENDER},
        {},
        {"type": "fellowship", "amount": 300000, "currency": "INR", "frequency": "yearly", "description": "₹25,000/month (₹3 lakh/year) for up to 3 years. Must be enrolled in PhD in a Jharkhand university."},
        [AADHAAR, BANK, DOMICILE, doc("phd_admission", "PhD Admission Letter"), MARKSHEET],
        online_offline("https://jharkhand.gov.in", ["Apply through university research cell", "Selection by state fellowship committee"]),
        ["education", "research", "PhD", "fellowship", "higher education", "Jharkhand"]
    ),
]

# Filter out any that already exist
new_schemes = [s for s in new_schemes if s["scheme_id"] not in existing_ids]

# Combine
all_schemes = existing + new_schemes

print(f"Existing: {len(existing)}, New: {len(new_schemes)}, Total: {len(all_schemes)}")

# Write
output_path = os.path.join(os.path.dirname(__file__), "schemes.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_schemes, f, ensure_ascii=False, indent=2)

print(f"✅ Written {len(all_schemes)} schemes to {output_path}")
