import expressions as exp
import rules


knownSimpleExpressions=(exp.NumericExpression, \
    exp.EmptyExpression, exp.StringExpression,)
#insert with a mind to order of operations
knownComplexExpressions=(exp.ParentheticalExpression,exp.MultiplyExpression,\
    exp.DivideExpression,exp.AddExpression,exp.SubtractExpression)


def getParenTokens(stringed):
    resultTokens=[]
    i=0
    depth=0
    leftover=''
    for token in stringed:
        if i%2==0:
            dividingpoints=[]
            c=0
            for char in token:
                if char=='(':
                    if depth>0:
                        depth+=1
                    else:
                        dividingpoints.append(c)
                        depth=1
                if char==')':
                    depth-=1
                    if depth<0:
                        raise ValueError()
                    if depth==0:
                        dividingpoints.append(c+1)
                        
                c+=1

            if len(dividingpoints)==0:
                leftover+=token
            else:
                added=leftover+token[0:dividingpoints[0]]
                resultTokens.append(added)
                if len(dividingpoints)>1:
                    for j in range(len(dividingpoints)-1):
                        added=token[dividingpoints[j]:dividingpoints[j+1]]
                        resultTokens.append(added)
                begin=dividingpoints[len(dividingpoints)-1]
                end=len(token)
                leftover=token[begin:end]
                
        else:
            leftover+='"%s"'%token
        i+=1
    if depth>0:
        raise ValueError()
    resultTokens.append(leftover)
    return resultTokens
                    

def processNonStringToken(resultTokens, lasttoken, token, tokenizer):
    items=token.split(tokenizer)
    if len(items)==1:
        lasttoken+=items[0]
    elif len(items)==2:
        resultTokens.append(lasttoken+items[0])
        lasttoken=items[1]
    else:
        resultTokens.append(lasttoken+items[0])
        for item in items[1:len(items)-1]:
            resultTokens.append(item)
        lasttoken=items[len(items)-1]
    return lasttoken

def splitIgnoringStringsAndParens(text,tokenizer):
    text=text.strip()
    tokens=text.split('"')
    try:
        parentokens=getParenTokens(tokens)
    except ValueError:
        raise InvalidExpression(text)
    i=0
    resultTokens=[]
    lasttoken=''
    for ptoken in parentokens:
        #outside a paren 
        if i % 2 == 0:
            items=ptoken.split('"')
            j=0
            for item in items:
                if j % 2 == 0:
                #not inside  quote
                    lasttoken=processNonStringToken(resultTokens, \
                            lasttoken,item, tokenizer)
                else:
                    lasttoken+='"%s"'%item
                j+=1
        else:
            lasttoken+=ptoken
        i=i+1
    resultTokens.append(lasttoken)
    return resultTokens
    


class InvalidExpression(Exception):
    text=''
    def __init__(self, text):
        self.text=text

def buildExpression(text):
    text=text.strip()
    for expression in knownSimpleExpressions:
        fitter=expression()
        if fitter.fits(text):
            resultExpression=fitter
            resultExpression.text=text
            return resultExpression
    for expression in knownComplexExpressions:
        fitter=expression()
        if fitter.fits(text):
            resultExpression=fitter
            resultExpression.buildSelf(text)
            resultExpression.text=text
            return resultExpression
    raise InvalidExpression(text)
    #if we get this far, and no valid expression
    #we've got something that ISN'T an expression
    

def buildExpressions(text):
    expressionTexts=splitIgnoringStringsAndParens(text.strip(),',')
    expressions=[]
    for ex in expressionTexts:
        expression=buildExpression(ex.strip())
        if not isinstance(expression, exp.EmptyExpression):
            expressions.append(expression)
    return expressions

knownRules=(rules.ParentheticalRule,rules.OrRule,rules.AndRule, rules.EqualRule, \
    rules.TrueRule,rules.PercentRule,rules.IntegerRule,rules.NumberRule,\
    rules.DateRule, rules.BeforeDateRule, rules.AfterDateRule, \
    rules.MinRule, rules.MaxRule, rules.InRule, rules.BetweenRule, \
    rules.StateRule, rules.ZipRule, rules.PhoneRule, rules.EmailRule, \
    rules.RequiredRule,rules.NotRule, rules.WarnRule, rules.SilentRule)
    
def buildRule(text):
    text=text.strip()
    for rule in knownRules:
        fitter=rule()
        if(fitter.fits(text)):
            fitter.buildSelf(text)
            return fitter
    print text
    raise InvalidExpression(text)
