import streamlit as st
import math
import time
import os
from datetime import datetime
from intasend import APIService
from dotenv import load_dotenv

# --- 1. ROBUST ENVIRONMENT LOADING ---
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# --- 2. KEY RETRIEVAL ---
SECRET_KEY = os.getenv("INTASEND_SECRET")
PUBLISHABLE_KEY = os.getenv("INTASEND_PUB")

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="KUCCPS Courses Eligibility portal", page_icon="🎓", layout="wide")

if not SECRET_KEY or not PUBLISHABLE_KEY:
    st.error("❌ **API Keys Not Detected!**")
    st.stop()

# --- 4. DATA STRUCTURES ---
subject_groups = {
    "Group I": ["English", "Kiswahili", "Mathematics"],
    "Group II": ["Biology", "Physics", "Chemistry", "General Science"],
    "Group III": ["History & Government", "Geography", "CRE", "IRE", "HRE"],
    "Group IV": ["Home Science", "Art & Design", "Agriculture", "Computer Studies", "Music", "Business Studies"],
    "Group V": ["French", "German", "Arabic", "Kenya Sign Language", "Aviation Technology", "Power Mechanics", "Electricity", "Drawing and Design", "Building Construction", "Wood Work", "Metal Work"]
}

clusters = {
    1: {"name": "Law & Legal Studies", "req": ["English", "Kiswahili", "Mathematics", ["Group II", "Group III"]]},
    2: {"name": "Business, Hospitality & Management", "req": ["English", "Mathematics", ["Group II"], ["Group III", "Group IV"]]},
    3: {"name": "Social Sciences, Media & Arts", "req": ["English", "Kiswahili", "Mathematics", ["Group III", "Group II"]]},
    4: {"name": "Geosciences & Environmental Studies", "req": ["English", "Kiswahili", "Mathematics", "Geography"]},
    5: {"name": "Engineering & Technology", "req": ["Mathematics", "Physics", "English", "Chemistry"]},
    6: {"name": "Architecture & Construction", "req": ["Mathematics", "Physics", ("English", "Kiswahili"), "Geography"]},
    7: {"name": "Computing & Information Technology", "req": ["Mathematics", "English", "Chemistry", "Physics"]},
    8: {"name": "Agribusiness & Entrepreneurship", "req": ["Chemistry", "Biology", ("Mathematics", "Physics"), "English"]},
    9: {"name": "General & Biological Sciences", "req": ["Mathematics", "Biology", "Chemistry", ("English", "Kiswahili")]},
    10: {"name": "Actuarial Science, Math & Economics", "req": ["Mathematics", "English", ["Group II", "Group III"], ["Group IV","Group III"]]},
    11: {"name": "Design & Creative Arts", "req": ["English", "Kiswahili", "Mathematics",["Group IV","Group III"]]},
    12: {"name": "Sports Science & Physical Education", "req": ["English", "Kiswahili", "Mathematics", "Biology"]},
    13: {"name": "Medicine & Health Sciences", "req": [("Mathematics", "Physics"), "Biology", "Chemistry", "English"]},
    14: {"name": "History & Archaeology", "req": [("English", "Kiswahili"), ["Group II", "Group III"], "Mathematics", "History & Government"]},
    15: {"name": "Agriculture & Environmental Sciences", "req": ["Chemistry", "Biology", ("Mathematics", "Physics"), ["Group IV"]]}, 
    16: {"name": "Geography & Urban Studies", "req": ["English", ["Group II", "Group III"], "Mathematics", "Geography"]},
    17: {"name": "Languages & International Studies", "req": [("English", "Kiswahili"), ("French", "German", "Arabic"), "Mathematics", ["Group II", "Group III"]]},
    18: {"name": "Music & Performing Arts", "req": [("English", "Kiswahili"), ["Group II", "Group III"], "Mathematics", "Music"]},
    19: {"name": "Education & Teaching", "req": ["English", ["Group III", "Kiswahili"], "Mathematics", ["Group II"]]}, 
    20: {"name": "Religious & Theological Studies", "req": [("English", "Kiswahili"), ["Group III"], ["Group III"], ("CRE", "IRE", "HRE")]}
}

