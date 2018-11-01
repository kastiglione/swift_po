import lldb
import re

DescriptionErrors = "expression produced error:"


@lldb.command("spo")
def _swift_po(debugger, expression, ctx, result, _):
    # type: (lldb.SBDebugger, str, lldb.SBExecutionContext, lldb.SBCommandReturnObject, dict) -> None
    """
    Swift `po` substitute. Works around known issues with po. This po does the following:
        1. handles object addresses (ex: 0x76543210)
        2. prefers `frame variable` for speed and avoiding unintentional strong references
        3. calls Swift's print() function, also to avoid unintentional strong references
    """

    frame = ctx.frame

    # If not Swift, do a vanilla `po`
    if frame.GuessLanguage() != lldb.eLanguageTypeSwift:
        print >> result, frame.EvaluateExpression(expression).description
        return

    # First try hex addresses as object pointers
    if re.match("0x[0-9a-fA-F]+$", expression):
        value = frame.EvaluateExpression(expression, _objc_options())
        description = value.description
        print >> result, (description or expression)
        return

    # Next try `frame variable` (GetValueForVariablePath)
    if re.match(r"[\w[\w\d]*(\.[\w\d]+)*$", expression):
        value = frame.GetValueForVariablePath(expression)
        if value.IsValid():
            description = value.description.rstrip()
            if description and not description.startswith(DescriptionErrors):
                print >> result, description
                return

    # Finally, use Swift's print() to avoid leaked objects, missing deinits.
    frame.EvaluateExpression("print({})".format(expression))


def _objc_options():
    options = lldb.SBExpressionOptions()
    options.SetLanguage(lldb.eLanguageTypeObjC)
    options.SetCoerceResultToId()
    return options
