# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from overrides import overrides
from typing import List, Generator, Union
from pathlib import Path

import numpy as np
from deeppavlov.core.common.registry import register
from deeppavlov.core.models.component import Component
from deeppavlov.core.common.log import get_logger
from deeppavlov.core.models.serializable import Serializable
from deeppavlov.core.data.utils import zero_pad

log = get_logger(__name__)


@register('random')
class RandomEmbedder(Component, Serializable):
    """
    Class implements fastText embedding model
    Attributes:
        model: fastText model instance
        tok2emb: dictionary with already embedded tokens
        dim: dimension of embeddings
        pad_zero: whether to pad sequence of tokens with zeros or not
        load_path: path with pre-trained fastText binary model

    """
    def __init__(self, load_path: [str, Path] = None, save_path: [str, Path] = None, dim: int = 100, pad_zero: bool = False,
                 **kwargs) -> None:
        """
        Initialize embedder with given parameters
        Args:
            load_path: path where to load pre-trained embedding model from
            save_path: is not used because model is not trainable; therefore, it is unchangable
            dim: dimensionality of fastText model
            pad_zero: whether to pad samples or not
            **kwargs: additional arguments
        """
        super().__init__(save_path=save_path, load_path=load_path)
        self.tok2emb = {}
        self.dim = dim
        self.pad_zero = pad_zero

    def save(self, *args, **kwargs) -> None:
        """
        Class do not save loaded model again as it is not trained during usage
        Args:
            *args: arguments
            **kwargs: arguments

        Returns:
            None
        """
        raise NotImplementedError

    def load(self, *args, **kwargs):
        """
        Load fastText binary model from self.load_path
        Args:
            *args: arguments
            **kwargs: arguments

        Returns:
            fastText pre-trained model
        """

        raise NotImplementedError

    @overrides
    def __call__(self, batch: List[List[str]], mean: bool = False, *args, **kwargs):
        """
        Embed sentences from batch
        Args:
            batch: list of tokenized text samples
            mean: whether to return mean embedding of tokens per sample
            *args: arguments
            **kwargs: arguments

        Returns:
            embedded batch
        """
        batch = [self._encode(sample, mean) for sample in batch]
        if self.pad_zero:
            batch = zero_pad(batch)
        # batch = [np.expand_dims(el, axis=0) for el in batch]
        # batch = np.vstack(batch)
        return batch

    def __iter__(self) -> Generator:
        """
        Iterate over all words from fastText model vocabulary
        Returns:
            iterator
        """
        raise NotImplementedError

    def _encode(self, tokens: List[str], mean: bool) -> Union[List[np.ndarray], np.ndarray]:
        """
        Embed one text sample
        Args:
            tokens: tokenized text sample
            mean: whether to return mean embedding of tokens per sample

        Returns:
            list of embedded tokens or array of mean values
        """
        embedded_tokens = []
        for t in tokens:
            try:
                emb = self.tok2emb[t]
            except KeyError:
                emb = np.random.uniform(-0.6, 0.6, self.dim)
                self.tok2emb[t] = emb
            embedded_tokens.append(emb)

        if mean:
            filtered = [et for et in embedded_tokens if np.any(et)]
            if filtered:
                return np.mean(filtered, axis=0)
            return np.zeros(self.dim, dtype=np.float32)

        embedded_tokens = np.vstack(embedded_tokens)
        return embedded_tokens