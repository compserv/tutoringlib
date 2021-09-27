import json
import sys

def writeJSONtoFile(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def readJSONtoDict(file):
    with open(file, 'r') as f:
        return json.load(f)

#purely for readability, this is a one-line job
def mergeCourseNames(web, rails):
    return rails["courseName"]

def mergeTutors(web, rails):
    #add all hkn-web tutors + info
    webNames = {}
    for tutor in web["tutors"]:
        cache = {}
        for element in ["name", "timeSlots", "officePrefs", "adjacentPref", "numAssignments"]:
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
    for name in webNames.keys():
        if name in railNames:
            keys = railNames[name].keys()
            for key in keys:
                if key == "numAssignments" and webNames[name][key] != railNames[name][key]:
                    print(name, webNames[name][key], railNames[name][key])
                else:
                    webNames[name][key] = railNames[name][key]
        else:
            not_matched_rails.append(name)

    not_matched_web = []
    for name in railNames.keys():
        if not name in webNames:
            not_matched_web.append(name)

    mergedTutors = list(webNames.values())
    return mergedTutors, not_matched_rails, not_matched_web

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
            merge["courses"] = railsDict[key]["courses"] if key[0] != "Online" else [1] * len(railsDict[key]["courses"])
            merge["adjacentSlotIDs"] = webDict[key]["adjacentSlotIDs"]
            merge["sid"] = webDict[key]["sid"]
            mergedList.append(merge)
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
    outJSON["tutors"], notInRails, notInWeb = mergeTutors(webJSON, railsJSON)
    outJSON["slots"], errors = mergeSlots(webJSON, railsJSON)
    """ Uncomment or comment for error output
    print("Tutors exist in hkn-web but not in hkn-rails")
    print(notInRails)
    print("Tutors exist in hkn-rails but not in hkn-web")
    print(notInWeb)
    print("(Office, Hour, Day) entries in hkn-web but not in hkn-rails")
    print(errors)
    """
    writeJSONtoFile(outJSON, outfile)
