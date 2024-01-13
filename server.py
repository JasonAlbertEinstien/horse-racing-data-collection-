import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

class URLInput(BaseModel):
    link: str

app = FastAPI()

def scrape_data(number:str , data:str):
#    page = requests.get("https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx?RaceDate="+data+"&Racecourse=ST&RaceNo="+number)
    URL = "https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx?RaceDate="+ data +"&Racecourse=ST&RaceNo=" +number
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("div", {"class": "performance"}).table.tbody
    rows = table.find_all('tr')
    data = []
    data.append([])
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    write_csv(data , number)
    convert_to_excel()
    return data

def write_csv(data: list , item:int):
    with open('data'+str(item)+'.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def convert_to_excel():
    df = pd.read_csv('data.csv')
    df.to_excel('data.xlsx', index=False)

@app.post("/generate-csv/{number}/{date}")
def generate_csv(number:int , data:str):
    try:
        for i in range(5):
            scrape_data(f"{i+1}" , data)
        return {"message": "Excel file generated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-excel")
def download_excel():
    try:
        return FileResponse('data.xlsx', filename='data.xlsx')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
