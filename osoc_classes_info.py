import csv
import requests
import re
from bs4 import BeautifulSoup
from time import gmtime, strftime

def osoc_classes_info(infotype, term="", dept=""):
    """
    1.Checking Valid Terms
    2.Checking Valid Departments
    3.Editing for Special Cases (All, L&S, etc)
    4.Scraping Data from OSOC
    5.Formatting Data
    """
    while not term in ["FL", "SP", "SU"]:
        term = input("Enter SU for Summer,  FL for Fall,  SP for Spring: ").upper()

    if isinstance(dept, list):
        dept = [item for item in dept if dept_usage(1, item)]
    else:
        while not dept_usage(1, dept):
            dept = input("Enter OSOC-Approved Department Abbreviation: ").upper()

    if "ALL" in dept:
        dept = dept_usage(0, dept)
    else:
        dept_replace, dept_equiv = dept_usage(-1)
        for index in range(0, len(dept_replace)):
            if dept_replace[index] in dept:
                dept = [dept_equiv[index] if department == dept_equiv[index] else department for department in dept[:]]

    listing = []
    for department in set(dept):
        current = 1
        next_page = True
        print(department)
        while next_page:
            url = "http://osoc.berkeley.edu/OSOC/osoc?p_term="+term+"&p_dept="+department+"&p_start_row="+str(current)
            request = requests.get(url)
            request.raise_for_status()
            soup = BeautifulSoup(request.text, "lxml")
            data = soup.find_all(['b', 'tt'])
            listing.append(infotype(data))
            if not "next results" in str(data[0]):
                next_page = False
            current += 100

    if len(dept) > 2:
        dept = ["Some"]
    file_name = "classes" + strftime("%Y%m%d-%H%M%S-", gmtime()) + "-" + term + "-" + dept[0] + ".csv"
    with open(file_name, "w") as csvwrite:
        output = csv.writer(csvwrite, delimiter=',')
        for i in range(0, len(listing)):
            output.writerows(listing[i])

def dept_usage(usage, dept=""):
    """
    Usage = 1? Checks if Department is Valid
    Usage = 0? Returns All Valid Departments
    Usage = -1? Returns Redundants Department Names and Equivalences
    Abbreviations from http://registrar.berkeley.edu/?PageID=deptabb.html
    """
    dept_a = ["A, RESEC", "AEROSPC", "AFRICAM", "AFRKANS", "AGRCHM", "AHMA", "ALTAIC", "AMERSTD", "ANTHRO", "ARABIC", "ARCH", "ARMENI", "ART", "ASAMST", "ASIANST", "AST", "ASTRON"]
    dept_b = ["BANGLA", "BIOENG", "BIOLOGY", "BIOPHY", "BOSCRSR", "BUDDSTD", "BULGARI", "BURMESE", "BUSADM"]
    dept_c = ["CATALAN", "CELTIC", "CHEM", "CHICANO", "CHINESE", "CHMENG", "CIVENG", "CLASSIC", "COGSCI", "COLWRIT", "COMLIT", "COMPBIO", "COMPSCI", "CRITTH", "CRWRIT", "CUNEIF", "CYPLAN", "CZECH"]
    dept_d = ["DANISH", "DATASCI", "DEMOG", "DESINV", "DEVENG", "DEVP", "DEVSTD", "DUTCH"]
    dept_e = ["EAEURST", "EALANG", "ECON", "EDUC", "EE", "EECS", "EGYPT", "ELENG", "ENE, RES", "ENGIN", "ENGLISH", "ENVDES", "ENVECON", "ENVSCI", "EPS", "ESPM", "ETHGRP", "ETHSTD", "EURAST", "EUST", "EWMBA"]
    dept_fh = ["FILIPN", "FILM", "FINNISH", "FOLKLOR", "FRENCH", "GEOG", "GERMAN", "GMS", "GPP", "GREEK", "GSPDP", "GWS", "HEBREW", "HIN-URD", "HISTART", "HISTORY", "HMEDSCI", "HUNGARI"]
    dept_ik = ["IAS", "ICELAND", "ILA", "INDENG", "INFO", "INTEGBI", "IRANIAN", "ISF", "ITALIAN", "JAPAN", "JEWISH", "JOURN", "KHMER", "KOREAN"]
    dept_lm = ["L%26S", "LANPRO", "LATAMST", "LATIN", "LAW", "LDARCH", "LEGALST", "LGBT", "LINGUIS", "MALAY", "MATH", "MATSCI", "MBA", "MCELLBI", "MECENG", "MEDIAST", "MEDST", "MESTU", "MFE", "MILAFF", "MILSCI", "MONGOLN", "MUSIC"]
    dept_no = ["NATAMST", "NATRES", "NAVSCI", "NESTUD", "NEUROSC", "NORWEGN", "NSE", "NUCENG", "NUSCTX", "NWMEDIA", "OPTOM"]
    dept_p = ["PACS", "PBHLTH", "PERSIAN", "PHDBA", "PHILOS", "PHYSED", "PHYSICS", "PLANTBI", "POLECON", "POLISH", "POLSCI", "PORTUG", "PSYCH", "PUBPOL", "PUNJABI"]
    dept_rs = ["RELIGST", "RHETOR", "ROMANI", "RUSSIAN", "S, SEASN", "SANSKR", "SASIAN", "SCANDIN", "SCMATHE", "SEASIAN", "SEMITIC", "SLAVIC", "SOCIOL", "SOCWEL", "SPANISH", "STAT", "STS", "SWEDISH"]
    dept_ty = ["TAGALG", "TAMIL", "TELUGU", "THAI", "THEATER", "TIBETAN", "TURKISH", "UGIS", "VIETNMS", "VISSCI", "VISSTD", "XMBA", "YIDDISH"]
    dept_others = ["BIO", "BUS ADM", "CMPBIO", "CS", "L&S", "MALAY/I", "MCB", "ME", "POLI SCI", "POLISCI", "UGBA"]
    dept_equiv = ["BIOLOGY", "BUSADM", "COMPBIO", "COMPSCI", "L%26S", "MALAY", "MCELLBI", "MECENG", "POLSCI", "BUSADM"]
    if usage == 1:
        return dept in dept_a + dept_b + dept_c + dept_d + dept_e + dept_fh + dept_ik + dept_lm + dept_no + dept_p + dept_rs + dept_ty + dept_others+["ALL"]
    elif usage == 0:
        return dept_a + dept_b + dept_c + dept_d + dept_e + dept_fh + dept_ik + dept_lm + dept_no + dept_p + dept_rs + dept_ty
    else:
        return dept_others, dept_equiv

