from bs4 import BeautifulSoup
import requests


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


def request_subject_page(payload_data):
    url = "https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf?aba=p-ensino"
    request_data = get_request_data(url)
    # print(request_data)
    # payload = {
    #     "form": "form",
    #     "form:nivel": "G",
    #     "form:checkTipo": "on",
    #     "form:tipo": 2,
    #     "form:checkCodigo": "on",
    #     "form:j_id_jsp_190531263_11": payload_data["subject_code"],
    #     "form:j_id_jsp_190531263_13": "",
    #     "form:unidades": 0,
    #     "form:btnBuscarComponentes": "Buscar Componentes",
    #     "javax.faces.ViewState": request_data["javax"],
    # }
    # print(payload)
    payload = {
        "formListagemComponentes": "formListagemComponentes",
        "javax.faces.ViewState": request_data["javax"],
        "formListagemComponentes:j_id_jsp_190531263_23": "formListagemComponentes:j_id_jsp_190531263_23",
        "id": payload_data["subject_id"],
        "publico": "public",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
    }
    response = requests.post(url, headers=headers, data=payload)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")

    return html_soup


def request_department_classes_page(payload_data):
    url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
    request_data = get_request_data(url)
    payload = {
        "formTurma": "formTurma",
        "formTurma:inputNivel": "G",
        "formTurma:inputDepto": payload_data["department_id"],
        "formTurma:inputAno": payload_data["year"],
        "formTurma:inputPeriodo": payload_data["semester"],
        "formTurma:j_id_jsp_1370969402_11": "Buscar",
        "javax.faces.ViewState": request_data["javax"],
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
    }

    response = requests.post(url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def request_department_subjects_page(payload_data):
    url = "https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf"
    request_data = get_request_data(url)
    payload = {
        "form": "form",
        "form:nivel": "G",
        "form:checkTipo": "on",
        "form:tipo": 2,
        "form:checkUnidade": "on",
        "form:unidades": payload_data["department_sigaa_id"],
        "form:btnBuscarComponentes": "Buscar Componentes",
        "javax.faces.ViewState": request_data["javax"],
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
    }

    response = requests.post(url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def get_ids_and_names(url):
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    list_depto = html_soup.find(id="formTurma:inputDepto")
    departamentos = {}
    for depto in list_depto.find_all("option"):
        departamentos[depto["value"]] = depto.text

    departamentos.pop("0", None)
    return departamentos
