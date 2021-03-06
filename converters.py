import data_structs as ds
import qm_utils as qmu
import utils as ut
import copy
import main as mn

# Class used for conversions, returns the converted rule list.
class Program:
    def __init__(self):
        self.rule_list = []

    # Used for the conversion from priority to constraint based, builds the rule list.
    def priority_to_intermediate(self, new_rule):
        if not self.rule_list:  # If rule list is empty, just add the new rule.
            self.rule_list.append(new_rule)
        else:
            merged = False  # Keeps track of merge process.
            for rule in self.rule_list[::-1]:  # Traverse the rule list backwards.
                if new_rule.conclusion == rule.conclusion:  # If the conclusions are the same, build OR formula.
                    rule.premise = ds.Formula.build_or_formula(rule.premise, new_rule.premise)
                    merged = True
                elif new_rule.conclusion == rule.conclusion.negate_literal():  # If conclusions are negations,
                    # build AND with negated premise.
                    new_rule.premise = ds.Formula.build_and_formula(new_rule.premise,
                                                                    ds.Formula.build_not_formula(rule.premise))
                    merged = False
                else:
                    continue
            if not merged:  # Add the rule to the front if not merged.
                self.rule_list.insert(0, new_rule)

    # Used for the conversion from intermediate to full tabular constraint, builds the rule list alphabetical order.
    def intermediate_to_full_tabular(self, new_rule):
        added = False
        for i in range(len(self.rule_list)):  # Loop over rule list and get index.
            if new_rule.conclusion == self.rule_list[i].conclusion.negate_literal():  # If the conclusions are
                # negations.
                rule = self.rule_list.pop(i)
                unspecified_literals_old = ds.Formula.get_unspecified_literals(rule.premise, new_rule.premise)  # Get
                # literals from the new_rule that are unspecified in the old rule.
                unspecified_literals_new = ds.Formula.get_unspecified_literals(new_rule.premise, rule.premise)  # Get
                # literals from the old that are unspecified in the new rule.

                for literal in unspecified_literals_old:  # Loop over unspecified literals and rebuild old rules.
                    new_lit = ds.Literal(literal.atom, literal.neg)
                    new_lit_neg = new_lit.negate_literal()
                    self.rule_list.insert(i, ds.Rule(rule.conclusion,
                                                     ds.Formula.build_sort_and_formula(rule.premise, new_lit_neg)))
                    self.rule_list.insert(i, ds.Rule(rule.conclusion,
                                                     ds.Formula.build_sort_and_formula(rule.premise, new_lit)))

                for literal in unspecified_literals_new:  # Build the new rules and insert.
                    new_lit = ds.Literal(literal.atom, literal.neg)
                    new_lit_neg = new_lit.negate_literal()
                    self.rule_list.insert(i, ds.Rule(new_rule.conclusion,
                                                     ds.Formula.build_sort_and_formula(new_rule.premise, new_lit_neg)))
                    self.rule_list.insert(i, ds.Rule(new_rule.conclusion,
                                                     ds.Formula.build_sort_and_formula(new_rule.premise, new_lit)))
                    added = True
        if not added:
            self.rule_list.insert(0, new_rule)  # Add the new rule to the front of the list.

    @staticmethod
    def full_tabular_to_intermediate(rule_list):
        rule_dict = qmu.qm_dict(rule_list)
        return qmu.apply_qm(rule_dict)

    def intermediate_to_priority(self, rules):
        facts = []
        establishedFactors = []
        for ri in rules[::-1]:
            notYetEvaluatedSituations = []
            conclusion = ri.conclusion
            factors = ut.get_relevant_factors(rules, conclusion)
            if not notYetEvaluatedSituations:
                notYetEvaluatedSituations = ut.relevant_situations(factors)
            if not establishedFactors:
                establishedFactors = []
            rule_base_i = ut.formula_to_full_tabular(ri.premise, factors)
            rule_base_j = []
            for rj in rule_base_i:
                if rj in notYetEvaluatedSituations:
                    newPremise = copy.copy(rj)
                    apply = True
                    for f in establishedFactors:
                        if ut.check_factor_in_formula(f.negate_literal(), rj):
                            apply = False
                            break
                        elif ut.check_factor_in_formula(f, rj):
                            newPremise = ut.remove_factor_from_formula(f, newPremise)
                    if apply and newPremise:
                        rule_base_j.append(ds.Rule(conclusion, newPremise))
                    notYetEvaluatedSituations.remove(rj)
            rule_dict = qmu.qm_dict(rule_base_j)  # Apply QM on rule_base_js
            new_rule_base = qmu.apply_qm(rule_dict)
            for rule in new_rule_base:
                facts += ut.factors_premise(rule.premise)
                self.rule_list.insert(0, rule)
            establishedFactors = ut.extractFacts(notYetEvaluatedSituations, facts)


# Priority based to intermediate constraint based conversion.
def pb_to_icb(rule_list):
    temp_program = Program()
    for ri in rule_list[::-1]:  # from ri to r1
        temp_program.priority_to_intermediate(ri)
    return temp_program.rule_list


# Intermediate constraint based to full-tabular constraint based conversion.
def icb_to_ftcb(rule_list):
    temp_program = Program()
    for ri in rule_list[::-1]:  # from ri to r1
        temp_program.intermediate_to_full_tabular(ri)
    return temp_program.rule_list


def ftcb_to_icb(rule_list):
    temp_program = Program()
    return temp_program.full_tabular_to_intermediate(rule_list)


def icb_to_pb(rule_list):  # Last rule has highest priority
    temp_program = Program()
    temp_program.intermediate_to_priority(rule_list)
    return temp_program.rule_list