# Added 'cid' to each entry to link with Cluster Calculations
min_grades = {
    "Architecture / Quantity Surveying": {"cid": 6, "points": 46, "subs": ["Mathematics", "Physics", "Geography", ("English", "Kiswahili")], "min_grade": 7},
    "urbanplanning/Buildingconstruction": {"cid": 6, "points": 46, "subs": ["Mathematics", "Physics", "Geography", ("English", "Kiswahili")], "min_grade": 7},
    "Agribusiness / Food Business": {"cid": 8, "points": 46, "subs": ["Biology", "Chemistry", ("Mathematics", "Physics"), ("English", "Kiswahili")], "min_grade": 7},
    "Enterepreneurship /Agric Economics": {"cid": 8, "points": 46, "subs": ["Biology", "Chemistry", ("Mathematics", "Physics"), ("English", "Kiswahili")], "min_grade": 7},
    "Biology / Chemistry / Biotech": {"cid": 9, "points": 46, "subs": ["Biology", "Chemistry", "Mathematics", ("English", "Kiswahili")], "min_grade": 7},
    "Biochem/Microbiology/Botany/Zoology": {"cid": 9, "points": 46, "subs": ["Biology", "Chemistry", "Mathematics", ("English", "Kiswahili")], "min_grade": 7},
    "Fashion/Industrial Design": {"cid": 11, "points": 46, "subs": [("English", "Kiswahili"), "Mathematics", ["Group IV", "Group III"]], "min_grade": 7},
    "Fine Arts / Graphic Design": {"cid": 11, "points": 46, "subs": [("English", "Kiswahili"), "Mathematics", ["Group IV", "Group III"]], "min_grade": 7},
    "Sports Science/Physical Education": {"cid": 12, "points": 46, "subs": ["Biology", ("English", "Kiswahili"), "Mathematics"], "min_grade": 7},
    "Agriculture / Horticulture": {"cid": 15, "points": 46, "subs": ["Biology", "Chemistry", ["Group IV"], ("English", "Kiswahili")], "min_grade": 7},
    "Environmental Science/Wildlife/Forestry": {"cid": 15, "points": 46, "subs": ["Biology", "Chemistry", ["Group IV"], ("English", "Kiswahili")], "min_grade": 7},
    "Int. Relations/Global Studies": {"cid": 17, "points": 46, "subs": [("English", "Kiswahili"), ("French", "German", "Arabic", "English"), "Mathematics"], "min_grade": 7},
    "Linguistics /French/Germany": {"cid": 17, "points": 46, "subs": [("English", "Kiswahili"), ("French", "German", "Arabic", "English"), "Mathematics"], "min_grade": 7},
    "Medicine & Surgery (MBChB)": {"cid": 13, "points": 60, "subs": ["Biology", "Chemistry", ("Physics", "Mathematics"), ("English", "Kiswahili")], "min_grade": 9},
    "Pharmacy": {"cid": 13, "points": 53, "subs": ["Biology", "Chemistry", ("Physics", "Mathematics"), ("English", "Kiswahili")], "min_grade": 8},
    "Nursing / Clinical Med / Lab Science": {"cid": 13, "points": 46, "subs": ["Biology", "Chemistry", ("Physics", "Mathematics"), ("English", "Kiswahili")], "min_grade": 7},
    "Engineering (b.tech & Bsc:Mechanical, Civil, Electrical,Mechatronics,Auronatical,Marine)": {"cid": 5, "points": 46, "subs": ["Mathematics", "Physics", "Chemistry", ("English", "Kiswahili")], "min_grade": 7},
    "Software Eng / Data Science / AI / Cybersecurity": {"cid": 7, "points": 46, "subs": ["Mathematics", "Physics", "Chemistry", ("English", "Kiswahili")], "custom": {"Mathematics": 7, "English": 7, "Kiswahili": 7, "Chemistry": 7, "Physics": 7}},
    "Computer Science": {"cid": 7, "points": 46, "subs": ["Mathematics", "Physics", "Chemistry", ("English", "Kiswahili")], "custom": {"Mathematics": 7, "English": 7, "Kiswahili": 7, "Chemistry": 7, "Physics": 6}},
    "IT / Information Systems": {"cid": 7, "points": 46, "subs": ["Mathematics", ("English", "Kiswahili")], "custom": {"Mathematics": 7, "English": 6, "Kiswahili": 6}},
    "Economics / Statistics": {"cid": 10, "points": 46, "subs": ["Mathematics"], "min_grade": 7},
    "ActuarialScience/FinancialMath": {"cid": 10, "points": 46, "subs": ["Mathematics"], "min_grade": 7},
    "Supply Chain/HR": {"cid": 2, "points": 46, "subs": ["Mathematics", ("English", "Kiswahili")], "min_grade": 6},
    "BCom / Finance / Marketing/Accounting": {"cid": 2, "points": 46, "subs": ["Mathematics", ("English", "Kiswahili")], "min_grade": 6},
    "Law (LLB)": {"cid": 1, "points": 46, "subs": [("English", "Kiswahili")], "min_grade": 9},
    "Education (Arts/Science)": {"cid": 19, "points": 46, "subs": [("English", "Kiswahili"), "Mathematics"], "min_grade": 7},
    "Social Sciences/Jornalism/Physchology": {"cid": 3, "points": 40, "subs": [("English", "Kiswahili")], "min_grade": 7},
    "Environmental Science": {"cid": 4, "points": 40, "subs": ["Geography", "Mathematics"], "min_grade": 6},
    "Environment studies / Meteorology": {"cid": 4, "points": 40, "subs": ["Geography", "Mathematics"], "min_grade": 6},
    "Geosciences / Geology": {"cid": 4, "points": 40, "subs": ["Geography", "Mathematics"], "min_grade": 6}
}

