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

warnings.filterwarnings("ignore", category=DeprecationWarning)

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
print("for svm: ")
print(model.score(x_test, y_test))

importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = cols

severityDictionary = {}
description_list = {}
precautionDictionary = {}
symptoms_dict = {}

print("----------------------------------------------------------------------------------------")


class ChatBot:
    def __init__(self):
        super().__init__()
        for index, symptom in enumerate(x):
            symptoms_dict[symptom] = index
        self.get_severity_dict()
        self.get_description()
        self.get_precaution_dict()
        self.state = 'start'

    def readn(self, nstr):
        engine = pyttsx3.init()

        engine.setProperty('voice', "english+f5")
        engine.setProperty('rate', 130)

        engine.say(nstr)
        engine.runAndWait()
        engine.stop()

    def calc_condition(self, exp, days):
        sum = 0
        for item in exp:
            sum = sum + severityDictionary[item]
        if ((sum * days) / (len(exp) + 1) > 13):
            print("You should take the consultation from doctor. ")
        else:
            print("It might not be that bad but you should take precautions.")

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
        return f'Hello {message}'

    def check_pattern(self, dis_list, inp):
        inp = inp.replace(' ', '_')
        patt = f"{inp}"
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

    def get_symptoms(self, tree, feature_names, message):
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]

        chk_dis = ",".join(feature_names).split(",")
        symptoms_present = []
        conf, cnf_dis = self.check_pattern(chk_dis, message)
        if conf == 1:
            print("searches related to input: ")
            for num, it in enumerate(cnf_dis):
                print(num, ")", it)
            if num != 0:
                print(f"Select the one you meant (0 - {num}):  ", end="")
                conf_inp = int(input(""))
            else:
                conf_inp = 0

            message = cnf_dis[conf_inp]
        else:
            print("Enter valid symptom.")

    def tree_to_code(self, tree, feature_names):
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]

        chk_dis = ",".join(feature_names).split(",")
        symptoms_present = []

        while True:

            print("\nEnter the symptom you are experiencing  \t\t", end="->")
            disease_input = input("")
            conf, cnf_dis = self.check_pattern(chk_dis, disease_input)
            if conf == 1:
                print("searches related to input: ")
                for num, it in enumerate(cnf_dis):
                    print(num, ")", it)
                if num != 0:
                    print(f"Select the one you meant (0 - {num}):  ", end="")
                    conf_inp = int(input(""))
                else:
                    conf_inp = 0

                disease_input = cnf_dis[conf_inp]
                break
            else:
                print("Enter valid symptom.")

        while True:
            try:
                num_days = int(input("Okay. From how many days ? : "))
                break
            except:
                print("Enter valid input.")

        def recurse(node, depth):
            indent = "  " * depth
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]

                if name == disease_input:
                    val = 1
                else:
                    val = 0
                if val <= threshold:
                    recurse(tree_.children_left[node], depth + 1)
                else:
                    symptoms_present.append(name)
                    recurse(tree_.children_right[node], depth + 1)
            else:
                present_disease = self.print_disease(tree_.value[node])
                red_cols = reduced_data.columns
                symptoms_given = red_cols[reduced_data.loc[present_disease].values[0].nonzero()]
                print("Are you experiencing any ")
                symptoms_exp = []
                for syms in list(symptoms_given):
                    inp = ""
                    print(syms, "? : ", end='')
                    while True:
                        inp = input("")
                        if (inp == "yes" or inp == "no"):
                            break
                        else:
                            print("provide proper answers i.e. (yes/no) : ", end="")
                    if (inp == "yes"):
                        symptoms_exp.append(syms)

                second_prediction = self.sec_predict(symptoms_exp)
                # print(second_prediction)
                self.calc_condition(symptoms_exp, num_days)
                if (present_disease[0] == second_prediction[0]):
                    print("You may have ", present_disease[0])
                    print(description_list[present_disease[0]])

                    # readn(f"You may have {present_disease[0]}")
                    # readn(f"{description_list[present_disease[0]]}")

                else:
                    print("You may have ", present_disease[0], "or ", second_prediction[0])
                    print(description_list[present_disease[0]])
                    print(description_list[second_prediction[0]])

                # print(description_list[present_disease[0]])
                precution_list = precautionDictionary[present_disease[0]]
                print("Take following measures : ")
                for i, j in enumerate(precution_list):
                    print(i + 1, ")", j)

                # confidence_level = (1.0*len(symptoms_present))/len(symptoms_given)
                # print("confidence level is " + str(confidence_level))

        recurse(0, 1)

    def print_result(self):

        self.tree_to_code(clf, cols)

    def get_response(self, message):
        if self.state == 'start':
            return self.get_info(message)
        # Each step you need to change the state to know which response to get
        return ''