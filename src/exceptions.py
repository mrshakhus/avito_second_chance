from fastapi import HTTPException, status

class TenderAPIException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class UserIsNotPresentException(TenderAPIException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Пользователь не существует или некорректен."

class AccessDeniedException(TenderAPIException):
    status_code=status.HTTP_403_FORBIDDEN
    detail="Недостаточно прав для выполнения действия."

class AbsentTenderException(TenderAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Тендер не найден."

class AbsentBidException(TenderAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Предложение не найдено."

class AbsentVersionException(TenderAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Версия не найдена."