import re

# Padroes principais de dados pessoais
CPF_REGEX = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b")
CPF_MASKED_REGEX = re.compile(r"\b(\*{3}|x{3})\.(\*{3}|x{3})\.(\*{3}|x{3})-(\*{2}|x{2})\b", re.IGNORECASE)
RG_REGEX = re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}\b")
RG_MASKED_REGEX = re.compile(r"\b(\*{1,2}|x{1,2})\.(\*{3}|x{3})\.(\*{3}|x{3})-(\*{1}|x{1})\b", re.IGNORECASE)
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
EMAIL_OBFUSCATED_REGEX = re.compile(r"\b[a-z0-9._%+-]+\s*(?:\(|\[)?\s*(at|arroba)\s*(?:\)|\])?\s*[a-z0-9.-]+\s*(?:\(|\[)?\s*(dot|ponto)\s*(?:\)|\])?\s*[a-z]{2,}\b", re.IGNORECASE)
PHONE_REGEX = re.compile(r"\b\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b")
PHONE_DDI_REGEX = re.compile(r"\+\d{1,3}\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b")
CEP_REGEX = re.compile(r"\b\d{5}-?\d{3}\b")
ADDRESS_REGEX = re.compile(r"\b(rua|avenida|av\.|travessa|alameda|quadra|lote|conjunto|bairro|bloco|apto|apartamento)\b", re.IGNORECASE)
ADDRESS_WITH_NUMBER_REGEX = re.compile(r"\b(rua|avenida|av\.|travessa|alameda|quadra|lote|conjunto|bairro|bloco|apto|apartamento)\s*\d{1,4}\b", re.IGNORECASE)
ADMIN_ADDRESS_REGEX = re.compile(r"\b(crn|shdf|shcn|sqs|sqn|sepn|sep|sds|srtvs|srtvn|sgan|sgas|soe|soes|sig)\b", re.IGNORECASE)
ADMIN_ADDRESS_WITH_NUMBER_REGEX = re.compile(r"\b(crn|shdf|shcn|sqs|sqn|sepn|sep|sds|srtvs|srtvn|sgan|sgas|soe|soes|sig)\s*\d{1,4}\b", re.IGNORECASE)
SEI_PROCESS_REGEX = re.compile(r"\b\d{5}-\d{8}/\d{4}-\d{2}\b")

# Campos explicitos costumam indicar dados pessoais
STRONG_FIELDS = [
    "cpf:",
    "rg:",
    "email:",
    "e-mail:",
    "telefone:",
    "celular:",
    "nome:",
    "endereço:",
    "endereco:",
    "oab:",
]

# Palavras-chave mais genericas
KEYWORDS = [
    "meu cpf",
    "meu rg",
    "meu nome",
    "meu endereço",
    "meu email",
    "meu e-mail",
    "telefone",
    "celular",
    "cadastro",
    "documento pessoal",
    "documentos pessoais",
    "meus documentos",
    "dados pessoais",
]


def has_personal_data(text: str) -> bool:
    # Interface simples para uso externo
    label, _ = label_and_weight(text)
    return label == "non_public"


def label_and_weight(text: str):
    # Retorna rotulo e peso de confianca
    t = text.lower()
    text_no_sei = SEI_PROCESS_REGEX.sub("", text)
    t_no_sei = text_no_sei.lower()
    # Excecoes institucionais (termos publicos que nao indicam PII)
    if re.search(r"\b(cadastro de entidades|entidades consignatarias|sigrh|lista atualizada|lista de ocorrencias|itens arremessados|estatisticas|edital|curso de formacao|ajuda financeira|consulta institucional)\b", t_no_sei):
        return "public", 1.0
    if re.search(r"\b(auto de infracao|auto de infracao demolitoria|prazo para recurso)\b", t_no_sei):
        return "public", 1.0
    if re.search(r"\b(nire|protocolo integrado|viabilidade)\b", t_no_sei):
        return "public", 1.0
    if CPF_REGEX.search(text_no_sei):
        return "non_public", 1.0
    if CPF_MASKED_REGEX.search(text_no_sei):
        return "non_public", 0.9
    if RG_REGEX.search(text_no_sei):
        return "non_public", 1.0
    if RG_MASKED_REGEX.search(text_no_sei):
        return "non_public", 0.9
    if EMAIL_REGEX.search(text_no_sei):
        return "non_public", 1.0
    if EMAIL_OBFUSCATED_REGEX.search(text_no_sei):
        return "non_public", 0.9
    if PHONE_REGEX.search(text_no_sei):
        return "non_public", 1.0
    if PHONE_DDI_REGEX.search(text_no_sei):
        return "non_public", 1.0
    if CEP_REGEX.search(text_no_sei) and ADDRESS_REGEX.search(text_no_sei):
        return "non_public", 1.0
    if ADDRESS_WITH_NUMBER_REGEX.search(text_no_sei):
        return "non_public", 0.8
    if ADMIN_ADDRESS_WITH_NUMBER_REGEX.search(text_no_sei):
        return "non_public", 0.8
    # Se for apenas numero de processo SEI sem outros sinais de PII, trate como publico
    if SEI_PROCESS_REGEX.search(text):
        return "public", 1.0
    if any(k in t_no_sei for k in STRONG_FIELDS):
        return "non_public", 0.9
    if any(k in t_no_sei for k in KEYWORDS):
        return "non_public", 0.6
    return "public", 1.0
