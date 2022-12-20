
# _*_ coding:utf-8 _*_

import ast
from ast import *
from .propgraph import *

class AstOp (NodeTransformer):
    def __init__(self, Tmpt):
        self.Tmpt = Tmpt
        self.pG   = None

        self.InitPg ()

    def InitPg (self):
        pG = PropGraph ()
        pG.Build (self.Tmpt)
        
    def visit(self, node):
        if node is None:
            return

        method = 'op_' + node.__class__.__name__.lower()
        operator = getattr(self, method, self.generic_visit)        
        return operator(node)

    def op_new_value (self, name):
        return Name(id=name, ctx=Load())

    def op_value (self, node):
        pass
    
    def op_return(self, node):
        print (ast.dump (node), end="\n\n")
    
    def op_assign(self, node):
        print (ast.dump (node), end="\n\n")

        for tg in node.targets:
            self.visit (tg)
        
        self.visit (node.value)

    def op_atrribute (self, node):
        print (ast.dump (node), end="\n\n")

    def op_call(self, node):
        print (ast.dump (node.func), end="\n\n")
        if isinstance(node.func, Attribute):
            self.visit (node.func)
        elif isinstance(node.func, Name):
            callee = self.GetId (node.func)         
        else:
            raise Exception("pg_call -> Unsupport!!!")
    
    def op_functiondef (self, node):
        print (ast.dump (node), end="\n\n")
        self.get_fargs (node)
        for st in node.body:
            self.visit (st)

    def op_classdef(self, node):
        print (ast.dump (node), end="\n\n")
        for st in node.body:
            self.visit (st)

class ClassOp(AstOp):
    def __init__(self, ClsName, FuncAst, Op):
        super(AstOp, self).__init__()
        self.ClsName = ClsName
        self.FuncAst = FuncAst
        self.Op      = Op

    def op_functiondef (self, node):
        print (ast.dump (node))

        arg = self.get_arg (node)
        callee = self.FuncAst.body[0].value
        callee.args = [arg]
        
        node.body = self.FuncAst.body
        return node

    def op_classdef(self, node):
        if self.ClsName != node.name:
            return

        if self.Op == 'INSERT_CALL':
            for st in node.body:
                self.visit (st)
        
        return node


class FuncOp(AstOp):
    def __init__(self, FuncName, UnitAst, Op):
        super(AstOp, self).__init__()
        self.UnitAst = UnitAst
        self.FuncName = FuncName
        self.Op = Op

    def op_for (self, node, argS, argE):
        if isinstance (node.iter, Call):
            callee = node.iter
            if callee.func.id == 'range':
                callee.args = [argS, argE]
        return node
    
    def op_functiondef (self, node):
        if node.name != self.FuncName:
            return node

        if self.Op == 'INSERT_FOR':
            forAst = self.op_for (self.UnitAst.body[0], Constant(value=0), self.get_arg(node))

            oldBody = node.body
            forAst = self.UnitAst.body[0]

            oldBody[0].value.args = [forAst.target]
            forAst.body = oldBody
            
            node.body = self.UnitAst.body

        elif self.Op == 'INSERT_ENTRY':
            enAst = self.UnitAst.body[0]
            node.body = self.UnitAst.body + node.body
        
        return node



class NewOO(AstOp):
    OOTmpt = \
"""
class demoCls:
    def __init__(self):
        pass

    def demoFunc1(self, arg1):
        pass

def RunFuzzer (x):
    dc = demoCls ()
    dc.demoFunc1 (x)
"""
    def __init__(self):
        super(NewOO, self).__init__(NewOO.OOTmpt)
        