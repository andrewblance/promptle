from dotenv import load_dotenv
import os
import datetime
import openai
import csv
import json
import ast

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 

def user_input():
    question = input("Imagine this, but... \n")
    return "Imagine this, but" + question

def generate_prompt(user, true):
    prompt = f"On a scale of 0 to 100, how similar is the piece of text '{user}' to '{true}'? Your response must be in the format of a single integer."
    return prompt

def callOpenAI(user_guess):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {
                "role": "user",
                "content": user_guess
                }
            ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )    
    return response.choices[0].message.content

def oneRound(originalPrompt):
    user_guess = input("what was the prompt that caused this?\n")
    generated_prompt = generate_prompt(user_guess, originalPrompt)
    answer = callOpenAI(generated_prompt)
    return answer

def record_answer(day,answers):
    avg_ans = sum(answers) / len(answers) 
    answers.insert(0,day)
    print(f'your score today is {avg_ans}')
    answers.append(avg_ans)

    f = open('data/user_data.csv', 'a')
    # create the csv writer
    writer = csv.writer(f, delimiter='|')
    # write a row to the csv file
    writer.writerow(answers)
    # close the file
    f.close()
    return avg_ans


def high_score_checker(avg_ans):
    with open('data/high_score.json', "r") as fp:
        data = json.load(fp)
        print(data)
        old_best_day = int(data["bestDay"])
        old_high_score = int(data["highscore"])
    
    if avg_ans > old_high_score:
        print(f"you have a new high score!\n\
            it used to be {old_high_score}\n")
        return True
    else:
        print(f"your high score is still: {old_high_score}\n")
        return False

def write_score(days_since_epoch,avg_ans,high):
    with open('data/high_score.json') as fp:
        data = json.load(fp)
        data["lastDayPlayed"] = days_since_epoch
        if high == True:
            data["bestDay"] = days_since_epoch
            data["highscore"] = avg_ans

    out_file = open("data/high_score.json", "w") 
    json.dump(data, out_file) 
    out_file.close() 

def allowed_to_play():
    with open('data/high_score.json') as fp:
        data = json.load(fp)
        lastday = int(data["lastDayPlayed"])
    if lastday == days_since_epoch():
        return True #False
    else: 
        return True

def main():

    originalPrompt = data_import("data/prompt_list.csv", days_since_epoch())
    modifiedArticle = data_import("data/wiki_list.csv", days_since_epoch()).replace(r'\n', '\n')
    print(modifiedArticle)

    if allowed_to_play():
        round=0
        answers = []
        while round<2:
            answer = oneRound(originalPrompt)
            answers.append(int(answer))
            print(answer)
            round+=1

        avg_ans = record_answer(days_since_epoch(), answers)
        high = high_score_checker(avg_ans)
        write_score(days_since_epoch(),avg_ans, high)
    
    else:
        print("play again tomorrow")
    




def days_since_epoch():
    today = datetime.datetime.today()
    the_epoch = datetime.datetime.strptime("11-12-2023", '%m-%d-%Y')
    gap = (today - the_epoch).days
    return gap

def data_import(file_name, row_number):
    with open(file_name, "r") as f:
        reader = csv.reader(f, delimiter='|')
        for idx, row in enumerate(reader):
            if idx == row_number:
                data = row[1]
                break
    return data

if __name__ == '__main__':
    main()
