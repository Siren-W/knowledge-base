import read, copy
from logical_classes import *
from student_code import KnowledgeBase

def format_facts_list(facts_list):
    formatted_facts = []
    for fact in facts_list:
        fact_type = fact.__class__.__name__  # Get the name of the class, e.g., "Fact"
        statement = fact.statement.predicate  # Accessing the statement predicate
        terms = [str(term.value) if hasattr(term, 'value') else str(term) for term in fact.statement.terms]  # Extracting terms and converting them to strings
        # fact_str = f"{fact_type}('{statement}', [{', '.join(terms)}]){', supported by' + str(fact.supported_by) if fact.supported_by else ''}"
        fact_str = f"{fact_type}('{statement}', [{', '.join(terms)}])"
        formatted_facts.append(fact_str)

    return "\n".join(formatted_facts)

def format_rules_list(rules_list):
    formatted_rules = []
    for rule in rules_list:
        rule_type = rule.__class__.__name__  # Get the name of the class, e.g., "Rule"
        lhs_statements = [
            f"{statement.predicate}([{', '.join([str(term.value) if hasattr(term, 'value') else str(term) for term in statement.terms])}])"
            for statement in rule.lhs
        ]
        rhs_statement = rule.rhs.predicate
        rhs_terms = [
            str(term.value) if hasattr(term, 'value') else str(term) for term in rule.rhs.terms
        ]

        rule_str = f"{rule_type}([{', '.join(lhs_statements)}], {rhs_statement}([{', '.join(rhs_terms)}]))"
        formatted_rules.append(rule_str)

    return "\n".join(formatted_rules)

if __name__ == "__main__":
    file = 'statements_kb4.txt'
    data = read.read_tokenize(file)
    KB = KnowledgeBase([], [])
    for item in data:
        if isinstance(item, Fact) or isinstance(item, Rule):
            KB.kb_assert(item)

    print(format_facts_list(KB.facts))
    print(format_rules_list(KB.rules))
    #
    # r1 = read.parse_input("rule: ((motherof ?x ?y)) -> (parentof ?x ?y)")
    # KB.kb_retract(r1)
    #
    # print('---')
    # print(format_facts_list(KB.facts))
    # print(format_rules_list(KB.rules))
    #
    # print('---')

    # KB = KnowledgeBase([], [])
    # fact1 = read.parse_input("fact: (hero A)")
    # fact2 = read.parse_input("fact: (person A)")
    # rule1 = read.parse_input("rule: ((hero ?x) (person ?x)) -> (goodman ?x)")
    # rule2 = read.parse_input("rule: ((goodman ?x) (wenttoschool ?x)) -> (doctor ?x)")
    # fact3 = read.parse_input("fact: (wenttoschool A)")
    # fact4 = read.parse_input("fact: (goodman A)")
    # ask1 = read.parse_input("fact: (goodman A)")
    # ask2 = read.parse_input("fact: (doctor A)")
    # ask3 = read.parse_input("rule: ((person A)) -> (goodman A)")
    #
    # KB.kb_assert(fact1)
    # KB.kb_assert(fact2)
    # KB.kb_assert(fact4)
    # KB.kb_assert(rule1)
    # KB.kb_assert(rule2)
    # KB.kb_assert(fact3)
    #
    # answer1 = KB.kb_ask(ask1)
    # print(format_facts_list(KB.facts))
    # print(format_rules_list(KB.rules))
    #
    # print(len(KB.facts[2].supported_by))
    #
    # print('---')
    #
    # KB.kb_retract(fact1)
    # answer4 = KB.kb_ask(ask1)
    #
    # print(format_facts_list(KB.facts))
    # print(format_rules_list(KB.rules))

    print('---')

    r1 = read.parse_input("rule: ((motherof ?x ?y)) -> (parentof ?x ?y)")

    print(format_facts_list(KB.facts))
    print(format_rules_list(KB.rules))

    print(KB.facts[10].statement)
    print(len(KB.facts[10].supported_by))

    print('---')

    KB.kb_retract(r1)
    ask1 = read.parse_input("fact: (parentof ada ?X)")
    ask2 = read.parse_input("fact: (auntof eva ?X)")
    ask3 = read.parse_input("fact: (grandmotherof ?X chen)")

    print(format_facts_list(KB.facts))
    print(format_rules_list(KB.rules))

    print(len(KB.facts[6].supported_by))



