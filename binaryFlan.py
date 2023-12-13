from Models.FakeModel import Model
from Models.FLAN_T5 import Flan

# import numpy as np
from checklist.editor import Editor
# from checklist.perturb import Perturb
# from checklist.test_types import MFT, INV, DIR
# from checklist.pred_wrapper import PredictorWrapper

import csv
editor = Editor()

## FLAN-T5
model = Flan()
filename = "FLAN_T5_tests.csv"

PE_ACCEPTABLE = [
    "energy at rest",
    "energy that a body has because of its position relative to other bodies",
    "energy stored in the car at the top of the initial drop",
    "the stored energy of the rollercoaster car when it is not moving.",
    "energy that has the potential to become another form of energy.",
]
PE_UNACCEPTABLE = [
    "energy in motion",
    "energy lost as the car goes down the hill",
    "opposite of kinetic energy",
    "energy that is conserved by not moving.",
    "energy that is lost due to heat"
]
PE_INSUFFICIENT = [
    "4 Joules at the top of the roller coaster",
    "measured in Joules",
    "equal to m*h*9.8",
    "when there is more potential energy at the top of the hill than the bottom",
    "is changed into kinetic energy as the car goes down the hill."
]

KE_ACCEPTABLE = [
    "energy in motion",
    "energy that the car has because it is moving",
    "the work needed to accelerate the roller coaster car from rest",
    "determined by the mass of the car and the velocity with which it is moving.",
    "is what quantifies the work an object performs due to its motion",
]
KE_UNACCEPTABLE = [
    "energy at rest",
    "never lost nor gained as the car moves",
    "the opposite of potantial energy",
    "energy that is spent by moving up and down the hill.",
    "energy that is lost due to heat",
]
KE_INSUFFICIENT = [
    "4 Joules at the bottom of the roller coaster",
    "measured in Joules",
    "equal to .5*m*v^2",
    "when there is more kinetic energy at the bottom of the hill than at the top.",
    "what transforms into heat through friction"
]

LCE_ACCEPTABLE = [
    "energy cannot be created or destroyed, only transformed",
    "the total energy of an isolated system remains constant",
    "energy can be converted from one form to another, but never created or destroyed",
    "that if there were no friction, the potential energy at the top of the rollercoaster would be the same as the kinetic energy at the bottom of the drop.",
    "energy cannot be created or destroyed",
]
LCE_UNACCEPTABLE = [
    "energy can be created or destroyed, not transformed",
    "the total energy of an isolated system will change",
    "that the energy of a closed system will change.",
    "in an open system, energy is conserved",
    "kinetic energy is always equal to potential energy",
]
LCE_INSUFFICIENT = [
    "K1 + U1 = K2 + U2",
    "potential energy transforms into kinetic energy",
    "As the car goes down the hill, some energy is lost to friction as heat",
    "If there were no friction, the energy would be the same at the start and at the finish.",
]

UNRELATED = [
    "This roller coaster is very fun"
    "The hill drops into a loop"
    "The car moves along the path"
    "The roller coaster has 4 hills"
    "The roller coaster has a height of 10 meters"
]

def getData(samples, expected):
    fails = 0
    data = [{"sample": "", "expected": {}, "actual": {}, "results": {}} for _ in range(len(samples.data))]
    for i, sample in enumerate(samples.data):
        data[i]["sample"] = sample
        data[i]["expected"] = expected
        d = model.get_results(sample)
        data[i]["actual"] = d
        label = d['PE'] if len(d['PE']) != 0 else d['KE'] if len(d['KE']) != 0 else d['LCE']
        score = 0
        if expected['PE'] == d['PE']:
            score += 1
            data[i]["results"]["PE"] = "PASS"
        else:
            data[i]["results"]["PE"] = "FAIL"
        if expected['KE'] == d['KE']:
            score += 1
            data[i]["results"]["KE"] = "PASS"
        else:
            data[i]["results"]["KE"] = "FAIL"
        if expected['LCE'] == d['LCE']:
            score += 1
            data[i]["results"]["LCE"] = "PASS"
        else:
            data[i]["results"]["LCE"] = "FAIL"

        if score != 3:
            print("FAIL: " + sample)
            print(" Actual: " + str(d))
            print(" Expected: " + str(expected))
            data[i]["results"]["Overall"] = "FAIL"
            fails += 1
        else:
            print("PASS: " + sample)
            print(" Actual: " + str(d))
            print(" Expected: " + str(expected))
            data[i]["results"]["Overall"] = "PASS"

    print(str(fails) + " fails out of " + str(len(samples.data)) + " tests")
    return data


