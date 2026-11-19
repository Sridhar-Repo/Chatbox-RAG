from fastapi import Request
from fastapi.responses import JSONResponse

from ..services.errors import (DomainError, EmptyDocument, FileTooLarge, InvalidQuestion,
                               UnreadableFile, UnsupportedFileType)

STATUS = {
    UnsupportedFileType: 400, UnreadableFile: 400, EmptyDocument: 400,
    InvalidQuestion: 400, FileTooLarge: 413,
}


async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=STATUS.get(type(exc), 400))
