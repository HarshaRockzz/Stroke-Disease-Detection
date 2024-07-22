
# **1. Library Import**
"""

!pip install -q condacolab
import condacolab
condacolab.install()
!conda --version

!conda create --name stroke-detection python==3.9.1

!conda activate stroke-detection

!pip install jupyter scikit-learn tensorflow tfx==1.11.0 flask joblib

!unzip Stroke-Disease-Detection.zip

import os
import pandas as pd
from typing import Text

from absl import logging
from tfx.orchestration import metadata, pipeline
from tfx.orchestration.beam.beam_dag_runner import BeamDagRunner
from modules import components

"""# **2. Data Loading**

## 2.1 Environment and Kaggle Credential

Set up the [Colab](https://colab.research.google.com) `operating system` environment with the `KAGGLE_USERNAME` variable and the `KAGGLE_KEY` variable to connect to the [Kaggle](https://kaggle.com) platform using [Kaggle's Beta API](https://www.kaggle.com/docs/api) Token.
"""

os.environ['KAGGLE_USERNAME'] = 'harsharockerzzzz'
os.environ['KAGGLE_KEY']      = 'b75c236a492526b84d0dc7517c37d48b'

"""## 2.2 Dataset Download

Download the dataset form Kaggle with the dataset file name, `healthcare-dataset-stroke-data.csv`. The dataset used in this project is the [Stroke Prediction Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset) dataset in the form of a `.csv` ([Comma-separated Values](https://en.wikipedia.org/wiki/Comma-separated_values)) file.
"""

!kaggle datasets download -d fedesoriano/stroke-prediction-dataset -f healthcare-dataset-stroke-data.csv

"""## 2.3 Dataset Preparation"""

df = pd.read_csv('healthcare-dataset-stroke-data.csv')
df = df.drop('id', axis=1)

df.isnull().sum()

df = df.dropna()
df.isnull().sum()

df.info()

df['age'] = df['age'].astype(int)

DATA_PATH = 'data'

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

df.to_csv(os.path.join(DATA_PATH, 'healthcare-dataset-stroke-data.csv'), index=False)
df

"""# **3. Set Pipeline Variable**"""

PIPELINE_NAME = 'stroke-disease-pipeline'

# Pipeline inputs
DATA_ROOT = 'data'
TRANSFORM_MODULE_FILE = 'modules/transform.py'
TUNER_MODULE_FILE = 'modules/tuner.py'
TRAINER_MODULE_FILE = 'modules/trainer.py'

# Pipeline outputs
OUTPUT_BASE = 'outputs'

serving_model_dir = os.path.join(OUTPUT_BASE, 'serving_model')
pipeline_root = os.path.join(OUTPUT_BASE, PIPELINE_NAME)
metadata_path = os.path.join(pipeline_root, 'metadata.sqlite')

"""# **4. Pipeline Initialization**"""

def init_local_pipeline(
    components, pipeline_root: Text
) -> pipeline.Pipeline:
    """Init local pipeline

    Args:
        components (dict): tfx components
        pipeline_root (Text): path to pipeline directory

    Returns:
        pipeline.Pipeline: apache beam pipeline orchestration
    """
    logging.info(f"Pipeline root set to: {pipeline_root}")
    beam_args = [
        '--direct_running_mode=multi_processing'
        # 0 auto-detect based on on the number of CPUs available
        # during execution time.
        '----direct_num_workers=0'
    ]

    return pipeline.Pipeline(
        pipeline_name=PIPELINE_NAME,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=True,
        metadata_connection_config=metadata.sqlite_metadata_connection_config(
            metadata_path
        ),
        eam_pipeline_args=beam_args
    )

logging.set_verbosity(logging.INFO)

components = components.init_components({
    'data_dir': DATA_ROOT,
    'transform_module': TRANSFORM_MODULE_FILE,
    'tuner_module': TUNER_MODULE_FILE,
    'training_module': TRAINER_MODULE_FILE,
    'training_steps': 5000,
    'eval_steps': 1000,
    'serving_model_dir': serving_model_dir
})

pipeline = init_local_pipeline(components, pipeline_root)
BeamDagRunner().run(pipeline=pipeline)

!zip -r data.zip data/
!zip -r images.zip images/
!zip -r outputs.zip outputs/
!pip freeze > requirements.txt

