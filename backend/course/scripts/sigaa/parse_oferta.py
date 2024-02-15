from bs4 import BeautifulSoup
from time import sleep
import requests
from course.models.models import Offer
from course.models.models import Subject
from course.models.models import Teacher, OfferTeacher
from django.db import IntegrityError

YEAR = 2024
SEMESTER = 1


# Input: Lista contendo os valores das disciplinas para ser refatorado (obtidos através dos tds)
# Output: Dicionário contendo as informações refatoradas para criar a oferta
def refactor_list(class_raw_data, subject_title):
    # print(class_raw_data)
    class_data = {}
    class_data["name"] = class_raw_data[0]
    class_data["semester"] = class_raw_data[1]

    raw_teachers = class_raw_data[2].split(")")  # todas strings terminam com ex: "(60h"
    class_data["teacher"] = "/".join(
        raw_teachers[i][0 : raw_teachers[i].find("(")].strip()
        for i in range(len(raw_teachers) - 1)
    )

    class_data["schedule"] = class_raw_data[3][0 : class_raw_data[3].find(" ")]

    class_data["students_qtd"] = class_raw_data[5]
    class_data["occupied"] = class_raw_data[6]
    class_data["place"] = class_raw_data[7]
    class_data["subject_code"] = subject_title.split(" ")[0]
    class_data["subject_name"] = subject_title.split(" - ", 1)[-1]

    # print(class_data)
    return class_data


def get_ids_and_names(url):
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    list_depto = html_soup.find(id="formTurma:inputDepto")

    departamentos = {}
    for depto in list_depto.find_all("option"):
        departamentos[depto["value"]] = depto.text

    departamentos.pop("0", None)
    return departamentos


def parse_oferta(department_id, department_name):
    html_soup = request_department_classes_page(
        {  # payload
            "department_id": department_id,
            "year": YEAR,
            "semester": SEMESTER,
        }
    )

    department_subjects = html_soup.find_all("tr", {"class": "agrupador"})
    if not department_subjects:
        print(f"Não existe oferta para o departamento: {department_name}")
        return

    line = department_subjects[0]
    class_raw_data = []
    while True:
        if line == None:
            break

        # Se é agrupador, conseguimos obter o nome da disciplina
        if line["class"][0] == "agrupador":
            subject_title = line.text.strip()

        # Se não for agrupador, é a td com as demais informações
        else:
            # Pegando o vetor de infos da turma
            subject_classes = line.find_all("td")
            for class_info in subject_classes:
                if class_info:  # Extraindo o valor dos tds
                    class_raw_data.append(
                        class_info.text.strip()
                        .replace("\t", "")
                        .replace("\r", "")
                        .replace("\n\n\n", " ")
                    )

            # Entra a lista de tds do parse desorganizada
            # Retorna um dicionário com as infos necessárias
            class_data = refactor_list(class_raw_data, subject_title)

            if not class_data:
                class_raw_data = []
                line = line.find_next_sibling("tr")
                continue

            try:  # Lógica de criação e vínculo de oferta (turma), disciplina e professor
                try:  # Verifica se a disciplina existe na database
                    subject_object = Subject.objects.get(
                        code=class_data["subject_code"]
                    )
                except:
                    print(
                        f'Não foi possível encontrar a disciplina: {class_data["subject_code"]-class_data["subject_name"]} no banco de dados'
                    )
                    class_raw_data = []
                    line = line.find_next_sibling("tr")
                    continue

                try:  # Tenta criar a turma para a disciplina
                    oferta, _ = Offer.objects.get_or_create(
                        subject=subject_object,
                        name=class_data["name"],
                        semester=class_data["semester"],
                        schedule=class_data["schedule"],
                        students_qtd=class_data["students_qtd"],
                        occupied=class_data["occupied"],
                        place=class_data["place"],
                    )
                    print(
                        f'Oferta criada para {class_data["subject_code"]}-{class_data["subject_name"]}'
                    )
                except:
                    print(
                        f'Erro ao criar ou dar get turma com o nome {class_data["name"]} na disciplina {class_data["subject_code"]}'
                    )
                    class_raw_data = []
                    line = line.find_next_sibling("tr")
                    continue

                try:  # Vincula um professo do bd ou cria um novo se nao achar
                    teacher, _ = Teacher.objects.get_or_create(
                        name=class_data["teacher"]
                    )

                    try:  # Criando relação entre professor e oferta
                        ot = OfferTeacher.objects.create(offer=oferta, teacher=teacher)
                    except Exception as e:
                        # print(e)
                        print(
                            f'Erro ao vincular {class_data["teacher"]} e {class_data["subject_code"]}-{class_data["name"]}'
                        )
                        class_raw_data = []
                        line = line.find_next_sibling("tr")
                        continue
                except:
                    print(
                        f'Erro ao criar ou dar get no professor {class_data["teacher"]} da turma {class_data["subject_code"]}-{class_data["name"]}'
                    )
                    class_raw_data = []
                    line = line.find_next_sibling("tr")
                    continue

            except IntegrityError as e:
                # print(e)
                print(
                    f'A oferta para {class_data["subject_code"]}-{class_data["subject_name"]} já existe no banco de dados'
                )
                class_raw_data = []
                line = line.find_next_sibling("tr")
                continue
            except Exception as e:
                # print(e)
                print(
                    f'A oferta para {class_data["subject_code"]}-{class_data["subject_name"]} não foi encontrada'
                )
                class_raw_data = []
                line = line.find_next_sibling("tr")
                continue

            class_raw_data = []

        # Pega a sequência de informações que são sequência do nome (demais infos)
        line = line.find_next_sibling("tr")

        if line == None:
            break


def get_request_data(url):
    response = requests.request("GET", url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return {
        "cookies": response.headers["Set-Cookie"].split(" ")[0],
        "javax": html_soup.find("input", {"name": "javax.faces.ViewState"})["value"],
    }


def request_department_classes_page(payload_data):
    url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
    request_data = get_request_data(url)
    payload = {
        "formTurma": "formTurma",
        "formTurma:inputNivel": "G",
        "formTurma:inputDepto": payload_data["department_id"],
        "formTurma:inputAno": payload_data["year"],
        "formTurma:inputPeriodo": payload_data["semester"],
        "formTurma:j_id_jsp_1370969402_11": "Buscar",
        "javax.faces.ViewState": request_data["javax"],
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
    }

    response = requests.post(url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def run():
    url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
    department_data = get_ids_and_names(url)
    for departament_id in department_data:
        department_name = department_data[departament_id].split(" - ")[0].split(" (")[0]
        if "PROGRAMA DE PÓS-GRADUAÇÃO" in (department_name):
            continue
        parse_oferta(departament_id, department_name)
