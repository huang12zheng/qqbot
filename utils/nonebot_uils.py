from typing import Any, Dict, Union, TypeVar, Optional, Callable, NoReturn, Awaitable, TYPE_CHECKING
from typing import Set, List, Type, Tuple
from nonebot.typing import T_State, T_StateFactory, T_Handler, T_RuleChecker
from nonebot.rule import Rule, startswith, endswith, keyword, command, regex
from nonebot import on_command
if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event

def commandHandle(cmd: Union[str, Tuple[str, ...]],
               rule: Optional[Union[Rule, T_RuleChecker]] = None,
               aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None):
    _ = on_command(cmd,rule=rule,aliases=aliases)
    return _.handle()