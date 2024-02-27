from backend.course.scripts.sigaa.page_requests import request_subject_page
from backend.course.scripts.sigaa.parser.relationships.auxiliar import (
    handle_corequisite,
    handle_equivalence,
    handle_prerequisite,
)


def parse_relationships(subject):
    subject_code, subject_id = subject.code, subject.id

    html_soup = request_subject_page({"subject_id": subject_id})
    table = html_soup.select_one(".visualizacao")

    # print(table)
    prerequisite = table.select("tr")[8]
    corequisite = table.select("tr")[9]
    equivalence = table.select("tr")[10]

    handle_prerequisite(prerequisite, subject_code)
    handle_corequisite(corequisite, subject_code)
    handle_equivalence(equivalence, subject_code)


def run():
    # Exemplo introdução ao processamento de imagens
    parse_relationships("CIC0004", 177944)
