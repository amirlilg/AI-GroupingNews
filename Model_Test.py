from sklearn.metrics import confusion_matrix

def fill_array(file):
    arr = []
    for line in file:
        arr.append(line)
test_address = input('Enter Test Name')
test_file = open(test_address, 'r')
test_lable_file = open(test_address+'.l')
test_lables = fill_array(test_lable_file)

pred_lables_file = open(test_address+'.guessedlabels', 'r')
pred_lables = fill_array(pred_lables_file)
confusion = confusion_matrix(test_lables, pred_lables)
print('confusion matrix')
print(confusion)
tn, fp, fn, tp = confusion.ravel()
precision = tp / (tp + fp)
recall = tp / (tp + fn)
fmeasure = 2 * (precision * recall) / (precision + recall)
print('precision : ' + str(precision) + '\n' + 'recall : ' + str(recall) + '\n' + 'fmeasure : ' + str(fmeasure))