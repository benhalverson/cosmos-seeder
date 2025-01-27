import os
import json
import click
from azure.identity import ManagedIdentityCredential
from azure.cosmos import CosmosClient

# Function to seed Cosmos DB
def seed_cosmos_db(cosmos_url, db_name, container_name, data_file):
    # Obtain Managed Identity credentials
    credential = ManagedIdentityCredential()
    client = CosmosClient(cosmos_url, credential=credential)

    # Access database and container
    database = client.get_database_client(db_name)
    container = database.get_container_client(container_name)

    # Load data from JSON file
    with open(data_file, 'r') as file:
        data = json.load(file)
    
    # Seed data
    for item in data:
        container.upsert_item(item)

    click.echo(f"Successfully seeded {len(data)} items to container '{container_name}'.")

# Function to trigger Azure Function
def trigger_azure_function(function_url):
    # Obtain Managed Identity credentials
    credential = ManagedIdentityCredential()
    token = credential.get_token("https://management.azure.com/.default")

    # Send request to the Azure Function
    headers = {
        'Authorization': f'Bearer {token.token}'
    }
    response = requests.post(function_url, headers=headers)

    if response.status_code == 200:
        click.echo("Successfully triggered the Azure Function.")
    else:
        click.echo(f"Failed to trigger the Azure Function. Status code: {response.status_code}. Response: {response.text}")

# CLI setup
@click.group()
def cli():
    """CLI tool to seed Cosmos DB and trigger Azure Function."""
    pass

@cli.command()
@click.option('--cosmos-url', required=True, help='The URL of the Cosmos DB account.')
@click.option('--db-name', required=True, help='The name of the database.')
@click.option('--container-name', required=True, help='The name of the container.')
@click.option('--data-file', required=True, type=click.Path(exists=True), help='Path to the JSON file containing data.')
def seed(cosmos_url, db_name, container_name, data_file):
    """Seed data into Cosmos DB."""
    seed_cosmos_db(cosmos_url, db_name, container_name, data_file)

@cli.command()
@click.option('--function-url', required=True, help='The URL of the Azure serverless function.')
def trigger(function_url):
    """Trigger the Azure serverless function."""
    trigger_azure_function(function_url)

if __name__ == "__main__":
    cli()
