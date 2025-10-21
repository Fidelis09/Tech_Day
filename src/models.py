# models.py
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Brinquedo:
    id: int  # Adicionar o ID
    nome: str
    tamanho: str
    preco: float
    faixa_etaria: str
    imagem: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Agendamento:
    id: int  # <-- ADICIONADO
    nome: str
    telefone: str
    dia: int
    mes: int
    ano: int
    inicio: int
    fim: int
    brinquedos: List[str]
    valor_total: float

    def to_dict(self):
        return asdict(self)