import validationrules as builder
import expressions as exp
import re

class InvalidFunction(Exception):
    def __init__(self, text):
        self.text=text

class Rule(exp.ComplexExpression):
    noisy=True
    def __init__(self):
        self.params=[]
        self.paramValues=[]
        self.validationresult=10
        self.message=''
        self.notmessage='An error was detected'
    def validate(self, value, otherMeasures):
        self.validationResult=0
        self.message=''
        self.notmessage='An error occurred.  The error provided no help information.'
        self.paramValues=[]
        self.paramNames=[]
        for param in self.params:
            try:
                self.paramValues.append(param.buildValue(otherMeasures))
                self.paramNames.append(param.buildName(otherMeasures))
            except builder.MissingMeasureException, e:
                self.validationResult=10
                format='Measure %s is required in this data set.'
                self.message=format%e.measurename
                
        if self.validationResult < 10:
            self.validationResult=max(self.validationResult,self.runValidation(value,otherMeasures))
        return self.validationResult
    #override this
    def runValidation(self, value,otherMeasures):
        raise Exception('not implemented')
    def validation(self):
        return validationresult
    def getMessage(self):
        return self.message
    def getNotMessage(self):
        return self.notmessage

class TrueRule(Rule):
    def fits(self, text):
        return text=='' or text.upper()=='TRUE'
    def runValidation(self, value, otherMeasures):
        self.message='No error occurred'
        self.notmessage='An error occurred'
        return 0
    def buildSelf(self, text):
        #don't do anything
        pass

parenFormat=re.compile('^\\(.*\\)$')
class ParentheticalRule(Rule):
    contents=None
    def fits(self, text):
        tokens=builder.getParenTokens(text.split('"'))
        #this prevents things like (haha) + (ho ho)
        if len(tokens)!=3:
            return False
        # on top of not being allowed to have more than 3
        #it must start and end with a parenthesis
        return parenFormat.match(text)
    def runValidation(self,value, otherMeasures):
        result = self.contents.validate(value,otherMeasures)
        self.message=self.contents.message
        self.notmessage=self.contents.notmessage
        return result
    def buildSelf(self, text):
        self.contents=None
        text=text.strip()
        innerval=text[1:len(text)-1]
        self.contents=builder.buildRule(innerval)

class FunctionRule(Rule):
    functionName='--'
    def fits(self,text):
        #-- is a standin for invalid
        if self.functionName=='--':
            raise Exception('Rule not implemented')
        if text.startswith(self.functionName):
            remainder=text.split(self.functionName,1)[1].strip()
            if remainder.startswith('(') and remainder.endswith(')'):
                tokens=builder.getParenTokens(remainder.split('"'))
                #this prevents things like (haha) + (ho ho)
                if len(tokens)!=3:
                    return False
                return True
        return False
    def buildSelf(self,text):
        remainder=text.split(self.functionName,1)[1].strip()
        paramtext=remainder[1:len(remainder)-1]
        self.params=builder.buildExpressions(paramtext)
        if not self.enoughParams():
            raise InvalidFunction(text)
    def enoughParams(self):
        return True
        
class OperatorRule(Rule):
    operator='-X-'
    def __init__(self):
        Rule.__init__(self)
        self.operands=[]
        
    def fits(self, text):
        if self.operator=='-X-':
            raise Exception('rule not implemented')
        tokens=builder.splitIgnoringStringsAndParens(text,self.operator)
        if len(tokens)>1:
            return True
        return False
    def runValidation(self, value, otherMeasures):
        return self.validateTogether(value,otherMeasures,self.operands)
    def buildSelf(self,text):
        self.operands=[]
        tokens=builder.splitIgnoringStringsAndParens(text,self.operator)
        for token in tokens:
            self.operands.append(builder.buildRule(token))

        
class AndRule(OperatorRule):
    operator=' and '
    def validateTogether(self, value, otherMeasures, operands):
        currentresult=0
        self.message=''
        for rule in operands:
            result=rule.validate(value, otherMeasures)

            if result>currentresult or (result==10 and currentresult==10):
                currentresult=result
                self.message=rule.message
            
            if currentresult==10 and rule.noisy:
                return 10
        self.notmessage='All of the following were true:  '
        interiormessages=[x.notmessage for x in self.operands if x.noisy]
        self.notmessage+=' and '.join(interiormessages)
        return currentresult

