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

    # Preenchendo o primeiro departamento da página
    # # Pra que?????
    # for row in table.findAll("tr")[1:2]:
    #     col = row.findAll("td")
    #     dept = col[0].string.replace("\n", "").replace("\t", "")
    #     dept = dept.split(" - ")
    #     initials = dept[0]
    #     name = dept[1].split(" (")[0]
    #     department = Department.objects.create(name=name, initials=initials)

    # Pular o titulo da tabela
    for row in table.findAll("tr")[2:]:
        col = row.findAll("td")

        if len(col) == 1:
            # Atualiza as informações antigas
            dept = col[0].string.replace("\n", "").replace("\t", "").split(" - ")
            initials = dept[0]  # ignorar por conta de conflitos
            name = dept[1].split(" (")[0]
            department = Department.objects.get(name=name)
            print(department)
            # try:
            #     department = Department.objects.get(name=name)
            #     print(f"O departamento já existe na database   : {department.name}")
            # except Department.DoesNotExist:
            #     department = Department.objects.create(name=name, initials=initials)
            #     print(f"Departamento foi registrado com sucesso: {department.name}")

        else:
            # Lê informações da Tabela
            course_data = extract_course_data(col)

            try:
                Course.objects.update_or_create(
                    code=course_data["code"],
                    department=department,
                    name=course_data["course_name"],
                    academic_degree=course_data["academic_degree"],
                    shift=course_data["shift"],
                    is_ead=course_data["mode"] != "Presencial",
                    coordinator_name=course_data["coordenador"],
                )
                print(
                    f"Curso adicionado: [{course_data['code']}] - {course_data['course_name']}"
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
        "code": (col[6].find("a")["href"][14:20]),
    }
    return data


def run():
    parse_departments()
