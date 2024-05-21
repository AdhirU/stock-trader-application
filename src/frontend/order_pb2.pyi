from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LeaderDetails(_message.Message):
    __slots__ = ["hostname", "id", "port"]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    hostname: str
    id: int
    port: str
    def __init__(self, id: _Optional[int] = ..., hostname: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

class LiveCheck(_message.Message):
    __slots__ = ["code"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: int
    def __init__(self, code: _Optional[int] = ...) -> None: ...

class NewOrders(_message.Message):
    __slots__ = ["latestOrder", "missingOrders"]
    LATESTORDER_FIELD_NUMBER: _ClassVar[int]
    MISSINGORDERS_FIELD_NUMBER: _ClassVar[int]
    latestOrder: int
    missingOrders: str
    def __init__(self, latestOrder: _Optional[int] = ..., missingOrders: _Optional[str] = ...) -> None: ...

class OrderDetails(_message.Message):
    __slots__ = ["orderNumber", "quantity", "stockName", "type"]
    ORDERNUMBER_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    orderNumber: int
    quantity: int
    stockName: str
    type: str
    def __init__(self, orderNumber: _Optional[int] = ..., stockName: _Optional[str] = ..., type: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class OrderNumber(_message.Message):
    __slots__ = ["orderNumber"]
    ORDERNUMBER_FIELD_NUMBER: _ClassVar[int]
    orderNumber: int
    def __init__(self, orderNumber: _Optional[int] = ...) -> None: ...

class ResponseMessage(_message.Message):
    __slots__ = ["code", "message", "transactionNumber"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONNUMBER_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    transactionNumber: int
    def __init__(self, code: _Optional[int] = ..., transactionNumber: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class Success(_message.Message):
    __slots__ = ["code"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: int
    def __init__(self, code: _Optional[int] = ...) -> None: ...

class TradeDetails(_message.Message):
    __slots__ = ["N", "stockName", "type"]
    N: int
    N_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    stockName: str
    type: str
    def __init__(self, stockName: _Optional[str] = ..., N: _Optional[int] = ..., type: _Optional[str] = ...) -> None: ...
