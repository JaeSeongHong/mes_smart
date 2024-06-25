import pandas as pd
import numpy as np
import json

from api.serializers import BomMasterSerializer


def excel_parser(path, obj):
    df = pd.read_excel(path)
    s = BomMasterSerializer(obj)

    dic = None
    with open('data/format.json', encoding='utf-8') as jf:
        dic = json.load(jf)

    no_col = list(filter(lambda x: 'no' == x['attribute'], dic))[0]

    # Make indices
    max_num, indices = -1, {}
    for i, column in enumerate(df.columns):
        refined_column = column.lower().strip()
        if refined_column in no_col['dub']:
            indices['no'] = {'index': i + 1}
            for j, cell in df.iloc[:, i].items():
                if np.isnan(cell):
                    max_num = j
                    break

            if max_num == -1:
                max_num = df.shape[0]


        rules = list(filter(lambda x: refined_column in x['dub'], dic))
        if len(rules) > 1:
            raise Exception('시스템 에러입니다. 관리자에게 문의하세요: 포멧 파일에 중복된 칼럼명이 존재 (format.json)')
        elif len(rules) < 1:
            continue

        rule = rules[0]
        indices[rule['attribute']] = {
            'index': i,
            'rule': rule
        }

    # Retrieve data
    items = []
    for i, row in df.iloc[:max_num].iterrows():
        item = {}
        for k, v in indices.items():
            rule = v['rule']
            cell = row.iloc[v['index']]
            if pd.isna(cell):
                if rule['null'] is False:
                    raise Exception('{} 행 {} 열에서 에러가 발생하였습니다: {} 열의 값은 비어있을 수 없습니다.'.format(i + 1, v['index'] + 1, rule['dub']))

                continue

            if rule['attribute'] in s.data and s.data[rule['attribute']] >= 0:
                item[rule['attribute']] = cell

        items.append(item)

    return items