diplomas = {
    "Medical Diplomas (Nursing/Clinical Medicine)": {"min_agg": 40, "Biology": 6, "Chemistry": 5, "lang": 6},
    "Technical Diplomas (Building&construction)": {"min_agg": 32, "Mathematics": 5, "Physics": 5, "lang": 5},
    "Business/Social Science Diplomas": {"min_agg": 32, "Mathematics": 4, "lang": 5},
    "Technical Diploma.Eng(civil/electrical&electronic/automotive/mechanical)": {"min_agg": 32, "Mathematics": 5, "Physics": 5, "lang": 5},
    "Quantity_surveying": {"min_agg": 32, "Mathematics": 5, "Physics": 5, "lang": 5,"Geography":4},
    "Diploma in law": {"min_agg": 42, "Mathematics": 6, "lang": 6},
    "Diploma_secondary_education_arts": {"min_agg": 42, "Mathematics": 4, "lang": 7},
    "Diploma_secondary_education_sciences": {"min_agg": 42, "Mathematics": 8,"lang": 6},
    
    "diploma_clinical_medicine_surgery": {"min_agg": 42, "Biology": 6, "chem_phys": 6, "lang": 6, "math_phys": 5},
    "diploma_orthopaedic_technology": {"min_agg": 42, "Biology": 6, "lang": 6, "Chemistry": 5,"Mathematics": 5},
    "diploma_pharmacy": {"min_agg": 42, "Biology": 6, "Chemistry": 6, "lang": 6, "Mathematics": 5},
    "diploma_radiography_imaging": {"min_agg": 42, "Physics": 6, "Biology": 6, "lang": 6, "Mathematics": 5},
    "diploma_orthopaedic_trauma_medicine": {"min_agg": 42, "Biology": 6, "lang": 6, "Mathematics": 5},
    "diploma_optometry": {"min_agg": 42, "Mathematics": 6, "lang": 6, "Biology": 5},
    "diploma_occupational_therapy": {"min_agg": 42, "lang": 6, "Biology": 5, "Mathematics": 5},
    "diploma_medical_engineering": {"min_agg": 42, "Mathematics": 5, "lang": 6, "Biology": 4,"Physics":5},
    "diploma_health_records_it": {"min_agg": 42, "Mathematics": 5, "Biology": 4, "lang": 6},
    "diploma_health_counselling": {"min_agg": 42, "Biology": 4, "lang": 6},
    "diploma_health_promotion": {"min_agg": 42, "Biology": 5, "lang": 6, "Mathematics": 4},
    "diploma_dental_technology": {"min_agg": 42, "Chemistry": 6, "Biology": 5, "lang": 6},
    "diploma_community_oral_health": {"min_agg": 42, "Biology": 6, "lang": 6, "Mathematics": 5},
    "diploma_community_health": {"min_agg": 42, "Biology": 4, "lang": 4, "Mathematics": 3},
    "certificate_community_health_assistant": {"min_agg": 32, "Biology": 3, "lang": 4, "Mathematics": 3},
    "certificate_emergency_medical_tech": {"min_agg": 32, "Biology": 3},
    "certificate_health_records_it": {"min_agg": 32, "Biology": 3, "lang": 3, "Mathematics": 2},
    "certificate_medical_engineering": {"min_agg": 25, "Biology": 3, "Mathematics": 3,"Physics":3 ,"lang": 3},
    "certificate_orthopaedic_trauma": {"min_agg": 32, "Biology": 5, "lang": 5, "Chemistry": 4},
    "cert_electrical_engineering": {"min_agg": 24, "Mathematics": 3, "Physics": 3, "lang": 3},
    "cert_building_technology": {"min_agg": 24, "Mathematics": 3, "Physics": 2, "lang": 3},
    "cert_automotive_engineering": {"min_agg": 24, "Mathematics": 3, "Physics": 3, "lang": 3},
    "cert_ict": {"min_agg": 24, "Mathematics": 3, "lang": 4}
}

