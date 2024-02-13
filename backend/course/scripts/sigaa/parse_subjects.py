from bs4 import BeautifulSoup
import requests
from course.models.models import Department, Subject
from django.db import IntegrityError

url = "https://sig.unb.br/sigaa/public/componentes/busca_componentes.jsf"


def get_ids_and_names():
    departamentos = {}
    response = requests.request("GET", url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    list_depto = html_soup.find(id="form:unidades")

    for depto in list_depto.find_all("option"):
        departamentos[depto["value"]] = depto.text

    departamentos.pop("0", None)
    return departamentos


def parse_subjects_from_department(department_sigaa_id, department):

    html_soup = request_department_subjects_page(
        {"department_sigaa_id": department_sigaa_id}
    )

    subjects = html_soup.select("tbody tr")
    # print(subjects)
    for subject in subjects:
        fields = subject.select("td")
        # Coleta os campos necessários para criação da matéria
        code, name, _, workload, link = fields
        subject_id = link.select_one("a")["onclick"].split(":")[4][1:7]

        try:
            Subject.objects.create(
                id=subject_id,
                code=code.text,
                department=department,
                name=name.text[:79],  # para materias com len >= 80
                credit=workload.text[:-1],  # Retira o h do final da string
            )
            print(f"Disciplina registrada com sucesso: {code.text}")
        except IntegrityError:
            print(f"Disciplina já existe na database : {code.text}")


def get_cookies():
    response = requests.request("GET", url)
    return response.headers["Set-Cookie"].split(" ")[0]


def get_request_data(url):
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")

    cookies = response.headers["Set-Cookie"].split(" ")[0]
    javax = html_soup.find("input", {"name": "javax.faces.ViewState"})["value"]

    data = {"javax": javax, "cookies": cookies}

    return data


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
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
    }

    response = requests.post(url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


# Esse parse tem a função de criar as disciplinas no banco de dados, é necessário que os departamentos já estejam criados
def run():
    departments = get_ids_and_names()
    for department_sigaa_id in departments:
        department_name = (
            departments[department_sigaa_id].split(" - ")[0].split(" (")[0]
        )
        try:
            print(f"Registrando disciplinas para: {department_name}")
            department_object = Department.objects.get(name=department_name)
            parse_subjects_from_department(department_sigaa_id, department_object)

        except Department.DoesNotExist:
            print(f"Departamento não possui disciplinas: {department_name}")
            continue
