# from datetime import datetime
from datetime import datetime
import re
from pathlib import Path

# funções auxiliares para as outras funções do programa.

def rename_after_save(save_path: Path, file: dict):
    with open(save_path, 'r', encoding=file.get("encoding", "utf-8")) as fp:
        mask = r"\"(?P<mes>\w+)/(?P<ano>\d{4})\""
        month = re.search(mask, fp.read())
    
    if month is not None:
        month_ref = month.group(0).replace("/", "-").replace("\"", "")
        
        name_updated = Path(file["path"]) / f"{save_path.stem} {month_ref}{save_path.suffix}"
        save_path.replace(name_updated)

        print(f"({__name__}.rename_after_save): renomeado")

def expand_config_variables(file_config: dict, remetentes: list[str] | None) -> dict:
    expanded_file = {}
    for key, value in file_config.items():
        if not isinstance(value, str):
            expanded_file[key] = value
            continue

        # SUBSTITUI A VARIAVEL PELO ANO ATUAL
        expanded_file[key] = re.sub(
            r"\$\{THISYEAR\}", datetime.now().year.__str__(), value
        )

        # SUBSTITUI VARIAVEL PELA FUNCAO RENAME_AFTER_SAVE
        if value == "${RENAME_AFTER_SAVE}":
            expanded_file[key] = rename_after_save

        if not remetentes:
            return expanded_file

        match = re.search(r"\$\{REMETENTE\.([0-9]*)\}", value)
        if match:
            expanded_file[key] = remetentes[int(match[1])]
    return expanded_file

# def to_date_text(dt: datetime) -> str:
#     # Transforma no formato de data para o comando search da RFC2060
#     month = [
#         '', "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
#         "Nov", "Dec"
#     ]
#     return f"{dt.day}-{month[dt.month]}-{dt.year:04}"
