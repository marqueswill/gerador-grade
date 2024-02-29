from course.scripts.sigaa.page_requests import request_department_subjects_page
from course.scripts.sigaa.parser.subjects.auxiliar import get_ids_and_names
from course.models.models import Department, Subject
from django.db import IntegrityError


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


# Esse parse tem a função de criar as disciplinas no banco de dados, é necessário que os departamentos já estejam criados
def run():
    url = "https://sig.unb.br/sigaa/public/componentes/busca_componentes.jsf"
    departments = get_ids_and_names(url)
    # departments = {508: "DEPTO CIÊNCIAS DA COMPUTAÇÃO"}
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
