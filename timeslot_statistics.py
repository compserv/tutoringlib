import json
import sys

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print("Error - please specify one file name with the combined JSON")

with open(filename) as f:
    data_json = json.load(f)

slot_stats = {}

def process_tutor_slots(tutor):
    timeslots = tutor["timeSlots"]
    officepref = tutor["officePrefs"]

    slots = data_json["slots"]

    for i, (t, o) in enumerate(zip(timeslots, officepref)):
        if t > 0 and o >= 0:
            curr_slot = slots[i]
            assert curr_slot["sid"] == i, "sid != i, {} != {}".format(curr_slot["sid"], i)
            # print("Time Pref:", t)
            # print("Office Pref:", o)
            # print(curr_slot)
            # print()
            slot_stats[curr_slot["sid"]] = slot_stats.get(curr_slot["sid"], 0) + 1

for tutor in data_json["tutors"]:
    process_tutor_slots(tutor)

for slot in data_json["slots"]:
    print(slot_stats.get(slot["sid"], -1), slot["office"], slot["day"], slot["hour"])
