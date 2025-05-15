from num2words import num2words
import re
from abreviacoes import abreviacoes
import sys
import string

def limpar_simbolos(texto):
    texto = re.sub(r"http\S+", "", texto)  # Remove URLs
    texto = re.sub(r"[^\w\s,.!?áéíóúãõâêôçÁÉÍÓÚÃÕÂÊÔÇ]", "", texto)  # Remove emojis e símbolos
    return texto

def converter_moeda(texto):
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

        texto = re.sub(padrao, substituir, texto)

    return texto

def converter_numeros(texto):
    # 1. Casos de moeda com símbolos conhecidos
    texto = converter_moeda(texto)

    # 2. Números colados a unidades (ex: 10kg → 10 kg). Só coloca espaço.
    texto = re.sub(r'(\d+)(°?[a-zA-Z²³µ%]+)', r'\1 \2', texto)

    # 3. Números com vírgula ou ponto → "dois vírgula cinco"
    texto = re.sub(r'\b(\d+)[.,](\d+)\b', lambda m: f"{num2words(int(m.group(1)), lang='pt_BR')} vírgula {num2words(int(m.group(2)), lang='pt_BR')}", texto)

    # 4. Horários → "10:45 -> dez e quarenta e cinco"
    texto = re.sub(r'\b([0-1]?\d|2[0-3]):00h?\b', lambda m: num2words(int(m.group(1)), lang='pt_BR'), texto)
    texto = re.sub(r'\b(\d+)[:](\d+)\b', lambda m: f"{num2words(int(m.group(1)), lang='pt_BR')} e {num2words(int(m.group(2)), lang='pt_BR')}", texto)

    # 5. Números inteiros simples → por extenso
    texto = re.sub(r'\b\d+\b', lambda m: num2words(int(m.group()), lang='pt_BR'), texto)

    return texto

def expandir_abreviacoes(texto):
    for abrev, exp in abreviacoes.items():
        padrao = r'(?<!\w)' + re.escape(abrev) + r'(?!\w)'
        texto = re.sub(padrao, exp, texto)
    return texto

def corrigir_pontuacao_final(texto):
    texto = texto.strip()

    if not texto:
        return texto

    if texto[-1] in ['.', '?', '!']:
        return texto

    if texto[-1].isalpha():
        return texto + '.'

    if texto[-1] in string.punctuation:
        return texto[:-1] + '.'

    return texto

def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"INPUT:{input_path}")
    print(f"Output:{output_path}")

    with open(input_path, 'r') as f:
        texto = f.read()

    #processamento dos dados
    texto = converter_numeros(texto)
    texto = expandir_abreviacoes(texto)
    texto = limpar_simbolos(texto)
    texto = corrigir_pontuacao_final(texto)

    with open(output_path, 'w') as f:
        f.write(texto)

    return texto


if __name__ == "__main__":
    main()

