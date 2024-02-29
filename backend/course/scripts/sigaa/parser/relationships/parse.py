from course.models.models import Subject
from course.scripts.sigaa.page_requests import request_subject_page
from course.scripts.sigaa.parser.relationships.auxiliar import (
    handle_corequisite,
    handle_equivalence,
    handle_prerequisite,
)


def parse_relationships(subject):
    # print(subject)

    html_soup = request_subject_page(
        {"subject_id": subject.id, "subject_code": subject.code}
    )
    table = html_soup.select_one("visualizacao")
    print(table)

    # prerequisite = table.select("tr")[8]
    # corequisite = table.select("tr")[9]
    # equivalence = table.select("tr")[10]

    # handle_prerequisite(prerequisite, subject.code)
    # handle_corequisite(corequisite, subject.code)
    # handle_equivalence(equivalence, subject.code)


def run():
    # Exemplo introdução ao processamento de imagens
    subject = Subject.objects.get(code="CIC0099")
    parse_relationships(subject)
