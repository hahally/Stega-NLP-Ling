import tensorflow as tf
import numpy as np
import random
from sklearn.metrics import f1_score, precision_score, recall_score
from TS_RNN.models import Tsrnn
import os
from sklearn.metrics import confusion_matrix
random.seed(202)
np.random.seed(2022)
tf.random.set_seed(2022)

def infer(test, 
          val_mode='test',
          tokens, 
          folds=5, 
          mode='rnn',
          model_path='',
          max_len=30, 
          num_classes=2):
    
    word2indx = tokens.word_index
    vocab_size = len(word2indx) + 1
    
    sentences = test.sentence.tolist()
    x_test = tokens.texts_to_sequences(sentences)
    x_test = tf.keras.preprocessing.sequence.pad_sequences(x_test, maxlen=max_len,padding='post',truncating='post')
    y_test = test.label.to_numpy()
    
    predictions = np.zeros([len(test), num_classes])
    
    for fold in range(1, folds+1):
        bst_model_path = os.path.join(model_path, f"{mode}.{fold}.h5")
        model = Tsrnn(mode=mode,vocab_size=vocab_size,max_len=max_len,num_classes=num_classes)
        model.build(input_shape=(max_len,vocab_size))
        model.load_weights(bst_model_path)
        predictions += model.predict(x_test) / folds
    
    pre = np.argmax(predictions, axis = -1)
    
    if val_mode == 'inference':
          return pre
          
    average = 'binary'
    if num_classes>2:
        average = 'micro'
    accuracy = (pre == y_test).sum()/len(pre)    
    f1_s = f1_score(y_test, pre, average=average)
    precision = precision_score(y_test, pre, average=average)
    recall = recall_score(y_test, pre, average=average)
    cm = confusion_matrix(y_test, pre)
    print(f'accuracy:{accuracy},f1:{f1_s},precision:{precision},recall:{recall}')
    print('cm:',cm)
    return accuracy, f1_s, precision, recall,cm