class OrRule(OperatorRule):
    operator=' or '
    def __init__(self):
        OperatorRule.__init__(self)
    def validateTogether(self,value,otherMeasures, operands):
        first=True
        errorlevel=10
        for rule in operands:
            result=rule.validate(value, otherMeasures)
            if result==0:
                self.message=''
                self.notmessage=rule.notmessage
                return 0
            else:
                errorlevel=min(result,errorlevel)
            if rule.noisy:
                if first:
                    self.message=rule.message
                    first=False
                else:
                    self.message+=' and %s'%rule.message
        return errorlevel

class EqualRule(FunctionRule):
    functionName='equals'
    def runValidation(self,value,otherMeasures):
        #coercing strings as a consistent data type
        targetval=self.paramValues[0]
        if len(self.paramValues)>1:
            decimalpoints=int(self.paramValues[1])
            value=round(float(value),decimalpoints)
            targetval=round(float(targetval),decimalpoints)
        try:
            equal=str(float(value))==str(float(targetval))
        except (TypeError, ValueError):
            equal=str(value)==str(targetval)
        if equal:
            self.notmessage='%s is %s'%(value,targetval)
            return 0
        else:
            self.message='%s is not equal to %s'%(value, self.paramNames[0])
            return 10
    def enoughParams(self):
        return len(self.params)>0

class BetweenRule(FunctionRule):
    functionName='between'
    def runValidation(self,value,otherMeasures):
        format='%s is not between %s and %s'%(value, 
            self.paramNames[0],self.paramNames[1])
        try:
            value=float(value)
        except:
            self.message='%s is not a number'%value
            return 10
        if value<min(self.paramValues[0],self.paramValues[1]):
            self.message=format
            return 10
        if value>max(self.paramValues[0],self.paramValues[1]):
            self.message=format
            return 10
        self.notmessage='%s is between %s and %s'%(value, self.paramNames[0], self.paramNames[1])
        return 0
        
    def enoughParams(self):
        return len(self.params)==2

class InRule(FunctionRule):
    functionName='in'
    def runValidation(self,value,otherMeasures):
        if value in self.paramValues:
            self.notmessage='%s in %s'%(value,','.join([k for k in self.paramNames]))
            return 0
        if str(value) in self.paramValues:
            self.notmessage='%s in %s'%(value,','.join([k for k in self.paramNames]))
            return 0
        try:
            if float(value) in self.paramValues:
                self.notmessage='%s in %s'%(value,','.join([k for k in self.paramNames]))
                return 0
        except (TypeError, ValueError):
            pass
        self.message='%s is not one of the following: %s'%(value,', '.join([k for k in self.paramNames]))
        return 10
    def enoughParams(self):
        return len(self.params)>0
        
class MaxRule(FunctionRule):
    functionName='max'
    def runValidation(self,passedvalue,otherMeasures):
        try:
            value=float(passedvalue)
        except:
            self.message='%s is not a number'%passedvalue
            return 10
        if value>self.paramValues[0]:
            self.message='%s is larger than %s'%(passedvalue,self.paramNames[0])
            return 10
        self.notmessage='%s is not larger than %s'%(value,self.paramNames[0])
        return 0
    
    def enoughParams(self):
        return len(self.params)==1

