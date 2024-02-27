from bs4 import BeautifulSoup
import requests
from django.db import IntegrityError
from course.models.models import (
    Course,
    Subject,
    CourseCurriculum,
    CurriculumSubject,
    Department,
)

# Maps some departments whose code format isn't recognized
DEPARTMENTS_MAP = {"GPP": "FACE", "REL": "IREL", "POL": "IPOL"}


def parse_course(course_id):
    # Try to get the course. If its not possible, exit the function
    try:
        course = Course.objects.get(id=course_id)
    except:
        print(f"course {course_id} does not exist in the DB")
        return

    print(f"--------- Parsing course {course.name} ----------")
    curriculum_ids = get_course_curriculum_ids(course_id)
    for curriculum_id in curriculum_ids:
        html_soup = request_curriculum_page(
            {
                "curriculum_id": curriculum_id,
                "course_id": course_id,
            }
        )

        header_soup = html_soup.select("table tr", limit=17)
        header_info = get_header_info(header_soup)

        try:
            curriculum = CourseCurriculum.objects.update_or_create(
                id=curriculum_id, code=header_info["code"], course=course
            )[0]

        except Exception as e:
            print(e)
            break

        parse_flow(html_soup, curriculum)
        parse_optationals(html_soup, curriculum)
        
        # Adds additional course information
        try:
            # print([course.name, curriculum_id, header_info])
            curriculum = CourseCurriculum.objects.filter(id=curriculum_id).update(
                course=course,
                code=header_info["code"],
                start_semester=header_info["start_semester"],
                total_workload=header_info["total_workload"],
                optional_workload=header_info["optional_workload"],
                mandatory_workload=header_info["mandatory_workload"],
                max_total_free_module=header_info["max_total_free_module"],
                max_period_workload=header_info["max_period_workload"],
                min_period_workload=header_info["min_period_workload"],
            )
            print(
                f"PARSE MATÉRIAS DO FLUXO CONCLUÍDO: {header_info['code']} - {course}\n\n"
            )
        except Exception as error:
            print(error)
            print(f"Could not save course curriculum: {curriculum.code}")
            pass


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


def get_request_data(url):
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return {
        "cookies": response.headers["Set-Cookie"].split(" ")[0],
        "javax": html_soup.find("input", {"name": "javax.faces.ViewState"})["value"],
    }


def request_curriculum_page(payload_data):
    url_referer = f"https://sig.unb.br/sigaa/public/curso/curriculo.jsf?lc=pt_BR&id={payload_data['course_id']}"
    request_data = get_request_data(url_referer)
    url = "https://sigaa.unb.br/sigaa/public/curso/curriculo.jsf"

    payload = {
        "formCurriculosCurso": "formCurriculosCurso",
        "nivel": "G",
        "javax.faces.ViewState": request_data["javax"],
        "formCurriculosCurso:j_id_jsp_154341757_30": "formCurriculosCurso:j_id_jsp_154341757_30",
        "id": payload_data["curriculum_id"],
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
    }

    response = requests.post(url, headers=headers, data=payload)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def parse_flow(html_soup, curriculum):
    semesters = html_soup.find("div", {"class": "yui-content"})
    if semesters:
        # Verificando se não está vazio
        semesters = semesters.find_all("div")[2:]  # pula optativas e complementares
    for semester in semesters:
        semester_number = semester["id"][8:]
        print("PARSING " + semester_number + "º SEMESTER")

        # Do not get the last term Ex: Carga Horária Total: 360hrs.
        semester_subjects_html = semester.find_all("tr")[:-1]
        for subject_html in semester_subjects_html:
            save_subject(curriculum, subject_html, semester_number)


def parse_optationals(html_soup, curriculum):
    print("\nPARSING CURRICULUM OPTIONAL SUBJECTS")

    optional_subjects_soup = html_soup.find(id="optativas")
    # optional_subjects_info = get_optional_subject_info(optional_subjects_soup)
    optional_subjects = optional_subjects_soup.find_all("tr")[:-1]
    for subject_html in optional_subjects:
        save_subject(curriculum, subject_html, 0)

    # # For each subject in the curriculum page
    # for curr_subject in optional_subjects_info:
    #     print(curr_subject["code"] + " - " + curr_subject["name"] + ":")

    #     # Try to get current subject from the DB
    #     # If its not there, proceed to create it
    #     try:
    #         subject = Subject.objects.get(code=curr_subject["code"])
    #     except Exception as error:
    #         print(f"    Could not find subject: ({error}). Trying to create it")
    #         code = curr_subject["code"]
    #         dept_initials = code[:3]

    #         # If the subject can't be found, get its department from its code
    #         # Try to find the department
    #         try:
    #             department = Department.objects.get(initials=dept_initials)
    #         except Exception as error:

    #             # If the department cannot be found, check if its initials are mapped
    #             # If the initials are not mapped or the mapped one fails, proceed to create subject without department
    #             if dept_initials in DEPARTMENTS_MAP:
    #                 new_dept_code = DEPARTMENTS_MAP[dept_initials]

    #                 try:
    #                     department = Department.objects.get(code=new_dept_code)
    #                 except Exception as error:
    #                     print(
    #                         f"  Could not find correct department ({error}). Creating subject without department"
    #                     )

    #             else:
    #                 print(
    #                     f"Could not find alternative department code ({error}). Creating subject without department"
    #                 )

    #             # Creates subject without department
    #             try:
    #                 subject = Subject(
    #                     name=curr_subject["name"],
    #                     code=curr_subject["code"],
    #                     credit=curr_subject["workload"],
    #                 )
    #                 subject.save()
    #                 print(f"    Subject created without department")
    #             except Exception as error:
    #                 # If all of the above fails, skip to the next subject
    #                 print(f"  Could not create subject ({error}). Skipping subject")
    #                 continue

    #         # Create subject if department is found
    #         try:
    #             subject = Subject.objects.create(
    #                 name=curr_subject["name"],
    #                 department=department,
    #                 code=curr_subject["code"],
    #                 credit=curr_subject["workload"],
    #             )
    #             print(f"    Subject created successfully")
    #         except IntegrityError:
    #             print(f"    Subject already exists")
    #         except Exception as error:
    #             print(f"    Could not create subject ({error}). Skipping iteration")
    #             continue

    #     # Create link between the subject and its course curriculum
    #     try:
    #         curriculum.append_subject(0, subject, status)

    #         print(
    #             f"    Linked {curr_subject['code']} to curriculum {header_info['code']}."
    #         )
    #     except Exception as error:
    #         print(error)
    #         print(f"    Could not link the subject with its course")
    #         continue


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


def get_optional_subject_info(opt_soup):
    opt_subjects_vector = opt_soup.find_all("tr")
    # Gets all optional curriculum subjects
    opt_subjects = [sub.find("td").text for sub in opt_subjects_vector]

    subjects = []
    for sub in opt_subjects:
        subject_info = {}
        fields = sub.split(" - ")

        # Assets that the parsed line is in the expected structure
        if len(fields[0]) == 7:
            subject_info["code"] = fields[0]
            subject_info["workload"] = int(fields[-1][:-1])

            # Prevent that subject names with "-" are wrongly parsed
            name_components = fields[1:-1]
            name = name_components[0]
            for component in name_components[1:0]:
                name += " - " + component
            subject_info["name"] = name

        if subject_info:
            subjects.append(subject_info)

    return subjects


def run():
    # Example data from Engenharia da computação
    parse_course(414610)
