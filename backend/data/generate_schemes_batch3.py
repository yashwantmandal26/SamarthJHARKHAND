"""Final batch: 7 more schemes to reach exactly 110."""
import json, os

SCHEMES_FILE = os.path.join(os.path.dirname(__file__), "schemes.json")
with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
    existing = json.load(f)
existing_ids = {s["scheme_id"] for s in existing}

def scheme(sid, name, name_hi, dept, cat, desc, hard, soft, benefits, docs, app, tags):
    return {"scheme_id": sid, "name": name, "name_hindi": name_hi, "department": dept, "category": cat, "description": desc,
        "eligibility": {"hard_constraints": {**hard, "domicile": "jharkhand"}, "soft_constraints": soft},
        "benefits": benefits, "documents_required": docs, "application_process": app, "tags": tags}

def doc(did, name, m=True): return {"id": did, "name": name, "mandatory": m}
A=doc("aadhaar","Aadhaar Card"); B=doc("bank_account","Bank Account (Aadhaar linked)")
D=doc("domicile","Jharkhand Domicile Certificate"); I=doc("income_cert","Family Income Certificate")
C=doc("caste_cert","Caste Certificate"); L=doc("land_record","Land Records")
AC=["SC","ST","OBC","General"]; ACM=AC+["Minority"]; AG=["male","female","other"]
def oo(u,s): return {"mode":["online","offline"],"online_url":u,"offline_steps":s}
def off(s): return {"mode":["offline"],"online_url":None,"offline_steps":s}

batch3 = [
    scheme("jk_cm_smart_school","CM Smart School Yojana","मुख्यमंत्री स्मार्ट स्कूल योजना",
        "Dept of School Education, Jharkhand","education",
        "Converting 4,000 government schools into smart schools with digital boards, tablets, and internet connectivity.",
        {"categories":ACM,"gender":AG},{},
        {"type":"service","amount":None,"currency":"INR","description":"Digital smart boards, tablets for students, free Wi-Fi. Covers Class 1-12 at upgraded schools."},
        [],off(["Enroll at designated smart schools","No extra fees"]),
        ["education","smart school","digital","technology","Jharkhand"]
    ),
    scheme("jk_van_dhan","Van Dhan Vikas Kendra","वन धन विकास केंद्र",
        "TRIFED / Ministry of Tribal Affairs, GoI","employment",
        "Value addition centres for tribal people to process and sell forest produce (lac, mahua, honey, herbs) at fair prices.",
        {"categories":["ST"],"gender":AG},{},
        {"type":"mixed","amount":15000,"currency":"INR","description":"Training in value-addition + ₹15,000 working capital per SHG. Market linkage through Tribes India/GEM."},
        [A,B,C],off(["Contact nearest TRIFED/tribal cooperative","Join Van Dhan SHG through JSLPS"]),
        ["tribal","forest produce","value addition","SHG","TRIFED","employment"]
    ),
    scheme("jk_cm_migrant","CM Migrant Worker Return Scheme","मुख्यमंत्री प्रवासी श्रमिक वापसी योजना",
        "Dept of Labour, Jharkhand","employment",
        "Skill mapping, job placement, and self-employment support for returned migrant workers from Jharkhand.",
        {"min_age":18,"max_age":55,"categories":AC,"gender":AG},{},
        {"type":"mixed","amount":25000,"currency":"INR","description":"Skill training + ₹25,000 self-employment grant + job placement assistance for returned migrants."},
        [A,B,D,doc("eshram","e-Shram Card",False)],
        off(["Register at District Employment Exchange","Attend skill mapping camp at Block level"]),
        ["employment","migrant","worker","skill","placement","Jharkhand"]
    ),
    scheme("pm_garib_kalyan_rojgar","PM Garib Kalyan Rojgar Abhiyan","प्रधानमंत्री गरीब कल्याण रोजगार अभियान",
        "Ministry of Rural Development, GoI","employment",
        "Employment in 25 infrastructure works for returned migrant workers in rural areas — convergence of 12 schemes.",
        {"min_age":18,"categories":AC,"gender":AG},{},
        {"type":"wages","amount":257,"currency":"INR","frequency":"daily","description":"₹257/day (Jharkhand rate) in construction of rural roads, housing, water bodies, fibre cable laying."},
        [A,B,doc("job_card","MGNREGA Job Card")],
        off(["Register at Gram Panchayat","Work allotted within 15 days"]),
        ["employment","rural","infrastructure","migrant","MGNREGA","central scheme"]
    ),
    scheme("jk_disability_scholarship","Jharkhand Disability Scholarship","झारखंड दिव्यांग छात्रवृत्ति",
        "Dept of Welfare, Jharkhand","education",
        "Scholarship for students with 40%+ disability studying in Class 1-12 and higher education in Jharkhand.",
        {"categories":ACM,"gender":AG,"special_conditions":["disabled"]},{},
        {"type":"scholarship","amount":15000,"currency":"INR","frequency":"yearly","description":"₹5,000-₹15,000/year based on disability level and class. Covers tuition+books+aids."},
        [A,B,doc("disability_cert","Disability Certificate (40%+)"),doc("school_cert","School Certificate")],
        oo("https://jharsewa.jharkhand.gov.in",["Apply online or at District Welfare Office"]),
        ["education","disability","scholarship","divyang","student"]
    ),
    scheme("jk_krishi_clinic","Kisan Call Centre & Krishi Clinic","किसान कॉल सेंटर और कृषि क्लिनिक",
        "Ministry of Agriculture, GoI","agriculture",
        "Toll-free helpline 1800-180-1551 for farmers — crop advice, pest management, weather alerts, market prices.",
        {"occupation":["farmer"],"categories":AC,"gender":AG},{},
        {"type":"service","amount":None,"currency":"INR","description":"24/7 toll-free helpline. Expert advice in Hindi. SMS weather alerts. Market price info via mKisan portal."},
        [],off(["Call 1800-180-1551 (toll-free)","SMS alerts via mKisan app","Visit Krishi Vigyan Kendra"]),
        ["agriculture","helpline","farmer","advisory","weather","market price"]
    ),
    scheme("jk_cm_sukha_rahat_2","CM Drought Relief 2.0 (Enhanced)","मुख्यमंत्री सूखा राहत 2.0 (बढ़ा हुआ)",
        "Dept of Agriculture, Jharkhand","agriculture",
        "Enhanced drought relief with increased compensation — ₹5,000/family plus input subsidy for next season recovery.",
        {"occupation":["farmer"],"categories":AC,"gender":AG},
        {"bpl_card":{"weight":0.6,"description":"BPL farming families first"}},
        {"type":"financial","amount":5000,"currency":"INR","frequency":"one_time","description":"₹5,000 immediate relief + free seeds/fertilizer for next season. Covers all drought-declared blocks."},
        [A,L,B],off(["Auto-enrolled based on drought declaration","Verify at Panchayat/Block office"]),
        ["agriculture","drought","relief","farmer","compensation","Jharkhand"]
    ),
]

batch3 = [s for s in batch3 if s["scheme_id"] not in existing_ids]
all_schemes = existing + batch3
print(f"Before: {len(existing)}, Adding: {len(batch3)}, Final Total: {len(all_schemes)}")

with open(SCHEMES_FILE, "w", encoding="utf-8") as f:
    json.dump(all_schemes, f, ensure_ascii=False, indent=2)
print(f"✅ Successfully written {len(all_schemes)} schemes!")
