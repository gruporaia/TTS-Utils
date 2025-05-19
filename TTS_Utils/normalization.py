from num2words import num2words
import re
from abreviacoes import abreviacoes
import sys
import string

def clean_symbols(text):
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"[^\w\s,.!?áéíóúãõâêôçÁÉÍÓÚÃÕÂÊÔÇ]", "", text)  # Remove emojis e símbolos
    return text

def converter_moeda(text):
    simbolos_moeda = {
        r'R\$': 'reais',
        r'USD': 'dólares',
        r'U\$': 'dólares'
    }

    for simbolo_regex, nome in simbolos_moeda.items():
        # captura o símbolo + número com possíveis pontos de milhar e opcional vírgula decimal
        padrao = fr'{simbolo_regex}\s*(\d{{1,3}}(?:\.\d{{3}})*(?:,\d+)?)'

        def substituir(m):
            orig = m.group(1)           # ex: "3.200,75" ou "10" ou "2.500"
            # se tiver vírgula, é decimal no formato BR
            if ',' in orig:
                # remove pontos de milhar, mantém vírgula
                inteiro_str, dec_str = orig.replace('.', '').split(',', 1)
                inteiro = int(inteiro_str)
                # garante dois dígitos nos centavos
                dec_str = (dec_str + "00")[:2]
                centavos = int(dec_str)

                partes = []
                if inteiro > 0:
                    partes.append(f"{num2words(inteiro, lang='pt_BR')} {nome}")
                if centavos > 0:
                    txt_cent = num2words(centavos, lang='pt_BR')
                    txt_cent += " centavo" + ("s" if centavos > 1 else "")
                    if inteiro > 0:
                        partes.append(f"e {txt_cent}")
                    else:
                        partes.append(txt_cent)
                return " ".join(partes)

            # se não tem vírgula mas tem ponto (milhar) — trata como inteiro
            elif '.' in orig:
                inteiro = int(orig.replace('.', ''))
                return f"{num2words(inteiro, lang='pt_BR')} {nome}"

            # caso puro inteiro (sem ponto nem vírgula)
            else:
                inteiro = int(orig)
                return f"{num2words(inteiro, lang='pt_BR')} {nome}"

        text = re.sub(padrao, substituir, text)

    return text

def convert_numbers(text):
    # 1. Casos de moeda com símbolos conhecidos
    text = converter_moeda(text)

    # 2. Números colados a unidades (ex: 10kg → 10 kg). Só coloca espaço.
    text = re.sub(r'(\d+)(°?[a-zA-Z²³µ%]+)', r'\1 \2', text)

    # 3. Números com vírgula ou ponto → "dois vírgula cinco"
    text = re.sub(r'\b(\d+)[,.](\d+)\b', lambda m: f"{num2words(int(m.group(1)), lang='pt_BR')} vírgula {num2words(int(m.group(2)), lang='pt_BR')}", text)

    # 4. Horários → "10:45 -> dez e quarenta e cinco"
    text = re.sub(r'\b([0-1]?\d|2[0-3]):00h?\b', lambda m: num2words(int(m.group(1)), lang='pt_BR'), text)
    text = re.sub(r'\b(\d+)[:](\d+)\b', lambda m: f"{num2words(int(m.group(1)), lang='pt_BR')} e {num2words(int(m.group(2)), lang='pt_BR')}", text)

    # 5. Números inteiros simples → por extenso
    text = re.sub(r'\b\d+\b', lambda m: num2words(int(m.group()), lang='pt_BR'), text)

    return text

def expand_abreviations(text):
    for abrev, exp in abreviacoes.items():
        padrao = r'(?<!\w)' + re.escape(abrev) + r'(?!\w)'
        text = re.sub(padrao, exp, text)
    return text

def correct_final_ponctuation(text):
    text = text.strip()

    if not text:
        return text

    if text[-1] in ['.', '?', '!']:
        return text

    if text[-1].isalpha():
        return text + '.'

    if text[-1] in string.punctuation:
        return text[:-1] + '.'

    return text

def normalize_text(text):
    text = convert_numbers(text)
    text = expand_abreviations(text)
    text = clean_symbols(text)
    text = correct_final_ponctuation(text)

    return text
