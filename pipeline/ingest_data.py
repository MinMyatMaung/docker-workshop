import argparse
import time

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    chunksize = params.chunksize

    dtype = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64",
    }

    parse_dates = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
    ]

    engine = create_engine(
        f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
    )

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    first = True
    total_rows = 0

    for df_chunk in tqdm(df_iter):
        start_time = time.time()

        if first:
            df_chunk.head(0).to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False,
            )
            first = False
            print(f"Table '{table_name}' created")

        df_chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
            index=False,
        )

        total_rows += len(df_chunk)
        end_time = time.time()

        print(
            f"Inserted {len(df_chunk)} rows "
            f"in {end_time - start_time:.2f} seconds. "
            f"Total inserted: {total_rows}"
        )

    print("Finished ingestion.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest NYC yellow taxi CSV data into Postgres"
    )

    parser.add_argument("--user", default="root", help="Postgres username")
    parser.add_argument("--password", default="root", help="Postgres password")
    parser.add_argument("--host", default="localhost", help="Postgres host")
    parser.add_argument("--port", default="5432", help="Postgres port")
    parser.add_argument("--db", default="ny_taxi", help="Postgres database name")
    parser.add_argument(
        "--table-name",
        default="yellow_taxi_data",
        help="Name of the table to create/insert into",
    )
    parser.add_argument(
        "--url",
        default="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz",
        help="URL of the CSV or CSV.GZ file",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=100000,
        help="Number of rows per chunk",
    )

    args = parser.parse_args()
    main(args)