states = \
("Alabama","Ala.","AL",
"Alaska","Alaska","AK",
"American Samoa","AS",
"Arizona","Ariz.","AZ",
"Arkansas","Ark.","AR",
"California","Calif.","CA",
"Colorado","Colo.","CO",
"Connecticut","Conn.","CT",
"Delaware","Del.","DE",
"District of Columbia","Dist. of Columbia","D.C.","DC",
"Florida","Fla.","FL",
"Georgia","Ga.","GA",
"Guam","Guam","GU",
"Hawaii","Hawaii","HI",
"Idaho","Idaho","ID",
"Illinois","Ill.","IL",
"Indiana","Ind.","IN",
"Iowa","Iowa","IA",
"Kansas","Kans.","KS",
"Kentucky","Ky.","KY",
"Louisiana","La.","LA",
"Maine","Maine","ME",
"Maryland","Md.","MD",
"Marshall Islands","MH",
"Massachusetts","Mass.","MA",
"Michigan","Mich.","MI",
"Micronesia","FM",
"Minnesota","Minn.","MN",
"Mississippi","Miss.","MS",
"Missouri","Mo.","MO",
"Montana","Mont.","MT",
"Nebraska","Nebr.","NE",
"Nevada","Nev.","NV",
"New Hampshire","N.H.","NH",
"New Jersey","N.J.","NJ",
"New Mexico","N.M.","NM",
"New York","N.Y.","NY",
"North Carolina","N.C.","NC",
"North Dakota","N.D.","ND",
"Northern Marianas","MP",
"Ohio","Ohio","OH",
"Oklahoma","Okla.","OK",
"Oregon","Ore.","OR",
"Palau","PW",
"Pennsylvania","Pa.","PA",
"Puerto Rico","P.R.","PR",
"Rhode Island","R.I.","RI",
"South Carolina","S.C.","SC",
"South Dakota","S.D.","SD",
"Tennessee","Tenn.","TN",
"Texas","Tex.","TX",
"Utah","Utah","UT",
"Vermont","Vt.","VT",
"Virginia","Va.","VA",
"Virgin Islands","V.I.","VI",
"Washington","Wash.","WA",
"West Virginia","W.Va.","WV",
"Wisconsin","Wis.","WI",
"Wyoming","Wyo.","WY",
)
states=[x.lower() for x in states]
class StateRule(FunctionRule):
    functionName='state'
    def runValidation(self,value,otherMeasures):
        try:
            value=str(value).strip()
        except:
            self.message='%s is not a state'%value
            return 10
        if value.lower() not in states:
            self.message='%s is not a state'%value
            return 10
        self.notmessage='%s is a state'%(value)
        return 0

    def enoughParams(self):
        return len(self.params)==0

class RegExpRule(FunctionRule):
    functionName='regexprule'
    checkexpression=re.compile('^$')
    def runValidation(self, value, otherMeasures):
        try:
            #eliminate decimals if we can
            value=str(int(value))
        except ValueError:
            try:
                value=str(value)
            except:
                self.message='%s is not %s.'%(value, self.expressiontype)
        if self.checkexpression.match(value):
            self.notmessage='%s is %s.'%(value, self.expressiontype)
            return 0
        self.message='%s is not %s.'%(value, self.expressiontype)
        return 10

class ZipRule(RegExpRule):
    functionName='zip'
    expressiontype='a zip code'
    checkexpression=re.compile('^[0-9]{5}$')

class PhoneRule(RegExpRule):
    functionName='phone'
    expressiontype='a phone number'
    checkexpression=re.compile('^\\([0-9]{3}\\) [0-9]{3}-[0-9]{4}$')

class EmailRule(RegExpRule):
    functionName='email'
    expressiontype='an email address'
    checkexpression=re.compile('^[A-Za-z][A-Za-z0-9_.-]*@[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+$')

class MinRule(FunctionRule):
    functionName='min'
    def runValidation(self,value,otherMeasures):
        try:
            value=float(value)
        except:
            self.message='%s is not a number'%value
            return 10
        if value<self.paramValues[0]:
            self.message='%s is smaller than %s'%(value,self.paramNames[0])
            return 10
        self.notmessage='%s is not smaller than %s'%(value,self.paramNames[0])
        return 0
    
    def enoughParams(self):
        return len(self.params)==1
        
class NumberRule(FunctionRule):
    functionName='number'
    def runValidation(self,value,otherMeasures):
        try:
            float(value)
            self.notmessage='%s is a number'%value
            return 0
        except (TypeError, ValueError):
            self.message='%s is not a number'%value
            return 10
    
    def enoughParams(self):
        return len(self.params)==0

