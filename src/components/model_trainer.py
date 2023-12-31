import os
import sys
from dataclasses import dataclass
from catboost import CatBoostRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor
)
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score

from src.pipeline.exception import CustomException
from src.pipeline.logger import logging
from src.pipeline.utils import save_object
from src.pipeline.utils import evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'model.pkl')

class ModelTrainer:
    def __init__(self) :
        self.model_trainer_config = ModelTrainerConfig()

    
    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info('Splitting train and test data')

            X_train, y_train, X_test, y_test = (
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]

            )

            #creating dictionaries of models
            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Linear Regression" : LinearRegression(),
                "k Neighbor" : KNeighborsRegressor(),
                "AdaBoost" : AdaBoostRegressor(),
                "CatBoost" : CatBoostRegressor(verbose = False),
                "XGBoost" : XGBRegressor()
            }

            params={
                "Decision Tree": {
                    'criterion':['friedman_mse',  'poisson'],
                    # 'splitter':['best','random'],
                    # 'max_features':['sqrt','log2'],
                },
                "Random Forest":{
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                 
                    # 'max_features':['sqrt','log2',None],
                    'n_estimators': [8,16,32,64,128,256]
                },
                

                "Linear Regression":{

                },

                "XGBoost":{
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators': [8,16,32,64,128,256]
                },

                "CatBoost":{
                    'depth': [6,8,10],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'iterations': [30, 50, 100]
                },

                "AdaBoost":{
                    'learning_rate':[.1,.01,0.5,.001],
                    # 'loss':['linear','square','exponential'],
                    'n_estimators': [8,16,32,64,128,256]
                },

                "k Neighbor": {
                    'n_neighbors' : [3,5,6,7,8],
                    'weights' : ['uniform', 'distance']
                }
                
            }

            model_report:dict = evaluate_models(X_train = X_train, y_train = y_train, X_test = X_test, y_test = y_test, models = models, param = params)

            #To get best model score from dict
            best_model_score  = max(sorted(model_report.values()))

            #To get best model name from dict

            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]

            best_model = models[best_model_name]

            if best_model_score < 0.6:
                raise CustomException("No Best Model Found")
            logging.info(f"Best Model Found on both training and testing dataset")


            save_object(
                file_path = self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )
        
            predicted =best_model.predict(X_test)

            r2_square = r2_score(y_test, predicted)

            return r2_square
    
        except Exception as e:
            raise CustomException(e, sys)

