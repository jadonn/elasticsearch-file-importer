import argparse

import utilities

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description='Read a data from a variety of file formats and post the data to Elasticsearch'
        )
    
    SUBPARSERS = PARSER.add_subparsers(title="data_type", description="Supported data format", help="Choose one of the supported data formats.")
    CSV_PARSER = SUBPARSERS.add_parser("CSV", help="Import a CSV file into Elasticsearch")
    CSV_PARSER.add_argument('csvFile', help='Path to the CSV file to read')
    CSV_PARSER.add_argument('esIndex', help='Name of the Elasticsearch index mapping')
    CSV_PARSER.add_argument('--stopWordsFile', help='Path to a file of stopwords')
    CSV_PARSER.add_argument('--force', help='Index regardless of the index mapping', action='store_true')
    CSV_PARSER.set_defaults(func=utilities.process_report)

    LOG_PARSER = SUBPARSERS.add_parser("Logs", help="Import a log into ElasticSearch")
    LOG_PARSER.add_argument("logFile", help="Path to the log file to read")
    LOG_PARSER.add_argument("formatFile", help="Path to file containing log format regex string.")
    LOG_PARSER.add_argument("esIndex", help="Name of the Elasticsearch index mapping")
    LOG_PARSER.set_defaults(func=utilities.process_log)

    JSON_PARSER = SUBPARSERS.add_parser("JSON", help="Import a JSON file into Elasticsearch")
    JSON_PARSER.add_argument("jsonFile", help="Path to JSON file to read")
    JSON_PARSER.add_argument("esIndex", help="Name of the Elasticsearch index mapping")
    JSON_PARSER.set_defaults(func=utilities.process_json)

    ARGS = PARSER.parse_args()
    ARGS.func(ARGS)