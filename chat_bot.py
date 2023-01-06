import re
import pandas as pd
import pyttsx3
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
import numpy as np
import csv
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

training = pd.read_csv('data/Training.csv')
testing = pd.read_csv('data/Testing.csv')
cols = training.columns
cols = cols[:-1]
x = training[cols]
y = training['prognosis']

reduced_data = training.groupby(training['prognosis']).max()

# mapping strings to numbers
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
testx = testing[cols]
testy = testing['prognosis']
testy = le.transform(testy)

clf1 = DecisionTreeClassifier()
clf = clf1.fit(x_train, y_train)
scores = cross_val_score(clf, x_test, y_test, cv=3)
print(scores.mean())

model = SVC()
model.fit(x_train, y_train)
print('for svm: ')
print(model.score(x_test, y_test))

importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = cols

severityDictionary = {}
description_list = {}
precautionDictionary = {}
symptoms_dict = {}

print('----------------------------------------------------------------------------------------')


class ChatBot:
    state = 'start'
    symptoms_given = []
    symptoms_given_index = 0
    symptoms_present = []
    _tree = None
    num_days = 0
    symptoms_exp = []
    feature_name = None
    disease_input = None
    node = 0
    depth = 1
    present_disease = None

    def __init__(self):
        super().__init__()
        for index, symptom in enumerate(x):
            symptoms_dict[symptom] = index
        self.get_severity_dict()
        self.get_description()
        self.get_precaution_dict()

    @staticmethod
    def begin():
        ChatBot.state = 'start'
        ChatBot.symptoms_given_index = 0
    def readn(self, nstr):
        engine = pyttsx3.init()

        engine.setProperty('voice', 'english+f5')
        engine.setProperty('rate', 130)

        engine.say(nstr)
        engine.runAndWait()
        engine.stop()

    def calc_condition(self, exp, days):
        sum = 0
        for item in exp:
            sum = sum + severityDictionary[item]
        if ((sum * days) / (len(exp) + 1) > 13):
            print('You should take the consultation from doctor. ')
        else:
            print('It might not be that bad but you should take precautions.')

    def get_description(self):
        global description_list
        with open('master_data/symptom_Description.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                _description = {row[0]: row[1]}
                description_list.update(_description)

    def get_severity_dict(self):
        global severityDictionary
        with open('master_data/symptom_severity.csv') as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            try:
                for row in csv_reader:
                    _diction = {row[0]: int(row[1])}
                    severityDictionary.update(_diction)
            except:
                pass

    def get_precaution_dict(self):
        global precautionDictionary
        with open('master_data/symptom_precaution.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                _prec = {row[0]: [row[1], row[2], row[3], row[4]]}
                precautionDictionary.update(_prec)

    def get_info(self, message):
        ChatBot.state = 'symptoms_step_1'
        return {'messages': [f'Hello {message}', 'Enter the symptom you are experiencing']}

    def check_pattern(self, dis_list, inp):
        inp = inp.replace(' ', '_')
        patt = f'{inp}'
        regexp = re.compile(patt)
        pred_list = [item for item in dis_list if regexp.search(item)]
        if (len(pred_list) > 0):
            return 1, pred_list
        else:
            return 0, []

    def sec_predict(self, symptoms_exp):
        df = pd.read_csv('Data/Training.csv')
        X = df.iloc[:, :-1]
        y = df['prognosis']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=20)
        rf_clf = DecisionTreeClassifier()
        rf_clf.fit(X_train, y_train)

        symptoms_dict = {symptom: index for index, symptom in enumerate(X)}
        input_vector = np.zeros(len(symptoms_dict))
        for item in symptoms_exp:
            input_vector[[symptoms_dict[item]]] = 1

        return rf_clf.predict([input_vector])

    def print_disease(self, node):
        node = node[0]
        val = node.nonzero()
        disease = le.inverse_transform(val[0])
        return list(map(lambda x: x.strip(), list(disease)))

    def get_symptoms_step_1(self, disease):
        ChatBot.tree_ = clf.tree_
        ChatBot.feature_name = [
            cols[i] if i != _tree.TREE_UNDEFINED else 'undefined!'
            for i in ChatBot.tree_.feature
        ]
        chk_dis = ','.join(cols).split(',')
        conf, cnf_dis = self.check_pattern(chk_dis, disease)
        if conf == 1:
            message = ['searches related to input:']
            for num, it in enumerate(cnf_dis):
                if num != 0:
                    return {'messages': [f'Select the one you meant (0 - {num}):']}
                message.append(f'{num}, {it}')
            ChatBot.disease_input = cnf_dis[0]
            ChatBot.state = 'symptoms_step_2'
            message.append('Okay. For how many days?:')
            return {'messages': message}
        else:
            return {'messages': ['Enter valid symptom.']}

    def get_symptoms_step_2(self, days):
        try:
            ChatBot.num_days = int(days)
            return self.recurse()
        except:
            return {'messages': ['Enter a valid number of days.']}

    def recurse(self):
        indent = '  ' * self.depth
        if ChatBot.tree_.feature[self.node] != _tree.TREE_UNDEFINED:
            name = ChatBot.feature_name[self.node]
            threshold = ChatBot.tree_.threshold[self.node]

            if name == ChatBot.disease_input:
                val = 1
            else:
                val = 0
            if val <= threshold:
                ChatBot.node = ChatBot.tree_.children_left[self.node]
                ChatBot.depth += 1
                return self.recurse()
            else:
                ChatBot.symptoms_present.append(name)
                return self.recurse()
        else:
            ChatBot.state = 'symptoms_step_3'
            return self.get_symptoms_step_3()

    def get_symptoms_step_3(self, message=''):
        ChatBot.present_disease = self.print_disease(ChatBot.tree_.value[ChatBot.node])
        red_cols = reduced_data.columns
        ChatBot.symptoms_given = red_cols[reduced_data.loc[ChatBot.present_disease].values[0].nonzero()]
        if ChatBot.symptoms_given_index == 0:
            ChatBot.symptoms_given_index += 1
            return {
                'messages': [
                    'Are you experiencing any of the following symptoms?',
                    ChatBot.symptoms_given[ChatBot.symptoms_given_index]
                ]
            }
        elif ChatBot.symptoms_given_index == len(ChatBot.symptoms_given) - 1:
            ChatBot.state = 'symptoms_step_4'
            return self.get_symptoms_step_4()
        else:
            return self.get_next_symptom(message)

    def get_next_symptom(self, response):
        response = response.lower()
        if response != 'yes' and response != 'no':
            return {'messages': ['Provide proper answers i.e. (yes/no)']}
        if response == 'yes':
            ChatBot.symptoms_exp.append(ChatBot.symptoms_given[ChatBot.symptoms_given_index])
        ChatBot.symptoms_given_index += 1
        return {'messages': [ChatBot.symptoms_given[ChatBot.symptoms_given_index]]}

    def get_symptoms_step_4(self):
        second_prediction = self.sec_predict(self.symptoms_exp)
        # print(second_prediction)
        self.calc_condition(self.symptoms_exp, self.num_days)
        messages = []
        if self.present_disease[0] == second_prediction[0]:
            messages.append(f'You may have {self.present_disease[0]}')
            messages.append(description_list[self.present_disease[0]])
        else:
            messages.append(f'You may have {self.present_disease[0]} or {second_prediction[0]}')
            messages.append(description_list[self.present_disease[0]])
            messages.append(description_list[second_prediction[0]])

        precution_list = precautionDictionary[self.present_disease[0]]
        messages.append('Take following measures :')
        for i, j in enumerate(precution_list):
            messages.append(f'({i + 1}), {j}')
        ChatBot.state = 'start'
        return {
            'messages': messages,
            'final': True
        }

    def get_response(self, message):
        if ChatBot.state == 'start':
            return self.get_info(message)
        elif ChatBot.state == 'symptoms_step_1':
            return self.get_symptoms_step_1(message)
        elif ChatBot.state == 'symptoms_step_2':
            return self.get_symptoms_step_2(message)
        elif ChatBot.state == 'symptoms_step_3':
            return self.get_symptoms_step_3(message)
        return {'message': []}
