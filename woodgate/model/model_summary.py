"""
model_summary.py - The model_summary.py module contains the
ModelSummary class definition.
"""
from tensorflow import keras


class ModelSummary:
    """
    ModelSummary - The ModelSummary class encapsulates logic
    related to summarizing the model.
    """

    @staticmethod
    def print(bert_model: keras.Model):
        """This method wraps the summary method of a keras.Model
        object which will print a summary of the model object in
        formatted text.

        :param bert_model:
        :type bert_model:
        :return:
        :rtype:
        """
        return bert_model.summary()
