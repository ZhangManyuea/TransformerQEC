# TransformerQEC

## Requirements

```bash
pip install numpy polars tqdm pyyaml ray torch positional-encodings[pytorch]
```

## Quantum Data Generation

The Python script (`data_gen.py`) generates synthetic data for quantum error correction experiments. It leverages the stim_experiments module for quantum circuit simulation and various utility functions for encoding, decoding, and data processing.

## Configuration

`config.yaml`: to specify parameters such as the distance, number of shots, dataset-directory and number-of-encoding-channels. Here's an example of a configuration file:

```yaml
# data
DISTANCE: 5
SHOTS: 2000
DATASET_DIR: "datasets"
ENCODING_CHANNEL: 6
```

## Usage

After setting the configuration file, execute the following command for data generation:

```python
python data_gen.py
```
This will generate synthetic data for quantum error correction experiments, including syndromes and errors. The data will be stored in CSV files in the specified dataset directory.

## Additional Notes

- The number of parallel executions is set to half of the available CPU cores for efficiency.
- The `get_n_shots` function generates and stores data for multiple shots of a quantum error correction circuit in parallel, leveraging Ray for parallelism.