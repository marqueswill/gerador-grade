import requests
from bs4 import BeautifulSoup


def get_request_data(url):
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")

    return {
        "cookies": response.headers["Set-Cookie"].split(" ")[0],
        "javax": html_soup.find("input", {"name": "javax.faces.ViewState"})["value"],
    }


def request_department_classes(payload_data):
    url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
    request_data = get_request_data(url)
    payload = {
        "formTurma": "formTurma",
        "formTurma:inputNivel": payload_data["nivel"],
        "formTurma:inputDepto": payload_data["codigo_dpt"],
        "formTurma:inputAno": payload_data["ano"],
        "formTurma:inputPeriodo": payload_data["semestre"],
        "formTurma:j_id_jsp_1370969402_11": "Buscar",
        "javax.faces.ViewState": request_data["javax"],
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
        "Host": "sigaa.unb.br",
        "Origin": "https://sigaa.unb.br",
        "Referer": "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    response = requests.post(url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


def request_department_subjects(payload_data):
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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": request_data["cookies"],
        "Host": "sigaa.unb.br",
        "Origin": "https://sigaa.unb.br",
        "Referer": url,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chro",
    }

    response = requests.post(url, data=payload, headers=headers)
    html_soup = BeautifulSoup(response.text.encode("utf8"), "html.parser")
    return html_soup


response1 = request_department_classes(
    {
        "nivel": "G",
        "codigo_dpt": 640,
        "ano": 2024,
        "semestre": 1,
    }
)

response2 = request_department_subjects({"department_sigaa_id": 640})
print(response2)

