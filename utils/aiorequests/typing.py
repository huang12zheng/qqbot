from typing import (Any, Callable, Dict, Iterable, List, NamedTuple, Optional,
                    Set, Tuple, Union)

from aiocqhttp import Event as CQEvent
from nonebot import (CommandSession, CQHttpError, Message, MessageSegment,
                     NLPSession, NoticeSession, RequestSession)

import requests
from requests import *