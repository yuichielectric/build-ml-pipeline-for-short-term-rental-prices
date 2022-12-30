#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import tempfile
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info("Download artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Read artifact")
    df = pd.read_csv(artifact_local_path)

    logger.info("Drop outliers")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Convert last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_path = os.path.join(tmp_dir, args.output_artifact)

        logger.info("Save artifact")
        df.to_csv(temp_path, index=False)

        logger.info("Upload artifact")
        artifact = wandb.Artifact(
            name=args.output_artifact,
            type=args.output_type,
            description=args.output_description
        )
        artifact.add_file(temp_path)
        run.log_artifact(artifact)

        artifact.wait()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact",
        type=str,
        help="The name of the artifact to use as input",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="The name of the artifact to use as output",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="The type of the artifact to use as output",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="The description of the artifact to use as output",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=int,
        help="The minimum price to keep in the dataset",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=int,
        help="The maximum price to keep in the dataset",
        required=True
    )


    args = parser.parse_args()

    go(args)
