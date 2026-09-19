from pathlib import Path
import fitz  # PyMuPDF

def create_sample_pdfs(output_dir: Path):
    """
    Generates realistic multi-page university regulation PDF documents
    with proper page numbers, section headers, and clauses.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Attendance Policy
    doc_att = fitz.open()
    
    # Page 1
    p1 = doc_att.new_page()
    text_p1 = """UNIVERSITY REGULATIONS MANUAL - SECTION 4
POLICY ON STUDENT ATTENDANCE AND LEAVE RULES (REVISED 2026)

1. General Principles
1.1 Regular attendance in lectures, tutorials, and practical laboratories is essential for academic continuity and pedagogical efficacy.
1.2 The academic session consists of a minimum of 90 instructional days per semester.

2. Minimum Attendance Requirement
2.1 Every student must maintain a minimum attendance of 75% in each registered theory and laboratory course in order to be eligible to appear for the end-semester examinations.
2.2 Attendance shall be calculated from the first official day of instruction until the last instructional day notified in the Academic Calendar.
2.3 Continuous absence without prior written permission for more than 14 consecutive calendar days shall result in the student's name being struck off the rolls.

3. Monitoring and Dissemination
3.1 Course instructors shall publish fortnightly attendance statements on the university student portal.
3.2 It is the sole responsibility of the student to monitor their attendance percentage and take corrective action.
"""
    p1.insert_text((50, 60), text_p1, fontsize=11, fontname="helv")

    # Page 2
    p2 = doc_att.new_page()
    text_p2 = """UNIVERSITY REGULATIONS MANUAL - SECTION 4 (CONTINUED)
POLICY ON STUDENT ATTENDANCE AND LEAVE RULES (REVISED 2026)

4. Condonation of Attendance Shortage
4.1 The Dean of Academic Affairs may condone attendance shortage up to a maximum of 10% (i.e., attendance between 65% and 74.9%) on genuine grounds:
    (a) Prolonged medical illness requiring hospitalization.
    (b) Participation in recognized Inter-University, National, or International cultural, sports, or academic competitions with prior Dean approval.
    (c) Bereavement of immediate family members (parents or siblings).
4.2 A non-refundable condonation fee of $50 per course must be deposited before the application is evaluated.
4.3 Medical leave certificates must be countersigned by the University Medical Officer and submitted to the Academic Section within seven (7) calendar days of returning to campus. Late submissions shall not be entertained under any circumstances.

5. Detention and Re-registration
5.1 Any student whose attendance falls below 65% in any course shall be deemed 'Detained' in that specific course.
5.2 Detained students are strictly barred from appearing for the end-semester examination in that course.
5.3 A detained student must re-register for the course when it is offered in subsequent semesters and satisfy all attendance and internal assessment requirements afresh.
"""
    p2.insert_text((50, 60), text_p2, fontsize=11, fontname="helv")
    doc_att.save(str(output_dir / "Attendance_Policy.pdf"))
    doc_att.close()

    # 2. Examination Rules
    doc_exam = fitz.open()

    # Page 1
    p1 = doc_exam.new_page()
    text_p1 = """UNIVERSITY ACADEMIC GUIDELINES - SECTION 7
EXAMINATION RULES, EVALUATION AND MALPRACTICE CODE (2026)

1. Eligibility Requirements for Semester Examinations
1.1 A student shall be eligible to appear for the End-Semester University Examinations only if they fulfill the following conditions:
    (a) Satisfied the minimum 75% attendance criteria or obtained formal approval for condonation under Regulation 4.1.
    (b) Cleared all outstanding tuition fees, library dues, hostel dues, and laboratory breakage charges.
    (c) Possesses an authentic University Examination Hall Ticket issued by the Controller of Examinations.
    (d) Has not been subjected to disciplinary suspension or debarment by the Proctorial Board.

2. Examination Hall Conduct
2.1 Candidates must occupy their designated seats at least 15 minutes before the scheduled commencement of the examination.
2.2 No student shall be admitted to the examination hall after 30 minutes from the commencement of the exam.
2.3 No student shall leave the examination hall during the first 60 minutes of the examination.
"""
    p1.insert_text((50, 60), text_p1, fontsize=11, fontname="helv")

    # Page 2
    p2 = doc_exam.new_page()
    text_p2 = """UNIVERSITY ACADEMIC GUIDELINES - SECTION 7 (CONTINUED)
EXAMINATION RULES, EVALUATION AND MALPRACTICE CODE (2026)

3. Malpractice and Penalties
3.1 Possession of mobile phones, smartwatches, programmable calculators, electronic earphones, or unauthorized paper chits in the examination hall constitutes gross malpractice.
3.2 Any candidate found communicating with another candidate or copying from any source shall be immediately booked under the Examination Malpractice Code.
3.3 Penalties for malpractice:
    (a) Category I (Possession of unauthorized material): Cancellation of performance in that specific subject and award of 'F' grade.
    (b) Category II (Copying or assisting in copying): Cancellation of performance in all registered subjects of the current semester.
    (c) Category III (Impersonation or assault on invigilators): Rustication from the University for a minimum of two academic years and police registration.

