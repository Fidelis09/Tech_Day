# utils.py
def validar_data(dia, mes, ano):
    try:
        dia, mes, ano = int(dia), int(mes), int(ano)
        return 1 <= dia <= 31 and 1 <= mes <= 12 and ano >= 2024
    except:
        return False
