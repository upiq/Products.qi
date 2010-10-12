import re
import Products.CMFPlone.RegistrationTool as BaseModule

password_chars=BaseModule.getValidPasswordChars

_checkEmail=BaseModule._checkEmail

#override the two values we care about
class QIRegistrationTool(BaseModule.RegistrationTool):
    default_member_id_pattern='^[A-Za-z][A-Za-z0-9_.-]*@[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+$'
    _ALLOWED_MEMBER_ID_PATTERN = re.compile(default_member_id_pattern)