import requests as req
import json
from datetime import datetime, timedelta

from src.models import Record
from config import BASEURL, TOKEN, APP 

def fetchRecords(email,sDate:str=datetime.today().strftime("%Y-%m-%d"),eDate:str=(datetime.today()+timedelta(days=7)).strftime("%Y-%m-%d"), limit:int = None):
    url=BASEURL+f"/records.json?totalCount=true&app={APP}"
    headers={
        'X-Cybozu-API-Token':TOKEN
    }
    query="&query="
    # Event date greater than sDate
    query+= f'日付>"{sDate}" '

    # Event date less than eDate
    query+= f'and 日付<"{eDate}" '

    # Event for User email, if no email return all records within dates
    if email:
        query += f'and 氏名 in ("{email}") '

    # limit number of records by limit
    if limit:
        query += f"limit {limit}"

    resp=req.get(url,headers=headers, params=query)
    if resp.status_code != 200:
        return {"error":resp.status_code, "message":resp.text}
    resp=json.loads(resp.content.decode())
    totalCount = resp['totalCount']
    records=list(map(Record,resp['records']))
    return {"count":totalCount, "records":records}
