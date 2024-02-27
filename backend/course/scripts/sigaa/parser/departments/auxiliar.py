from bs4 import BeautifulSoup
import requests


def extract_course_data(col):
    data = {
        "course_name": (
            col[0].string.replace("\n", "").replace("\t", "").capitalize().strip()
        ),
        "academic_degree": (
            col[1].string.replace("\n", "").replace("\t", "").capitalize().strip()
        ),
        "shift": (
            col[2].string.replace("\n", "").replace("\t", "").capitalize().strip()[0]
        ),
        "mode": (
            col[4].string.replace("\n", "").replace("\t", "").capitalize().strip()
        ),
        "coordenador": (
            col[5].string.replace("\n", "").replace("\t", "")
            if col[5].string != None
            else None
        ),
        "id": (col[6].find("a")["href"][14:20]),
    }
    return data
