__version__ = "0.3.4"

import kagglehub.logger  # configures the library logger.
from kagglehub import colab_cache_resolver, http_resolver, kaggle_cache_resolver, registry
from kagglehub.auth import login, whoami
from kagglehub.competition import competition_download
from kagglehub.datasets import dataset_download, dataset_upload
from kagglehub.models import model_download, model_upload

from kagglehub.cache import added_resources, write_added_resources
from kagglehub.dj import pipeline_scoped, get_asset_path, download_notebook_output_files, import_pipeline_module

registry.model_resolver.add_implementation(http_resolver.ModelHttpResolver())
registry.model_resolver.add_implementation(kaggle_cache_resolver.ModelKaggleCacheResolver())
registry.model_resolver.add_implementation(colab_cache_resolver.ModelColabCacheResolver())

registry.dataset_resolver.add_implementation(http_resolver.DatasetHttpResolver())
registry.dataset_resolver.add_implementation(kaggle_cache_resolver.DatasetKaggleCacheResolver())
registry.dataset_resolver.add_implementation(colab_cache_resolver.DatasetColabCacheResolver())

registry.competition_resolver.add_implementation(http_resolver.CompetitionHttpResolver())
registry.competition_resolver.add_implementation(kaggle_cache_resolver.CompetitionKaggleCacheResolver())
