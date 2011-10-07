import validationrules as builder
import re
from qi.sqladmin import models as DB

class Expression:
    text=''
    def __init__(self):
        self.text=''
    def fits(self,text):
        raise Exception('unimplemented expression type')
    def buildValue(self,otherMeasures):
        raise Exception('unimplemented expression type')
        
class ComplexExpression(Expression):
    def buildSelf(self,text):
        raise Exception('unimplemented expression type')


class EmptyExpression(Expression):
    def fits(self, text):
        return text==''
    def buildValue(self,otherMeasures):
        return None
    def buildName(self,otherMeasures):
        return ''

numberFormat=re.compile('^[0-9]+(\\.[0-9]+)?$')
class NumericExpression(Expression):
    
    
    def fits(self,text):
        return numberFormat.match(text)
    def buildValue(self,otherMeasures):
        return float(self.text)
    def buildName(self, otherMeasures):
        return self.text

stringFormat=re.compile('^\"[^\"]*\"$')
class StringExpression(Expression):
    
    
    def fits(self,text):
        return stringFormat.match(text)
    def buildValue(self, otherMeasures):
        return self.text[1:-1]
    def buildName(self, otherMeasures):
        return self.text[1:-1]


parenFormat=re.compile('^\\(.*\\)$')
class ParentheticalExpression(ComplexExpression):
    contents=None
    def fits(self, text):
        tokens=builder.getParenTokens(text.split('"'))
        if len(tokens)!=3:
            return False
        # on top of not being allowed to have more than 3
        #it must start and end with a parenthesis
        return parenFormat.match(text)
    def buildValue(self, otherMeasures):
        return self.contents.buildValue(otherMeasures)
    def buildSelf(self, text):
        self.contents=None
        text=text.strip()
        innerval=text[1:len(text)-1]
        self.contents=builder.buildExpression(innerval)
    def buildName(self,ptherMeasures):
        return '(%s)'%self.contents.buildName(otherMeasures)

#this is abstract
class OperatorExpression(ComplexExpression):
    operator='--X--'
    def __init__(self):
        ComplexExpression.__init__(self)
        self.operands=[]
    def fits(self, text):
        if self.operator=='--X--':
            raise Exception('expression not implemented')
        tokens=builder.splitIgnoringStringsAndParens(text,self.operator)
        if len(tokens)>1:
            return True
        return False
    def buildValue(self, otherMeasures):
        return self.combine(otherMeasures, self.operands)
    def buildName(self,otherMeasures):
        names=[operand.buildName(otherMeasures) for operand in self.operands]
        return self.operator.join(names)
    def combine(self, otherMeasures, operands):
        raise Exception('expression not implemented')
    
    def buildSelf(self, text):
        self.operands=[]
        tokens=builder.splitIgnoringStringsAndParens(text,self.operator)
        for token in tokens:
            self.operands.append(builder.buildExpression(token))
    
class AddExpression(OperatorExpression):
    operator='+'
    def combine(self,otherMeasures,operands):
        result=0.0
        for value in operands:
            result+=float(value.buildValue(otherMeasures))
        return result


class MultiplyExpression(OperatorExpression):
    operator='*'
    def combine(self,otherMeasures,operands):
        result=1.0
        for value in operands:
            result*=float(value.buildValue(otherMeasures))
        return result

class SubtractExpression(OperatorExpression):
    operator='-'
    def combine(self,otherMeasures,operands):
        result=operands[0].buildValue(otherMeasures)
        
        for value in operands[1:]:
            result-=float(value.buildValue(otherMeasures))
        return result

class DivideExpression(OperatorExpression):
    operator='/'
    def combine(self,otherMeasures,operands):
        result=operands[0].buildValue(otherMeasures)
        
        for value in operands[1:]:
            result/=float(value.buildValue(otherMeasures))
        return result
