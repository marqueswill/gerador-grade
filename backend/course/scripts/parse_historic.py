import PyPDF2
import re

reader = PyPDF2.PdfReader('historico.pdf')

def filter_coursed(text):
    pos1 = text.find('COMPONENTES CURRICULARES CURSADOS')
    pos2 = text.find('COMPONENTES CURRICULARES OBRIGATÓRIOS PENDENTES')
    return text[pos1:pos2]

def filter_semesters(text):
    pos1 = text.find('2022.1')
    pos2 = text.find('LEGENDA')
    return text[pos1:pos2]

def filter_apr(text):
    pos1 = text.find('ENADE')
    return text[pos1:]

def get_apr():
    text = ''
    for page in reader.pages:
        txt = filter_coursed(page.extract_text().upper())
        if(txt):
            text += txt
    return text

apr = filter_apr((filter_semesters(get_apr())))

regex = r"(?P<ano>\d+\.\d+)\s+(?P<disciplina>.*?)\s+(\d+\s+)?(?P<situacao>(APR|MATR|CUMP|REPR))\s+(?P<codigo>\w+)\s+(?P<credito>\d+)\s+(?P<frequencia>\d+,\d+)\s+(?P<mencao>\w+)?"

matches2 = re.finditer(regex, apr)

for match in matches2:
    print("DISCIPLINA:", match.group("disciplina"))
    print("SITUAÇÃO:", match.group("situacao"))
    print("CÓDIGO:", match.group("codigo"))
    print("CRÉDITOS:", match.group("credito"))
    print("FREQUÊNCIA:", match.group("frequencia"))
    print("MENÇÃO:", match.group("mencao"))
    print()
