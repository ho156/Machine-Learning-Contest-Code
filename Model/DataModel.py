

from keras import models, layers
import pandas as pd
import numpy as np
from keras.utils import plot_model
import logging
from matplotlib import pyplot as plt
import os


class DataModel:
    """
    功能：对处理好的数据进行数据建模，并对test数据进行预测
    输入：
    ----1.特征工程处理好的train数据
    ----2.特征工程处理好的test数据
    ----3.原始test数据
    输出：
    ----1.建模之后的模型文件
    ----2.test数据预测的结果，并作为一列加入原始test数据
    """

    def __init__(self, trainFeaFilePath, tesFeatFilePath, rawTestFilePath):
        # Feature Enginering Train Data
        self.trainFeaFilePath = trainFeaFilePath
        # Feature Enginering Test Data
        self.tesFeatFilePath = tesFeatFilePath
        # Raw Test Data
        self.rawTestFilePath = rawTestFilePath

        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        self.handler = logging.FileHandler("log.txt")
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    # Read Files
    def readFile(self, filePath):
        if os.path.isfile(filePath):
            postfix = os.path.splitext(filePath)[1]
            if postfix.endswith(".csv"):
                return pd.read_csv(filePath)
            elif postfix.endswith(".xlsx"):
                return pd.read_excel(filePath)
            elif postfix.endswith(".xls"):
                return pd.read_excel(filePath)
            else:
                self.logger.error("file format is wrong")
        else:
            self.logger.error("not file")

    # Concat Predict Values and Raw Test Data
    def concatRes(self, rawTestData, result):
        return pd.concat([rawTestData, result], axis=1)

    # Save to csv File
    def save2File(self, dataFrame, savePath="", name="outputCsv.csv", index=False):
        filePath = savePath + name
        try:
            return dataFrame.to_csv(filePath, index=index)
        except:
            self.logger.error("failed to save file")

    # Split X and Y
    def splitData(self, data, column):
        """
        :param data: dataframe format data need to be splited train values and train target
        :param column: the train target column
        :return: the numpy data foramat train values and targete
        """
        y = data.loc[:, [column]]
        x = data.drop([column], axis=1)
        return x, y

    # Neural Networks Structures
    def buildModel(self, trainData):
        model = models.Sequential()
        model.add(layers.Dense(64, activation='tanh', input_shape=(trainData.shape[1],)))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(64, activation='tanh'))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(16, activation='tanh'))
        model.add(layers.Dense(4, activation='tanh'))
        model.add(layers.Dense(1))
        model.compile(optimizer='Nadam', loss='mse', metrics=['mae'])
        return model

    # Fit Train Data
    def fitData(self, model, trainDataValues, trainDataTarget, epochs=20):
        model.fit(trainDataValues, trainDataTarget, epochs=epochs,
                  batch_size=100, verbose=0)
        return model

    # Save Model
    def saveMoel(self, model, savePath="", name="fitModel.h5"):
        filePath = savePath + name
        return model.save(filePath)

    # Predict Test Data
    def predictData(self, trainedModel, testData):
        return trainedModel.predict(testData)

    def visualizeModel(self, model, savePath="", name="model.png"):
        filePath = savePath + name
        plot_model(model, to_file=filePath, show_shapes='True')

    # K Fold cross Validation
    def validation(self, trainFeaValues, trainFeaTarget, k=10, epochs=100):
        print(trainFeaValues.shape, trainFeaTarget[:5])

        num_val_samples = len(trainFeaValues) // k
        all_val_loss, all_val_mae = [], []
        for i in range(k):
            print('processing fold %d' % i)
            val_data = trainFeaValues[i * num_val_samples:(i + 1) * num_val_samples]
            val_target = trainFeaTarget[i * num_val_samples:(i + 1) * num_val_samples]
            partial_train_data = np.concatenate([trainFeaValues[:i * num_val_samples],
                                                 trainFeaValues[(i + 1) * num_val_samples:]], axis=0)
            partial_train_target = np.concatenate([trainFeaTarget[:i * num_val_samples],
                                                   trainFeaTarget[(i + 1) * num_val_samples:]], axis=0)
            model = self.buildModel(partial_train_data)
            history = model.fit(partial_train_data, partial_train_target,
                                epochs=epochs, batch_size=100,
                                validation_data=(val_data, val_target))
            all_val_loss.append(history.history["val_loss"])
            all_val_mae.append(history.history["val_mean_absolute_error"])
        return all_val_loss, all_val_mae

    # visualize mean validation mae
    def visMeanValMae(self, meanValMae, savePath="", name="Mean_Validation_Mae.jpg"):
        filePath = savePath + name
        plt.figure(figsize=(50, 50))
        plt.plot(meanValMae, label="Mean Validation Mae")
        plt.savefig(filePath)

    # Excute Programs
    def excute(self):

        trainFeaData = self.readFile(self.trainFeaFilePath)
        trainFeaData.drop(["Unnamed: 0"], axis=1, inplace=True)
        testFeaData = self.readFile(self.tesFeatFilePath)
        #         testFeaData.drop(["Unnamed: 0"], axis = 1, inplace = True)
        rawTestData = self.readFile(self.rawTestFilePath)
        trainFeaValues, trainTarget = self.splitData(trainFeaData, "运价（元/吨）")
        # print(trainTarget.head())
        # print(trainFeaData.shape, trainFeaData.head())
        # print(testFeaData.shape, testFeaData.head())
        test = trainFeaData.drop("运价（元/吨）", axis=1)
        # print(test.columns ==testFeaData.columns)
        # print(testFeaData.shape)
        # print(trainFeaValues.columns ==testFeaData.columns)
        # print(trainTarget.head())

        # Confirm Model
        model = self.buildModel(trainFeaValues.values)
        # self.visualizeModel(model)

        """
        # validation

        All_Val_loss, All_Val_Mae = self.validation(trainFeaValues.values, trainTarget.values)
        meanValLoss = np.sum(All_Val_loss, axis=0)/len(All_Val_loss)
        meanValMae = np.sum(All_Val_Mae, axis=0)/len(All_Val_Mae)

        plt.figure(figsize=(100, 50))

        f, ax = plt.subplots(2, 1)

        ax[0].plot(meanValLoss)
        ax[0].set_title("meanValLoss")
        ax[1].plot(meanValMae)
        ax[1].set_title("meanValmae")
		plt.subplots_adjust()
        plt.savefig("meanVal")
        #self.visMeanValMae(meanValLoss)
        #self.visMeanValMae(meanValMae)
        print("---")
        """

        # Fit Train Data
        model.fit(trainFeaValues, trainTarget, epochs=100,
                  batch_size=100, verbose=0)
        model.save("fitedModel_1.h5")

        result = model.predict(testFeaData)
        print(result[:100])
        # Predict Test Data
        result = pow(result, 2) - 0.4176
        print(result[:100])
        result_df = pd.DataFrame(result, columns=["运价（元/吨）"])
        outputData = self.concatRes(rawTestData, result_df)
        self.save2File(outputData)
