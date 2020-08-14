"""
definition.py - This file contains the Definition class which
encapsulates logic related to defining the model layers.
"""
import os
from bert.loader import (
    StockBertConfig,
    map_stock_config_to_params,
    load_stock_weights
)
import tensorflow as tf
from tensorflow import keras
from bert import BertModelLayer
from bert.tokenization.bert_tokenization import FullTokenizer
from ..build.file_system_configuration import \
    FileSystemConfiguration


class Definition:
    """
    Definition - Class - The Definition class encapsulates logic
    related to defining the model architecture.
    """

    #: The `bert_dir` attribute represents the path to a
    #: directory on the host file system containing the BERT
    #: model. This attribute is set via the `BERT_DIR`
    #: environment variable. If the `BERT_DIR` environment
    #: variable is not set, then the `bert_dir` attribute
    #: defaults to `$WOODGATE_BASE_DIR/bert`. The program will
    #: attempt to create `BERT_DIR` if it does not already
    #: exist.
    bert_dir: str = os.getenv(
        "BERT_DIR",
        os.path.join(
            FileSystemConfiguration.woodgate_base_dir,
            "bert"
        )
    )
    os.makedirs(bert_dir, exist_ok=True)

    bert_config: str = os.getenv(
        "BERT_CONFIG",
        os.path.join(
            bert_dir,
            "bert_config.json"
        )
    )

    bert_model: str = os.getenv(
        "BERT_MODEL",
        os.path.join(
            bert_dir,
            "bert_model.ckpt"
        )
    )

    @classmethod
    def get_tokenizer(cls):
        """

        :return:
        :rtype:
        """
        tokenizer: FullTokenizer = FullTokenizer(
            vocab_file=os.path.join(cls.bert_dir, "vocab.txt")
        )
        return tokenizer

    @classmethod
    def create_model(
            cls,
            max_sequence_length: int,
            number_of_intents: int
    ):
        """
        The create_model method is a helper which accepts
        max input sequence length and the number of intents
        (classification bins/buckets). The logic returns a
        BERT model that matches the specified architecture.

        :param max_sequence_length: max length of input sequence
        :type max_sequence_length: int
        :param number_of_intents: number of bins/buckets
        :type number_of_intents: int
        :return: model definition
        :rtype: keras.Model
        """

        with tf.io.gfile.GFile(cls.bert_config) as reader:
            bc = StockBertConfig.from_json_string(reader.read())
            bert_params = map_stock_config_to_params(bc)
            bert_params.adapter_size = None
            bert = BertModelLayer.from_params(
                bert_params,
                name="bert"
            )

        input_ids = keras.layers.Input(
            shape=(max_sequence_length,),
            dtype='int32',
            name="input_ids"
        )
        bert_output = bert(input_ids)

        cls_out = keras.layers.Lambda(
            lambda seq: seq[:, 0, :])(bert_output)
        cls_out = keras.layers.Dropout(0.5)(cls_out)
        logits = keras.layers.Dense(
            units=768, activation="tanh")(cls_out)
        logits = keras.layers.Dropout(0.5)(logits)
        logits = keras.layers.Dense(
            units=number_of_intents, activation="softmax")(logits)

        model: keras.Model = keras.Model(
            inputs=input_ids, outputs=logits)
        model.build(input_shape=(None, max_sequence_length))

        load_stock_weights(bert, cls.bert_model)

        return model