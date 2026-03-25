import pandas as pd

def load_students_list(path):

    df = pd.read_excel(path)

    std_list = {}

    for _, row in df.iterrows():

        sid = str(row['학번']).strip()

        name = str(row['성명']).strip()

        std_list[sid] = name

    #print('std_list:', std_list)

    return std_list


def load_correct_answer(path):

    df = pd.read_excel(path)

    answer_key = {}
    score_table = {}

    for _, row in df.iterrows():

        q = int(row['문항']) - 1

        answers = [int(x) for x in str(row['정답']).replace(' ', '').split(',')]

        answer_key[q] = answers

        score_table[q] = float(row['배점'])

    #print('answer_key:', answer_key)
    #print('score_table:', score_table)

    return answer_key, score_table


def save_result(results, extra, std_list, answer_key, score_table, subject_name):

    data = []

    for sid, sname in std_list.items():
        row = {'학번': sid, '이름': sname,
               '객관식': 0, '주관식': 0, '총점': 0}
        score = 0
        #print('results[sid]:', results[sid])

        # 채점
        if sid in results:
            for q,k in answer_key.items():
                a = results[sid][q]

                if set(a) == set(k):
                    row[f'{q+1}'] = 'o'
                    score += score_table[q]
                else:
                    row[f'{q+1}'] = 'x'
                
                row[f'A{q+1}'] = ','.join(map(str,a))

            row['객관식'] = score
            row['주관식'] = extra
            row['총점'] = score + extra
        else:
            for q in answer_key.keys():
                row[f'{q+1}'] = 'x'

        data.append(row)

    df = pd.DataFrame(data)

    out = f'{subject_name}/{subject_name}-채점결과.xlsx'

    df.to_excel(out, index=False)

    print('\n채점 완료')
    print('결과 파일:', out)
