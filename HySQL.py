import os
import re
import json
from tabulate import tabulate
from collections import defaultdict

# All instructions list
instructions = ['DELETE', 'FROM', 'SELECT', 'WHERE', 'UPDATE', 'INSERT', 'JOIN', 'SET', 'ORDER', 'GROUP', 'VALUE', 'CREATE', 'DROP', 'TOP']

# Error handler
def error(error: str, info: str, ifExit=True) -> None:
    print(f'{error}: {info}')
    if ifExit: exit()

# Check the condition is True or False
def checker(head: list, rows: list, conditions: list) -> bool:
    temp = {x: y for x, y in zip(head, rows)}
    row, condition, value = conditions
    if row not in temp: return False
    elif condition == '=': return str(temp[row]) == str(value)
    elif condition == '>': return str(temp[row]) > str(value)
    elif condition == '<': return str(temp[row]) < str(value)
    elif condition == '>=': return str(temp[row]) >= str(value)
    elif condition == '<=': return str(temp[row]) <= str(value)
    elif condition == 'LIKE': return temp[row] != None and re.match(value, str(temp[row]))
    return False

# Return all results that match the condition
def whereFilter(head: list, body: list, query_where: list, IorX: str) -> list:
    array = []
    for i, bd in enumerate(body):
        if query_where['AND'] != []:
            for where in query_where['AND']:
                if not checker(head, bd, where): array.append(i)
        if query_where['OR'] != []:
            for where in query_where['OR']:
                if checker(head, bd, where):
                    if i in array: array.remove(i)
        if query_where['NOT'] != []:
            for where in query_where['NOT']:
                if checker(head, bd, where): array.append(i)
    array = [(x if IorX == 'x' else i) for i, x in enumerate(body) if i not in array]
    return array

# Re-concat string from array
def stringConcat(array: list) -> list:
    trigger = False
    l, i = 1, 0
    while i < l:
        x, l = str(array[i]), len(array)
        if x[0] == "'" and x[-1] == "'":
            array[i] = x[1:-1]
            i += 1
            continue
        elif "'" in x and trigger == False:
            trigger = not trigger
            array[i] = x.replace("'", '')
        elif "'" in x and trigger == True:
            trigger = not trigger
            array[i - 1] += ' ' + x.replace("'", '')
            del array[i]
        elif "'" not in x and trigger == True:
            array[i - 1] += ' ' + x
            del array[i]
            i -= 1

        # convert to int
        try:
            array[i] = int(array[i])
            i += 1
            continue
        except: pass

        # convert to float
        try:
            array[i] = float(array[i])
            i += 1
            continue
        except: pass

        # go to next string
        i += 1

    return array

