import csv
import json
import os



from ..sources.congress.house import ClerkRecord



HOUSE_DATA = "/data/house.json"
WEB_PREFIX = "https://spacepowermonkey.com/mfpkg-pol-tracker/"



def _save_record(record, path):
    with open("/docs/" + path, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, ["Member", "Vote", "Party", "State", "Profile"])
        csvwriter.writeheader()
        for vote in record.votes:
            csvwriter.writerow({
                "Member": vote.member,
                "Vote": vote.vote,
                "Party": vote.party,
                "State": vote.state,
                "Profile": vote.profile,
            })
    return


def _save_index(index, path):
    with open("/docs/" + path, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, ["Roll", "Issue", "Question", "Description", "Time", "Results"])
        csvwriter.writeheader()
        for record in index.records:
            result_path = WEB_PREFIX + f"votes/{index.congress}-{index.session}-{record.roll}.csv"
            csvwriter.writerow({
                "Roll": record.roll,
                "Issue": record.info,
                "Question": record.question,
                "Description": record.description,
                "Time": record.time,
                "Results": result_path,
            })
    return

def _generate_index_page(index, path):
    index_page = "---\n"
    index_page += f"title: Congress {index.congress}-{index.session} Record\n"
    index_page += "layout: page\n"
    index_page += "---\n"
    index_page += "\n\n"
    index_page += f"This congress voted on the following issues:\n\n"
    index_page += "Roll | Issue | Question | Description | Time | Results\n"
    index_page += " --- | --- | --- | --- | --- | --- \n"

    for record in index.records:
        index_page += f"{record.roll} | {record.info} | {record.question} | {record.description} | {record.time} | [\[CSV\]](votes/{index.congress}-{index.session}-{record.roll}.csv)\n"
        _save_record(record, f"votes/{index.congress}-{index.session}-{record.roll}.csv")
    
    index_page += "\n"
    
    with open("/docs/" + path, "w") as outfile:
        outfile.write(index_page)
    return


def _save_people(index, path):
    with open("/docs/" + path, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, ["Name", "District", "Party", "Hometown", "SwearIn", "Ref"])
        csvwriter.writeheader()
        for person in index.people:
            csvwriter.writerow({
                "Name": person.name,
                "District": person.district,
                "Party": person.party,
                "Hometown": person.hometown,
                "SwearIn": person.swear_in,
                "Ref": person.ref,
            })
    return

def _generate_people_page(index, path):
    index_page = "---\n"
    index_page += f"title: Congress {index.congress}-{index.session} Record\n"
    index_page += "layout: page\n"
    index_page += "---\n"
    index_page += "\n\n"
    index_page += f"This congress voted on the following issues:\n\n"
    index_page += "Name | Party | District | Hometown | SwearIn | Ref\n"
    index_page += " --- | --- | --- | --- | --- | --- \n"

    for person in index.people:
        index_page += f"{person.name} | {person.party} | {person.district} | {person.hometown} | {person.swear_in} | {person.ref}\n"    
    index_page += "\n"
    
    with open("/docs/" + path, "w") as outfile:
        outfile.write(index_page)
    return



def run():
    with open(HOUSE_DATA) as datafile:
        config = json.load(datafile)
    os.makedirs("/docs/votes", exist_ok=True)
    os.makedirs("/docs/people", exist_ok=True)
    
    house_data = []
    for entry in config["sessions"]:
        session_record = ClerkRecord(entry["congress"], entry["session"])
        session_record.fetch()
        house_data.append(session_record)
    
    index_page = "---\n"
    index_page += "title: Politics Report\n"
    index_page += "layout: page\n"
    index_page += "---\n"
    index_page += "\n\n"

    index_page += "## List of Congress Sessions\n\n"
    index_page += "The following sessions are currently available. Download data as a [\[CSV\]](/index.csv)\n\n"
    index_page += "Congress | Session | Votes | People\n"
    index_page += "--- | --- | ---\n"

    with open("/docs/index.csv", "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, ["Congress", "Session", "Votes", "People"])
        csvwriter.writeheader()

        for entry in house_data:
            entry_index = f"votes/{entry.congress}-{entry.session}-index"
            entry_people = f"people/{entry.congress}-{entry.session}-members"
            index_page += f"{entry.congress} | {entry.session} | [\[View\]]({entry_index + '.html'}) [\[CSV\]]({entry_index + '.csv'}) | [\[View\]]({entry_people + '.html'}) [\[CSV\]]({entry_people + '.csv'})\n"
            _save_index(entry, entry_index + '.csv')
            _generate_index_page(entry, entry_index + '.md')
            _save_people(entry, entry_people + '.csv')
            _generate_people_page(entry, entry_people + '.md')

            csvwriter.writerow({
                "Congress": entry.congress,
                "Session": entry.session,
                "Votes": WEB_PREFIX + entry_index + '.csv',
                "People": WEB_PREFIX + entry_people + '.csv',
            })
        
    index_page += "\n"
    
    with open("/docs/index.md", "w") as outfile:
        outfile.write(index_page)

    return
