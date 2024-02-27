from bs4 import BeautifulSoup
import requests
from backend.course.scripts.sigaa.page_requests import get_ids_and_names, request_department_subjects_page
from backend.course.scripts.sigaa.parser.departments.auxiliar import (
    extract_course_data,
)
from course.models.models import Course, Department
from django.db import IntegrityError


def parse_unity(department_sigaa_id, department_name):

    html_soup = request_department_subjects_page(
        {"department_sigaa_id": department_sigaa_id}
    )

    first_subject = html_soup.select("tbody tr td")

    if first_subject:
        subjects_code = first_subject[0].text
        department_initials = "".join(filter(str.isalpha, subjects_code))
        try:
            Department.objects.create(
                name=department_name,
                initials=department_initials,
            )
            print(f"Departamento foi registrado com sucesso: {department_name}")
        except Department.DoesNotExist:
            print(f"Não foi possível criar o departamento: {department_name}")
    else:
        print(f"O departamento não possui disciplinas  : {department_name}")


def parse_departments():
    url = "https://sig.unb.br/sigaa/public/curso/lista.jsf?nivel=G&aba=p-ensino"

    response = requests.get(url)
    html_soup = BeautifulSoup(response.text, "html.parser")

    # Procurando a table listagem no html
    table = html_soup.find("table", {"class": "listagem"})
    department = None

    # Pular o titulo da tabela
    for row in table.findAll("tr")[2:]:
        col = row.findAll("td")

        if len(col) == 1:
            # Atualiza as informações antigas
            dept = col[0].string.replace("\n", "").replace("\t", "").split(" - ")
            initials = dept[0]  # ignorar por conta de conflitos
            name = dept[1].split(" (")[0]
            department = Department.objects.get(name=name)
            print(f"\n{department}")

        else:
            course_data = extract_course_data(col)

            try:
                Course.objects.update_or_create(
                    department=department,
                    id=course_data["id"],
                    name=course_data["course_name"],
                    coordinator_name=course_data["coordenador"],
                    academic_degree=course_data["academic_degree"],
                    shift=course_data["shift"],
                    is_ead=course_data["mode"] != "Presencial",
                )
                print(
                    f"Curso adicionado/atualizado: [{course_data['id']}] - {course_data['course_name']}"
                )
            except Exception as e:
                print(e)
                pass


def run():
    url = "https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf?aba=p-ensino"
    departments = get_ids_and_names(url)
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
            parse_unity(department_sigaa_id, department_name)

            continue

    # provavelmente não precisa mais?
    parse_departments()