with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows([["Test Category", "Test Type", "Test Description", "Sample",
                       "Expected PE", "Expected KE", "Expected LCE",
                       "Actual PE", "Actual KE,", "Actual LCE",
                       "PE Result", "KE Result", "LCE Result", "Overall Result"]])
    print("Successfully created file")


def writeData(category, type, description, data):
    rows = [[] for _ in range(len(data))]
    for i in range(len(data)):
        rows[i] = ([category,
                    type,
                    description,
                    data[i]["sample"],
                    data[i]["expected"]["PE"],
                    data[i]["expected"]["KE"],
                    data[i]["expected"]["LCE"],
                    data[i]["actual"]["PE"],
                    data[i]["actual"]["KE"],
                    data[i]["actual"]["LCE"],
                    data[i]["results"]["PE"],
                    data[i]["results"]["KE"],
                    data[i]["results"]["LCE"],
                    data[i]["results"]["Overall"]])

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    return


# Knowledge

samples = editor.template(
    "Potential energy is {pe_acceptable}",
    pe_acceptable=PE_ACCEPTABLE
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_acceptable}",
    ke_acceptable=KE_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_acceptable}.",
    lce_acceptable=LCE_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Knowledge", "MFT", "Acceptable definitions", data)

samples = editor.template(
    "Potential energy is {pe_unacceptable}",
    pe_unacceptable=PE_UNACCEPTABLE
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_unacceptable}",
    ke_unacceptable=KE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_unacceptable}.",
    lce_unacceptable=LCE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Knowledge", "MFT", "Unacceptable definitions", data)

samples = editor.template(
    "Potential energy is {pe_insufficient}",
    pe_insufficient=PE_INSUFFICIENT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_insufficient}",
    ke_insufficient=KE_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_insufficient}.",
    lce_insufficient=LCE_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Knowledge", "MFT", "Unacceptable definitions", data)

samples = editor.template(
    "{unrelated}.",
    unrelated = UNRELATED
)

data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Knowledge", "MFT", "Unrelated definitions", data)

samples = editor.template(
    "Potential energy is {pe_acceptable}. Potential energy is {pe_unacceptable}.",
    pe_acceptable=PE_ACCEPTABLE, pe_unacceptable=PE_UNACCEPTABLE
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_acceptable}. Kinetic energy is {ke_unacceptable}.",
    ke_acceptable=KE_ACCEPTABLE, ke_unacceptable=KE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_acceptable}. The Law of Conservation of energy states {lce_unacceptable}.",
    lce_acceptable=LCE_ACCEPTABLE, lce_unacceptable=LCE_UNACCEPTABLE,
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Knowledge", "INV", "Acceptable definition followed by Unacceptable", data)

samples = editor.template(
    "Potential energy is {pe_unacceptable}. Potential energy is {pe_acceptable}",
    pe_acceptable=PE_ACCEPTABLE, pe_unacceptable=PE_UNACCEPTABLE
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_unacceptable}. Kinetic energy is {ke_acceptable}",
    ke_acceptable=KE_ACCEPTABLE, ke_unacceptable=KE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_unacceptable}. The Law of Conservation of energy states {lce_acceptable}",
    lce_acceptable=LCE_ACCEPTABLE, lce_unacceptable=LCE_UNACCEPTABLE,
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Knowledge", "DIR", "Unacceptable definition followed by acceptable", data)

samples = editor.template(
    "Potential energy is {pe_insufficient}. Potential energy is {pe_acceptable}",
    pe_insufficient=PE_INSUFFICIENT, pe_acceptable=PE_ACCEPTABLE
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_insufficient}. Kinetic energy is {ke_acceptable}",
    ke_insufficient=KE_INSUFFICIENT, ke_acceptable=KE_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_insufficient}. The Law of Conservation of energy states {lce_acceptable}",
    lce_insufficient=LCE_INSUFFICIENT, lce_acceptable=LCE_ACCEPTABLE,
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Knowledge", "DIR", "Unacceptable definition followed by acceptable", data)

