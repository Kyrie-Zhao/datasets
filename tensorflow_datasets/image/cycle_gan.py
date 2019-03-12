# coding=utf-8
# Copyright 2019 The TensorFlow Datasets Authors.
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

"""CycleGAN dataset."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import numpy as np
import tensorflow as tf

from tensorflow_datasets.core import api_utils
import tensorflow_datasets.public_api as tfds


# From https://arxiv.org/abs/1703.10593
_CITATION = """\
@article{DBLP:journals/corr/ZhuPIE17,
  author    = {Jun{-}Yan Zhu and
               Taesung Park and
               Phillip Isola and
               Alexei A. Efros},
  title     = {Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial
               Networks},
  journal   = {CoRR},
  volume    = {abs/1703.10593},
  year      = {2017},
  url       = {http://arxiv.org/abs/1703.10593},
  archivePrefix = {arXiv},
  eprint    = {1703.10593},
  timestamp = {Mon, 13 Aug 2018 16:48:06 +0200},
  biburl    = {https://dblp.org/rec/bib/journals/corr/ZhuPIE17},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
"""


_DL_URL = "https://people.eecs.berkeley.edu/~taesung_park/CycleGAN/datasets/"

_DATA_OPTIONS = ["ae_photos", "apple2orange", "summer2winter_yosemite", "horse2zebra", "monet2photo", "cezanne2photo", "ukiyoe2photo", "vangogh2photo", "maps", "cityscapes", "facades", "iphone2dslr_flower"]

_DL_URLS = {name: _DL_URL + name + ".zip" for name in _DATA_OPTIONS}


class CycleGANConfig(tfds.core.BuilderConfig):
  """BuilderConfig for CycleGAN.""" 
  
  @api_utils.disallow_positional_args
  def __init__(self, data=None, **kwargs):
    """Constructs a CycleGANConfig. 
    Args:
      data: `str`, one of `_DATA_OPTIONS`.
      **kwargs: keyword arguments forwarded to super.
    """
    if data not in _DATA_OPTIONS:
      raise ValueError("data must be one of %s" % _DATA_OPTIONS)
  
    super(CycleGANConfig, self).__init__(**kwargs)
    self.data = data

    
class CycleGAN(tfds.core.GeneratorBasedBuilder):
  """CycleGAN dataset."""
  
  BUILDER_CONFIGS = [
      CycleGANConfig(
          name=config_name,
          description="A dataset consisting of (trainA and testA) images of typeA and (trainB and testB) images of typeB", 
          version="0.1.0",
          data=config_name,
      ) for config_name in _DATA_OPTIONS
  ]

  def _info(self):
    return tfds.core.DatasetInfo(
        builder=self,
        description="A dataset consisting of (trainA and testA) images of typeA and (trainB and testB) images of typeB",
        features=tfds.features.FeaturesDict({
            "image": tfds.features.Image(),
            "label": tfds.features.ClassLabel(names=["A", "B"]), 
        }),
        supervised_keys=("image", "label"),
        urls=["https://people.eecs.berkeley.edu/~taesung_park/CycleGAN/datasets/"],
    )

  def _split_generators(self, dl_manager):
    url = _DL_URLS[self.builder_config.name]
    data_dirs = dl_manager.download_and_extract(url) 
    
    path_to_dataset = os.path.join(data_dirs, tf.io.gfile.listdir(data_dirs)[0])
     
    trainA_files = tf.io.gfile.glob(os.path.join(path_to_dataset, 'trainA'))
    trainB_files = tf.io.gfile.glob(os.path.join(path_to_dataset, 'trainB'))
    testA_files = tf.io.gfile.glob(os.path.join(path_to_dataset, 'testA'))
    testB_files = tf.io.gfile.glob(os.path.join(path_to_dataset, 'testB'))
    
    return [
        tfds.core.SplitGenerator(
            name="trainA",
            num_shards=10,
            gen_kwargs={"files": trainA_files,
                        "label": "A",
            }
        ),
        tfds.core.SplitGenerator(
            name="trainB",
            num_shards=10,
            gen_kwargs={"files": trainB_files,
                        "label": "B",
            }
        ),
        tfds.core.SplitGenerator(
            name="testA",
            num_shards=1,
            gen_kwargs={"files": testA_files,
                        "label": "A",
            }
        ),
        tfds.core.SplitGenerator(
            name="testB",
            num_shards=1,
            gen_kwargs={"files": testB_files,
                        "label": "B",
            }
        ),
    ]

  def _generate_examples(self, files, label): 
    path=files[0]
    images=tf.io.gfile.listdir(path)  

    for image in images:
      yield{
          "image": os.path.join(path, image),
          "label": label,
      }
