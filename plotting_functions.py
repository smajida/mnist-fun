import numpy as np
from keras_model import *
from additional_functions import *
import matplotlib  # necessary to save plots remotely; comment out if local
matplotlib.use('Agg')  # comment out if local
import matplotlib.pyplot as plt
from keras.utils import np_utils
import pandas as pd


def train_models_on_noisy_data(characteristic_noise_vals, X_or_y):
    ''' 
    INPUT:  (1) 1D numpy array: if on X, should be the standard deviations of
                the gaussian noise being added; if on y, should be the 
                percentages of labels to be randomly changed
            (2) string: 'X' or 'y' corresponding to which data to make noisy
    OUTPUT: None, directly at least. All models will be saved to /models    

    This function loads the basic data, then loops through the characteristic
    noise values and trains models on those noisy data. Classwise accuracies 
    can then be calculated from these models. 
    '''
    model_param = set_basic_model_param(0)
    X_train, y_train, X_test, y_test = load_and_format_mnist_data(model_param,
                                            categorical_y=False)
    for cnv in characteristic_noise_vals:
        name_to_append = '{}_{}'.format(X_or_y, cnv)
        model_param = set_basic_model_param(name_to_append)
        if X_or_y == 'X':
            print 'Training models with noise lev of {}'.format(cnv)
            noisy_X_train = add_gaussian_noise(X_train, mean=0, stddev=cnv)
            y_train = np_utils.to_categorical(y_train, model_param['n_classes'])
            y_test = np_utils.to_categorical(y_test, model_param['n_classes'])
            model = compile_model(model_param)
            fit_and_save_model(model, model_param, noisy_X_train, y_train, 
                               X_test, y_test)
        if X_or_y == 'y':
            print 'Training models with {}% random labels'.format(cnv)
            noisy_y_train = add_label_noise(y_train, cnv)
            noisy_y_train = np_utils.to_categorical(noisy_y_train, 
                                                    model_param['n_classes'])
            y_test = np_utils.to_categorical(y_test, model_param['n_classes'])
            model = compile_model(model_param)
            fit_and_save_model(model, model_param, X_train, noisy_y_train, 
                               X_test, y_test)


def calc_all_classwise_accs(noise_stddevs):
    '''
    INPUT:  (1) 1D numpy array: The standard deviations of the gaussian noise 
                being added to the data
    OUTPUT: (1) dictionary of lists: The accuracies over all standard deviations 
                for each digit in MNIST
    '''
    model_param = set_basic_model_param(noise_stddevs[0])
    X_train, y_train, X_test, y_test = load_and_format_mnist_data(model_param, 
                                                categorical_y=False)
    unique_classes = np.unique(y_test)
    classwise_accs = {unique_class: [] for unique_class in unique_classes}
    for noise_stddev in noise_stddevs:
        print '''Calculating classwise accs for model characteristic noise value
                of of {}'''.format(x)
        name_to_append = '{}_{}'.format('X', noise_stddev)
        model = load_model('models/KerasBaseModel_v.0.1_{}'.format(name_to_append))
        classwise_accs_to_add = predict_classwise_top_n_acc(model, X_test,
                                                            y_test)
        for elt in classwise_accs_to_add.keys():
            classwise_accs[elt].append(classwise_accs_to_add[elt])
    return classwise_accs


def plot_acc_vs_noisy_X(noise_stddevs, classwise_accs):
    unique_classes = sorted(classwise_accs.keys())
    color_inds = np.linspace(0, 1, len(unique_classes))
    for color_ind, unique_class in zip(color_inds, unique_classes):
        rolling_mean = pd.rolling_mean(np.array(classwise_accs[unique_class]),
                                       window=3, center=False)
        null_ind_from_rolling = np.where(pd.isnull(rolling_mean))[0]
        orig_vals_to_fill_nulls = np.array(classwise_accs[unique_class])[null_ind_from_rolling]
        rolling_mean[null_ind_from_rolling] = orig_vals_to_fill_nulls
        plt.plot(noise_stddevs, rolling_mean, 
                 color=plt.cm.jet(color_ind), label=str(unique_class))
    plt.xlabel('Standard Deviation of Gaussian Noise Added to Training Data')
    plt.ylabel('Accuracy')
    plt.legend(loc=3)
    #plt.ylim(.96, 1.01)
    plt.savefig('classwise_accuracy_vs_noisy_X_jet_3.png', dpi=200)

if __name__ == '__main__':
    pass
    #noise_stddevs = np.linspace(0, 192, 97)
    #train_models_on_noisy_data(noise_stddevs, 'X')
    #classwise_accs = calc_all_classwise_accs(noise_stddevs)
    #plot_acc_vs_noisy_X(noise_stddevs, classwise_accs)
