import bs4
import dataclasses
import json
import re
import requests



CLERK_URL = "https://clerk.house.gov"

VOTE_URL_BASE = f"{CLERK_URL}/Votes/MemberVotes"
VOTE_PARAMS = "?CongressNum={congressNum}&Session={session}"

MEMBER_URL_BASE = f"{CLERK_URL}/Members/"

SESSIONS = ["", "1st", "2nd"]



@dataclasses.dataclass
class VoteEntry:
    member : str
    vote : str
    party : str
    state : str
    profile : str



class VoteRecord(object):
    PATTERN_ROLL_CALL = re.compile("Roll Call (\d+)")

    def __init__(self):
        self.session = None
        self.roll = None
        self.info = None
        self.time = None

        self.question = None
        self.description = None

        self.votes = []
        return


class ClerkRecord(object):
    def __init__(self, congress, session):
        self.congress = congress
        self.session = session

        self.records = []

        return
    
    def fetch(self):
        listings = []
        listings = self._fetch_listing()
        for vote_stub in listings:
            self._fetch_vote(vote_stub)        
        return


    def _fetch_listing(self):
        session_params = VOTE_PARAMS.format(**{
            "congressNum": self.congress,
            "session": SESSIONS[self.session]
        })
        session_first_url = VOTE_URL_BASE + session_params

        listings = []
        query_urls = [session_first_url]
        for url in query_urls:
            response = requests.get(url)
            response.raise_for_status()

            page_html = response.text
            page_soup = bs4.BeautifulSoup(page_html, features="html.parser")

            headings = page_soup.find_all("div", "roll-call-first-col")
            for heading in headings:
                listings.append( heading.find("a")["href"] )
            
            next_link = page_soup.find("a", attrs={"aria-label":"Next"})
            if next_link is not None:
                next_url = next_link["data-action"][:-2]
                next_url.replace("&amp;", "&")
                query_urls.append(CLERK_URL + next_url)
        
        return listings


    def _fetch_vote(self, vote_stub):
        url = CLERK_URL + vote_stub
        record = VoteRecord()

        response = requests.get(url)
        response.raise_for_status()

        page_html = response.text
        page_soup = bs4.BeautifulSoup(page_html, features="html.parser")

        vote_info = page_soup.find("h1", id="pageDetail").text.strip()
        vote_details = page_soup.find("div", "role-call-vote")

        vote_info = vote_info.split("|", maxsplit=1)
        record.roll = int( VoteRecord.PATTERN_ROLL_CALL.match( vote_info[0].strip() ).group(1) )
        if len(vote_info) > 1:
            record.info = vote_info[1].strip()

        vote_timing = vote_details.find("div", "first-row heading").text.split("|", maxsplit=1)
        record.time = vote_timing[0].strip()
        record.session = vote_timing[1].strip()

        record.question = vote_details.find("p", "roll-call-first-row").text.split(":", maxsplit=1)[1]
        record.description = vote_details.find("p", "roll-call-description").text.strip()

        vote_table = page_soup.find("tbody", id="member-votes")
        if vote_table is not None:
            vote_rows = vote_table.find_all("tr")[:-1]
            
            for row in vote_rows:
                profile = row.find("a")["href"]
                name = row.find_all("td", attrs={"data-label":"member",})[1].text
                party = row.find("td", attrs={"data-label":"party"}).text
                vote = row.find("td", attrs={"data-label":"vote"}).text
                state = row.find("td", attrs={"data-label":"state", "class":"visible-xs"}).text

                record.votes.append( VoteEntry(name, vote, party, state, profile))
        
        self.records.append( record )
        return


    def fetch_person(self, reference):
        # Get everything from member detail view
        return
