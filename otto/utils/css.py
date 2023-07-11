from typing import cast

import tinycss2.ast
import tinycss2.parser


def parse_stylesheet(css: str) -> list[tinycss2.ast.Node]:
    """Parse a stylesheet."""
    return cast(list[tinycss2.ast.Node], tinycss2.parser.parse_stylesheet(css))


def serialize_stylesheet(parsed: list[tinycss2.ast.Node]) -> str:
    """Serialize a stylesheet."""
    return "".join([rule.serialize() for rule in parsed])


def get_identity(rule: tinycss2.ast.Node) -> str:
    """Get the identity of a rule."""
    qual_rule = cast(tinycss2.ast.QualifiedRule, rule)
    return "".join([token.value for token in qual_rule.prelude if hasattr(token, "value")]).strip()


def find_all_rules_by_classes(
    css_classes: set[str],
    parsed: list[tinycss2.ast.Node],
) -> list[tinycss2.ast.Node]:
    """Find all rules by classes."""
    return [
        rule for rule in parsed if isinstance(rule, tinycss2.ast.QualifiedRule) and get_identity(rule) in css_classes
    ]


def get_token_value_by_ident(rule_node: tinycss2.ast.Node, ident: str) -> list[tinycss2.ast.Node]:
    """Get the value of a token by its ident."""
    rule = cast(tinycss2.ast.QualifiedRule, rule_node)
    result_tokens: list[tinycss2.ast.Node] = []
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