def info_general(data):
    """
    index (5 Start) => Course:
    +1 => [Department] [Course] [Primary OR Secondary Section] [Section Number] [Type]
    Note: For Summer, Primary classes have additional info

    +2 => Course Title:
    +3 to +5 => [Course Title]
    +6 => Location:
    +7 => [Days of Week] [Time], [Location]
    +8 => Instructor:
    +9 => [Last Name] [First Initial] [Middle Initial]
    +10 => Status/Last Changed:
    +11 => [CANCELLED OR ADDED OR OR UPDATED]: [Date]
    +12 => Course Control Number:
    +13 => [CCN] OR "SEE DEPT"
    +14 => Units/Credit:
    +15 => [Unit Value(s)]

    For Fall, Spring
        +16 => Final Exam Group:
        +17 => [Group]
        +18 => Restrictions:
        +19 => [Varies]

    For Summer
        +16 => Session Dates:
        +17 => [Start Date]-[Final Date]
        +18 => Summer Fees:
        +19 => UC Undergraduate $[Amount].00,  UC Graduate $[Amount].00,  Visiting $[Amount].00

    +20 => Note:
    +21 => [Requirements,  Other Name,  Other Location,  Other Instructors]
    +22 => Enrollment on [Date]
    +23 => Limit:[] Enrolled:[] Waitlist:[] Avail Seats:[]
    """
    listing = []
    for index, info in enumerate(data):
        rows = []
        if "Course:" in str(info):
            rows.append(data[index].text)
            listing.append(rows)
    return listing

def info_class_size(data):
    """
    +1 => [Department] [Course] [Type] [Section] [Type]
    +9 => [Last Name] [First Initial] [Middle Initial]
    +22 => Enrollment on [Date]
    +23 => Limit:[] Enrolled:[] Waitlist:[] Avail Seats:[]
    """
    listing = []
    for index, info in enumerate(data):
        rows = []
        if "Course:" in str(info):
            class_number = str(data[index+1].text)
            if "course" in class_number:
                rows.append(class_number[:len(class_number)-17])
            else:
                rows.append(class_number[:len(class_number)-1])
            teacher = str(data[index+9].text)
            if not teacher:
                teacher = "UNKNOWN"
            rows.append(teacher)
            date_data = str(data[index+22].text)
            rows.append(date_data[14:(len(date_data)-2)])
            seat_data = str(data[index+23].text)
            if "SEE" in seat_data:
                rows.append("NA")
                rows.append("NA")
                rows.append("NA")
                rows.append("NA")
            else:
                rows.append(seat_data[6:seat_data.find("Enrolled")-1])
                rows.append(seat_data[seat_data.find("Enrolled")+9:seat_data.find("Waitlist")-1])
                rows.append(seat_data[seat_data.find("Waitlist")+9:seat_data.find("Avail")-1])
                rows.append(seat_data[seat_data.find("Avail")+12:len(seat_data)-1])
            listing.append(rows)
    return listing

