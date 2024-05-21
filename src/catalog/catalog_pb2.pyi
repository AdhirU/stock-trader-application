from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StockDetails(_message.Message):
    __slots__ = ["price", "quantity"]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    price: float
    quantity: int
    def __init__(self, price: _Optional[float] = ..., quantity: _Optional[int] = ...) -> None: ...

class StockName(_message.Message):
    __slots__ = ["stockName"]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    stockName: str
    def __init__(self, stockName: _Optional[str] = ...) -> None: ...

class SuccessMessage(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: int
    def __init__(self, message: _Optional[int] = ...) -> None: ...

class TradeDetails(_message.Message):
    __slots__ = ["N", "stockName", "type"]
    N: int
    N_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    stockName: str
    type: str
    def __init__(self, stockName: _Optional[str] = ..., N: _Optional[int] = ..., type: _Optional[str] = ...) -> None: ...