class HySQL:
    def __init__(self, input: str) -> None:
        self.input = input.replace(' ', '\n').split('\n')
        while '' in self.input: self.input.remove('')
        self.mode = ''
        self.query = defaultdict(list)

    def format(self):
        instruction = ''
        for x in self.input:
            if x.upper() in instructions: instruction = x.upper()
            elif x != '': self.query[instruction].append(x)
        for x in self.query:
            self.query[x] = [str(x).replace('(', '').replace(')', '').replace(',', '').strip() for x in self.query[x]]
            while '' in self.query[x]: self.query[x].remove('')
            self.query[x] = stringConcat(self.query[x])

        if 'UPDATE' in self.query:
            self.mode = 'UPDATE'
            self.query['UPDATE'] = [str(x).replace(',', '') for x in self.query['UPDATE'] if x not in ['', ',']]
        if 'DELETE' in self.query:
            self.mode = 'DELETE'
            self.query['DELETE'] = [str(x).replace(',', '') for x in self.query['DELETE'] if x not in ['', ',']]
        if 'CREATE' in self.query:
            self.mode = 'CREATE'
            self.query['CREATE'] = [str(x).replace(',', '') for x in self.query['CREATE'] if x not in ['', ',']]
        if 'DROP' in self.query:
            self.mode = 'DROP'
            self.query['DROP'] = [str(x).replace(',', '') for x in self.query['DROP'] if x not in ['', ',']]
        if 'FROM' in self.query:
            self.query['FROM'] = [str(x).replace(',', '') for x in self.query['FROM'] if x not in ['', ',']]
        if 'INSERT' in self.query:
            self.mode = 'INSERT'
            self.query['INSERT'] = [str(x).replace(',', '') for x in self.query['INSERT'] if x not in ['', ',']]
        if 'ORDER' in self.query:
            self.query['ORDER'] = [str(x).replace(',', '') for x in self.query['ORDER'] if x not in ['', ',']]
        if 'SELECT' in self.query:
            self.mode = 'SELECT'
            self.query['SELECT'] = [str(x).replace(',', '') for x in self.query['SELECT']]
            asIndex = [i for i, x in enumerate(self.query['SELECT']) if x == 'AS']
            temp = []
            for i in asIndex: self.query['SELECT'][i - 1:i + 2] = [[self.query['SELECT'][i - 1], self.query['SELECT'][i + 1]], '', '']
            self.query['SELECT'] = [x for x in self.query['SELECT'] if x != '']
        if 'SET' in self.query:
            self.query['SET'] = [str(x).replace(',', '') for x in self.query['SET']]
            l = len(self.query['SET'])
            for n in range(0, l, 3): self.query['SET'].append([self.query['SET'][n], self.query['SET'][n + 2]])
            self.query['SET'] = self.query['SET'][l:]
        if 'WHERE' in self.query:
            condition = 'AND'
            temp = defaultdict(list)
            for x in self.query['WHERE']:
                if x in ['NOT', 'AND', 'OR']: condition = x
                else: temp[condition].append(x)
            for x in temp:
                l = len(temp[x])
                for n in range(0, l, 3): temp[x].append([temp[x][n], temp[x][n + 1], temp[x][n + 2]])
                temp[x] = temp[x][l:]
            self.query['WHERE'] = temp

        return self.mode, self.query

    def excute(self):
        mode, query = self.format()

        if mode == 'SELECT':
            path = query['FROM'][0]
            if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')

            with open(f'./database/{path}.table', 'r', encoding="utf-8") as f:
                # Load database
                dataset = json.load(f)

                # Order
                if 'ORDER' in query:
                    if query['ORDER'][0] != 'BY': error('Syntax Error', '"ORDER" must used with "BY".')
                    query['ORDER'] = query['ORDER'][1:]

                    # Preprocess
                    l = len(query['ORDER'])
                    if l & 1: error('Value Error', '"ORDER" must be used with "ASC" ro "DESC"')
                    for n in range(0, l, 2): query['ORDER'].append([query['ORDER'][n + 1], query['ORDER'][n]])
                    query['ORDER'] = query['ORDER'][l:]
                    
                    # Sort json
                    for sort, key in query['ORDER']:
                        try: dataset.sort(key=lambda x: x[key], reverse=(True if sort == 'DESC' else False))
                        except: error('Value Error', f'Cannot sort by "{key}". Please make sure every data has this row.', ifExit=False)

                # Select all rows from dataset
                head = []
                for row in dataset:
                    for x in row:
                        if x not in head: head.append(x)

                # Select all cols from dataset
                body = []
                for data in dataset:
                    temp = []
                    for index in head:
                        if index in data: temp.append(data[index])
                        else: temp.append(None)
                    body.append(temp)

                if 'WHERE' in query: body = whereFilter(head, body, query['WHERE'], IorX='x')

            if '*' not in query['SELECT']:
                # Get selected rows
                selected_head = []
                for row in query['SELECT']:
                    if type(row) == list and row[0] not in selected_head: selected_head.append(row[0])
                    elif row not in selected_head: selected_head.append(row)
                selected_head = set(list(range(len(head)))) - set([head.index(x) for x in selected_head])

                # Remove unselected rows from head
                for index, j in enumerate(selected_head): head = head[:j - index] + head[j - index + 1:]

                # Remove unselected rows from body
                for i in range(len(body)):
                    for index, j in enumerate(selected_head): body[i] = body[i][:j - index] + body[i][j - index + 1:]

            # AS function
            for row in query['SELECT']:
                if type(row) == list: head[head.index(row[0])] = row[1]
            
            if 'TOP' in query: body = body[:int(query['TOP'][0])]

            # Show result table
            tabel = tabulate(body, headers=head, tablefmt="fancy_grid")
            print(tabel)
            print(f'Excuted successfully.')

            # Return result
            return [{x: y for x, y in zip(head, data)} for data in body]

        if mode == 'UPDATE':
            path = query['UPDATE'][0]
            if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')

            with open(f'./database/{path}.table', 'r') as f:
                # Load database
                dataset = json.load(f)

                # Select all rows from dataset
                head = []
                for row in dataset:
                    for x in row:
                        if x not in head: head.append(x)

                # Select all cols from dataset
                body = []
                for data in dataset:
                    temp = []
                    for index in head:
                        if index in data: temp.append(data[index])
                        else: temp.append(None)
                    body.append(temp)

                if 'WHERE' in query: update = whereFilter(head, body, query['WHERE'], IorX='i')

                # Update database
                for i in range(len(dataset)):
                    if i in update:
                        for sets in query['SET']:
                            dataset[i][sets[0]] = sets[1]

                # Store to database
                with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps(dataset, indent=4))

                print(f'Updated successfully.')

        if mode == 'INSERT':
            path = query['INSERT'][1]
            if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')
            elif query['INSERT'][0] != 'INTO': error('Syntax Error', '"INSERT" must be user with "INTO"')

            with open(f'./database/{path}.table', 'r') as f:
                # Preprocess
                query['INSERT'] = query['INSERT'][2:]

                # Input check
                if len(query['INSERT']) != len(query['VALUE']): error('Value Error', 'Insert columns must be same as value columns.')

                # Load database
                dataset = json.load(f)
                dataset += [{x: y for x, y in zip(query['INSERT'], query['VALUE'])}]

                # Store to database
                with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps(dataset, indent=4))

                print(f'Inserted successfully.')

        if mode == 'DELETE':
            path = query['FROM'][0]
            if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')

            with open(f'./database/{path}.table', 'r') as f:
                # Load database
                dataset = json.load(f)

                # Select all rows from dataset
                head = []
                for row in dataset:
                    for x in row:
                        if x not in head: head.append(x)

                # Select all cols from dataset
                body = []
                for data in dataset:
                    temp = []
                    for index in head:
                        if index in data: temp.append(data[index])
                        else: temp.append(None)
                    body.append(temp)

                if 'WHERE' in query: delete = whereFilter(head, body, query['WHERE'], IorX='i')

                for i, x in enumerate(dataset):
                    if i in delete:
                        if '*' in query['DELETE']: dataset[i] = ''
                        else:
                            for j in query['DELETE']:
                                if j in dataset[i]: del dataset[i][j]
                dataset = [x for x in dataset if x != '']

                # Store to database
                with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps(dataset, indent=4))

                print(f'Deleted successfully.')

        if mode == 'CREATE':
            path = query['CREATE'][0]
            if os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} exists.')
            query['CREATE'] = query['CREATE'][1:]

            dataset = {}
            for n in range(0, len(query['CREATE']), 2): dataset[query['CREATE'][n]] = query['CREATE'][n + 1]

            # Create database
            with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps([dataset], indent=4))

            print(f'Created table "{path}" successfully.')

        if mode == 'DROP':
            path = query['DROP'][1]
            if query['DROP'][0] != 'TABLE': error('Syntax Error', '"DROP" must be user with "TABLE"')
            query['DROP'] = query['DROP'][1:]

            for table in query['DROP']:
                if not os.path.isfile(f'./database/{table}.table'): error('Error', f'Table {table} not found.', ifExit=False)
                else:
                    os.remove(f'./database/{table}.table')
                    print(f'Table {table} has been droped.')