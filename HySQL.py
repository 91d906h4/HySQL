import json
import os
import re
import time
from collections import defaultdict

from tabulate import tabulate

# All instructions list
instructions = ['DELETE', 'FROM', 'SELECT', 'WHERE', 'UPDATE', 'INSERT', 'JOIN', 'SET', 'ORDER', 'GROUP', 'VALUE', 'CREATE', 'DROP', 'LIMIT', 'ON']

# Error handler
def error(error: str, info: str, ifExit=True) -> None:
    print(f'{error}: {info}')
    if ifExit: exit()

# Condition checker
def checker(head: list, rows: list, conditions: list) -> bool:
    temp = {x: y for x, y in zip(head, rows)}
    row, condition, value = conditions
    if row not in temp: return False
    elif condition == '=': return not str(temp[row]) == str(value)
    elif condition == '>': return not str(temp[row]) > str(value)
    elif condition == '<': return not str(temp[row]) < str(value)
    elif condition == '>=': return not str(temp[row]) >= str(value)
    elif condition == '<=': return not str(temp[row]) <= str(value)
    elif condition == '!=': return not str(temp[row]) != str(value)
    elif condition == 'LIKE': return not re.match(value, str(temp[row]))
    return True

# Return all results that match the condition
def whereFilter(head: list, body: list, query_where: list, IorX: str) -> list:
    len_body = len(body)
    array = {x: x for x in range(len_body)}

    for i, bd in enumerate(body):
        if query_where['AND'] != []:
            for where in query_where['AND']:
                if checker(head, bd, where):
                    if i in array: del array[i]
        if query_where['OR'] != []:
            for where in query_where['OR']:
                if not checker(head, bd, where):
                    if i in array: array[i] = i
        if query_where['NOT'] != []:
            for where in query_where['NOT']:
                if not checker(head, bd, where):
                    if i in array: del array[i]
    array = list(array.keys())

    # Mode 'i': return index, 'x': return raw data.
    if IorX == 'x':
        for i, x in enumerate(array): array[i] = body[x]

    return array

# String preprocess
def stringPreprocess(input: str) -> list:
    # Split string
    array, temp, inString = [], '', False
    for char in input + ' ':
        # If current char is space or new-line, append the string(temp) to the result list.
        if char in [' ', '\n'] and inString == False:
            array.append(temp)
            temp = ''
        # If current char is single apostrophe('), start record input as string (string will not ignore spaces and commas).
        elif char == "'" and inString == False:
            temp += char
            inString = True
        # End string recording.
        elif char == "'" and inString == True:
            temp += char
            inString = False
        # If current char is not in a string, then ignore spaces and commas.
        elif char in [',', ' '] and inString == False: continue
        else: temp += char

    # Clean string
    temp = []
    for text in array:
        text = str(text).strip()

        if len(text) > 0 and text[-1] == ',': text = text[:-1]
        if len(text) > 0 and text[0] == '(': text = text[1:]
        if len(text) > 0 and text[-1] == ')': text = text[:-1]
        if len(text) > 0 and text[0] == "'": text = text[1:]
        if len(text) > 0 and text[-1] == "'": text = text[:-1]
        if text == '': continue

        # Try to convert to int
        try:
            text = int(text)
            temp.append(text)
            continue
        except: pass

        # Try to convert to float
        try:
            text = float(text)
            temp.append(text)
            continue
        except: pass

        temp.append(text)

    return temp

