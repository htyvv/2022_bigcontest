from tkinter import Grid
from lightgbm import LGBMClassifier, plot_importance
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix, plot_confusion_matrix, classification_report
import matplotlib.pyplot as plt
import shap
import pandas as pd
import numpy as np
import seaborn as sns
import eli5
from eli5.sklearn import PermutationImportance



class LGBM():
    # {'n_estimators': list(np.linspace(100, 5000, 50)),
    #                          'learning_rate': [0.2, 0.1, 0.05, 0.01],
    #                          'max_depth': list(range(3,11)),
    #                          'subsample': [0,7, 0.8, 0.9, 1],
    #                          'colsample_bytree':[0.5, 0.75, 1]}
    
    def __init__(self, train_X, train_Y, val_X, val_Y, random_state):
        self.train_X = train_X
        self.train_Y = train_Y
        self.val_X = val_X
        self.val_Y = val_Y
        self.params = {'n_estimators': [2000, 3000, 4000],
                         'learning_rate': [0.1, 0.05, 0.01],
                         'max_depth': [5,7,9]}
        self.random_state = random_state
        
        
    def grid_search(self):
        train_X = self.train_X
        train_Y = self.train_Y
        val_X = self.val_X
        val_Y = self.val_Y
        params = self.params
        
        def evaluate_macroF1_lgb(y_true, y_pred):  
            y_pred_label = np.round(y_pred)
            f1 = f1_score(y_true, y_pred_label, average='macro')
            print('f1 score:', f1)
            return ('f1_score', f1, True)
        
        
        lgbm = LGBMClassifier()
        lgbm_grid = RandomizedSearchCV(lgbm, param_distributions= params, n_iter=3, scoring="f1", cv=3, refit=True, random_state=self.random_state)
        lgbm_grid.fit(train_X, train_Y, early_stopping_rounds=50, eval_metric=evaluate_macroF1_lgb, eval_set=[(val_X, val_Y)])
        
        print('best parameters : ', lgbm_grid.best_params_)
        print('best val score : ', round(lgbm_grid.best_score_, 4))
        
        best_model = lgbm_grid.best_estimator_
        
        return best_model
    
    def val_score(self, model):
        val_X = self.val_X
        val_Y = self.val_Y
        
        pred = model.predict(val_X)
        F1_score = f1_score(val_Y, pred, average='macro', labels=np.unique(pred))
        print("f1_score: ", F1_score)
        print(classification_report(val_Y, pred))
        
    def confusion_matrix(self, model):
        val_X = self.val_X
        val_Y = self.val_Y
        
        label=['0', '1']
        plot = plot_confusion_matrix(model,
                                    val_X, val_Y, 
                                    display_labels=label,
                                    # cmap=plt.cm.Blue,  (plt.cm.Reds, plt.cm.rainbow)
                                    normalize=None) # 'true', 'pred', 'all', default=None
        plot.ax_.set_title('Confusion Matrix')
        plt.show()
        
    def feature_importance(self, model):
        fig, ax = plt.subplots(figsize=(9,11))
        plot_importance(model, ax=ax)
        plt.show()
        
        
    def shap(self, model):
        val_X = self.val_X
        
        explainer = shap.TreeExplainer(model) 
        shap_values = explainer.shap_values(val_X)
        
        plt.subplot(121)
        shap.initjs() 
        shap.summary_plot(shap_values, val_X)
        plt.show()
        
        plt.subplot(122)
        shap.summary_plot(shap_values, val_X, plot_type = "bar")
        plt.show()
        
    def permutation_importance(self, model):
        val_X = self.val_X
        val_Y = self.val_Y
        perm = PermutationImportance(model, scoring = "f1", random_state = self.random_state).fit(val_X, val_Y)
        eli5.show_weights(perm, top = 20, feature_names = val_X.columns.tolist())
        
    def pred_testset(self, test_X, model):
        pred = model.predict(test_X)
        test_X['is_applied'] = pred
        return test_X
        
        