samples = editor.template(
    "Potential energy is {pe_insufficient}. Potential energy is {pe_unacceptable}",
    pe_insufficient=PE_INSUFFICIENT, pe_unacceptable=PE_UNACCEPTABLE
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_insufficient}. Kinetic energy is {ke_unacceptable}",
    ke_insufficient=KE_INSUFFICIENT, ke_unacceptable=KE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_insufficient}. The Law of Conservation of energy states {lce_unacceptable}",
    lce_insufficient=LCE_INSUFFICIENT, lce_unacceptable=LCE_UNACCEPTABLE,
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Knowledge", "DIR", "Unacceptable definition followed by unacceptable", data)

samples = editor.template(
    "Potential energy is not {pe_acceptable}",
    pe_acceptable=PE_ACCEPTABLE
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is not {ke_acceptable}",
    ke_acceptable=KE_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy does not state {lce_acceptable}.",
    lce_acceptable=LCE_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Negation", "MFT", "Negation of acceptable definitions", data)

samples = editor.template(
    "Potential energy is not {pe_unacceptable}",
    pe_unacceptable=PE_UNACCEPTABLE
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is not {ke_unacceptable}",
    ke_unacceptable=KE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy does not state {lce_unacceptable}.",
    lce_unacceptable=LCE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})
writeData("Negation", "MFT", "Negation of unacceptable definitions", data)

PE_TYPO_CORRECT = [
    "pontenshul energy that body has becuse of its posiion relative to other bdies.",
    "potental energy store in te car at the tp of the initl drp.",
]
KE_TYPO_CORRECT = [
    "Kintic enery is energy tht the car hs bcase i is movng.",
    "Kinetec enrgy is the wrk neded to acelerate the rolercoaser car from rest.",
]
LCE_TYPO_CORRECT = [
    "the lw of consevashun of energy says that energy canot be create or destroy, ony transfomed.",
    "the law of conversion of energy the totl energy of an isolated systm remain constnt.",
]

samples = editor.template(
    "{pe_typo_correct}",
    pe_typo_correct=PE_TYPO_CORRECT
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_typo_correct}",
    ke_typo_correct=KE_TYPO_CORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_typo_correct}.",
    lce_typo_correct=LCE_TYPO_CORRECT
)

data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Robustness", "INV", "Misspelling of acceptable definitions", data)

PE_TYPO_INCORRECT = [
    "Potential energy i energy in moton.",
    "Potentia energy is the energy lose as th car go down the hil.",
]
KE_TYPO_INCORRECT = [
    "Kinetic enery is energy tht the car hs bcase i is movng.",
    "Kinetic ergy is the wrk neded to acelerate the rolercoaser car from rest.",

]
LCE_TYPO_INCORRECT = [
    "LCE says that energy canot be create or destroy, ony transfomed.",
    "law of conserve energy state the totl energy of an isolated systm remain constnt.",
]

samples = editor.template(
    "{pe_typo_incorrect}",
    pe_typo_incorrect=PE_TYPO_INCORRECT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_typo_incorrect}",
    ke_typo_incorrect=KE_TYPO_INCORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_typo_incorrect}.",
    lce_typo_incorrect=LCE_TYPO_INCORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Robustness", "INV", "Misspelling of unacceptable definitions", data)

PE_TYPO_INSUFFICIENT = [
    "The potentia energ at the top of te rollercoaer is 4.9 juls.",
    "Potential enrgy is measur in jules.",
]
KE_TYPO_INSUFFICIENT = [
    "The kinetic energy at the botom of the hile is 4.8 joul.",
    "Kinetic nergy transfourms into heet thrugh fricton",
]
LCE_TYPO_INSUFFICIENT = [
    "The potensial energy trainsforms in to kinetic energy becuz of the law of conservashun of energy.",
    "As the car goes down the hill, some energ is lost to fricshiun as heat.",
]

samples = editor.template(
    "{pe_typo_insufficient}",
    pe_typo_insufficient=PE_TYPO_INSUFFICIENT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_typo_insufficient}",
    ke_typo_insufficient=KE_TYPO_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_typo_insufficient}.",
    lce_typo_insufficient=LCE_TYPO_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Robustness", "INV", "Misspelling of insufficient definitions", data)