class HySQL:
    def __init__(self, input='') -> None:
        self.input = input
        self.mode = '' # Modes: SELECT, INSERT, UPDATE, DELETE, CREATE, DROP (the modes are exclusive.)
        self.query = defaultdict(list)

    # API functions
    def ORDER_BY(self, input) -> None: self.input += ' ORDER BY ' + str(input)
    def GROUP_BY(self, input) -> None: self.input += ' GROUP BY ' + str(input)
    def SELECT(self, input) -> None: self.input += ' SELECT ' + str(input)
    def INSERT(self, input) -> None: self.input += ' INSERT ' + str(input)
    def DELETE(self, input) -> None: self.input += ' DELETE ' + str(input)
    def UPDATE(self, input) -> None: self.input += ' UPDATE ' + str(input)
    def CREATE(self, input) -> None: self.input += ' CREATE ' + str(input)
    def LIMIT(self, input) -> None: self.input += ' LIMIT ' + str(input)
    def VALUE(self, input) -> None: self.input += ' VALUE ' + str(input)
    def WHERE(self, input) -> None: self.input += ' WHERE ' + str(input)
    def FROM(self, input) -> None: self.input += ' FROM ' + str(input)
    def DROP(self, input) -> None: self.input += ' DROP ' + str(input)
    def JOIN(self, input) -> None: self.input += ' JOIN ' + str(input)
    def SET(self, input) -> None: self.input += ' SET ' + str(input)

    def format(self):
        self.input = stringPreprocess(self.input)

        instruction = ''
        for x in self.input:
            if isinstance(x, str) and x.upper() in instructions: instruction = x.upper()
            else: self.query[instruction].append(x)

        for x in ['UPDATE', 'DELETE', 'CREATE', 'INSERT', 'DROP']:
            if x in self.query:
                self.mode = x
                break

        if 'SELECT' in self.query:
            self.mode = 'SELECT'
            asIndex = [i for i, x in enumerate(self.query['SELECT']) if x == 'AS']
            temp = []
            for i in asIndex: self.query['SELECT'][i - 1:i + 2] = [[self.query['SELECT'][i - 1], self.query['SELECT'][i + 1]], '', '']
            self.query['SELECT'] = [x for x in self.query['SELECT'] if x != '']
        if 'SET' in self.query:
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
        if 'ORDER' in self.query:
            if self.query['ORDER'][0] != 'BY': error('Syntax Error', '"ORDER" must used with "BY".')
            self.query['ORDER'] = self.query['ORDER'][1:]
            l, n, temp = len(self.query['ORDER']), 0, []
            if l == 1: self.query['ORDER'].append('ASC')
            while n < l:
                if self.query['ORDER'][n + 1] not in ['ASC', 'DESC']:
                    temp.append(['ASC', self.query['ORDER'][n]])
                    n += 1
                else:
                    temp.append([self.query['ORDER'][n + 1], self.query['ORDER'][n]])
                    n += 2
            self.query['ORDER'] = temp

        return self.mode, self.query

    def excute(self, view=True):
        mode, query = self.format()

        if mode == 'SELECT':
            for path in query['FROM']:
                if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')

            # Load database
            # print('start read file', '==>', time.time())
            dataset = []
            for path in query['FROM']:
                f = open(f'./database/{path}.table', 'r', encoding='UTF-8')
                dataset += json.load(f)
                f.close()
            # print('end read file  ', '==>', time.time())

            # Order
            # print('start sort     ', '==>', time.time())
            for sort, key in query['ORDER']:
                try: dataset.sort(key=lambda x: x[key], reverse=(True if sort == 'DESC' else False))
                except: error('Value Error', f'Cannot sort by "{key}". Please make sure every data has this row.', ifExit=False)
            # print('end sort       ', '==>', time.time())

            # print('start head body', '==>', time.time())
            # Select all rows from dataset
            head = []
            for row in dataset:
                for x in row:
                    if x not in head: head.append(x)

            # print('start head body1', '==>', time.time())
            # Select all cols from dataset
            body = []
            for data in dataset:
                temp = []
                for index in head: temp.append(data[index] if index in data else None)
                body.append(temp)
            # print('end head body  ', '==>', time.time())

            # print('start filter   ', '==>', time.time())
            if 'WHERE' in query: body = whereFilter(head, body, query['WHERE'], IorX='x')
            if 'LIMIT' in query: body = body[:int(query['LIMIT'][0])]
            # print('end filter     ', '==>', time.time())

            # print('start select   ', '==>', time.time())
            if '*' not in query['SELECT']:
                # Get selected rows
                selected_head = []
                for row in query['SELECT']:
                    if type(row) == list and row[0] not in selected_head: selected_head.append(row[0])
                    elif row not in selected_head: selected_head.append(row)
                selected_head = set(list(range(len(head)))) - set([head.index(x) if x in head else None for x in selected_head])

                # Remove unselected rows from head
                for i, j in enumerate(selected_head): head = head[:j - i] + head[j - i + 1:]

                # Remove unselected rows from body
                for i in range(len(body)):
                    for index, j in enumerate(selected_head): body[i] = body[i][:j - index] + body[i][j - index + 1:]
            # print('end select     ', '==>', time.time())

            # 'AS' function
            for row in query['SELECT']:
                if type(row) == list:
                    if row[0] in head: head[head.index(row[0])] = row[1]

            # Show result table
            if view:
                tabel = tabulate(body, headers=head, tablefmt="fancy_grid")
                print(tabel)

            print(f'Excuted successfully.')

            # Return result in json
            return [{x: y for x, y in zip(head, data)} for data in body]

        if mode == 'UPDATE':
            path = query['UPDATE'][0]
            if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')

            # Load database
            f = open(f'./database/{path}.table', 'r')
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
                for index in head: temp.append(data[index] if index in data else None)
                body.append(temp)

            if 'WHERE' in query: update = whereFilter(head, body, query['WHERE'], IorX='i')
            if 'LIMIT' in query: update = update[:int(query['LIMIT'][0])]

            # Update database
            for i in range(len(dataset)):
                if i in update:
                    for sets in query['SET']: dataset[i][sets[0]] = sets[1]

            # Store to database
            try:
                with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps(dataset))
                print(f'Updated successfully.')
                return True
            except: return False

        if mode == 'INSERT':
            path = query['INSERT'][1]
            if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')
            elif query['INSERT'][0] != 'INTO': error('Syntax Error', '"INSERT" must be user with "INTO"')

            # Remove 'INSERT' keyword and table name
            query['INSERT'] = query['INSERT'][2:]

            # Load database
            f = open(f'./database/{path}.table', 'r')
            dataset = json.load(f)

            # Input check
            if len(query['INSERT']) != len(query['VALUE']): error('Value Error', 'Insert columns must be same as value columns.')

            # Insert data to table
            dataset += [{x: y for x, y in zip(query['INSERT'], query['VALUE'])}]

            # Store to database
            try:
                with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps([dataset]))
                print(f'Inserted successfully.')
                return True
            except: return False

        if mode == 'DELETE':
            path = query['FROM'][0]
            if not os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} not found.')

            # Load database
            f = open(f'./database/{path}.table', 'r')
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
                for index in head: temp.append(data[index] if index in data else None)
                body.append(temp)

            if 'WHERE' in query: delete = whereFilter(head, body, query['WHERE'], IorX='i')
            if 'LIMIT' in query: delete = delete[:int(query['LIMIT'][0])]

            for i, x in enumerate(dataset):
                if i in delete:
                    if '*' in query['DELETE']: dataset[i] = ''
                    else:
                        for j in query['DELETE']:
                            if j in dataset[i]: del dataset[i][j]
            dataset = [x for x in dataset if x != '']

            # Store to database
            try:
                with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps(dataset))
                print(f'Deleted successfully.')
                return True
            except: return False

        if mode == 'CREATE':
            path = query['CREATE'][1]
            if os.path.isfile(f'./database/{path}.table'): error('Error', f'Table {path} exists.')
            query['CREATE'] = query['CREATE'][1:]

            dataset = {}
            for n in range(0, len(query['CREATE']), 2): dataset[query['CREATE'][n]] = query['CREATE'][n + 1]

            # Create database
            try:
                with open(f'./database/{path}.table', 'w') as f: f.write(json.dumps([dataset]))
                print(f'Created table "{path}" successfully.')
                return True
            except: error('Fatal', f'Failed to create table "{path}".')

        if mode == 'DROP':
            path = query['DROP'][1]
            if query['DROP'][0] != 'TABLE': error('Syntax Error', '"DROP" must be user with "TABLE"')
            query['DROP'] = query['DROP'][1:]

            for table in query['DROP']:
                if not os.path.isfile(f'./database/{table}.table'): error('Error', f'Table {table} not found.', ifExit=False)
                else:
                    try:
                        os.remove(f'./database/{table}.table')
                        print(f'Table {table} has been droped successfully.')
                        return True
                    except: return False
