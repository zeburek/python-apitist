"""
Author: Parviz Khavari
Email: me@parviz.pw

This file is created in order to provide a better experience while using
standard Python `ast` library.

It should give you an easier way to create python code using standart AST
classes.
"""

import ast
import typing as t
from enum import IntEnum


class Conversions(IntEnum):
    NO_FORMATTING = -1
    STRING_FORMATTING = 115
    REPR_FORMATTING = 114
    ASCII_FORMATTING = 97


def _empty_list(value):
    return value or []


# Literals


def Num(n):
    return ast.Num(n=n)


def Str(s):
    return ast.Str(s=s)


def FormattedValue(value, conversion: Conversions, format_spec):
    return ast.FormattedValue(
        value=value, conversion=conversion, format_spec=format_spec
    )


def JoinedStr(values: t.List[t.Union[ast.Str, ast.FormattedValue]]):
    return ast.JoinedStr(values=values)


def Bytes(s):
    return ast.Bytes(s=s)


def List(elts: t.List, ctx: t.Union[ast.Load, ast.Store]):
    return ast.List(elts=elts, ctx=ctx)


def Tuple(elts: t.List, ctx: t.Union[ast.Load, ast.Store]):
    return ast.Tuple(elts=elts, ctx=ctx)


def Set(elts: t.List):
    return ast.Set(elts=elts)


def Dict(keys: t.List, values: t.List):
    return ast.Dict(keys=keys, values=values)


# Variables


def Name(id: str, ctx: t.Union[ast.Load, ast.Store, ast.Del] = ast.Load()):
    return ast.Name(id=id, ctx=ctx)


def Starred(
    value: str, ctx: t.Union[ast.Load, ast.Store, ast.Del] = ast.Store()
):
    return ast.Starred(value=value, ctx=ctx)


# Expressions


def Expr(value):
    return ast.Expr(value=value)


def UnaryOp(op, operand):
    return ast.UnaryOp(op=op, operand=operand)


def BinOp(left, op, right):
    return ast.BinOp(left=left, op=op, right=right)


def BoolOp(op, values: t.List):
    return ast.BoolOp(op=op, values=values)


def Compare(left, ops: t.List, comparators: t.List):
    return ast.Compare(left=left, ops=ops, comparators=comparators)


def Call(
    func: t.Union[ast.Name, ast.Attribute],
    args: t.List = None,
    keywords: t.List[ast.keyword] = None,
):
    args = _empty_list(args)
    keywords = _empty_list(keywords)
    return ast.Call(func=func, args=args, keywords=keywords)


def keyword(arg, value):
    return ast.keyword(arg=arg, value=value)


def IfExp(test, body, orelse):
    return ast.IfExp(test=test, body=body, orelse=orelse)


def Attribute(
    value, attr, ctx: t.Union[ast.Load, ast.Store, ast.Del] = ast.Load()
):
    return ast.Attribute(value=value, attr=attr, ctx=ctx)


# Statements


def Assign(targets, value):
    return ast.Assign(targets=targets, value=value)


# Imports


def Import(names: t.List[t.Union[ast.alias, t.Tuple]]):
    names = [alias(*n) if isinstance(n, t.Tuple) else n for n in names]
    return ast.Import(names=names)


def ImportFrom(
    module: str, names: t.List[t.Union[ast.alias, t.Tuple]], level: int = 0
):
    names = [alias(*n) if isinstance(n, t.Tuple) else n for n in names]
    return ast.ImportFrom(module=module, names=names, level=level)


def alias(name: str, asname: str = None):
    return ast.alias(name=name, asname=asname)


# Function and class definitions


def FunctionDef(
    name: str,
    args: ast.arguments = None,
    body: t.List = None,
    decorator_list: t.List = None,
    returns=None,
):
    if args is None:
        args = arguments()
    body = _empty_list(body)
    decorator_list = _empty_list(decorator_list)
    return ast.FunctionDef(
        name=name,
        args=args,
        body=body,
        decorator_list=decorator_list,
        returns=returns,
    )


def Lambda(args: ast.arguments = None, body=None):
    return ast.Lambda(args=args, body=body)


def arguments(
    args: t.List[ast.arg] = None,
    vararg: ast.arg = None,
    kwonlyargs: t.List[ast.arg] = None,
    kwarg: ast.arg = None,
    defaults: t.List = None,
    kw_defaults: t.List = None,
):
    args = _empty_list(args)
    kwonlyargs = _empty_list(kwonlyargs)
    defaults = _empty_list(defaults)
    kw_defaults = _empty_list(kw_defaults)
    return ast.arguments(
        args=args,
        vararg=vararg,
        kwonlyargs=kwonlyargs,
        kwarg=kwarg,
        defaults=defaults,
        kw_defaults=kw_defaults,
    )


def arg(arg: str, annotation=None):
    return ast.arg(arg=arg, annotation=annotation)


def Return(value):
    return ast.Return(value=value)


def Yield(value):
    return ast.Yield(value=value)


def YieldFrom(value):
    return ast.YieldFrom(value=value)


def Global(names: t.List[str]):
    return ast.Global(names=names)


def Nonlocal(names: t.List[str]):
    return ast.Nonlocal(names=names)


def ClassDef(
    name: str,
    bases: t.List = None,
    keywords: t.List = None,
    body: t.List = None,
    decorator_list: t.List = None,
):
    bases = _empty_list(bases)
    keywords = _empty_list(keywords)
    body = _empty_list(body)
    decorator_list = _empty_list(decorator_list)
    return ast.ClassDef(
        name=name,
        bases=bases,
        keywords=keywords,
        body=body,
        decorator_list=decorator_list,
    )
