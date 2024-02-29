from course.scripts.sigaa.page_requests import (
    get_ids_and_names,
    request_department_classes_page,
)
from course.scripts.sigaa.parser.offers.auxiliar import (
    SEMESTER,
    YEAR,
    refactor_list,
)
from course.models.models import Offer, Subject, Teacher, OfferTeacher
from django.db import IntegrityError


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


def run():
    url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
    department_data = get_ids_and_names(url)
    for departament_id in department_data:
        department_name = department_data[departament_id].split(" - ")[0].split(" (")[0]
        if "PROGRAMA DE PÓS-GRADUAÇÃO" in (department_name):
            continue
        parse_oferta(departament_id, department_name)
