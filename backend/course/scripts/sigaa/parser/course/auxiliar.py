from bs4 import BeautifulSoup
import requests
from django.db import IntegrityError

from course.models.models import Department, Subject

# Maps some departments whose code format isn't recognized
DEPARTMENTS_MAP = {"GPP": "FACE", "REL": "IREL", "POL": "IPOL"}


def get_course_curriculum_ids(course_id):
    url = f"https://sig.unb.br/sigaa/public/curso/curriculo.jsf?lc=pt_BR&id={course_id}"
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    # Get the course ID from a JS function on the <a> onClick action
    ids = []
    lines = html_soup.find_all("tr")

    for line in lines:

        if line["class"][0] in ["linha_par", "linha_impar"]:
            colums = line.find_all("td")
            if colums[1].text.strip() == "Ativa":
                curriculum_id = int(
                    colums[2].find("a")["onclick"].split(":")[-2].split("'")[1]
                )
                ids.append(curriculum_id)

    return ids


def save_subject(curriculum, subject_html, semester_number):
    html_subject_rows = subject_html.find_all("td")
    # print(html_subject_rows)

    subject_info = html_subject_rows[0].text.split(" - ")

    # Get status code
    status_code = {"Obrigatória": "OBR", "Optativa": "OPT", "Módulo Livre": "ML"}
    status = html_subject_rows[1].text.strip()
    status = status_code[status]

    code = subject_info[0].strip()

    # Prevent that subject names with "-" are wrongly parsed
    name_components = subject_info[1:-1]

    name = name_components[0]
    for component in name_components[1:0]:
        name += " - " + component

    # Get credits in hours format
    credit = int(subject_info[-1][:-1])

    # Try to get current subject from the DB
    # If its not there, proceed to create it
    try:
        subject = Subject.objects.get(code=code)
    except Exception as error:
        print(f"Could not find subject {name}: {error}. Trying to create it")
        # If the subject can't be found, get its department from its code
        dept_initials = code[0:3]

        # Try to find the department
        try:
            department = Department.objects.get(initials=dept_initials)
        except Exception as error:

            # If the department cannot be found, check if its initials are mapped
            # If the initials are not mapped or the mapped one fails, proceed to create subject without department
            if dept_initials in DEPARTMENTS_MAP:
                new_deps_initials = DEPARTMENTS_MAP[dept_initials]

                try:
                    department = Department.objects.get(initials=new_deps_initials)
                except Exception as error:
                    print(
                        f"Could not find correct department: {error}. Creating subject {name} without department"
                    )

            else:
                print(
                    f"Could not find alternative department code: {error}. Creating subject {name} without department"
                )

            # Creates subject without department
            try:
                subject = Subject(name=name, code=code, credit=credit)
                subject.save()
                print(f"Subject {name} created without department")
            except Exception as error:
                # If all of the above fails, skip to the next subject
                print(f"Could not create subject {name}: {error}. Skipping subject")
                return

        # Create subject if department is found
        try:
            subject = Subject.objects.update_or_create(
                name=name, department=department, code=code, credit=credit
            )[0]
            print(f"Subject {name} created")
        except IntegrityError:
            print(f"Subject {name} is already created")
        except Exception as error:
            print(f"Could not create subject {name}: {error}. Skipping subject")
            return

    # Append the created subject

    curriculum.append_subject(semester_number, subject, status)
    print(f"Added {code} to curriculum")


def get_header_info(header_soup):
    import re

    # replace tabs and newlines
    header_info = {}
    trimmed_header = [
        elem.text.replace("\t", "").replace("\n", "") for elem in header_soup
    ]

    # Erro na geração de código do sigaa não fecha uma tag <tr>
    bug = trimmed_header[9]
    corrected = bug[0 : trimmed_header[9].find("Optativas")].split("h")

    # Get course detailed workload
    header_info["code"] = trimmed_header[0].split(":")[1].strip()
    header_info["start_semester"] = trimmed_header[2].split(":")[1].strip()
    header_info["total_workload"] = int(re.findall(r"\d+", trimmed_header[4])[0])
    header_info["mandatory_workload"] = int(re.findall(r"\d+", trimmed_header[8])[0])
    header_info["optional_workload"] = int(re.findall(r"\d+", corrected[0])[0])
    # header_info["additional_workload"] = int(re.findall(r"\d+", corrected[1])[0])
    header_info["max_total_free_module"] = int(re.findall(r"\d+", corrected[3])[0])
    header_info["max_period_workload"] = int(re.findall(r"\d+", corrected[4])[0])
    header_info["min_period_workload"] = int(re.findall(r"\d+", corrected[5])[0])

    return header_info
