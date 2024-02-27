from backend.course.scripts.sigaa.parser.course.parse import parse_course
from backend.course.scripts.sigaa.parser.departments.parse import (
    run as parse_departments,
)
from backend.course.scripts.sigaa.parser.offers.parse import run as parse_offer
from backend.course.scripts.sigaa.parser.relationships.parse import parse_relationships
from backend.course.scripts.sigaa.parser.subjects.parse import run as parse_subjects

from course.scripts.refactor_course_name import run as refactor_course

from course.models.models import Course, Subject


# Faz o parse das informações
def run():
    # Cria os cursos e os departamentos
    print("\n###### INICIANDO O PARSE DOS DEPARTAMENTOS ######\n")
    parse_departments()
    print("\n###### PARSE DOS DEPARTAMENTOS CONCLUÍDO ######\n")

    # Cria todas as disciplinas com base nos departamentos
    print("\n###### INICIANDO PARSE DAS DISCIPLINAS ######\n")
    parse_subjects()
    print("\n######  PARSE DAS DISCIPLINAS CONCLUÍDO ######\n")

    # Cria as matérias e suas turmas da oferta
    print("\n###### INICIANDO O PARSE DA OFERTA ######\n")
    parse_offer()
    print("\n###### PARSE DA OFERTA CONCLUÍDO ######\n")

    # Get all course IDs
    course_ids = [course.id for course in Course.objects.all()]
    print("\n###### INICIANDO O PARSE DOS CURSOS ######\n")
    for course_id in course_ids:
        print(f"\n###### INICIANDO O PARSE DO CURSO {course_id} ######\n")
        parse_course(course_id)
        print("\n###### PARSE DO CURSO CONCLUÍDO ######\n")
        break

    refactor_course()
    print("\n###### PARSE DOS CURSOS CONCLUÍDO ######\n")

    print("\n###### INICIANDO PARSE DE EQUIVALÊNCIAS e PRÉ-REQUISITOS ######\n")
    subjects = [(subject.code) for subject in Subject.objects.all()]
    for subject in subjects:
        print(f"\n###### {subject.code} - {subject.name.upper()} ######\n")
        try:
            parse_relationships(subject)
        except:
            print("Erro no parse\n")

    print("\n###### PRE PROCESSANDO OS DADOS DOS CURSOS ######\n")
    for course in Course.objects.all():
        course.preprocess_info()

    print("\n###### PRE PROCESSANDO OS DADOS DAS MATÉRIAS ######\n")
    for subject in Subject.objects.all():
        subject.preprocess_info()