class IntegerRule(FunctionRule):
    functionName='int'
    def runValidation(self,value,otherMeasures):
        try:
            fval=float(value)
            ival=int(fval)
            if(ival==fval):
                self.notmessage='%s is a whole number'%value
                return 0
        except ValueError:
            pass
        except TypeError:
            pass
        self.message='%s is not a whole number'%value
        return 10
    
    def enoughParams(self):
        return len(self.params)==0

class PercentRule(FunctionRule):
    functionName='percent'
    def runValidation(self,value,otherMeasures):
        try:
            fval=float(value)
            if(fval>=0.0 and fval<=1.0):
                self.notmessage='%s is a percentage'
                return 0
        except (ValueError, TypeError):
            pass    
        self.message='%s is not a percentage value'%value
        return 10
    
    def enoughParams(self):
        return len(self.params)==0

class RequiredRule(FunctionRule):
    functionName='required'
    def runValidation(self, value, otherMeasures):
        #we've already handled the required lookup in Rule
        return 0
    def enoughParams(self):
        return len(self.params)>0

from datetime import date
class DateRule(FunctionRule):
    functionName='date'
    def runValidation(self,value, otherMeasures):
        date=self.parseDate(value)
        if date is None:
            self.message='%s is not a valid date (MM/DD/YYYY)'%value
            return 10

        if not self.validatedetails(date, value):
            return 10
        return 0
    def validatedetails(self,date, datetext):
        return True
    def parseDate(self, datestring):
        if datestring is None:
            return None
        try:
            month, day, year=datestring.split('/')
            month=int(month)
            day=int(day)
            year=int(year)
        except (AssertionError, ValueError):
            return None
        if year<1900:
            return None
        try:
            return date(year, month, day)
        except ValueError:
            return None
    def enoughParams(self):
        return len(self.params)==0

class BeforeDateRule(DateRule):
    functionName='beforedate'
    def validatedetails(self, date, datetext):
        other=self.parseDate(self.paramValues[0])
        result= date<other
        if not result:
            self.message='%s is not before %s'%(datetext,self.paramNames[0])
            return False
        return True
    def enoughParams(self):
        return len(self.params)==1
    
class AfterDateRule(DateRule):
    functionName='afterdate'
    def validatedetails(self, date, datetext):
        other=self.parseDate(self.paramValues[0])
        result= other<date
        if not result:
            self.message='%s is not after %s'%(datetext,self.paramNames[0])
            return False
        return True
    def enoughParams(self):
        return len(self.params)==1
        

class NotRule(Rule):
    def fits(self,text):
        if text.startswith('not '):
            remainder=text.split('not ',1)[1].strip()
            return True
        return False
    def buildSelf(self,text):
        if text.startswith('not '):
            remainder=text.split('not ',1)[1].strip()
            self.innerRule=builder.buildRule(remainder)
            return True
            
    def runValidation(self,value,otherMeasures):
        self.message='no information'
        
        result=self.innerRule.validate(value,otherMeasures)
        self.notmessage=self.innerRule.message
        self.message=self.innerRule.notmessage
        if result==0:
            return 10
        elif result<6:
            result=10
        else:
            result=0
        return result


class WarnRule(Rule):
    def fits(self, text):
        if text.startswith('warn '):
            remainder=text.split('warn ', 1)[1].strip()
            return True
        return False
    def buildSelf(self, text):
        if text.startswith('warn '):
            remainder=text.split('warn ',1)[1].strip()
            self.innerRule=builder.buildRule(remainder)
    def runValidation(self, value, otherMeasures):
        result=self.innerRule.validate(value, otherMeasures)
        self.message=self.innerRule.message
        self.notmessage=self.innerRule.notmessage
        if result==0:
            return 0
        else:
            return 5
class SilentRule(Rule):
    noisy=False
    def fits(self, text):
        if text.startswith('silent '):
            remainder=text.split('silent ', 1)[1].strip()
            return True
        return False
    def buildSelf(self, text):
        if text.startswith('silent '):
            remainder=text.split('silent ',1)[1].strip()
            self.innerRule=builder.buildRule(remainder)
    def runValidation(self, value, otherMeasures):
        result=self.innerRule.validate(value, otherMeasures)
        self.message=self.innerRule.message
        self.notmessage=self.innerRule.notmessage
        return result