4. Supplementary Examinations
4.1 Supplementary examinations shall be conducted within 45 calendar days of the publication of regular semester results.
4.2 Only students who secured an 'F' (Fail) grade in regular examinations are eligible to register for supplementary examinations.
4.3 A student may register for a maximum of four (4) supplementary subjects per examination cycle.
"""
    p2.insert_text((50, 60), text_p2, fontsize=11, fontname="helv")
    doc_exam.save(str(output_dir / "Examination_Rules.pdf"))
    doc_exam.close()

    # 3. Academic Regulations 2026
    doc_acad = fitz.open()

    # Page 1
    p1 = doc_acad.new_page()
    text_p1 = """UNIVERSITY BULLETIN 2026
ACADEMIC REGULATIONS FOR UNDERGRADUATE AND POSTGRADUATE PROGRAMMES

1. Degree Requirements and Credit Framework
1.1 The Bachelor of Technology (B.Tech) degree requires successful completion of 160 cumulative academic credits.
1.2 The standard course load per semester is between 20 and 24 credits. No student is permitted to register for more than 26 credits without prior written permission from the Academic Council.
1.3 The maximum allowable duration to complete the 4-year degree is six (6) consecutive academic years.

2. Grading System and CGPA Calculation
2.1 Academic performance is evaluated on a 10-point scale:
    - Grade 'O' (Outstanding): 10 grade points (Marks >= 90%)
    - Grade 'A+' (Excellent): 9 grade points (Marks 80-89%)
    - Grade 'A' (Very Good): 8 grade points (Marks 70-79%)
    - Grade 'B+' (Good): 7 grade points (Marks 60-69%)
    - Grade 'B' (Above Average): 6 grade points (Marks 55-59%)
    - Grade 'C' (Pass): 5 grade points (Marks 50-54%)
    - Grade 'F' (Fail): 0 grade points (Marks < 50%)
2.2 Semester Grade Point Average (SGPA) is calculated as: Sum(Course Credits * Grade Points) / Sum(Course Credits).
2.3 Cumulative Grade Point Average (CGPA) reflects the weighted average of all completed semesters.
"""
    p1.insert_text((50, 60), text_p1, fontsize=11, fontname="helv")

    # Page 2
    p2 = doc_acad.new_page()
    text_p2 = """UNIVERSITY BULLETIN 2026 (CONTINUED)
ACADEMIC REGULATIONS FOR UNDERGRADUATE AND POSTGRADUATE PROGRAMMES

3. Academic Probation and Dismissal
3.1 A student who secures a CGPA of less than 5.0 at the conclusion of any academic year shall be placed on Academic Probation.
3.2 A student on Academic Probation must seek mandatory counseling from their assigned Faculty Advisor and cannot hold office in student clubs or represent the university in external events.
3.3 Failure to raise the CGPA above 5.0 after two consecutive probation semesters shall result in referral to the Academic Senate for termination of enrollment.

4. Course Add/Drop and Withdrawal
4.1 Course registration modifications (Add/Drop) are permitted during the first ten (10) instructional days of each semester.
4.2 Course withdrawal without academic penalty is permitted up to the eighth (8th) week of the semester, resulting in a 'W' notation on the official transcript.
"""
    p2.insert_text((50, 60), text_p2, fontsize=11, fontname="helv")
    doc_acad.save(str(output_dir / "Academic_Regulations_2026.pdf"))
    doc_acad.close()

    # 4. Student Code of Conduct
    doc_conduct = fitz.open()
    p1 = doc_conduct.new_page()
    text_p1 = """STUDENT HANDBOOK & CODE OF CONDUCT (2026)
CAMPUS ETHICS, HOSTEL POLICIES AND DISCIPLINARY MEASURES

1. Anti-Ragging Policy
1.1 Ragging in any form—physical, verbal, or psychological—is strictly prohibited both inside and outside the university premises.
1.2 The University enforces a Zero Tolerance Policy towards ragging in compliance with Supreme Court directives and National Regulatory Guidelines.
1.3 Any student found guilty of ragging shall face immediate suspension, expulsion from the University, and criminal prosecution.

2. Hostel Regulations and Curfew
2.1 All residential students must return to their respective hostel blocks by 10:00 PM on weekdays and 10:30 PM on weekends.
2.2 Night-out permissions must be applied through the digital warden portal at least 24 hours in advance with explicit parental consent.
2.3 Possession or consumption of alcohol, narcotics, tobacco, or hazardous substances on campus is punishable by immediate expulsion and eviction.

3. Student Grievance Redressal
3.1 Students with academic or administrative grievances may submit a formal petition to the Student Grievance Committee.
3.2 All petitions shall be reviewed and adjudicated within fifteen (15) working days of receipt.
"""
    p1.insert_text((50, 60), text_p1, fontsize=11, fontname="helv")
    doc_conduct.save(str(output_dir / "Student_Code_of_Conduct.pdf"))
    doc_conduct.close()

    print(f"Generated sample regulation PDFs in: {output_dir}")

if __name__ == "__main__":
    import sys
    base_dir = Path(__file__).resolve().parent.parent
    sample_dir = base_dir / "sample_data"
    create_sample_pdfs(sample_dir)
