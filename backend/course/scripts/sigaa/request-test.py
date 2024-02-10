from bs4 import BeautifulSoup
import requests as request


def request_course_curriculum_page(request_data):
    url = "https://sig.unb.br/sigaa/public/curso/curriculo.jsf"
    payload = {
        "formCurriculosCurso": "formCurriculosCurso",
        "nivel": "G",
        "javax.faces.ViewState": get_javax(url),
        "formCurriculosCurso:j_id_jsp_154341757_30": "formCurriculosCurso:j_id_jsp_154341757_30",
        "id": request_data["id"],
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": get_cookies(url),
    }

    response = request.post(url=url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def request_departments_page():
    url = "https://sig.unb.br/sigaa/public/curso/lista.jsf?nivel=G&aba=p-ensino"
    response = request.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def request_subject_page(request_data):
    url = "https://sig.unb.br/sigaa/public/componentes/busca_componentes.jsf"
    payload = {
        "form": "form",
        "form:nivel": "G",
        "form:checkTipo": "on",
        "form:tipo": 2,
        "form:j_id_jsp_190531263_11": "",
        "form:j_id_jsp_190531263_13": "",
        "form:checkUnidade": "on",
        "form:unidades": request_data["dapartment_sigaa_id"],
        "form:btnBuscarComponentes": "Buscar Componentes",
        "javax.faces.ViewState": "j_id1",  # ?
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": get_cookies(url),
    }

    response = request.post(url=url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def request_department_offers_page(request_data):
    url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"

    payload = {
        "formTurma": "formTurma",
        "formTurma:inputNivel": "G",
        "formTurma:inputDepto": request_data["id"],
        "formTurma:inputAno": request_data["year"],
        "formTurma:inputPeriodo": request_data["period"],
        "formTurma:j_id_jsp_1370969402_11": "Buscar",
        "javax.faces.ViewState": get_javax(url),  # j_id1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": url,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://sigaa.unb.br",
        "Connection": "keep-alive",
        "Cookie": get_cookies(url),
        "Upgrade-Insecure-Request": "1",
        "Cache-Control": "max-age=0",
    }
    response = request.post(url=url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def request_department_subjects_page(request_data):
    url = "https://sig.unb.br/sigaa/public/componentes/busca_componentes.jsf"
    payload = {
        "form": "form",
        "form:nivel": "G",
        "form:checkTipo": "on",
        "form:tipo": 2,
        "form:j_id_jsp_190531263_11": "",
        "form:j_id_jsp_190531263_13": "",
        "form:checkUnidade": "on",
        "form:unidades": request_data["dapartment_sigaa_id"],
        "form:btnBuscarComponentes": "Buscar Componentes",
        "javax.faces.ViewState": "j_id1",  # ?
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": get_cookies(url),
    }

    response = request.post(url=url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


# Testar pra ver se é necessário
def get_javax(url):
    response = request.request("GET", url)
    cookies = response.headers["Set-Cookie"].split(" ")[0]
    return cookies


def get_cookies(url):
    response = request.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    javax = html_soup.select("#javax\.faces\.ViewState")[0]["value"]
    return javax


response = request_course_curriculum_page({"id": 354})
print(response)
