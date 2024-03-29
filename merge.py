import json
import sys

def writeJSONtoFile(data, file):
    with open(file, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def readJSONtoDict(file):
    with open(file, 'r', encoding='utf8') as f:
        return json.load(f)

EXEMPTED_NAMES = [] # Place hkn-rails names of people who are exempted

#purely for readability, this is a one-line job
def mergeCourseNames(web, rails):
    return rails["courseName"]

def mergeTutors(web, rails):
    #add all hkn-web tutors + info
    webNames = {}
    empty_timeslots_onlyinhknweb = set()
    for tutor in web["tutors"]:
        cache = {}
        for element in ["name", "timeSlots", "officePrefs", "adjacentPref", "numAssignments"]:
            if element == "timeSlots":
                total_sum = sum(abs(number) for number in tutor["timeSlots"])
                if total_sum == 0:
                    empty_timeslots_onlyinhknweb.add(tutor["name"])
            cache[element] = tutor[element]
        webNames[cache["name"]] = cache

    #add all hkn-rails tutors + info
    railNames = {}
    for tutor in rails["tutors"]:
        cache = {}
        for element in ["name", "tid", "courses", "numAssignments"]:
            cache[element] = tutor[element]
        railNames[cache["name"]] = cache

    not_matched_rails = []
    assignment_mismatches = []
    for name in webNames.keys():
        if name in railNames:
            keys = railNames[name].keys()
            for key in keys:
                if key == "numAssignments" and webNames[name][key] != railNames[name][key]:
                    assignment_mismatches.append((name, webNames[name][key], railNames[name][key]))
                else:
                    webNames[name][key] = railNames[name][key]
        else:
            not_matched_rails.append(name)
            if name in empty_timeslots_onlyinhknweb:
                empty_timeslots_onlyinhknweb.remove(name)

    not_matched_web = []
    for name in railNames.keys():
        if not name in webNames:
            not_matched_web.append(name)
    
    if True:
        for name in not_matched_rails:
            if name in webNames:
                del webNames[name]
    
    for exempt_name in EXEMPTED_NAMES:
        del webNames[exempt_name]
        if exempt_name in empty_timeslots_onlyinhknweb:
            empty_timeslots_onlyinhknweb.remove(exempt_name)
        print("Exempted", exempt_name)

    mergedTutors = list(webNames.values())
    return mergedTutors, not_matched_rails, not_matched_web, empty_timeslots_onlyinhknweb, assignment_mismatches

SPECIAL_DAY_CONVERSION = {"Tuesday" : "Tues", "Thursday" : "Thus"}

def shorten_day_of_week(day_of_week):
    return SPECIAL_DAY_CONVERSION.get(day_of_week, day_of_week[:3])

def hash_rails_element(element):
    return (element["office"], element["hour"], shorten_day_of_week(element["day"]))

def hash_web_element(element):
    return (element["office"].replace("Hybrid/", ""), element["hour"], element["day"])

def mergeSlots(web, rails):
    #create dictionary for both web and rails that maps the tuple
    # (office, hour, day) to the corresponding data in each database
    webDict = {}
    for element in web["slots"]:
        cache = {}
        for key in element:
            if key not in ["office", "hour", "day"]:
                cache[key] = element[key]
        webDict[hash_web_element(element)] = cache

    railsDict = {}
    for element in rails["slots"]:
        cache = {}
        for key in element:
            if key not in ["office", "hour", "day"]:
                cache[key] = element[key]
        railsDict[hash_rails_element(element)] = cache

    #map web slot ids to rails slot ids
    webIDtorailsID = {}
    for key in webDict:
        webID = webDict[key]["sid"]
        if key in railsDict:
            railsID = railsDict[key]["sid"]
            webIDtorailsID[webID] = railsID

    mergedList = []
    web_errors = []
    for key in webDict:
        if key in railsDict:
            merge = {}
            merge["hour"] = key[1]
            merge["name"] = railsDict[key]["name"]
            merge["day"] = key[2]
            merge["office"] = key[0] #webDict[key]["office"]
            merge["courses"] = railsDict[key]["courses"]
            merge["adjacentSlotIDs"] = webDict[key]["adjacentSlotIDs"] if key[0] != "Online" else [1] * len(webDict[key]["adjacentSlotIDs"])
            merge["sid"] = webDict[key]["sid"]
            mergedList += [merge]
        else:
            web_errors.append(key)
    return mergedList, web_errors

if __name__ == "__main__":
    if len(sys.argv) == 1:
        outfile = "DESTINATION_NAME.json"
        railsfile = "hkn-rails-tutoring.json"
        webfile = "hknweb-tutoring.json"
    elif len(sys.argv) == 4:
        outfile = sys.argv[3]
        railsfile = sys.argv[2]
        webfile = sys.argv[1]
    else:
        print("Error - please specify three file names in order of web JSON, rails JSON, and destination JSON")

    webJSON = readJSONtoDict(webfile)
    railsJSON = readJSONtoDict(railsfile)
    outJSON = {}
    outJSON["courseName"] = mergeCourseNames(webJSON, railsJSON)
    outJSON["tutors"], notInRails, notInWeb, empty_timeslots_onlyinhknweb, assignment_mismatches = mergeTutors(webJSON, railsJSON)
    outJSON["slots"], errors = mergeSlots(webJSON, railsJSON)
    # """ Uncomment or comment for error output
    print("Assignment mismatches (name, hknweb reported hours, hkn-rails position hours)")
    for mismatch in assignment_mismatches:
        print(" ".join(str(m) for m in mismatch))
    print("----------------")
    print("Tutors exist in hkn-web but not in hkn-rails")
    print(notInRails)
    print("----------------")
    print("Tutors exist in hkn-rails but not in hkn-web")
    print(notInWeb)
    print("----------------")
    print("(Office, Hour, Day) entries in hkn-web but not in hkn-rails")
    print(errors)
    print("----------------")
    print("Empty TimeSlot Preferences AND in hkn-rails:")
    print(empty_timeslots_onlyinhknweb)
    # """
    writeJSONtoFile(outJSON, outfile)
