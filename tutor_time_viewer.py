import json

with open('sandbox/hknrails_output.json') as f:
    data_json = json.load(f)

def show_tutor_slots(tutor_name):
    tutor = [d for d in data_json["tutors"] if d["name"].startswith(tutor_name)][0]

    timeslots = tutor["timeSlots"]
    officepref = tutor["officePrefs"]

    slots = data_json["slots"]

    for i, (t, o) in enumerate(zip(timeslots, officepref)):
        if t > 0 and o >= 0:
            curr_slot = slots[i]
            assert curr_slot["sid"] == i, "sid != i, {} != {}".format(curr_slot["sid"], i)
            print("Time Pref:", t)
            print("Office Pref:", o)
            print(curr_slot)
            print()
