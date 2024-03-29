from typing import cast

import tinycss2.ast
import tinycss2.parser


def parse_stylesheet(css: str) -> list[tinycss2.ast.QualifiedRule]:
    return cast(list[tinycss2.ast.QualifiedRule], tinycss2.parser.parse_stylesheet(css))


def serialize_stylesheet(parsed: list[tinycss2.ast.QualifiedRule]) -> str:
    return "".join([rule.serialize() for rule in parsed])


def get_identity(rule: tinycss2.ast.QualifiedRule) -> str:
    assert isinstance(rule, tinycss2.ast.QualifiedRule)
    return "".join([token.value for token in rule.prelude if hasattr(token, "value")]).strip()


# def find_rule_by_class(css_class: str, parsed: list):
#   for rule in parsed:
#     if isinstance(rule, tinycss2.ast.QualifiedRule):
#       identity = get_identity(rule)
#       if identity == css_class:
#         return rule
#   return None

# def find_all_rules_by_class(css_class: str, parsed: list):
#   result = []
#   for rule in parsed:
#     if isinstance(rule, tinycss2.ast.QualifiedRule):
#       identity = get_identity(rule)
#       if identity == css_class:
#         result.append(rule)
#   return result


def find_all_rules_by_classes(
    css_classes: set[str], parsed: list[tinycss2.ast.QualifiedRule]
) -> list[tinycss2.ast.QualifiedRule]:
    result = []
    for rule in parsed:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            identity = get_identity(rule)
            if identity in css_classes:
                result.append(rule)
    return result


def get_token_value_by_ident(rule: tinycss2.ast.QualifiedRule, ident: str) -> list[tinycss2.ast.QualifiedRule]:
    result_tokens = []
    record_next_tokens = False
    for token in rule.content:
        if not record_next_tokens and isinstance(token, tinycss2.ast.IdentToken) and token.value == ident:
            record_next_tokens = True
        elif record_next_tokens and isinstance(token, tinycss2.ast.IdentToken):
            record_next_tokens = False
            break
        elif (
            record_next_tokens
            and not isinstance(token, tinycss2.ast.WhitespaceToken)
            and not isinstance(token, tinycss2.ast.LiteralToken)
        ):
            result_tokens.append(token)
    return result_tokens
