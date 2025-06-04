# Text To Speech Utils
Aplicações de TTS (Text-to-Speech) em português frequentemente exigem ferramentas auxiliares, como métricas de avaliação, normalização de texto e criação de datasets. Este repositório oferece implementações prontas para acelerar o desenvolvimento de projetos de TTS em pt-BR, com os seguintes módulos disponíveis:
- Construtor automático de datasets a partir de áudios em português: a partir de arquivos de áudio brutos, são extraídas e transcritas frases, gerando um CSV com o texto e o caminho para cada trecho correspondente.
- Normalização de texto: transforma frases com números, siglas, símbolos e abreviações em versões por extenso, facilitando a leitura por modelos de TTS.
- Métricas de avaliação: este repositório tem código pronto para cálculo das métricas SECS, UTMOS e CER.

**Confira nossa aplicação que utiliza esses componentes para elaborar um pipeline automático de finetuning de modelos TTS, a [TTS-AutoTune]()**.

## 🛠️ Como usar

### Instalando dependências
```
pip install "git+https://github.com/gruporaia/TTS-Utils.git"
```

OBS: Caso seja necessário, é possível flexibilizar as versões das dependências alterando o arquivo pyproject.toml, mas não garantimos o funcionamento do pacote.

### Funcionamento

#### Construtor Automático de Dataset
```
from TTS_Utils import build_dataset

input_path = "pasta_com_audio_bruto"
output_path = "pasta_para_salvar_csv_e_segmentos_de_audio"

build_dataset(input_path, output_path)
```

#### Normalização Textual
```
from TTS_Utils import normalize_text

texto = "Exemplo de texto com números: 10, 20.5, 30kg e 40%"
normalizado = normalize_text(texto)
# Saída: "Exemplo de texto com números dez, vinte vírgula cinco, trinta quilos e quarenta por cento."
```
### Métricas de Avaliação 

```
from TTS_Utils.metrics import UTMOS, SECS, CER


audio_gerado = 'audios/audiogerado.wav'
voz_referencia = 'audios/voz.wav'
prompt = 'o rato roeu a roupa do rei de roma'

# UTMOS (Universal Text-to-Speech MOS)
# Avalia a qualidade perceptual de um áudio gerado por TTS.
utmos_score = UTMOS(audio_gerado)
# Saída: score numérico representando a qualidade subjetiva.

# SECS (Short-Time Energy Correlation Similarity)
# Mede a similaridade energética entre o áudio gerado e o áudio de referência.
secs_score = SECS(voz_referencia, audio_gerado)
# Saída: valor de similaridade entre -1 e 1.

# CER (Character Error Rate)
# Calcula a taxa de erro por caractere entre a transcrição esperada e a reconhecida a partir do áudio gerado.
cer_value = CER(audio_gerado, prompt)
# Saída: valor percentual indicando o quanto os textos diferem.

```
### Próximos passos 
- Melhorias no módulo de normalização textual, garantindo a corretude e precisão da normalização de uma maior variedade de frases e abreviações.
- Melhorias no módulo de construção automática de datasets, ampliando corretude, desempenho e quantidade de línguas, por exemplo.
- Adição de novas métricas de avaliação.
- Adição de outros módulos utilitários, como a normalização textual inversa.

## 💻 Quem somos
| ![LogoRAIA](https://github.com/user-attachments/assets/ce3f8386-a900-43ff-af84-adce9c17abd2) |  Este projeto foi desenvolvido pelos membros do **RAIA (Rede de Avanço de Inteligência Artificial)**, uma iniciativa estudantil do Instituto de Ciências Matemáticas e de Computação (ICMC) da USP - São Carlos. Somos estudantes que compartilham o objetivo de criar soluções inovadoras utilizando inteligência artificial para impactar positivamente a sociedade. Para saber mais, acesse [nosso site](https://gruporaia.vercel.app/) ou [nosso Instagram](instagram.com/grupo.raia)! |
|------------------|-------------------------------------------|

### Desenvolvedores
- **Antonio Carlos** - [LinkedIn](https://www.linkedin.com/in/ant%C3%B4nio-carlos-micheli-b10bb4289/) | [GitHub](https://github.com/Antonioonet)
- **Arthur Trottmann** - [LinkedIn](https://www.linkedin.com/in/arthur-ramos-9b81b9201/) | [GitHub](https://github.com/ArthurTRamos)
- **Caio Petroncini** - [LinkedIn](https://www.linkedin.com/in/caio-petroncini-7105941aa/) | [GitHub](https://github.com/Petroncini)
- **Lucas Brandão** - [LinkedIn](https://www.linkedin.com/in/lucas-de-souza-brandão-590b1228b/) | [GitHub](https://github.com/sb-lucas)
- **Pedro Soares** - [LinkedIn](https://www.linkedin.com/in/pedro-soares-b3625b238/) | [GitHub](https://github.com/pedrsrs)