def info_plain_total(data):
    """
    +1 => [Department] [Course] [{P, S}] [Section] [{LEC, SEM, DIS, LAB, SLF, GRP, VOL, IND}]
    +3 => [Name]
    +7 => [Days] [Time],  [Location]
    +9 => [Last,  First]
    +11 => [Status] OR [Date]
    +13 => [CCN]
    +15 => [Unit Value(s)]

    For Fall, Spring
        +17 => [Group]
        +19 => [Varies]

    For Summer
        +17 => [Start Date]-[Final Date]
        +19 => UC Undergraduate $[Amount].00,  UC Graduate $[Amount].00,  Visiting $[Amount].00

    +21 => [Requirements,  Other Name,  Other Location,  Other Instructors]
    +22 => Enrollment on [Date]
    +23 => Limit:[] Enrolled:[] Waitlist:[] Avail Seats:[]
    """
    listing = []
    for index, info in enumerate(data):
        rows = []
        if "Course:" in str(info):
            rows.append(" ".join(data[index+1].text.strip().split()))
            rows.append(" ".join(data[index+3].text.strip().split()))
            rows.append(" ".join(data[index+7].text.strip().split()))
            rows.append(" ".join(data[index+9].text.strip().split()))
            rows.append(" ".join(data[index+11].text.strip().split()))
            rows.append(" ".join(data[index+13].text.strip().split()))
            rows.append(" ".join(data[index+15].text.strip().split()))
            rows.append(" ".join(data[index+17].text.strip().split()))
            rows.append(" ".join(data[index+19].text.strip().split()))
            rows.append(" ".join(data[index+21].text.strip().split()).replace("&nbsp", ""))
            rows.append(str(data[index+22].text)[14:(len(str(data[index+22].text))-2)])
            rows.append(" ".join(data[index+23].text.strip().split()))
            listing.append(rows)
    return listing

def regex_info(testing, info=""):
	"""
	Note: These Patterns may not match correctly due to unique edge cases.
	"""
    if info == 1:
        truthy = re.match(r"([A-Z,'/\-.]+ *)*\d{1,3}(AC|BC|TA|[A-Z]{1,2})? (P|S) (\d{3}|\d+-\d+|\d{2}[A-Z]|[A-Z]\d{2}) (DIS|LEC|LAB|SEM|IND|GRP|FLD|STD|REC|VOL|TUT|COL|WBL|SLF|WOR|SES|INT|SUP|CLC|WBD|CON|REA)", testing)
    elif info == 7:
        truthy = re.match(r"((M|Tu|W|Th|F|SA|Su|T)+ \d{0,4}-\d{0,4}(P|A),( ([A-Z]{0,2}\d{1,4}[A-Z]{0,2} )*\D*)?|UNSCHED\S*|TBA|CANCELLED|NO FACILITY)", testing)
    elif info == 9:
        truthy = re.match(r"(([A-Z]*-*\s*)*[A-Z']+(, )?[A-Z]( [A-Z])?,? ?[A-Z]+|[A-Z]*( [A-Z]*)*)", testing)
    elif info == 11:
        truthy = re.match(r"((UPDATED|ADDED|CANCELLED): \d{2}/\d{2}/\d{2})", testing)
    elif info == 13:
        truthy = re.match(r"(\d{5}|SEE DEPT|SEE NOTE)", testing)
    elif info == 15:
        truthy = re.match(r"(\.?\d(-\d)?(: [A-Z][\S]*)*|: SU)", testing)
    elif info == 23:
        truthy = re.match(r"(Limit:\d{1,4} Enrolled:\d{1,4} Waitlist:\d{1,3} Avail Seats:\d{1,4}|SEE DEPT|See primary section for enrollment data\.)", testing)
    else:
        truthy = False
    if testing in [None, ""]:
        truthy = True
    return bool(truthy)

def info_regex(data):
    """
    Provides a Check of Above regex_info Function
    """
    listing = []
    for index, info in enumerate(data):
        rows = []
        if "Course:" in str(info):
            rows.append(" ".join(data[index+1].text.strip().split()))
            rows.append(regex_info(" ".join(data[index+1].text.strip().split()), 1))
            rows.append(" ".join(data[index+23].text.strip().split()))
            rows.append(regex_info(" ".join(data[index+23].text.strip().split()), 23))
            listing.append(rows)
    return listing