import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import NamedTuple

from .helpers import expand_config_variables
from .imaplib_ext import IMAP4_SSL_EXT

TZINFO_BR = timezone(timedelta(hours=-3))
DT_FMT = "%c UTC%z"


def baixa_relatorios(config_path: str):
    """
    Script que mantém o histórico de atualizações para evitar downloads desnecessários
    """
    with open(Path(config_path).resolve(), "r", encoding="utf-8") as fp:
        config = json.load(fp)

    history_path = Path(config["history_path"]).resolve()
    history = History(history_path)

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
                remetente = file["remetente"]
                save_path = file["path"]
            except KeyError as ex:
                print(f"[{idx}]->{ex}: atributo obrigatório não encontrado")
                continue

            print(f"\u001b[35m[{filename}]\u001b[0m")

            uid = gmail.uid_search_filename(filename, remetente)
            if not uid:
                print("o servidor não encontrou este arquivo")
                continue

            save_as = file.get("save_as")
            save_path = Path(save_path) / (save_as if save_as else filename)
            save_path = save_path.resolve()

            last_email_date = gmail.uid_fetch_datetime(uid)
            history_date = history.get_email_date(filename)
            print(f"última atualização: {history_date.strftime(DT_FMT)} \u001b[33m[{datetime.now(TZINFO_BR) - history_date}]\u001b[0m")
            if file.get("always_save"):
                print("sempre é baixado")
            elif save_path.is_file() and last_email_date <= history_date:
                print("\033[33mjá está atualizado\u001b[0m")
                continue
            else:
                print("está desatualizado")

            payload: bytes | None = gmail.uid_fetch_payload(uid)
            if not payload:
                print(f"o servidor não retornou dados\t UID: {uid}")
                continue

            save_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"salvando \"{filename}")
            try:
                with open(save_path, "wb") as fp:
                    fp.write(payload)
            except PermissionError:
                print("\033[31mPermissionError\u001b[0m: Verifique se o arquivo está aberto em algum computador")
                print(f"\033[31m{filename} não foi atualizado\u001b[0m")
                continue

            print("\033[32matualizado\u001b[0m")
            if file.get("after_save"):
                file["after_save"](save_path, file)

            history.update(filename, last_email_date)

    print("")
    history.save_to_file()


class HistoryInfo(NamedTuple):
    filename: str
    email_date: datetime = datetime(1000, 1, 1, tzinfo=TZINFO_BR)
    update_date: datetime = datetime(1000, 1, 1, tzinfo=TZINFO_BR)


class History:
    """
    Objeto de histórico mantém dados das últimas atualizações e salva em um arquivo json.
    """

    def __init__(self, history_path: Path):
        self.path = history_path

        if self.path.is_file():
            print("histórico encontrado")
            self.list = self.__from_file()
        else:
            print("histórico não foi encontrado. criando novo...")
            self.list = []

    def __from_file(self) -> list[HistoryInfo]:
        with open(self.path, encoding="utf-8") as fp:
            hist = [
                HistoryInfo(
                    file["filename"],
                    datetime.strptime(file["email_date"], DT_FMT),
                    datetime.strptime(file["update_date"], DT_FMT),
                )
                for file in json.load(fp)
            ]
        return hist

    def save_to_file(self):
        print("histórico está sendo salvo.")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fp:
            save_list = [
                {
                    "filename": val.filename,
                    "email_date": val.email_date.strftime(DT_FMT),
                    "update_date": val.update_date.strftime(DT_FMT),
                }
                for val in self.list
            ]
            json.dump(save_list, fp, indent=4)

        print("histórico foi salvo.")

    def update(self, filename: str, date: datetime) -> None:
        updated_file = HistoryInfo(
            filename,
            date,
            datetime.now(TZINFO_BR),
        )

        if any(file.filename == filename for file in self.list):
            self.list = [
                (updated_file if file.filename == filename else file)
                for file in self.list
            ]
        else:
            self.list.append(updated_file)

    def get_email_date(self, filename) -> datetime:
        try:
            file: HistoryInfo = [
                *filter(lambda val: val.filename == filename, self.list)
            ][0]

            return file.email_date
        except IndexError:
            print("não foi encontrado no histórico")
            return datetime(1000, 1, 1, tzinfo=TZINFO_BR)
