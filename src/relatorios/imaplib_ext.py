from datetime import datetime
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from imaplib import IMAP4_SSL


class IMAP4_SSL_EXT(IMAP4_SSL):
    '''
    Funções customizadas da biblioteca imaplib
    '''

    # mais informações em:
    # RFC2060, código fonte do imaplib, e documentação do imaplib

    def uid_fetch_datetime(self, uid: str) -> datetime:
        '''
        solicita a data do servidor imap e retorna um objeto datetime
        '''

        query = "(BODY[HEADER.FIELDS (DATE)])"
        date: bytes = self.uid('FETCH', uid, query)[1][0][1]
        # formato da resposta: (rsp, [(data_key, data_value), ...])

        return parsedate_to_datetime(date.strip()[6:].decode())

    def uid_search_filename(self, filename: str, remetente: str) -> str:
        '''
        Solicita mensagens cujo anexo têm o nome especificado 
        e retorna o UID da mensagem mais recente.
        '''

        self.literal = bytes(f"Filename={filename}", 'utf-8') # type: ignore
        query = f"CHARSET UTF-8 FROM \"{remetente}\" BODY"
        uids: bytes = self.uid('SEARCH', query)[1][0]
        #formato da resposta: (rsp, [uids])

        try:
            return uids.split()[-1].decode()
        except IndexError:
            return ''

    def uid_fetch_payload(self, uid: str) -> bytes | None:
        """
        salva arquivo baixado no caminho configurado.
        """

        data = self.uid('FETCH', uid, "(RFC822)")[1][0][1]
        #formato da resposta: (rsp, [(data_key, data_value), ...])

        email_message = message_from_bytes(data)
        for part in email_message.walk():
            if (part.get_content_maintype() == "multipart"
                    or part.get("Content-Disposition") is None):
                continue
            payload = part.get_payload(decode=True)
            return payload if isinstance(payload, bytes) else None
