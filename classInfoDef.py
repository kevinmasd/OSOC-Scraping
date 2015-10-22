import csv
import requests
import re
from bs4 import BeautifulSoup
from time import gmtime,  strftime

def classes_from_osoc(infotype, term="", dept=""):
	
	valid_term = ["FL", "SP", "SU"]
	while not (term in valid_term):
		term = input("Enter SU for Summer,  FL for Fall,  SP for Spring: ").upper()
	
	valid_dept_a_to_c = ["A, RESEC", "AEROSPC", "AFRICAM", "AFRKANS", "AGRCHM", "AHMA", "ALTAIC", "AMERSTD", "ANTHRO", "ARABIC", "ARCH", "ARMENI", "ART", "ASAMST", "ASIANST", "AST", "ASTRON", "BANGLA", "BIOENG", "BIOLOGY", "BIOPHY", "BOSCRSR", "BUDDSTD", "BULGARI", "BURMESE", "BUSADM", "CATALAN", "CELTIC", "CHEM", "CHICANO", "CHINESE", "CHMENG", "CIVENG", "CLASSIC", "COGSCI", "COLWRIT", "COMLIT", "COMPBIO", "COMPSCI", "CRITTH", "CRWRIT", "CUNEIF", "CYPLAN", "CZECH"]
	valid_dept_d_to_h = ["DANISH", "DATASCI", "DEMOG", "DESINV", "DEVENG", "DEVP", "DEVSTD", "DUTCH", "EAEURST", "EALANG", "ECON", "EDUC", "EE", "EECS", "EGYPT", "ELENG", "ENE, RES", "ENGIN", "ENGLISH", "ENVDES", "ENVECON", "ENVSCI", "EPS", "ESPM", "ETHGRP", "ETHSTD", "EURAST", "EUST", "EWMBA", "FILIPN", "FILM", "FINNISH", "FOLKLOR", "FRENCH", "GEOG", "GERMAN", "GMS", "GPP", "GREEK", "GSPDP", "GWS", "HEBREW", "HIN-URD", "HISTART", "HISTORY", "HMEDSCI", "HUNGARI"]
	valid_dept_i_to_o = ["IAS", "ICELAND", "ILA", "INDENG", "INFO", "INTEGBI", "IRANIAN", "ISF", "ITALIAN", "JAPAN", "JEWISH", "JOURN", "KHMER", "KOREAN", "L%26S", "LANPRO", "LATAMST", "LATIN", "LAW", "LDARCH", "LEGALST", "LGBT", "LINGUIS", "MALAY", "MATH", "MATSCI", "MBA", "MCELLBI", "MECENG", "MEDIAST", "MEDST", "MESTU", "MFE", "MILAFF", "MILSCI", "MONGOLN", "MUSIC", "NATAMST", "NATRES", "NAVSCI", "NESTUD", "NEUROSC", "NORWEGN", "NSE", "NUCENG", "NUSCTX", "NWMEDIA", "OPTOM"]
	valid_dept_p_to_y = ["PACS", "PBHLTH", "PERSIAN", "PHDBA", "PHILOS", "PHYSED", "PHYSICS", "PLANTBI", "POLECON", "POLISH", "POLSCI", "PORTUG", "PSYCH", "PUBPOL", "PUNJABI", "RELIGST", "RHETOR", "ROMANI", "RUSSIAN", "S, SEASN", "SANSKR", "SASIAN", "SCANDIN", "SCMATHE", "SEASIAN", "SEMITIC", "SLAVIC", "SOCIOL", "SOCWEL", "SPANISH", "STAT", "STS", "SWEDISH", "TAGALG", "TAMIL", "TELUGU", "THAI", "THEATER", "TIBETAN", "TURKISH", "UGIS", "VIETNMS", "VISSCI", "VISSTD", "XMBA", "YIDDISH"]
	valid_dept_others = ["ALL", "BIO", "CMPBIO", "CS", "L&S", "MALAY/I", "MCB", "UGBA", "BUS ADM"]
	# Abbreviations from http://registrar.berkeley.edu/?PageID=deptabb.html
	dept = input("Enter OSOC-Approved Department Abbreviation: ").upper()
	if dept == "ALL":
		dept = valid_dept_a_to_c+valid_dept_d_to_h+valid_dept_i_to_o+valid_dept_p_to_y
	while not (dept in valid_dept_a_to_c or dept in valid_dept_d_to_h or dept in valid_dept_i_to_o or dept in valid_dept_p_to_y or dept in valid_dept_others):
	
	
	
	dept = ["L%26S" if department=="L&S" else department for department in dept[:]]
	listing = []
	for department in set(dept):
		current = 1
		next_page = True
		print(department)
		while next_page:
			url = "http://osoc.berkeley.edu/OSOC/osoc?p_term="+term+"&p_dept="+department+"&p_start_row="+str(current)
			r  = requests.get(url)
			r.raise_for_status()
			soup = BeautifulSoup(r.text,  "lxml")
			data = soup.find_all(['b', 'tt'])
			listing.append(infotype(data))
			if not ("next results" in str(data[0])):
				next_page = False
			current += 100
	
	date_time = strftime("%Y%m%d-%H%M%S-",  gmtime())
	if len(dept) > 2:
		dept = ["Some"]
	file_name = "classes"+date_time+"-"+term+"-"+dept[0]+".csv"
	with open(file_name, "w") as csvwrite:
		a = csv.writer(csvwrite,  delimiter=',')
		for i in range(0, len(listing)):
			a.writerows(listing[i])

