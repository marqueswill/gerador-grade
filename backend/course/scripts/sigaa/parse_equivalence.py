from bs4 import BeautifulSoup
import requests
from course.models.models import Equivalence, PreRequisiteSet, Subject, CoRequisite


def parse_equivalence(subject_code, subject_id):

    html_soup = request_subject_page({"subject_id": subject_id})
    table = html_soup.select_one(".visualizacao")

    print(table)
    prerequisite = table.select("tr")[8]
    corequisite = table.select("tr")[9]
    equivalence = table.select("tr")[10]

    handle_prerequisite(prerequisite, subject_code)
    handle_corequisite(corequisite, subject_code)
    handle_equivalence(equivalence, subject_code)


def handle_corequisite(corequisite, subject_code):
    corequisite_list = corequisite.text.split()[2:-1]
    # Always find subject
    subject = Subject.objects.get(code=subject_code)
    for disciplina in corequisite_list:
        # Caso não seja (, ), OU e E
        if disciplina != "(" and disciplina != ")":
            if disciplina.upper() != "OU" and disciplina.upper() != "E":
                # Cria o pré-requisito
                try:
                    corequisite = Subject.objects.get(code=disciplina)
                    CoRequisite.objects.create(subject=subject, corequisite=corequisite)
                except:
                    print(f"Disciplina não encontrada para có-requisito: {disciplina}")


def handle_prerequisite(prerequisit, subject_code):
    prerequisit_list = prerequisit.text.split()[2:-1]
    # Always find subject
    subject = Subject.objects.get(code=subject_code)
    prerequisit_set = PreRequisiteSet.objects.create(subject=subject)
    for disciplina in prerequisit_list:
        if disciplina != "(" and disciplina != ")":
            # Cria um novo conjunto de disciplina
            if disciplina.upper() == "OU":
                subject = Subject.objects.get(code=subject_code)
                prerequisit_set = PreRequisiteSet.objects.create(subject=subject)
            elif disciplina.upper() == "E":
                continue
            else:
                # Adiciona a disciplina no conjunto de pré-requisitos atual
                try:
                    subject = Subject.objects.get(code=disciplina)
                    prerequisit_set.prerequisite.create(subject=subject)
                except:
                    print(f"Disciplina não encontrada para pré-requisito: {disciplina}")


def handle_equivalence(equivalences, subject_code):
    equivalences_list = equivalences.text.split()[2:-1]
    destination = Subject.objects.get(code=subject_code)
    for equivalence in equivalences_list:
        if equivalence != "(" and equivalence != ")":
            # Cria um novo conjunto de disciplina
            if equivalence.upper() == "OU":
                continue
            elif equivalence.upper() == "E":
                print("Equivalencia com E")
                continue
            else:
                # Adiciona a disciplina no conjunto de pré-requisitos atual
                # TODO verificar campos covarage e direction
                try:
                    Equivalence.objects.create(
                        subject_id=equivalence, destination=destination
                    )
                except:
                    print(f"Disciplina {equivalence} não existe no BD")


def get_cookies():
    url = "https://sig.unb.br/sigaa/public/componentes/busca_componentes.jsf"
    response = requests.request("GET", url)
    return response.headers["Set-Cookie"].split(" ")[0]


def get_request_data(url):
    response = requests.request("GET", url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return {
        "cookies": response.headers["Set-Cookie"].split(" ")[0],
        "javax": html_soup.find("input", {"name": "javax.faces.ViewState"})["value"],
    }


def request_subject_page(payload_data):
    url = "https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf?aba=p-ensino"
    request_data = get_request_data(url)
    print(request_data)
    payload = {
        "formListagemComponentes": "formListagemComponentes",
        "javax.faces.ViewState": request_data["javax"],
        "formListagemComponentes:j_id_jsp_190531263_23": "formListagemComponentes:j_id_jsp_190531263_23",
        "id": payload_data["subject_id"],
        "publico": "public",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
    }
    response = requests.post(url, headers=headers, data=payload)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def run():
    # Exemplo introdução ao processamento de imagens
    parse_equivalence("CIC0004", 177944)
