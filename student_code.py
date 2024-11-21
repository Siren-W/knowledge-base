import read, copy
from util import *
from logical_classes import *

verbose = 0
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

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact or Rule) - Fact or Rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_rule):
        """Retract a fact or a rule from the KB

        Args:
            fact_rule (Fact or Rule) - Fact or Rule to be retracted

        Returns:
            None
        """
        ####################################################
        # Student code goes here
        def remove_if_no_support(fr):
            if isinstance(fr, Fact):
                if not fr.asserted and len(fr.supported_by) == 0:
                    self.facts.remove(fr)
                    remove_supports(fr)
            elif isinstance(fr, Rule):
                if not fr.asserted and len(fr.supported_by) == 0:
                    self.rules.remove(fr)
                    remove_supports(fr)

        def remove_supports(fr):
            new_facts = []
            remove_list = []
            for fact in self.facts[:]:
                if fact in fr.supports_facts:
                    if len(fact.supported_by) > 2 and fr in fact.supported_by:
                        index = fact.supported_by.index(fr)

                        # If `fr` is an instance of Rule, remove the element before it
                        if isinstance(fr, Rule):
                            if index > 0:  # To ensure we don't go out of bounds
                                fact.supported_by.pop(index - 1)
                        else:
                            if index < len(fact.supported_by) - 1:  # Ensure we don't go out of bounds
                                fact.supported_by.pop(index + 1)

                        # Remove `fr` itself
                        fact.supported_by.pop(index)
                        new_facts.append(fact)

                    else: remove_list.append(fact)

                else: new_facts.append(fact)
            self.facts = new_facts
            for fact in remove_list:
                remove_supports(fact)



            for supported_rule in fr.supports_rules[:]:
                self.rules = [rule for rule in self.rules if rule != supported_rule]
                remove_supports(supported_rule)


        # Start retraction process
        if not isinstance(fact_rule, (Fact, Rule)) or fact_rule.supported_by:
            return

        if isinstance(fact_rule, Fact):
            for fact in self.facts[:]:
                if fact.asserted and fact == fact_rule:
                    self.facts.remove(fact)
                    remove_supports(fact)
        elif isinstance(fact_rule, Rule):
            for rule in self.rules[:]:
                if rule == fact_rule and not rule.supported_by:
                    self.rules.remove(rule)
                    remove_supports(rule)


class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing
        """
        ####################################################
        # Student code goes here
        if not isinstance(rule, Rule) or not isinstance(fact, Fact):
            return

        bindings = match(rule.lhs[0], fact.statement)

        if bindings:
            new_lhs = [
                instantiate(statement, bindings)
                for i, statement in enumerate(rule.lhs) if i != 0
            ]

            new_rhs = instantiate(rule.rhs, bindings)

            if new_lhs:
                # If there are still conditions remaining, create a new curried Rule
                new_rule = Rule([new_lhs, new_rhs], supported_by=[fact, rule])
                fact.supports_rules.append(new_rule)
                rule.supports_rules.append(new_rule)
                kb.kb_add(new_rule)
            else:
                # If no LHS conditions are remaining, create a new Fact
                item = next((i for i in kb.facts if i == Fact(new_rhs)), None)
                if item:
                    item.supported_by.extend([fact, rule])

                new_fact = Fact(new_rhs, supported_by=[fact, rule])
                fact.supports_facts.append(new_fact)
                rule.supports_facts.append(new_fact)
                kb.kb_add(new_fact)
