from course.scripts.sigaa.page_requests import request_curriculum_page
from course.scripts.sigaa.parser.course.auxiliar import (
    get_course_curriculum_ids,
    get_header_info,
    save_subject,
)
from course.models.models import (
    Course,
    CourseCurriculum,
)


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
    optional_subjects = optional_subjects_soup.find_all("tr")[:-1]
    for subject_html in optional_subjects:
        save_subject(curriculum, subject_html, 0)


def run():
    # Example data from Engenharia da computação
    parse_course(414610)