PE_PARA_ACCEPTABLE = [
    "Energy that a body has because of its position relative to other bodies is potential energy",
    "The car stores energy at the top of the initial drop as potential energy",
]
KE_PARA_ACCEPTABLE = [
    "The car has kinetic energy because it is moving.",
    "The work needed to accelerate the rollercoaster car from rest is kinetic energy.",
]
LCE_PARA_ACCEPTABLE = [
    "The Law of Conservation of Energy states that energy can be converted from one form to another but cannot be created or destroyed.",
    "The Law of Conservation of Energy says that if there were no friction, the potential energy at the top of the rollercoaster would be the same as the kinetic energy at the bottom of the drop."
]

samples = editor.template(
    "{pe_para_acceptable}.",
    pe_para_acceptable=PE_PARA_ACCEPTABLE
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_para_acceptable}.",
    ke_para_acceptable=KE_PARA_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_para_acceptable}.",
    lce_para_acceptable=LCE_PARA_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Robustness", "INV", "Paraphrased version of acceptable definitions", data)

PE_PARA_UNACCEPTABLE = [
    "The car loses energy as it goes down the hill, which is potential energy.",
    "Potential energy stands in contrast to kinetic energy.",
]
KE_PARA_UNACCEPTABLE = [
    "The car does not experience any change in kinetic energy as it moves through the rollercoaster.",
    "Kinetic energy is the antithesis of potential energy.",
]
LCE_PARA_UNACCEPTABLE = [
    "The Law of Conservation of Energy asserts that energy can be created and destroyed.",
    "The energy of a closed system changes, as stated by the Law of Conservation of Energy.",
    "In an open system, energy is not conserved, as per the Law of Conservation of Energy."
]

samples = editor.template(
    "{pe_para_unacceptable}.",
    pe_para_unacceptable=PE_PARA_UNACCEPTABLE
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_para_unacceptable}.",
    ke_para_unacceptable=KE_PARA_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_para_unacceptable}.",
    lce_para_unacceptable=LCE_PARA_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Robustness", "INV", "Paraphrased version of unacceptable definitions", data)

PE_PARA_INSUFFICIENT = [
    "The potential energy at the top of the rollercoaster equals 4.9 joules",
    "Joules measure potential energy",
]
KE_PARA_INSUFFICIENT = [
    "There is a greater amount of kinetic energy at the bottom of the hill compared to the top.",
    "Friction causes the transformation of kinetic energy into heat.",
]
LCE_PARA_INSUFFICIENT = [
    "The Law of Conservation of Energy says that some energy is lost as heat due to friction as the car descends the hill.",
    "In the absence of friction, the energy remains constant from the start to the finish, as stated by the Law of Conservation of Energy",
]

samples = editor.template(
    "{pe_para_insufficient}.",
    pe_para_insufficient=PE_PARA_INSUFFICIENT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_para_insufficient}.",
    ke_para_insufficient=KE_PARA_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_para_insufficient}.",
    lce_para_insufficient=LCE_PARA_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Robustness", "INV", "Paraphrased version of insufficient definitions", data)

