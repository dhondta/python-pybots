#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Utility functions for parsing Reverse Polish Notation (RPN).

"""
import math


SUPPORTED_OPERATORS = ['+', '-', '*', '/', '^', '%']
SUPPORTED_MATH_OPS  = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log',
                       'log10']
SUPPORTED_MATH_NBRS = ['e', 'pi']


def parse_postfix(expression):
    """
    Evaluate a postfix notation of an input expression.
    
    See: https://en.wikipedia.org/wiki/Reverse_Polish_notation
    
    :param expression: expression to be evaluated
    :return:           evaluated expression
    """
    stack = []
    for token in expression.split(' '):
        if token in SUPPORTED_OPERATORS:
            operand1 = stack.pop()
            operand2 = stack.pop()
            stack.append(eval("operand2 %s operand1" % token))
        elif token in SUPPORTED_MATH_OPS:
            operand = stack.pop()
            stack.append(eval("math.%s(operand)" % token))
        elif token in SUPPORTED_MATH_NBRS:
            stack.append(eval("math.%s" % token))
        else:
            stack.append(float(token))
    return stack.pop()
    

# alias for parse_postfix
parse_reverse_polish = parse_postfix
