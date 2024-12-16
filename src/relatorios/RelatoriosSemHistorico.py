import json
from pathlib import Path

from .helpers import expand_config_variables
from .imaplib_ext import IMAP4_SSL_EXT


def baixa_sem_historico(config_path: str):
    """
    Script que não verifica nem salva histórico
    """

    with open(Path(config_path).resolve(), "r", encoding="utf-8") as fp:
        config = json.load(fp)

    file_list = map(
        lambda file: expand_config_variables(file, config.get("remetentes")),
        config["file_list"],
    )

    with IMAP4_SSL_EXT("imap.gmail.com") as gmail:
        gmail.login(config["username"], config["password"])
        gmail.select("inbox")

        for idx, file in enumerate(file_list):
            print("")

            try:
                filename = file["filename"]
                save_path = file["path"]
                remetente = file["remetente"]
            except KeyError as ex:
                print(f"[{idx}]->{ex}: atributo obrigatório não encontrado")
                continue

            print(f"\u001b[35m[{filename}]\u001b[0m")
            uid = gmail.uid_search_filename(filename, remetente)
            if not uid:
                print("o servidor não encontrou este arquivo")
                continue

            payload: bytes | None = gmail.uid_fetch_payload(uid)
            if not payload:
                print(f"o servidor não retornou dados\t UID: {uid}")
                continue

            save_as = file.get("save_as")
            save_path = Path(save_path) / (save_as if save_as else filename)
            save_path = save_path.resolve()

            save_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"salvando \"{filename}\"")
            try:
                with open(save_path, "wb") as fp:
                    fp.write(payload)
            except PermissionError:
                print("\033[31mPermissionError\u001b[0m: Verifique o arquivo está aberto em algum computador")
                print(f"\033[31m{filename} não foi atualizado\u001b[0m")
                continue

            print("\033[32matualizado\u001b[0m")

            if file.get("after_save"):
                file["after_save"](save_path, file)