artisan_trades = ["Artisan in Electrical Installation", "Artisan in Masonry & Building", "Artisan in Plumbing", "Artisan in Food & Beverage","cert_plumbing","Welding","motorvehiclemechanic"]
grade_map = {'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8, 'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3, 'D-': 2, 'E': 1}

# --- 5. LOGIC FUNCTIONS ---
def find_best_from_groups(groups, user_grades, used):
    best_sub, best_pts = None, -1
    for g_name in groups:
        if g_name in subject_groups:
            for sub in subject_groups[g_name]:
                if sub in user_grades and sub not in used:
                    if user_grades[sub] > best_pts:
                        best_pts, best_sub = user_grades[sub], sub
    return best_sub, best_pts

def check_eligibility(rule, agg_points, user_grades):
    if agg_points < rule["points"]: return False
    for req in rule["subs"]:
        if isinstance(req, tuple):
            avail = [user_grades[s] for s in req if s in user_grades]
            if not avail or max(avail) < rule.get("min_grade", 0): return False
        elif isinstance(req, list):
            res_sub, res_pts = find_best_from_groups(req, user_grades, [])
            if not res_sub or res_pts < rule.get("min_grade", 0): return False
        else:
            if req not in user_grades: return False
            thr = rule.get("custom", {}).get(req, rule.get("min_grade", 0))
            if user_grades[req] < thr: return False
    return True

# --- 6. UI SECTION ---
st.title("🎓 KCSE CAREER & COURSE GUIDE KENYA")

if 'paid' not in st.session_state: st.session_state.paid = False

with st.sidebar:
    st.header("Results Entry")
    num_subs = st.radio("Number of Subjects:", [7, 8, 9], index=1)
    agg_pts = st.number_input("Aggregate KCSE Points (0-84):", 0, 84, 46)
    
    user_grades = {}
    all_subjects = sorted([s for g in subject_groups.values() for s in g])
    
    for i in range(num_subs):
        s = st.selectbox(f"Subject {i+1}", ["Select"] + all_subjects, key=f"s{i}")
        g = st.selectbox(f"Grade {i+1}", list(grade_map.keys()), key=f"g{i}")
        if s != "Select": user_grades[s] = grade_map[g]

