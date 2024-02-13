from bs4 import BeautifulSoup
import requests
from course.models.models import Department
from django.db import IntegrityError

url = "https://sig.unb.br/sigaa/public/componentes/busca_componentes.jsf"


def parse_department(department_sigaa_id, department_name):

    html_soup = request_department_subjects_page(
        {"department_sigaa_id": department_sigaa_id}
    )

    first_subject = html_soup.select("tbody tr td")

    if first_subject:
        subjects_code = first_subject[0].text
        department_initials = "".join(filter(str.isalpha, subjects_code))
        try:
            Department.objects.create(
                name=department_name, initials=department_initials
            )
            print(f"Departamento foi registrado com sucesso: {department_name}")
        except:
            print(f"Não foi possível criar o departamento: {department_name}")
    else:
        print(f"O departamento não possui disciplina   : {department_name}")


def get_cookies():
    response = requests.request("GET", url)
    return response.headers["Set-Cookie"].split(" ")[0]


def get_ids_and_names():
    departamentos = {}
    response = requests.request("GET", url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    list_depto = html_soup.find(id="form:unidades")

    for depto in list_depto.find_all("option"):
        departamentos[depto["value"]] = depto.text

    departamentos.pop("0", None)
    return departamentos


def get_request_data(url):
    response = requests.request("GET", url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return {
        "cookies": response.headers["Set-Cookie"].split(" ")[0],
        "javax": html_soup.find("input", {"name": "javax.faces.ViewState"})["value"],
    }


def request_department_subjects_page(payload_data):
    url = "https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf"
    request_data = get_request_data(url)
    payload = {
        "form": "form",
        "form:nivel": "G",
        "form:checkTipo": "on",
        "form:tipo": 2,
        "form:checkUnidade": "on",
        "form:unidades": payload_data["department_sigaa_id"],
        "form:btnBuscarComponentes": "Buscar Componentes",
        "javax.faces.ViewState": request_data["javax"],
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
        "Host": "sigaa.unb.br",
        "Origin": "https://sigaa.unb.br",
        "Referer": url,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chro",
    }

    response = requests.post(url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def run():
    departments = get_ids_and_names()
    for department_sigaa_id in departments:
        department_name = (
            departments[department_sigaa_id].split(" - ")[0].split(" (")[0]
        )
        if "PROGRAMA DE PÓS-GRADUAÇÃO" in department_name:
            print(f"O departamento será desconsiderado     : {department_name}")
            continue
        try:
            Department.objects.get(name=department_name)
            print(f"O departamento já existe na database   : {department_name}")
        except Department.DoesNotExist:
            parse_department(department_sigaa_id, department_name)

            continue
