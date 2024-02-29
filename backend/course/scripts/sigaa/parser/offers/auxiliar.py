
YEAR = 2024
SEMESTER = 1


# Input: Lista contendo os valores das disciplinas para ser refatorado (obtidos através dos tds)
# Output: Dicionário contendo as informações refatoradas para criar a oferta
def refactor_list(class_raw_data, subject_title):
    # print(class_raw_data)
    class_data = {}
    class_data["name"] = class_raw_data[0]
    class_data["semester"] = class_raw_data[1]

    raw_teachers = class_raw_data[2].split(")")  # todas strings terminam com ex: "(60h"
    class_data["teacher"] = "/".join(
        raw_teachers[i][0 : raw_teachers[i].find("(")].strip()
        for i in range(len(raw_teachers) - 1)
    )

    class_data["schedule"] = class_raw_data[3][0 : class_raw_data[3].find(" ")]

    class_data["students_qtd"] = class_raw_data[5]
    class_data["occupied"] = class_raw_data[6]
    class_data["place"] = class_raw_data[7]
    class_data["subject_code"] = subject_title.split(" ")[0]
    class_data["subject_name"] = subject_title.split(" - ", 1)[-1]

    # print(class_data)
    return class_data