def info_general(data):
	"""
	index (5 Start) => Course:
	+1 => [Department] [Course] [Primary OR Secondary] [Section Number] [Type]
	"(?:[A-Z]+ *)*(?:H|C|R|N|W)*\d{1,3}(?:AC|BC|[A-Z])? (?:P|S) (?:\d{3}|1-\d+) (?:LEC|SEM|DIS|LAB|SLF|GRP|VOL|IND|TUT|COL|WBL|SUP)"
	Note: For Summer,  LEC classes have additional info
	
	+2 => Course Title:
	+3 to +5 => [Course Title]
	"(?:[A-Z]+[a-z]* *)* ?"

	+6 => Location:
	+7 => [Days of Week] [Time], [Location]
	"(?:^(?:M|Tu|W|Th|F|SA|Su|T)+ \d{0,4}-\d{0,4}(?:P|A), (?:\d{1,4} )*\D*$|TBA|CANCELLED|UNSCHED NOFACILITY)"

	+8 => Instructor:
	+9 => [Last Name] [First Initial] [Middle Initial]
	"(?:^(?:[A-Z]*-*\s*)*[A-Z]+(?:, )?[A-Z](?: [A-Z])?,? ?[A-Z]+$|^[A-Z]*(?: [A-Z]*)*$)"

	+10 => Status/Last Changed:
	+11 => [CANCELLED OR ADDED OR OR UPDATED]: [Date]
	"(?:^(?:UPDATED|ADDED|CANCELLED): \d{2}/\d{2}/\d{2}$| )"

	+12 => Course Control Number:
	+13 => [CCN] OR "SEE DEPT"
	"(?:\d{5}|SEE DEPT)"

	+14 => Units/Credit:
	+15 => [Unit Value(s)]
	"^\d(?:-\d)?(?:: [A-Z][\S]*)*$"

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
		if ("Course:" in str(info)):
			rows.append(data[index].text)
			listing.append(rows)
	return listing

def info_class_size(data):
	"""
	index (5 Start) => Course:
	+1 => [Department] [Course] [Type] [Section] [Type]
	+9 => [Last Name] [First Initial] [Middle Initial]
	+22 => Enrollment on [Date]
	+23 => Limit:[] Enrolled:[] Waitlist:[] Avail Seats:[]
	"""
	listing = []
	for index, info in enumerate(data):
		rows = []
		if ("Course:" in str(info)):
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
	index (5 Start) => Course:
	+1 => [Department] [Course] [{P, S}] [Section] [{LEC, SEM, DIS, LAB, SLF, GRP, VOL, IND}]
	Note: For Summer,  LEC classes have additional info
	+2 => Course Title:
	+3 to +5 => [Name]
	+6 => Location:
	+7 => [Days] [Time],  [Location]
	+8 => Instructor:
	+9 => [Last,  First]
	+10 => Status/Last Changed:
	+11 => [Status] OR [Date]
	+12 => Course Control Number:
	+13 => [CCN]
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
		if ("Course:" in str(info)):
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
			rows.append(" ".join(data[index+23].text.strip().split()))
			listing.append(rows)
	return listing

def do():
	classes_from_osoc(info_plain_total,"SP","ALL")