samples = editor.template(
    "PE is {pe_acceptable}",
    pe_acceptable=PE_ACCEPTABLE
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "KE is {ke_acceptable}",
    ke_acceptable=KE_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "LCE states {lce_acceptable}.",
    lce_acceptable=LCE_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Robustness", "INV", "Acronyms of acceptable definitions", data)

samples = editor.template(
    "PE is {pe_unacceptable}",
    pe_unacceptable=PE_UNACCEPTABLE
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "KE is {ke_unacceptable}",
    ke_unacceptable=KE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "LCE states {lce_unacceptable}.",
    lce_unacceptable=LCE_UNACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Robustness", "INV", "Acronyms of unacceptable definitions", data)

samples = editor.template(
    "PE is {pe_insufficient}",
    pe_insufficient=PE_INSUFFICIENT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "KE is {ke_insufficient}",
    ke_insufficient=KE_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "LCE states {lce_insufficient}.",
    lce_insufficient=LCE_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Robustness", "INV", "Acronyms of insufficient definitions", data)

samples = editor.template(
    "Potential energy is {pe_acceptable}. {unrelated}.",
    pe_acceptable=PE_ACCEPTABLE, unrelated=UNRELATED, nsamples=10
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_acceptable}. {unrelated}.",
    ke_acceptable=KE_ACCEPTABLE, unrelated=UNRELATED, nsamples=10
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_acceptable}. {unrelated}.",
    lce_acceptable=LCE_ACCEPTABLE, unrelated=UNRELATED, nsamples=10
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Robustness", "INV", "Adding random unrelated sentence to acceptable definition", data)

samples = editor.template(
    "Potential energy is {pe_unacceptable}. {unrelated}.",
    pe_unacceptable=PE_UNACCEPTABLE, unrelated=UNRELATED, nsamples=10
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_unacceptable}. {unrelated}.",
    ke_unacceptable=KE_UNACCEPTABLE, unrelated=UNRELATED, nsamples=10
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_unacceptable}. {unrelated}.",
    lce_unacceptable=LCE_UNACCEPTABLE, unrelated=UNRELATED, nsamples=10
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Robustness", "INV", "Adding random unrelated sentence to unacceptable definition", data)

PE_SYNONYM_CORRECT = [
    "energy that a body has because of its position relative to other bodies.",
    "energy inside the car at the top of the initial drop.",
]
KE_SYNONYM_CORRECT = [
    "energy that the vehicle has because it is moving.",
    "the work needed to change the speed the rollercoaster car from rest.",
]
LCE_SYNONYM_CORRECT = [
    "that energy can be turned from one form to another, but never created or destroyed.",
    "that if there were no rubbing, the potential energy at the top of the rollercoaster.",
    "would equal to the kinetic energy at the bottom of the drop.",
]

samples = editor.template(
    "Potential energy is {pe_synonym_correct}",
    pe_synonym_correct=PE_SYNONYM_CORRECT
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_synonym_correct}",
    ke_synonym_correct=KE_SYNONYM_CORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_synonym_correct}.",
    lce_synonym_correct=LCE_SYNONYM_CORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Taxonomy", "INV", "Synonyms within acceptable definitions", data)

PE_SYNONYM_INCORRECT = [
    "the energy lost as the car rolls down the hill.",
    "the opposite of kinetic energy.",
]
KE_SYNONYM_INCORRECT = [
    "never lost or gained as the car moves through the rollercoaster.",
    "the opposite of potential energy.",
]
LCE_SYNONYM_INCORRECT = [
    "that energy can be made and taken.",
    "that the energy of a closed system will differ.",
    "that in an open system, energy is constant",
]

samples = editor.template(
    "Potential energy is {pe_synonym_incorrect}",
    pe_synonym_incorrect=PE_SYNONYM_INCORRECT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_synonym_incorrect}",
    ke_synonym_incorrect=KE_SYNONYM_INCORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_synonym_incorrect}.",
    lce_synonym_incorrect=LCE_SYNONYM_INCORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Taxonomy", "INV", "Synonyms within unacceptable definitions", data)

PE_SYNONYM_INSUFFICIENT = [
    "The potential energy at the tip of the rollercoaster is 4.9 joules.",
    "Potential energy is calculated in joules.",
]
KE_SYNONYM_INSUFFICIENT = [
    "There is higher kinetic energy at the bottom of the hill than at the top.",
    "Kinetic energy turns into heat through friction",
]
LCE_SYNONYM_INSUFFICIENT = [
    "As the car goes down the hill, some energy does away to friction as heat.",
    "If there were no friction, the energy would stay the same.",
]

samples = editor.template(
    "{pe_synonym_insufficient}",
    pe_synonym_insufficient=PE_SYNONYM_INSUFFICIENT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_synonym_insufficient}",
    ke_synonym_insufficient=KE_SYNONYM_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_synonym_insufficient}.",
    lce_synonym_insufficient=LCE_SYNONYM_INSUFFICIENT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Taxonomy", "INV", "Synonyms within insufficient definitions", data)

