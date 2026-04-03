"""
Batch 2: Additional 41 schemes to reach 110 total.
Run after generate_schemes.py
"""
import json, os

SCHEMES_FILE = os.path.join(os.path.dirname(__file__), "schemes.json")

with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
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

def doc(did, name, mandatory=True):
    return {"id": did, "name": name, "mandatory": mandatory}

A = doc("aadhaar", "Aadhaar Card")
B = doc("bank_account", "Bank Account (Aadhaar linked)")
D = doc("domicile", "Jharkhand Domicile Certificate")
I = doc("income_cert", "Family Income Certificate")
C = doc("caste_cert", "Caste Certificate")
L = doc("land_record", "Land Records (Khatian/ROR)")

AC = ["SC", "ST", "OBC", "General"]
ACM = ["SC", "ST", "OBC", "General", "Minority"]
AG = ["male", "female", "other"]

def oo(url, steps): return {"mode": ["online", "offline"], "online_url": url, "offline_steps": steps}
def off(steps): return {"mode": ["offline"], "online_url": None, "offline_steps": steps}
def on(url, steps): return {"mode": ["online"], "online_url": url, "offline_steps": steps}

batch2 = [
    scheme("jk_ignoaps", "Indira Gandhi National Old Age Pension (IGNOAPS)", "इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन",
        "Ministry of Rural Development, GoI", "social_security",
        "Central pension for BPL elderly: ₹200/month (60-79 years), ₹500/month (80+ years). Jharkhand tops up via Sarvajan.",
        {"min_age": {"general_male": 60, "female": 60}, "categories": AC, "gender": AG},
        {"bpl_card": {"weight": 0.9, "description": "BPL only"}},
        {"type": "financial", "amount": 500, "currency": "INR", "frequency": "monthly", "description": "₹200/month (60-79 yrs); ₹500/month (80+ yrs). State adds top-up."},
        [A, B, D, doc("age_proof", "Age Proof (Birth/School Certificate)")],
        oo("https://jharsewa.jharkhand.gov.in", ["Apply at Block/Circle office"]),
        ["pension", "elderly", "BPL", "old age", "central scheme"]
    ),
    scheme("igndps", "Indira Gandhi National Disability Pension (IGNDPS)", "इंदिरा गांधी राष्ट्रीय दिव्यांग पेंशन",
        "Ministry of Rural Development, GoI", "social_security",
        "Central pension for BPL persons with severe disability (80%+): ₹300/month (18-79), ₹500/month (80+).",
        {"min_age": 18, "categories": AC, "gender": AG, "special_conditions": ["disabled"]},
        {"bpl_card": {"weight": 0.9, "description": "BPL only"}},
        {"type": "financial", "amount": 500, "currency": "INR", "frequency": "monthly", "description": "₹300/month (18-79 yrs, 80%+ disability); ₹500/month (80+ yrs)."},
        [A, B, D, doc("disability_cert", "Disability Certificate (80%+)")],
        oo("https://jharsewa.jharkhand.gov.in", ["Apply at Block/Circle office"]),
        ["pension", "disabled", "disability", "BPL", "central scheme"]
    ),
    scheme("ignwps", "Indira Gandhi National Widow Pension (IGNWPS)", "इंदिरा गांधी राष्ट्रीय विधवा पेंशन",
        "Ministry of Rural Development, GoI", "social_security",
        "Central pension for BPL widows aged 40-79: ₹300/month. 80+ years: ₹500/month.",
        {"gender": ["female"], "min_age": 40, "marital_status": ["widow"], "categories": AC},
        {"bpl_card": {"weight": 0.9, "description": "BPL only"}},
        {"type": "financial", "amount": 500, "currency": "INR", "frequency": "monthly", "description": "₹300/month (40-79 yrs); ₹500/month (80+ yrs) for BPL widows."},
        [A, B, D, doc("death_cert", "Husband's Death Certificate")],
        oo("https://jharsewa.jharkhand.gov.in", ["Apply at Block/Circle office"]),
        ["pension", "widow", "BPL", "women", "central scheme"]
    ),
    scheme("jk_cm_sukanya", "Mukhyamantri Sukanya Yojana", "मुख्यमंत्री सुकन्या योजना",
        "Dept of Social Welfare, Jharkhand", "women",
        "₹20,000 one-time incentive for unmarried girls reaching 18 years to promote education and prevent child marriage.",
        {"gender": ["female"], "min_age": 18, "max_age": 19, "marital_status": ["unmarried"], "categories": ACM},
        {},
        {"type": "financial", "amount": 20000, "currency": "INR", "frequency": "one_time", "description": "₹20,000 lump sum at age 18 for unmarried girls from BPL/SECC families."},
        [A, B, D, doc("birth_cert", "Birth Certificate")],
        off(["Apply through Anganwadi Sevika", "Verified by Block office"]),
        ["women", "girl", "unmarried", "18 years", "education", "Jharkhand"]
    ),
    scheme("jk_dial_112", "Dial 112 Emergency Service", "डायल 112 आपातकालीन सेवा",
        "Jharkhand Police / Home Department", "social_security",
        "Single emergency number for Police, Fire, and Ambulance services across Jharkhand. Free 24/7.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "24/7 unified emergency response: Police, Fire Brigade, Ambulance. Average response time: 15 minutes."},
        [],
        off(["Dial 112 from any phone", "GPS tracking enabled", "No documents needed"]),
        ["emergency", "police", "ambulance", "fire", "safety", "Jharkhand"]
    ),
    scheme("pm_awas_urban_2", "PM Awas Yojana Urban 2.0 (PMAY-U 2.0)", "पीएम आवास योजना शहरी 2.0",
        "Ministry of Housing & Urban Affairs, GoI", "housing",
        "Extended urban housing with interest subsidy for EWS/LIG. Targets 1 crore new urban houses by 2028.",
        {"housing_status": ["homeless", "kutcha_house", "slum", "rented"], "max_income_annual": 900000, "categories": ACM, "gender": AG},
        {"bpl_card": {"weight": 0.6, "description": "EWS/LIG priority"}},
        {"type": "housing_subsidy", "amount": 250000, "currency": "INR", "description": "Central assistance up to ₹2.5 lakh for EWS; interest subsidy on home loans for LIG/MIG."},
        [A, B, I, doc("no_house_cert", "Self-declaration of no pucca house")],
        oo("https://pmaymis.gov.in", ["Apply online or at municipal office"]),
        ["housing", "urban", "EWS", "LIG", "central scheme", "PMAY 2.0"]
    ),
    scheme("jk_aapki_yojana", "Aapki Yojana Aapki Sarkar (AYAS)", "आपकी योजना आपकी सरकार",
        "Chief Minister's Office, Jharkhand", "social_security",
        "Door-to-door governance camps bringing all government services directly to villages. Certificate issuance on spot.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "One-stop camp for Aadhaar enrollment, ration card, pension, caste/income certificates — all at village level."},
        [A],
        off(["Attend AYAS camp in your panchayat", "All services provided free", "No prior application needed"]),
        ["governance", "certificates", "village camp", "doorstep", "Jharkhand"]
    ),
    scheme("jk_johar", "JOHAR (Jharkhand Opportunities for Harnessing Rural Growth)", "जोहार योजना",
        "Dept of Rural Development, Jharkhand (World Bank aided)", "employment",
        "Livelihood enhancement project for SHG women, farmers, and rural entrepreneurs through skill training and market linkage.",
        {"categories": ACM, "gender": AG},
        {"bpl_card": {"weight": 0.5, "description": "BPL/vulnerable families"}},
        {"type": "mixed", "amount": 50000, "currency": "INR", "description": "SHG grants, farmer producer organization support, skill training, and market access. ₹50,000 per SHG."},
        [A, B],
        off(["Contact JSLPS block coordinator", "Join/form SHG through Sakhi Mandal"]),
        ["employment", "SHG", "rural", "livelihood", "women", "World Bank", "Jharkhand"]
    ),
    scheme("jk_sip", "Jharkhand Skill Improvement Programme", "झारखंड कौशल विकास कार्यक्रम",
        "Dept of Labour & Employment, Jharkhand", "employment",
        "Short-term skill training (2-6 months) in ITI trades for Jharkhand youth, integrated with placement support.",
        {"min_age": 15, "max_age": 35, "categories": AC, "gender": AG},
        {},
        {"type": "training", "amount": None, "currency": "INR", "description": "Free training in 40+ trades (electrician, plumber, welder, etc.) + stipend + placement assistance."},
        [A, B, D, doc("marksheet", "Class 8/10 Marksheet")],
        off(["Register at nearest ITI or skill centre", "Selection by district committee"]),
        ["employment", "skill", "training", "ITI", "youth", "Jharkhand"]
    ),
    scheme("pm_kusum", "PM KUSUM (Solar for Farmers)", "पीएम कुसुम (किसानों के लिए सौर ऊर्जा)",
        "Ministry of New & Renewable Energy, GoI", "agriculture",
        "Solar pump and grid-connected solar plant subsidies for farmers to replace diesel pumps and earn from solar energy.",
        {"occupation": ["farmer"], "categories": AC, "gender": AG},
        {},
        {"type": "subsidy", "amount": None, "currency": "INR", "description": "60% subsidy on solar pumps (2-10 HP). Farmers can sell surplus solar power to grid and earn."},
        [A, L, B],
        oo("https://pmkusum.mnre.gov.in", ["Apply through state JREDA portal", "Or at district agriculture office"]),
        ["agriculture", "solar", "pump", "renewable energy", "farmer", "central scheme"]
    ),
    scheme("jk_krishi_yantra", "Jharkhand Krishi Yantra Subsidy", "झारखंड कृषि यंत्र अनुदान",
        "Dept of Agriculture, Jharkhand", "agriculture",
        "Subsidy up to 80% on farm machinery (tractor, power tiller, thresher) for small/marginal farmers.",
        {"occupation": ["farmer"], "farmer_type": ["marginal", "small"], "categories": AC, "gender": AG},
        {},
        {"type": "subsidy", "amount": 500000, "currency": "INR", "description": "50-80% subsidy on farm machinery. SC/ST: 80%; General: 50%. Max ₹5 lakh subsidy."},
        [A, L, B, C],
        off(["Apply at Block Agriculture Office", "Select machinery from approved dealer list"]),
        ["agriculture", "machinery", "tractor", "subsidy", "farmer", "Jharkhand"]
    ),
    scheme("jk_matsya", "Jharkhand Matsya Vikas Yojana (Fisheries)", "झारखंड मत्स्य विकास योजना",
        "Dept of Fisheries, Jharkhand", "agriculture",
        "Subsidies for fish farming — pond construction, fish seed, feed, and equipment for rural fish farmers.",
        {"min_age": 18, "categories": AC, "gender": AG},
        {"bpl_card": {"weight": 0.5, "description": "BPL families prioritized"}},
        {"type": "subsidy", "amount": 200000, "currency": "INR", "description": "40-60% subsidy on pond construction, fish seed, aerators. SC/ST get higher subsidy."},
        [A, B, D, L],
        off(["Apply at District Fisheries Office", "Technical guidance provided free"]),
        ["fisheries", "fish", "pond", "rural", "subsidy", "Jharkhand"]
    ),
    scheme("pm_kisan_maandhan", "PM Kisan Maandhan Yojana", "प्रधानमंत्री किसान मानधन योजना",
        "Ministry of Agriculture, GoI", "agriculture",
        "Voluntary pension for small/marginal farmers: ₹3,000/month after 60. Equal contribution by government.",
        {"occupation": ["farmer"], "farmer_type": ["marginal", "small"], "min_age": 18, "max_age": 40, "categories": AC, "gender": AG},
        {},
        {"type": "pension", "amount": 3000, "currency": "INR", "frequency": "monthly_after_60", "description": "₹3,000/month pension after 60. Contribution: ₹55-200/month (age-based). Govt matches 50%."},
        [A, B, L],
        oo("https://maandhan.in", ["Register at nearest CSC", "Contribution auto-deducted from bank account"]),
        ["agriculture", "pension", "farmer", "retirement", "central scheme"]
    ),
    scheme("jk_birsa_health", "Birsa Seva Vahini (Free Ambulance)", "बिरसा सेवा वाहिनी (मुफ्त एम्बुलेंस)",
        "Dept of Health, Jharkhand", "social_security",
        "Free emergency ambulance service covering all blocks. Dial 102 for pregnancy/child transport, 108 for emergencies.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free 24/7 ambulance. 102: maternal/child transport. 108: emergency. GPS tracked. Avg response: 20 min."},
        [],
        off(["Dial 102 (maternal/child) or 108 (emergency)", "No ID required", "Service available in all 24 districts"]),
        ["health", "ambulance", "emergency", "maternal", "free transport", "Jharkhand"]
    ),
    scheme("jk_sahiya_incentive", "Sahiya (ASHA) Incentive Scheme", "सहिया (आशा) प्रोत्साहन योजना",
        "Dept of Health, Jharkhand", "social_security",
        "Monthly honorarium + performance incentives for Sahiya (ASHA) workers providing maternal/child healthcare at village level.",
        {"gender": ["female"], "min_age": 25, "max_age": 45, "categories": ACM},
        {},
        {"type": "financial", "amount": 36000, "currency": "INR", "frequency": "yearly", "description": "₹3,000/month honourarium + per-case incentives (ANC, delivery, immunization). Total ~₹5,000+/month."},
        [A, B, D, doc("asha_cert", "ASHA/Sahiya Training Certificate")],
        off(["Apply at Block PHC/CHC", "Complete ASHA training module", "Deployed by ANM/Medical Officer"]),
        ["health", "ASHA", "Sahiya", "women", "village health", "Jharkhand"]
    ),
    scheme("jk_nikshay_poshan", "Nikshay Poshan Yojana (TB Patients)", "निक्षय पोषण योजना (टीबी मरीज)",
        "Ministry of Health, GoI", "social_security",
        "₹500/month nutrition support for all TB patients during treatment to improve recovery.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "financial", "amount": 500, "currency": "INR", "frequency": "monthly", "description": "₹500/month via DBT during entire TB treatment (6-24 months). Also covers MDR-TB patients."},
        [A, B, doc("nikshay_id", "Nikshay Registration ID from DOTS centre")],
        off(["Register at nearest DOTS (TB treatment) centre", "Nikshay ID issued automatically", "₹500/month from registration"]),
        ["health", "TB", "tuberculosis", "nutrition", "central scheme"]
    ),
    scheme("jk_rashtriya_swasthya", "Rashtriya Swasthya Bima Yojana (RSBY)", "राष्ट्रीय स्वास्थ्य बीमा योजना",
        "Ministry of Labour, GoI", "social_security",
        "Health insurance for BPL families & unorganized workers: ₹30,000/year coverage for hospitalisation.",
        {"categories": AC, "gender": AG},
        {"bpl_card": {"weight": 0.9, "description": "BPL families only"}},
        {"type": "health_insurance", "amount": 30000, "currency": "INR", "frequency": "yearly", "description": "₹30,000/year family hospitalisation cover. Smart card based. Pre-existing diseases covered from day 1."},
        [A, B, doc("bpl_cert", "BPL Certificate/Ration Card")],
        off(["Enrollment camps at block level", "Smart card issued with biometrics"]),
        ["health", "insurance", "BPL", "hospitalisation", "central scheme"]
    ),
    scheme("jk_free_medicine", "Mukhyamantri Jan Aushadhi Yojana (Free Medicine)", "मुख्यमंत्री जन औषधि योजना",
        "Dept of Health, Jharkhand", "social_security",
        "Free essential medicines at government hospitals and Jan Aushadhi centres across Jharkhand.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "800+ free generic medicines at government hospitals. Jan Aushadhi stores sell at 50-90% discount."},
        [doc("prescription", "Doctor's Prescription", True)],
        off(["Visit any government hospital pharmacy", "Or nearest Jan Aushadhi Kendra", "Show OPD prescription"]),
        ["health", "medicine", "free", "generic", "hospital", "Jharkhand"]
    ),
    scheme("jk_minority_scholarship", "State Minority Scholarship", "राज्य अल्पसंख्यक छात्रवृत्ति",
        "Minority Welfare Dept, Jharkhand", "education",
        "Scholarship for meritorious minority students in Class 1-10 to support education expenses.",
        {"categories": ["Minority"], "student_class": [1,2,3,4,5,6,7,8,9,10], "max_income_annual": 200000, "gender": AG},
        {},
        {"type": "scholarship", "amount": 10000, "currency": "INR", "frequency": "yearly", "description": "₹1,000-₹10,000/year based on class level. Covers books, uniform, and tuition fees."},
        [A, doc("minority_cert","Minority Community Certificate"), I, B, doc("school_cert","School Certificate")],
        on("https://scholarships.gov.in", ["Apply on NSP portal", "School verifies application"]),
        ["education", "minority", "scholarship", "school", "student"]
    ),
    scheme("jk_sc_st_hostels", "SC/ST Free Hostel Scheme", "अनुसूचित जाति/जनजाति मुफ्त छात्रावास",
        "Dept of Welfare, Jharkhand", "education",
        "Free hostel accommodation with meals for SC/ST students studying in government schools and colleges.",
        {"categories": ["SC", "ST"], "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free hostel stay + 3 meals/day. Available at district-level Eklavya/Kasturba hostels."},
        [A, C, doc("school_cert", "School/College Admission Proof"), I],
        off(["Apply through school/college principal", "Allotment by District Welfare Officer"]),
        ["education", "hostel", "SC", "ST", "free accommodation", "Jharkhand"]
    ),
    scheme("jk_bicycle_scheme", "Free Bicycle for Students", "छात्र-छात्राओं को मुफ्त साइकिल",
        "Dept of School Education, Jharkhand", "education",
        "Free bicycle to Class 9 students of government schools to reduce dropouts and improve attendance.",
        {"student_class": [9], "categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": 3500, "currency": "INR", "description": "Free bicycle (worth ~₹3,500) to all Class 9 students in government/government-aided schools."},
        [A, doc("school_cert", "Class 9 Enrollment Certificate")],
        off(["Automatically distributed through schools", "No separate application needed"]),
        ["education", "bicycle", "Class 9", "government school", "dropout", "Jharkhand"]
    ),
    scheme("jk_uniform_scheme", "Free Uniform & Books Scheme", "मुफ्त यूनिफॉर्म और किताब योजना",
        "Dept of School Education, Jharkhand", "education",
        "Free school uniforms (2 sets) and textbooks for all students in government schools (Class 1-8).",
        {"student_class": [1,2,3,4,5,6,7,8], "categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "2 sets of uniforms + all NCERT/state textbooks free. Distributed at school level."},
        [],
        off(["Automatically provided at government schools", "No separate application"]),
        ["education", "uniform", "books", "free", "school", "Jharkhand"]
    ),
    scheme("jk_smart_ration", "Jharkhand Smart Ration Card (AePDS)", "झारखंड स्मार्ट राशन कार्ड (एईपीडीएस)",
        "Dept of Food & Public Distribution, Jharkhand", "social_security",
        "Aadhaar-enabled smart ration card system for portable PDS. Collect ration from any FPS in the state.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Aadhaar-authenticated ration collection from ANY fair price shop using biometrics. Portability across districts."},
        [A, doc("ration_card", "Existing Ration Card")],
        oo("https://aahar.jharkhand.gov.in", ["Link Aadhaar with ration card online", "Or at nearest CSC/Block Supply Office"]),
        ["ration", "food", "smart card", "portability", "Aadhaar", "Jharkhand"]
    ),
    scheme("pm_shri_schools", "PM SHRI Schools Scheme", "पीएम श्री स्कूल योजना",
        "Ministry of Education, GoI", "education",
        "Upgradation of 14,500 schools into PM SHRI model schools with modern infrastructure, labs, and NEP 2020 pedagogy.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Smart classrooms, science/computer labs, library, sports facilities at upgraded government schools. Free admission."},
        [],
        off(["Admission through regular school process", "Selected government schools upgraded as PM SHRI"]),
        ["education", "school", "infrastructure", "NEP", "central scheme"]
    ),
    scheme("jk_annapurna", "Annapurna Yojana", "अन्नपूर्णा योजना",
        "Ministry of Rural Development, GoI", "social_security",
        "10 kg free food grains/month to eligible senior citizens (65+) who are not getting pension from any source.",
        {"min_age": {"general_male": 65, "female": 65}, "categories": AC, "gender": AG},
        {"bpl_card": {"weight": 0.9, "description": "BPL elderly not receiving pension"}},
        {"type": "food", "amount": None, "currency": "INR", "frequency": "monthly", "description": "10 kg food grains (rice/wheat) free per month to destitute elderly not receiving any pension."},
        [A, doc("age_proof", "Age Proof")],
        off(["Apply at Block/Panchayat office", "Must not be receiving any pension"]),
        ["food", "elderly", "free ration", "senior citizen", "central scheme"]
    ),
    scheme("jk_cm_jan_samvad", "Mukhyamantri Jan Samvad (Grievance Portal)", "मुख्यमंत्री जन संवाद (शिकायत पोर्टल)",
        "CM Office, Jharkhand", "social_security",
        "Online public grievance portal for Jharkhand citizens to register complaints and track resolution.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "File complaints online. Track status. Resolution within 30 days. Covers all departments."},
        [A, doc("mobile", "Mobile Number")],
        oo("https://jansunwai.jharkhand.gov.in", ["Register complaint online", "Or call toll-free helpline", "Track with complaint ID"]),
        ["grievance", "complaint", "redressal", "helpline", "Jharkhand"]
    ),
    scheme("jk_udyami_scheme", "Mukhyamantri Laghu Udyami Yojana", "मुख्यमंत्री लघु उद्यमी योजना",
        "Dept of Industries, Jharkhand", "employment",
        "₹2 lakh grant to 25 lakh families for starting micro-businesses. Linked with SECC data for BPL families.",
        {"min_age": 18, "max_income_annual": 300000, "categories": ACM, "gender": AG},
        {"bpl_card": {"weight": 0.9, "description": "SECC-listed BPL families only"}},
        {"type": "financial", "amount": 200000, "currency": "INR", "frequency": "one_time", "description": "₹2 lakh grant (not loan) per family for starting any micro-enterprise. No repayment needed."},
        [A, B, D, doc("ration_card", "Ration Card (SECC listed)")],
        oo("https://cm-laghu-udyami.jharkhand.gov.in", ["Apply online through portal", "Select from empanelled business activities"]),
        ["employment", "micro enterprise", "grant", "BPL", "self-employment", "Jharkhand"]
    ),
    scheme("jk_nalkup_sinchai", "Jharkhand Niji Nalkup Sinchai Yojana", "झारखंड निजी नलकूप सिंचाई योजना",
        "Dept of Agriculture, Jharkhand", "agriculture",
        "Subsidy for boring private tube wells for irrigation. 60-80% subsidy based on category.",
        {"occupation": ["farmer"], "categories": AC, "gender": AG},
        {},
        {"type": "subsidy", "amount": 100000, "currency": "INR", "description": "60% subsidy (General), 80% (SC/ST) for boring tube wells up to 70m depth. Max ₹1 lakh."},
        [A, L, B],
        off(["Apply at Block Agriculture Office", "Geo-tagging of bore well location required"]),
        ["agriculture", "irrigation", "tube well", "bore well", "subsidy", "Jharkhand"]
    ),
    scheme("jk_krishi_input", "Jharkhand Krishi Input Anudan", "झारखंड कृषि इनपुट अनुदान",
        "Dept of Agriculture, Jharkhand", "agriculture",
        "Input subsidy for disaster-affected farmers — seeds, fertilizers, pesticides after crop loss for recovery.",
        {"occupation": ["farmer"], "categories": AC, "gender": AG},
        {},
        {"type": "financial", "amount": 13500, "currency": "INR", "frequency": "on_claim", "description": "₹6,800/hectare (rain-fed), ₹13,500/hectare (irrigated), ₹18,000/hectare (perennial crops)."},
        [A, L, B, doc("crop_damage_report", "Crop Damage Assessment Report")],
        oo("https://dbtagriculture.jharkhand.gov.in", ["Apply online on DBT Agriculture portal", "Block agriculture officer verifies damage"]),
        ["agriculture", "disaster", "input subsidy", "seeds", "fertilizer", "Jharkhand"]
    ),
    scheme("jk_toilet_scheme", "Swachh Bharat Mission (SBM) - Toilet", "स्वच्छ भारत मिशन - शौचालय",
        "Ministry of Jal Shakti, GoI", "housing",
        "₹12,000 incentive for constructing individual household toilets to achieve Open Defecation Free (ODF) status.",
        {"categories": ACM, "gender": AG},
        {"bpl_card": {"weight": 0.7, "description": "BPL/SECC listed households"}},
        {"type": "financial", "amount": 12000, "currency": "INR", "frequency": "one_time", "description": "₹12,000 (₹12K central + MNREGA convergence) for constructing twin-pit/septic tank toilet."},
        [A, B, doc("photo", "Photo of constructed toilet")],
        off(["Apply at Gram Panchayat", "Construction verified by Block coordinator", "Amount credited after verification"]),
        ["sanitation", "toilet", "SBM", "ODF", "central scheme", "housing"]
    ),
    scheme("jk_jal_jeevan", "Jal Jeevan Mission (Har Ghar Jal)", "जल जीवन मिशन (हर घर जल)",
        "Ministry of Jal Shakti, GoI", "housing",
        "Piped tap water connection to every rural household. Functional Household Tap Connection (FHTC) at no cost.",
        {"categories": ACM, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free piped tap water connection supplying 55 litres/person/day. Quality monitoring through WQMS."},
        [],
        off(["Contact Gram Panchayat or Jal Sahiya", "No application needed — mission-driven coverage"]),
        ["water", "tap", "piped water", "rural", "central scheme", "housing"]
    ),
    scheme("jk_aganwadi_worker", "Anganwadi Worker/Helper Honorarium", "आंगनवाड़ी कार्यकर्ता/सहायिका मानदेय",
        "Dept of Women & Child Development, Jharkhand", "women",
        "Monthly honorarium for Anganwadi Workers (₹10,000/month) and Helpers (₹5,500/month) providing ICDS services.",
        {"gender": ["female"], "min_age": 18, "max_age": 44, "categories": ACM},
        {},
        {"type": "financial", "amount": 120000, "currency": "INR", "frequency": "yearly", "description": "AWW: ₹10,000/month; AWH: ₹5,500/month. Performance incentives up to ₹1,000/month extra."},
        [A, B, D, doc("selection_letter", "AWW/AWH Selection Letter")],
        off(["Apply through CDPO (Child Development Project Officer)", "Selection at Block level"]),
        ["women", "Anganwadi", "ICDS", "child nutrition", "honourarium", "Jharkhand"]
    ),
    scheme("jk_cm_cycle_girl", "Free Bicycle for Girls (Class 8)", "छात्राओं को मुफ्त साइकिल (कक्षा 8)",
        "Dept of School Education, Jharkhand", "education",
        "Free bicycle specifically for girls in Class 8 in government schools to improve retention and reduce dropout.",
        {"gender": ["female"], "student_class": [8], "categories": ACM},
        {},
        {"type": "service", "amount": 3500, "currency": "INR", "description": "Free bicycle (~₹3,500) for all girls enrolled in Class 8 at government/aided schools."},
        [A, doc("school_cert", "Class 8 Enrollment Certificate")],
        off(["Distributed through school", "No application needed"]),
        ["education", "bicycle", "girls", "Class 8", "dropout prevention", "Jharkhand"]
    ),
    scheme("jk_seeds_distribution", "Free Seed Distribution (Kharif/Rabi)", "मुफ्त बीज वितरण (खरीफ/रबी)",
        "Dept of Agriculture, Jharkhand", "agriculture",
        "Free or subsidized high-yield variety seeds (rice, wheat, pulses, oilseeds) for Kharif and Rabi seasons.",
        {"occupation": ["farmer"], "farmer_type": ["marginal", "small"], "categories": AC, "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free/subsidized certified seeds: 10-20 kg rice, 20 kg wheat, 5 kg dal seeds per farmer per season."},
        [A, L],
        off(["Collect from Block Agriculture Office before sowing", "Or at Kisan Mela/agriculture camps"]),
        ["agriculture", "seeds", "kharif", "rabi", "farmer", "free", "Jharkhand"]
    ),
    scheme("jk_eklavya_school", "Eklavya Model Residential School (EMRS)", "एकलव्य मॉडल आवासीय विद्यालय",
        "Ministry of Tribal Affairs, GoI", "education",
        "CBSE-affiliated residential schools for ST students in tribal areas with free education, boarding, and meals.",
        {"categories": ["ST"], "gender": AG},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free education (Class 6-12) + hostel + meals + uniforms + books. CBSE curriculum. Sports and labs."},
        [A, C, doc("school_cert", "Class 5 Pass Certificate"), doc("tribal_cert", "ST Certificate")],
        off(["Admission through entrance exam", "Apply at school directly or district tribal welfare office"]),
        ["education", "tribal", "ST", "residential school", "CBSE", "free", "central scheme"]
    ),
    scheme("jk_kasturba_gandhi", "Kasturba Gandhi Balika Vidyalaya (KGBV)", "कस्तूरबा गांधी बालिका विद्यालय",
        "Ministry of Education, GoI", "education",
        "Free residential schools for girls from SC/ST/OBC/Minority in educationally backward blocks (Class 6-12).",
        {"gender": ["female"], "categories": ["SC", "ST", "OBC", "Minority"]},
        {},
        {"type": "service", "amount": None, "currency": "INR", "description": "Free education (Class 6-12) + hostel + meals + uniforms for girls. Focus on educationally backward areas."},
        [A, C, doc("school_cert", "Class 5 Pass Certificate")],
        off(["Apply through school or district education office", "Preference to out-of-school girls and dropouts"]),
        ["education", "girls", "residential", "SC", "ST", "OBC", "Minority", "central scheme"]
    ),
]

batch2 = [s for s in batch2 if s["scheme_id"] not in existing_ids]
all_schemes = existing + batch2

print(f"Before batch2: {len(existing)}, Adding: {len(batch2)}, Total: {len(all_schemes)}")

with open(SCHEMES_FILE, "w", encoding="utf-8") as f:
    json.dump(all_schemes, f, ensure_ascii=False, indent=2)

print(f"✅ Total {len(all_schemes)} schemes written.")
