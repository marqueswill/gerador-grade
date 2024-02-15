from bs4 import BeautifulSoup
from requests import get
from course.models.models import Department, Course


def parse_departments():
    url = "https://sig.unb.br/sigaa/public/curso/lista.jsf?nivel=G&aba=p-ensino"

    response = get(url)
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


def run():
    parse_departments()
