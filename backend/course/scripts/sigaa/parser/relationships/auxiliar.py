from bs4 import BeautifulSoup
import requests

from course.models.models import (
    CoRequisite,
    Equivalence,
    PreRequisiteSet,
    Subject,
)


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


# TODO: refazer considerando os diferente currículos
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
