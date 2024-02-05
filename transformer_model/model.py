'''
# class MultiSelfAttention(nn.Module)
    Multi-Head Self Attention module for transformer models.
    Args:
    - embeddings (int): Dimensionality of the token embeddings.
    - heads (int): Number of attention heads.
    - mask (bool): Whether to apply masking in self-attention.

# class TransformerBlock(nn.Module)
    Transformer Block module for building transformer models.
    Args:
    - embeddings (int): Dimensionality of the token embeddings.
    - heads (int): Number of attention heads in the multi-head self-attention layer.
    - ff_dimension (int): Dimensionality of the feed-forward layer.
    - mask (bool): Whether to apply masking in the multi-head self-attention layer.

# class Transformer(nn.Module)
    Transformer model for sequence-to-sequence tasks.
    Args:
    - embeddings (int): Dimensionality of the token embeddings.
    - heads (int): Number of attention heads in the multi-head attention layers.
    - depth (int): Number of transformer layers.
    - seq_length (int): Length of the input sequence. If None, it will be determined automatically.
    - num_tokens (int): Number of distinct tokens in the input sequence.
    - output_size (tuple): Output size of the transformer, represented as (channels, height, width).


Source:
https://peterbloem.nl/blog/transformers
https://pypi.org/project/positional-encodings/
'''

import torch, yaml
import torch.nn as nn

from positional_encodings.torch_encodings import PositionalEncoding2D
from .encoders import transformer_encoder_model, TransformerBlock

with open("config.yaml", 'r') as file:
    data = yaml.safe_load(file)
DEVICE = data['DEVICE']


class Transformer(nn.Module):
    """
    Args:
    - embeddings (int): Dimensionality of the token embeddings.
    - heads (int): Number of attention heads in the multi-head attention layers.
    - depth (int): Number of transformer layers.
    - seq_length (int): Length of the input sequence. If None, it will be determined automatically.
    - num_tokens (int): Number of distinct tokens in the input sequence.
    - output_size (tuple): Output size of the transformer, represented as (channels, height, width).
    """
    def __init__(self, 
                encoder="custom",
                embeddings=256, 
                heads=8, 
                depth=6, 
                seq_length=6*6*6, 
                num_tokens=10, 
                output_size=(3, 11, 11)
            ):

        super().__init__()

        assert encoder in ["builtin", "custom"]

        self.num_tokens = num_tokens
        self.embeddings = embeddings
        self.output_size = output_size
        self.token_emb = nn.Embedding(num_tokens, embeddings)
        self.pos_emb = PositionalEncoding2D(embeddings)

        if encoder == "custom":
            tblocks = []
            for _ in range(depth):
                tblocks.append(TransformerBlock(embeddings=embeddings, heads=heads))
            self.tblocks = nn.Sequential(*tblocks)
            
        elif encoder == "builtin":
            tblocks = transformer_encoder_model(
                            embeddings=embeddings, 
                            heads=heads,
                            depth=depth,
                            batch_first=True
                )
            self.tblocks = tblocks

        middle_layer = (seq_length*embeddings + embeddings) // 2
        self.to_probs = nn.Sequential(
                nn.Linear(seq_length*embeddings, middle_layer),
                nn.Linear(middle_layer, embeddings),
                nn.Linear(embeddings, torch.prod(torch.tensor(output_size)).item())
        )


    def forward(self, x):
        """
        x (input tensor): (batch, xy_coord, round_coord)
        output (output_tensor): (batch, flattened_output_size)
        """

        # embeddings
        position_shape = *(x.shape), self.embeddings
        for_tokens = x.reshape(x.shape[0], -1)
        tokens = self.token_emb(for_tokens)
        # b, seq, k = tokens.shape
        temp_pos = torch.zeros(position_shape)
        positions = self.pos_emb(temp_pos.to(DEVICE)).reshape(x.shape[0], -1, self.embeddings).to(DEVICE)
        x = tokens + positions

        # transformer blocks
        x = self.tblocks(x)

        # final output layer
        # x = x.mean(dim=1) # avg pool
        x = torch.flatten(x, start_dim=1)
        output = self.to_probs(x)
        # output = F.log_softmax(x, dim=1)
        # output = output.reshape((x.shape[0], *self.output_size))

        return output

if __name__ == '__main__':
    # testing
    input_seq_length = (8, 24, 5)
    x = torch.randint(low=0, high=9, size=(input_seq_length))

    model = Transformer(encoder="builtin", seq_length=24*5)
    print(model(x))