# Payment Logic
if not st.session_state.paid:
    st.info("Please enter your results in the sidebar and pay to view your career report.")
    phone = st.text_input("M-Pesa Number (e.g., 0712345678)")
    if st.button("Unlock Report - KES 94.00"):
        if phone:
            try:
                service = APIService(token=SECRET_KEY, publishable_key=PUBLISHABLE_KEY, test=False)
                f_phone = phone.strip().replace("+", "")
                if f_phone.startswith("0"): f_phone = "254" + f_phone[1:]
                
                response = service.collect.mpesa_stk_push(phone_number=f_phone, email="user@kuccps.go.ke", amount=94, narrative="KUCCPS Results")
                invoice_id = response['invoice']['invoice_id']
                
                with st.spinner("Push sent! Waiting for payment..."):
                    timeout = time.time() + 60
                    while time.time() < timeout:
                        status = service.collect.status(invoice_id)
                        if status['invoice']['state'] == 'COMPLETE':
                            st.session_state.paid = True
                            st.rerun()
                        elif status['invoice']['state'] == 'FAILED':
                            st.error("Payment failed.")
                            break
                        time.sleep(3)
            except Exception as e:
                st.error(f"Payment Error: {e}")
        else:
            st.warning("Please enter your phone number.")

# --- 7. RESULTS DISPLAY ---
if st.session_state.paid:
    st.balloons()
    col1, col2 = st.columns([1, 1])
    
    # Pre-calculate all cluster weights
    calc_clusters = {}
    for cid, cinfo in clusters.items():
        used, c_sum, possible = [], 0, True
        for req in cinfo["req"]:
            sub, pts = None, 0
            if isinstance(req, str):
                if req in user_grades: sub, pts = req, user_grades[req]
                else: possible = False
            elif isinstance(req, tuple):
                avail = [s for s in req if s in user_grades]
                sub = max(avail, key=lambda x: user_grades[x]) if avail else None
                pts = user_grades[sub] if sub else 0
                if not sub: possible = False
            elif isinstance(req, list):
                sub, pts = find_best_from_groups(req, user_grades, used)
                if not sub: possible = False
            
            if not possible: break
            c_sum += pts
            used.append(sub)
        
        weight = math.sqrt((c_sum/48.0)*(agg_pts/84.0))*48 if possible and agg_pts >= 46 else 0.0
        calc_clusters[cid] = weight

    with col1:
        st.header("📊 Cluster Weight Analysis")
        
        for cid, weight in calc_clusters.items():
            if weight > 0:
                st.write(f"**C{cid}: {clusters[cid]['name']}**")
                st.progress(weight/48.0)
                st.caption(f"Weight: {weight:.3f}")

    with col2:
        st.header("📜 Qualifying Programs")
        
        # 1. Degree Programs (Independent Block)
        if agg_pts >= 46:
            st.subheader("🎓 University Degree Courses")
            for name, rule in min_grades.items():
                if check_eligibility(rule, agg_pts, user_grades):
                    cid_link = rule.get('cid')
                    w = calc_clusters.get(cid_link, 0.0)
                    st.success(f"✅ {name}")
                    if w > 0: st.caption(f"Est. Cluster Weight: {w:.2f}")

        # 2. Diploma Programs (Independent Block - will show for anyone > 32)
        if agg_pts >= 25:
            st.subheader("📜 TVET Diploma /Certificate Programs")
            lang_pts = max(user_grades.get("English", 0), user_grades.get("Kiswahili", 0))
            for d_name, d_req in diplomas.items():
                if agg_pts >= d_req['min_agg']:
                    eligible = True
                    for key, val in d_req.items():
                        if key == 'lang' and lang_pts < val: eligible = False
                        elif key not in ['min_agg', 'lang'] and user_grades.get(key, 0) < val: eligible = False
                    if eligible:
                        st.info(f"🔷 {d_name}")
        
        # 3. Artisan Programs
        if agg_pts < 32:
            st.subheader("🛠 Artisan & Trade Courses")
            for trade in artisan_trades:
                st.warning(f"🔨 {trade}")

    if st.button("Download Full PDF Report"):
        st.write("Report generated and ready for download.")