PE_NEGANT_CORRECT = [
    "energy that a body does not lack because of its position relative to other bodies.",
    "energy not outside the car at the top of the initial drop.",
]
KE_NEGANT_CORRECT = [
    "energy that the car has because it is not still.",
    "the work needed to change the speed the rollercoaster car from not moving.",
]
LCE_NEGANT_CORRECT = [
    "that energy can be transformed from one form to another, but not ever created or destroyed.",
    "that the total energy of an isolated system remains not variable.",
]

samples = editor.template(
    "Potential energy is {pe_negant_correct}",
    pe_negant_correct=PE_NEGANT_CORRECT
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_negant_correct}",
    ke_negant_correct=KE_NEGANT_CORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_negant_correct}.",
    lce_negant_correct=LCE_NEGANT_CORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})

writeData("Taxonomy", "INV", "Negated antonyms within acceptable definitions", data)

PE_NEGANT_INCORRECT = [
    "energy not stationary.",
    "not the same as kinetic energy.",
]
KE_NEGANT_INCORRECT = [
    "energy not in motion.",
    "not the same as potential energy.",
]
LCE_NEGANT_INCORRECT = [
    "that the energy of a not open system will change.",
    "that in a not closed system, energy is conserved",
]

samples = editor.template(
    "Potential energy is {pe_negant_incorrect}",
    pe_negant_incorrect=PE_NEGANT_INCORRECT
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_negant_incorrect}",
    ke_negant_incorrect=KE_NEGANT_INCORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_negant_incorrect}.",
    lce_negant_incorrect=LCE_NEGANT_INCORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Taxonomy", "INV", "Negated antonyms within unacceptable definitions", data)

PE_ANT_ACCEPTABLE = [
    "Potential energy is energy while moving",
    "Potential energy is energy released by the car at the top of the initial drop",
]
KE_ANT_ACCEPTABLE = [
    "Kinetic energy is energy that the car has because it is resting",
    "Kinetic energy is the work needed to slow down the rollercoaster car",
]
LCE_ANT_ACCEPTABLE = [
    "The law of conservation of energy says that if there were no friction, the potential energy at the top of the rollercoaster would be different from the kinetic energy at the bottom of the drop.",
    "The law of conservation of energy states that the total energy of an isolated system changes sometimes."
]

samples = editor.template(
    "{pe_ant_acceptable}",
    pe_ant_acceptable=PE_ANT_ACCEPTABLE
)
data = getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{ke_ant_acceptable}",
    ke_ant_acceptable=KE_ANT_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "{lce_ant_acceptable}",
    lce_ant_acceptable=LCE_ANT_ACCEPTABLE
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

writeData("Taxonomy", "DIR", "Antonyms within acceptable definitions", data)

PE_SPANISH_CORRECT = [
    "Potential energy is energy that a body has because of its position relativa a other bodies.",
    "Potential energy is the stored energy of the rollercoaster car when no se esta moviendo.",
    "Potential energy is energy that has the potential to convertirse en otro form of energy.",
]
KE_SPANISH_CORRECT = [
    "Kinetic energy is the work necesario para accelerate the rollercoaster car from rest.",
    "Kinetic energy is determined by the mass del carro and the velocity with which it is moving.",
    "Kinetic energy quantifies the work an object performs debido a su movimiento",
]
LCE_SPANISH_CORRECT = [
    "LCE states that energy can be convertida from one form to another, but never created or destroyed.",
    "LCE says that if there were no friction, the potential energy en la cima del rollercoaster would be the same as the kinetic energy at the bottom of the drop.",
    "LCE is a physical law that states that energy no se puede crear or destroyed but only transformed",
]

samples = editor.template(
    "Potential energy is {pe_spanish_correct}",
    pe_spanish_correct=PE_SPANISH_CORRECT,
)
data = getData(samples, {"PE": "Acceptable", "KE": "Unacceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "Kinetic energy is {ke_spanish_correct}",
    ke_spanish_correct=KE_SPANISH_CORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Acceptable", "LCE": "Unacceptable"})

samples = editor.template(
    "The Law of Conservation of energy states {lce_spanish_correct}.",
    lce_spanish_correct=LCE_SPANISH_CORRECT
)
data += getData(samples, {"PE": "Unacceptable", "KE": "Unacceptable", "LCE": "Acceptable"})
writeData("Fairness", "INV", "Spanish translation within acceptable definitions", data)

