"""Proposed Neural nets architectures suited for MNIST"""

import torch
import torch.nn as nn

from typing import List
from ..base_architectures import BaseEncoder, BaseDecoder
from ....models.base.base_utils import ModelOuput
from ....models import BaseAEConfig


class Encoder_AE_CELEBA(BaseEncoder):
    """
    A Convolutional encoder Neural net suited for CELEBA-64 and Autoencoder-based models.

    It can be built as follows:

    .. code-block::

            >>> from pythae.models.nn.benchmarks.celeba import Encoder_AE_CELEBA
            >>> from pythae.models import AEConfig
            >>> model_config = AEConfig(input_dim=(3, 64, 64), latent_dim=64)
            >>> encoder = Encoder_AE_CELEBA(model_config)
            >>> encoder
            ... Encoder_AE_CELEBA(
            ...   (conv_layers): Sequential(
            ...     (0): Conv2d(3, 128, kernel_size=(5, 5), stride=(2, 2), padding=(1, 1))
            ...     (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (2): ReLU()
            ...     (3): Conv2d(128, 256, kernel_size=(5, 5), stride=(2, 2), padding=(1, 1))
            ...     (4): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (5): ReLU()
            ...     (6): Conv2d(256, 512, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))
            ...     (7): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (8): ReLU()
            ...     (9): Conv2d(512, 1024, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))
            ...     (10): BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (11): ReLU()
            ...   )
            ...   (embedding): Linear(in_features=16384, out_features=64, bias=True)
            ... )



    and then passed to a :class:`pythae.models` instance

        >>> from pythae.models import AE
        >>> model = AE(model_config=model_config, encoder=encoder)
        >>> model.encoder
        ... Encoder_AE_CELEBA(
        ...   (conv_layers): Sequential(
        ...     (0): Conv2d(3, 128, kernel_size=(5, 5), stride=(2, 2), padding=(1, 1))
        ...     (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (2): ReLU()
        ...     (3): Conv2d(128, 256, kernel_size=(5, 5), stride=(2, 2), padding=(1, 1))
        ...     (4): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (5): ReLU()
        ...     (6): Conv2d(256, 512, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))
        ...     (7): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (8): ReLU()
        ...     (9): Conv2d(512, 1024, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))
        ...     (10): BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (11): ReLU()
        ...   )
        ...   (embedding): Linear(in_features=16384, out_features=64, bias=True)
        ... )

    .. note::

        Please note that this encoder is only suitable for Autoencoder based models since it only
        outputs the embeddings of the input data under the key `embedding`.

        .. code-block::

            >>> import torch
            >>> input = torch.rand(2, 3, 64, 64)
            >>> out = encoder(input)
            >>> out.embedding.shape
            ... torch.Size([2, 64])

    """
    def __init__(self, args: BaseAEConfig):
        BaseEncoder.__init__(self)

        self.input_dim = (3, 64, 64)
        self.latent_dim = args.latent_dim
        self.n_channels = 3

        layers = nn.ModuleList()

        layers.append(
            nn.Sequential(
                nn.Conv2d(self.n_channels, 128, 5, 2, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.Conv2d(128, 256, 5, 2, padding=1),
                nn.BatchNorm2d(256),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.Conv2d(256, 512, 5, 2, padding=2),
                nn.BatchNorm2d(512),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.Conv2d(512, 1024, 5, 2, padding=2),
                nn.BatchNorm2d(1024),
                nn.ReLU(),
            )
        )

        self.layers = layers
        self.depth = len(layers)

        self.embedding = nn.Linear(1024 * 4 * 4, args.latent_dim)

    def forward(self, x: torch.Tensor, output_layer_levels:List[int]=None):
        """Forward method
        
        Returns:
            ModelOuput: An instance of ModelOutput containing the embeddings of the input data under
            the key `embedding`"""
        output = ModelOuput()

        if output_layer_levels is not None:

            assert all(self.depth >= levels > 0), (
                f'Cannot output layer deeper than depth ({self.depth}) or with non-positive indice. '\
                f'Got ({output_layer_levels})'
                )

        out = x

        for i in range(self.depth):
            out = self.layers[i](out)

            if output_layer_levels is not None:
                if i+1 in output_layer_levels:
                    output[f'embedding_layer_{i+1}'] = out
        
        output['embedding'] = self.embedding(out.reshape(x.shape[0], -1))

        return output


class Encoder_VAE_CELEBA(BaseEncoder):
    """
    A Convolutional encoder Neural net suited for CELEBA-64 and 
    Variational Autoencoder-based models.

    It can be built as follows:

    .. code-block::

            >>> from pythae.models.nn.benchmarks.celeba import Encoder_VAE_CELEBA
            >>> from pythae.models import VAEConfig
            >>> model_config = VAEConfig(input_dim=(3, 64, 64), latent_dim=64)
            >>> encoder = Encoder_VAE_CELEBA(model_config)
            >>> encoder
            ... Encoder_VAE_CELEBA(
            ...   (conv_layers): Sequential(
            ...     (0): Conv2d(3, 128, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
            ...     (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (2): ReLU()
            ...     (3): Conv2d(128, 256, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
            ...     (4): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (5): ReLU()
            ...     (6): Conv2d(256, 512, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
            ...     (7): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (8): ReLU()
            ...     (9): Conv2d(512, 1024, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
            ...     (10): BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (11): ReLU()
            ...   )
            ...   (embedding): Linear(in_features=16384, out_features=64, bias=True)
            ...   (log_var): Linear(in_features=16384, out_features=64, bias=True)
            ... )



    and then passed to a :class:`pythae.models` instance

        >>> from pythae.models import VAE
        >>> model = VAE(model_config=model_config, encoder=encoder)
        >>> model.encoder
        ... Encoder_VAE_CELEBA(
        ...   (conv_layers): Sequential(
        ...     (0): Conv2d(3, 128, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
        ...     (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (2): ReLU()
        ...     (3): Conv2d(128, 256, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
        ...     (4): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (5): ReLU()
        ...     (6): Conv2d(256, 512, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
        ...     (7): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (8): ReLU()
        ...     (9): Conv2d(512, 1024, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1))
        ...     (10): BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (11): ReLU()
        ...   )
        ...   (embedding): Linear(in_features=16384, out_features=64, bias=True)
        ...   (log_var): Linear(in_features=16384, out_features=64, bias=True)
        ... )


    .. note::

        Please note that this encoder is only suitable for Autoencoder based models since it only
        outputs the embeddings of the input data under the key `embedding`.

        .. code-block::

            >>> import torch
            >>> input = torch.rand(2, 3, 64, 64)
            >>> out = encoder(input)
            >>> out.embedding.shape
            ... torch.Size([2, 64])
            >>> out.log_covariance.shape
            ... torch.Size([2, 64])

    """
    def __init__(self, args: BaseAEConfig):
        BaseEncoder.__init__(self)

        self.input_dim = (3, 64, 64)
        self.latent_dim = args.latent_dim
        self.n_channels = 3

        layers = nn.ModuleList()

        layers.append(
            nn.Sequential(
                nn.Conv2d(self.n_channels, 128, 5, 2, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.Conv2d(128, 256, 5, 2, padding=1),
                nn.BatchNorm2d(256),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.Conv2d(256, 512, 5, 2, padding=2),
                nn.BatchNorm2d(512),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.Conv2d(512, 1024, 5, 2, padding=2),
                nn.BatchNorm2d(1024),
                nn.ReLU(),
            )
        )

        self.layers = layers
        self.depth = len(layers)

        self.embedding = nn.Linear(1024 * 4 * 4, args.latent_dim)
        self.log_var = nn.Linear(1024 * 4 * 4, args.latent_dim)

    def forward(self, x: torch.Tensor, output_layer_levels:List[int]=None):
        """Forward method
        
        Returns:
            ModelOuput: An instance of ModelOutput containing the embeddings of the input data under
            the key `embedding` and the **log** of the diagonal coefficient of the covariance 
            matrices under the key `log_covariance`"""
        output = ModelOuput()

        if output_layer_levels is not None:

            assert all(self.depth >= levels > 0), (
                f'Cannot output layer deeper than depth ({self.depth}) or with non-positive indice. '\
                f'Got ({output_layer_levels})'
                )

        out = x

        for i in range(self.depth):
            out = self.layers[i](out)

            if output_layer_levels is not None:
                if i+1 in output_layer_levels:
                    output[f'embedding_layer_{i+1}'] = out
        
        output['embedding'] = self.embedding(out.reshape(x.shape[0], -1))
        output['log_covariance'] = self.log_var(out.reshape(x.shape[0], -1))

        return output


class Decoder_AE_CELEBA(BaseDecoder):
    """
    A Convolutional decoder Neural net suited for CELEBA-64 and Autoencoder-based 
    models.

    It can be built as follows:

    .. code-block::

            >>> from pythae.models.nn.benchmarks.celeba import Decoder_AE_CELEBA
            >>> from pythae.models import VAEConfig
            >>> model_config = VAEConfig(input_dim=(3, 64, 64), latent_dim=64)
            >>> decoder = Decoder_AE_CELEBA(model_config)
            >>> decoder
            ... Decoder_AE_CELEBA(
            ...   (fc): Linear(in_features=64, out_features=65536, bias=True)
            ...   (deconv_layers): Sequential(
            ...     (0): ConvTranspose2d(1024, 512, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))
            ...     (1): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (2): ReLU()
            ...     (3): ConvTranspose2d(512, 256, kernel_size=(5, 5), stride=(2, 2), padding=(1, 1))
            ...     (4): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (5): ReLU()
            ...     (6): ConvTranspose2d(256, 128, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2), output_padding=(1, 1))
            ...     (7): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            ...     (8): ReLU()
            ...     (9): ConvTranspose2d(128, 3, kernel_size=(5, 5), stride=(1, 1), padding=(1, 1))
            ...     (10): Sigmoid()
            ...   )
            ... )


    and then passed to a :class:`pythae.models` instance

        >>> from pythae.models import VAE
        >>> model = VAE(model_config=model_config, decoder=decoder)
        >>> model.decoder
        ... Decoder_AE_CELEBA(
        ...   (fc): Linear(in_features=64, out_features=65536, bias=True)
        ...   (deconv_layers): Sequential(
        ...     (0): ConvTranspose2d(1024, 512, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))
        ...     (1): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (2): ReLU()
        ...     (3): ConvTranspose2d(512, 256, kernel_size=(5, 5), stride=(2, 2), padding=(1, 1))
        ...     (4): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (5): ReLU()
        ...     (6): ConvTranspose2d(256, 128, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2), output_padding=(1, 1))
        ...     (7): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        ...     (8): ReLU()
        ...     (9): ConvTranspose2d(128, 3, kernel_size=(5, 5), stride=(1, 1), padding=(1, 1))
        ...     (10): Sigmoid()
        ...   )
        ... )


    .. note::

        Please note that this encoder is only suitable for Autoencoder based models since it only
        outputs the embeddings of the input data under the key `embedding`.

        .. code-block::

            >>> import torch
            >>> input = torch.randn(2, 64)
            >>> out = decoder(input)
            >>> out.reconstruction.shape
            ... torch.Size([2, 3, 64, 64])
    """
    def __init__(self, args: dict):
        BaseDecoder.__init__(self)
        self.input_dim = (3, 64, 64)
        self.latent_dim = args.latent_dim
        self.n_channels = 3

        layers = nn.ModuleList()

        layers.append(
            nn.Sequential(
                nn.Linear(args.latent_dim, 1024 * 8 * 8)
            )
        )

        layers.append(
            nn.Sequential(
                nn.ConvTranspose2d(1024, 512, 5, 2, padding=2),
                nn.BatchNorm2d(512),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.ConvTranspose2d(512, 256, 5, 2, padding=1, output_padding=0),
                nn.BatchNorm2d(256),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.ConvTranspose2d(256, 128, 5, 2, padding=2, output_padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
            )
        )

        layers.append(
            nn.Sequential(
                nn.ConvTranspose2d(128, self.n_channels, 5, 1, padding=1),
                nn.Sigmoid(),
            )
        )

        self.layers = layers
        self.depth = len(layers)

    def forward(self, z: torch.Tensor, output_layer_levels:List[int]=None):
        """Forward method
        
        Returns:
            ModelOuput: An instance of ModelOutput containing the reconstruction of the latent code 
            under the key `reconstruction`"""
        output = ModelOuput()

        if output_layer_levels is not None:

            assert all(self.depth >= levels > 0), (
                f'Cannot output layer deeper than depth ({self.depth}) or with non-positive indice. '\
                f'Got ({output_layer_levels})'
                )

        out = z

        for i in range(self.depth):
            out = self.layers[i](out)

            if output_layer_levels is not None:
                if i+1 in output_layer_levels:
                    output[f'reconstruction_layer_{i+1}'] = out

            if i == 0:
                out = out.reshape(z.shape[0], 1024, 8, 8)

        output['reconstruction'] = out

        return output
