from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class InputRequest(_message.Message):
    __slots__ = ["inputs"]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    inputs: str
    def __init__(self, inputs: _Optional[str] = ...) -> None: ...

class InputResponse(_message.Message):
    __slots__ = ["outputs"]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    outputs: str
    def __init__(self, outputs: _Optional[str] = ...) -> None: ...

class LoadRequest(_message.Message):
    __slots__ = ["bitfileName"]
    BITFILENAME_FIELD_NUMBER: _ClassVar[int]
    bitfileName: str
    def __init__(self, bitfileName: _Optional[str] = ...) -> None: ...

class LoadResponse(_message.Message):
    __slots__ = ["message", "success"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
