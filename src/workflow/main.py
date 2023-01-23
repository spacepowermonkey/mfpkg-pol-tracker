import json
import os



from ..sources.congress.house import ClerkRecord



HOUSE_DATA = "/data/house.json"
WEB_PREFIX = "https://spacepowermonkey.com/mfpkg-pol-tracker/"



def _save_record(record, path):
    with open("/docs/" + path, "w") as csvfile:
        csvfile.write("Member,Vote,Party,State,Profile")
        for vote in record.votes:
            row = ",".join([vote.member, vote.vote, vote.party, vote.state, vote.profile]) + "\n"
            csvfile.write(row)
    return


def _save_index(index, path):
    with open("/docs/" + path, "w") as csvfile:
        csvfile.write("Roll,Issue,Question,Description,Time,Results")
        for record in index.records:
            result_path = WEB_PREFIX + f"votes/{index.congress}-{index.session}-{record.roll}.csv"
            row = ",".join([str(record.roll), str(record.info), str(record.question), str(record.description), str(record.time), result_path])
            csvfile.write(row)
    return

def _generate_page(index, path):
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



def run():
    with open(HOUSE_DATA) as datafile:
        config = json.load(datafile)
    os.makedirs("/docs/votes", exist_ok=True)
    
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
    index_page += "The following sessions are currently available:\n\n"
    index_page += "Congress | Session | Links\n"
    index_page += "--- | --- | ---\n"

    for entry in house_data:
        entry_index = f"votes/{entry.congress}-{entry.session}-index"
        index_page += f"{entry.congress} | {entry.session} | [\[View\]]({entry_index + '.html'} [\[CSV\]]({entry_index + '.csv'})\n"
        _save_index(entry, entry_index + '.csv')
        _generate_page(entry, entry_index + '.md')
        
    index_page += "\n"
    
    with open("/docs/index.md", "w") as outfile:
        outfile.write(index_page)

    return
