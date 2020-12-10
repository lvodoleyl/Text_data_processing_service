from app_service import db
from app_service.models import Rule, SystemOfConclusions, \
    LinguisticVariable, Term, HistoryInputOutput, HistoryOfConclusions
from app_service.systems_of_conclusions.src import run_system


class ManagerSystemsOfConclusions:
    def system_format_json_user(self, system: SystemOfConclusions) -> dict:
        return {
            'id': system.id,
            'name': system.name,
            'description': system.description,
            'linguistic_variables': [
                {
                    'name': l_v.name,
                    'lower': l_v.lower,
                    'upper': l_v.upper,
                    'type_output': l_v.type_output,
                } for l_v in system.linguistic_vars
            ]
        }

    def system_format_json_expert(self, system: SystemOfConclusions) -> dict:
        return {
            'id': system.id,
            'name': system.name,
            'description': system.description,
            'linguistic_variables': [
                {
                    'name': l_v.name,
                    'lower': l_v.lower,
                    'upper': l_v.upper,
                    'type_output': l_v.type_output,
                    'terms': [
                        {
                            'name': term.name,
                            'type_membership_function': term.type_membership_function,
                            'points': term.points
                        } for term in l_v.terms
                    ]
                } for l_v in system.linguistic_vars
            ],
            'rules': [
                rule.rule for rule in system.rules
            ]
        }

    def create_linguistic_variable(self, linguistic_variables_json: dict, system_id: int) -> LinguisticVariable:
        l_v = LinguisticVariable(
            name=linguistic_variables_json['name'],
            lower=linguistic_variables_json['lower'],
            upper=linguistic_variables_json['upper'],
            type_output=linguistic_variables_json['type_output'],
            system_id=system_id
        )
        db.session.add(l_v)
        db.session.commit()
        return l_v

    def create_term(self, term_json: dict, linguistic_variable_id: int) -> Term:
        term = Term(
            name=term_json['name'],
            type_membership_function=term_json['type_membership_function'],
            points=term_json['points'],
            linguistic_id=linguistic_variable_id
        )
        db.session.add(term)
        db.session.commit()
        return term

    def create_rule(self, rule: str, system_id: int) -> Rule:
        rule = Rule(
            system_id=system_id,
            rule=rule
        )
        db.session.add(rule)
        db.session.commit()
        return rule

    # TODO maybe get user_id from token
    def create_system_of_conclusions(self, system_in_json: dict, user_id: int) -> SystemOfConclusions:
        system = SystemOfConclusions(
            name=system_in_json['name'],
            description=system_in_json['description'],
            user_id=user_id
        )
        db.session.add(system)
        db.session.commit()
        for linguistic_var in system_in_json['linguistic_variables']:
            new_linguistic_var = self.create_linguistic_variable(linguistic_var, system.id)
            for term in linguistic_var['terms']:
                self.create_term(term, new_linguistic_var.id)
        for rule in system_in_json['rules']:
            self.create_rule(rule, system.id)
        return system

    def get_systems_overview(self) -> list:
        return db.session.query(SystemOfConclusions).all()

    def get_system(self, system_id: int):
        return db.session.query(SystemOfConclusions).filter(SystemOfConclusions.id == system_id).first()

    def update_system_of_conclusions(self, system: SystemOfConclusions, system_in_json: dict) -> SystemOfConclusions:
        system.name = system_in_json['name']
        system.description = system_in_json['description']
        num_lin_var = 0
        for linguistic_var in system_in_json['linguistic_variables']:
            if len(system.linguistic_vars) > num_lin_var:
                new_linguistic_var = system.linguistic_vars[num_lin_var]
                new_linguistic_var.name = linguistic_var['name']
                new_linguistic_var.lower = linguistic_var['lower']
                new_linguistic_var.upper = linguistic_var['upper']
                new_linguistic_var.type_output = linguistic_var['type_output']
                db.session.add(new_linguistic_var)
                db.session.commit()
            else:
                new_linguistic_var = self.create_linguistic_variable(linguistic_var, system.id)
            num_term = 0
            for term in linguistic_var['terms']:
                if len(new_linguistic_var.terms) > num_term:
                    new_term = new_linguistic_var.terms[num_term]
                    new_term.name = term['name']
                    new_term.type_membership_function = term['type_membership_function']
                    new_term.points = term['points']
                    db.session.add(new_term)
                    db.session.commit()
                else:
                    self.create_term(term, new_linguistic_var)
                num_term += 1
            num_lin_var += 1
        num_rule = 0
        for rule in system_in_json['rules']:
            if len(system.rules) > num_rule:
                new_rule = system.rules[num_rule]
                new_rule.rule = rule
            else:
                self.create_rule(rule, system.id)
            num_rule += 1
        return system

    def delete_system(self, system: SystemOfConclusions) -> int:
        db.session.delete(system)
        db.session.commit()
        return 0

    def make_fuzzy_conclusion(self, user_id: int, system_id: int, input_values: list) -> float:
        system = self.get_system(system_id)
        story = HistoryOfConclusions(user_id, system_id)
        db.session.add(story)
        db.session.commit()
        num_input = 0
        res_output = None
        for l_var in system.linguistic_vars:
            new_input_output = HistoryInputOutput(
                type_output=l_var.type_output,
                value=None if l_var.type_output else input_values[num_input],
                id_request=story.id,
                id_variable=l_var.id
            )
            num_input += 0 if l_var.type_output else 1
            db.session.add(new_input_output)
            db.session.commit()
            res_output = new_input_output if l_var.type_output else res_output
        recommendation = run_system(system, input_values)
        res_output.value = recommendation
        db.session.add(res_output)
        db.session.commit()
        return recommendation

    def get_history_request_system_of_conclusions(self, user_id: int, system_id: int) -> list:
        return db.session.query(HistoryOfConclusions).filter(HistoryOfConclusions.user_id == user_id
                                                             and HistoryOfConclusions.system_id == system_id).all()

    def history_format_json(self, history: HistoryOfConclusions) -> dict:
        input_v = []
        output_v = 0
        for input_output in history.input_output:
            if input_output.type_output:
                output_v = input_output.value
            else:
                input_v.append(input_output.value)
        return {
            'system_id': history.system_id,
            'date': history.date,
            'input': input_v,
            'output': output_v
        }
