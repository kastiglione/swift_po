from __future__ import print_function
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
        print(frame.EvaluateExpression(expression).description, file=result)
        return

    # First try hex addresses as object pointers
    if re.match("0x[0-9a-fA-F]+$", expression):
        value = frame.EvaluateExpression(expression, _objc_options())
        print(value.description or expression, file=result)
        return

    # Next try `frame variable` using GetValueForVariablePath()
    value = frame.GetValueForVariablePath(expression)
    if value.error.success:
        description = value.description.rstrip()
        if description and not description.startswith(DescriptionErrors):
            print(description, file=result)
            return

    # Finally, use Swift's print() to avoid leaked objects.
    err = frame.EvaluateExpression("print({})".format(expression))
    if err.error.fail:
        print(err.error.description, file=result)


def _objc_options():
    options = lldb.SBExpressionOptions()
    options.SetLanguage(lldb.eLanguageTypeObjC)
    options.SetCoerceResultToId()
    return options
