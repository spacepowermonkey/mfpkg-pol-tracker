import json
import os



from ..sources.congress.house import ClerkRecord



HOUSE_DATA = "/data/house.json"



def _save_record(record, path):
    with open(path, "w") as csvfile:
        csvfile.write("Member,Vote,Party,State,Profile")
        for vote in record.votes:
            row = ",".join([vote.member, vote.vote, vote.party, vote.state, vote.profile]) + "\n"
            csvfile.write(row)
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

    for entry in house_data:
        index_page += f"## Congress {entry.congress}-{entry.session} Record\n\n"
        index_page += f"This congress voted on the following issues:\n\n"
        index_page += "Roll | Issue | Question | Description | Time | Results\n"
        index_page += " --- | --- | --- | --- | --- | --- \n"

        for record in entry.records:
            index_page += f"{record.roll} | {record.info} | {record.question} | {record.description} | {record.time} | [\[CSV\]](votes/{entry.congress}-{entry.session}-{record.roll}.csv)\n"
            _save_record(record, f"/docs/votes/{entry.congress}-{entry.session}-{record.roll}.csv")
        
        index_page += "\n\n\n"
    
    with open("/docs/index.md", "w") as outfile:
        outfile.write(index_page)

    return
