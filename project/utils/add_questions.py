import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from main import *
import json


def get_last_question_number():
    # Ordenar as questões em ordem decrescente pelo número da pergunta e obter o número da última pergunta
    last_question = questions_collection.find_one(sort=[("question_number", -1)])
    return last_question["question_number"] if last_question else 0

def import_questions_from_json(file_path):
    with open(file_path, 'r') as file:
        questions_data = json.load(file)

    last_question_number = get_last_question_number()

    for data in questions_data:
        last_question_number += 1  # Incrementar o número da última pergunta
        question = Question(
            question_number=last_question_number,
            question=data.get('TextQuestion'),
            theme=data.get('Theme'),
            location=data.get('Location')
        )
        question_dict = question.dict()

        # Insira a pergunta na coleção
        questions_collection.insert_one(question_dict)

        print(f"Pergunta {question.question_number} adicionada com sucesso.")

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.realpath(__file__))
    json_file_name = "questions_to_add.json"
    json_file_path = os.path.join(script_directory, json_file_name)
    import_questions_from_json(json_file_path)


client.close()
