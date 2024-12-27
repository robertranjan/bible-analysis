# bible-analysis/main.py
"""main"""

# bible-analysis/main.py
import argparse
import json

from analysis.travel import mapper
from core.tagger import bible_search, reference_extrator
from core.tagger.entity_tagging import tag_named_entities
from core.tagger.event_tagging import tag_events
from core.tagger.lifespan_tagging import tag_lifespan_phrases
from core.tagger.occupation_tagging import tag_occupations
from core.tagger.relationship_tagging import tag_relationships
from core.translation_loader import translation_manager
from core.utils import file_utils, tagging_utils
from core.utils.logger_utils import get_logger
from core.visualization import visualization

logger = get_logger(__file__.rsplit("/", 1)[-1])


def setup_parsers():
    """Set up argument parsers for all sub-commands."""
    parser = argparse.ArgumentParser(
        description="CLI to process Bible text, extract entities, and perform searches."
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    setup_tag_entities_parser(subparsers)
    setup_search_parser(subparsers)
    setup_reference_parser(subparsers)
    setup_extract_parser(subparsers)
    setup_travel_parser(subparsers)
    setup_timeline_parser(subparsers)  # Added timeline parser
    return parser


def setup_timeline_parser(subparsers):
    """Set up timeline parser for generating charts."""
    timeline_parser = subparsers.add_parser(
        "science",
        help="Generate and visualize timeline charts for scientific and biblical events.",
    )
    timeline_parser.add_argument(
        "--input-file",
        type=str,
        default="data/input/science/facts.json",
        help="Input CSV file for timeline data (default: %(default)s).",
    )
    timeline_parser.add_argument(
        "--add-event",
        action="store_true",
        help="Add a new event to the timeline data.",
    )
    timeline_parser.add_argument(
        "--item",
        type=str,
        help="Name of the event (e.g., 'The Expanding Universe').",
    )
    timeline_parser.add_argument(
        "--category",
        type=str,
        help="Category of the event (e.g., 'Cosmology').",
    )
    timeline_parser.add_argument(
        "--bible-reference",
        type=str,
        help="Bible reference associated with the event (e.g., 'Isaiah 40:22').",
    )
    timeline_parser.add_argument(
        "--recorded-timeframe",
        type=int,
        help="Timeframe when the event was recorded (e.g., -700).",
    )
    timeline_parser.add_argument(
        "--scientific-comment-year",
        type=int,
        help="Year when scientists commented on the event (e.g., 1929).",
    )
    timeline_parser.add_argument(
        "--confirmed",
        type=bool,
        help="Whether the detail is confirmed by scientists (True/False).",
    )
    timeline_parser.add_argument(
        "--scientific-commentary",
        type=str,
        help="Details of the scientific commentary.",
    )


def setup_travel_parser(subparsers):
    """setup travel parser"""
    reference_parser = subparsers.add_parser(
        "trips",
        help="view travels",
    )
    reference_parser.add_argument(
        "--input-file",
        type=str,
        default="data/input/travel/journey_data.json",
        help="vivew travel map (default: %(default)s).",
    )
    reference_parser.add_argument(
        "--output-file",
        type=str,
        default="data/output/travel-maps.csv",
        help="vivew travel map (default: %(default)s).",
    )


def setup_tag_entities_parser(subparsers):
    """Set up tag-entities parser."""
    extract_parser = subparsers.add_parser(
        "tag-entities",
        help="Extract entities, occupations, and lifespans from Bible JSON data.",
    )
    extract_parser.add_argument(
        "--input-file",
        type=str,
        default="data/input/nwt_bible.json",
        help="Input JSON file for Bible data (default: %(default)s).",
    )
    extract_parser.add_argument(
        "--output-json",
        type=str,
        default="data/output/bible_entities.json",
        help="Output JSON file for extracted entities (default: %(default)s).",
    )
    extract_parser.add_argument(
        "--output-csv",
        type=str,
        default="data/output/bible_entities.csv",
        help="Output CSV file for extracted entities (default: %(default)s).",
    )
    extract_parser.add_argument(
        "--books",
        type=str,
        nargs="*",
        help="Specify one or more books to extract entities from (e.g., genesis exodus).",
    )
    extract_parser.add_argument(
        "--translation",
        type=str,
        default="nwt",
        help="Bible translation, e.g., nwt | asv | kj21",
    )


def setup_search_parser(subparsers):
    """setup search parser"""
    search_parser = subparsers.add_parser(
        "search",
        help="Search for a phrase in the Bible text and display matches.",
    )
    search_parser.add_argument(
        "--input-file",
        type=str,
        default="data/input/nwt_bible.json",
        help="Input JSON file for Bible data (default: %(default)s).",
    )
    search_parser.add_argument(
        "--phrase",
        type=str,
        required=True,
        help="Phrase to search for in the Bible text.",
    )
    search_parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top matches to display (default: %(default)s).",
    )
    search_parser.add_argument(
        "--translation",
        type=str,
        required=True,
        help="Bible translation, ex: nwt | asv | kj21 ",
    )
    search_parser.add_argument(
        "--csv", action="store_true", help="Output the results in CSV format."
    )


def setup_reference_parser(subparsers):
    """setup reference parser"""
    reference_parser = subparsers.add_parser(
        "reference",
        help="Extract text for a specific Bible reference.",
    )
    reference_parser.add_argument(
        "--input-file",
        type=str,
        default="data/input/nwt_bible.json",
        help="Input JSON file for Bible data (default: %(default)s).",
    )
    reference_parser.add_argument(
        "--reference",
        type=str,
        required=True,
        help="Bible reference to extract (e.g., 'Gen 1:1', 'John 3:16').",
    )
    reference_parser.add_argument(
        "--translation",
        type=str,
        required=True,
        help="Bible translation, ex: nwt | asv | kj21 ",
    )


def setup_extract_parser(subparsers):
    """setup extract parser"""
    translation_parser = subparsers.add_parser(
        "extract",
        help="Extract a specific translation from the multi-translation JSON.",
    )
    translation_parser.add_argument(
        "--input-file",
        type=str,
        default="data/input/multi_translation.json",
        help="Input JSON file for multi-translation Bible data (default: %(default)s).",
    )
    translation_parser.add_argument(
        "--translation",
        type=str,
        required=True,
        help="Translation to extract (e.g., 'asv', 'kj21', 'nwt').",
    )
    translation_parser.add_argument(
        "--output-file",
        type=str,
        default="data/output/extracted_translation.json",
        help="Output JSON file for extracted translation (default: %(default)s).",
    )


def flatten_chapter_results(chapter_results, book, chapter_num):
    """Flatten chapter results into a list of records."""
    flat_results = []
    for verse_num, results in chapter_results.items():
        if not isinstance(results, dict):  # Debug unexpected data structure
            raise ValueError(f"Expected results as a dict but got {type(results)}")
        for result_type, items in results.items():
            for item in items:
                if not isinstance(item, dict):  # Debug unexpected data structure
                    raise ValueError(
                        f"Expected item as a dict but got {type(item)},\nitem: {item}"
                    )

                # pull out these and remove from item
                trigger = item["trigger"]
                context = item["context"]

                # remove below to avoid duplicates in "extras"
                del item["context"]
                del item["trigger"]

                flat_results.append(
                    {
                        "book": book,
                        "chapter": chapter_num,
                        "verse": verse_num,
                        "type": result_type,
                        "trigger": trigger,
                        "context": context,
                        "extras": item,
                    }
                )

    return flat_results


def perform_entity_analysis(input_file, output_json, output_csv, translation, books):
    """Perform entity analysis using modular taggers."""
    logger.debug("Loading Bible data from %s", input_file)
    bible_data = file_utils.load_from_json(input_file)

    combined_results = []
    for book, chapters in bible_data[translation].items():
        # skip current-book when it's not in requested books
        if books and book not in books:
            continue

        for chapter_num, verses in chapters.items():
            chapter_results = {}
            for verse_num, verse_text in verses.items():
                doc = tagging_utils.nlp(verse_text)  # Load NLP model once per verse

                # Modular tagging
                unique_tags = set()
                chapter_results[str(verse_num)] = {}
                chapter_results[str(verse_num)] = tag_named_entities(doc, unique_tags)
                chapter_results[str(verse_num)]["occupations"] = tag_occupations(doc)

                chapter_results[str(verse_num)]["lifespans"] = tag_lifespan_phrases(
                    doc,
                    verse_text,
                    unique_tags,
                )
                chapter_results[str(verse_num)]["relationships"] = tag_relationships(
                    doc, verse_text, unique_tags
                )
                chapter_results[str(verse_num)]["events"] = tag_events(doc)

            # Flatten and deduplicate chapter results
            flat_results = flatten_chapter_results(chapter_results, book, chapter_num)
            deduplicated_results = tagging_utils.deduplicate_records(flat_results)

            # Store deduplicated results back into combined_results
            combined_results.extend(deduplicated_results)

    # Save results
    file_utils.save_to_json(combined_results, output_json)
    file_utils.save_combined_results_to_csv(combined_results, output_csv)

    logger.debug(
        "Entity analysis completed. Results saved to %s and %s", output_json, output_csv
    )


def handle_command(args):
    """Handle the parsed command."""
    if args.command == "tag-entities":
        logger.debug("Starting entity tagging for %s", args.input_file)
        perform_entity_analysis(
            args.input_file,
            args.output_json,
            args.output_csv,
            args.translation,
            books=args.books,
        )
    elif args.command == "search":
        logger.debug("Searching for phrase: '%s' in %s", args.phrase, args.input_file)

        matches = bible_search.find_matches(
            args.input_file,
            args.phrase,
            args.translation,
            top_n=args.top_n,
            output_csv=args.csv,
        )
        if not args.csv:
            for match in matches:
                print(
                    f"{match['book']} {match['chapter']}:{match['verse']} - {match['text']}"
                )
        logger.debug("Search completed.")
        if matches:
            logger.debug("Found %d matches.", len(matches))
    elif args.command == "reference":
        result = reference_extrator.extract_reference(
            args.input_file, args.reference, args.translation
        )
        print(result)
    elif args.command == "trips":
        mapper.map_travel(args.input_file)
    elif args.command == "extract":
        with open(args.input_file, "r", encoding="utf-8") as f:
            multi_translation_data = json.load(f)

        single_translation_data = translation_manager.extract_translation(
            multi_translation_data, args.translation
        )

        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(single_translation_data, f, indent=4)

        print(f"Extracted {args.translation} translation saved to {args.output_file}")
    elif args.command == "science":
        events = file_utils.load_from_json(args.input_file)
        if args.add_event:
            new_event = {
                "Item": args.item,
                "Category": args.category,
                "Bible Reference": args.bible_reference,
                "Recorded Timeframe": args.recorded_timeframe,
                "Detail Confirmed by Scientists": args.confirmed,
                "Scientific Commentary": args.scientific_commentary,
                "Scientific Comment Year": args.scientific_comment_year,
                "Timeframe Difference": args.scientific_comment_year
                - visualization.parse_year(args.recorded_timeframe),
            }
            events.append(new_event)
            with open(args.input_file, "w", encoding="utf-8") as file:
                json.dump(events, file, indent=4)
            print(f"Added event: {new_event}")
        else:
            visualization.generate_mermaid_charts(events)
    else:
        print("Invalid command. Use --help for available options.")


def main():
    """Main function to handle CLI."""
    parser = setup_parsers()
    args = parser.parse_args()
    handle_command(args)


if __name__ == "__main__":
    main()
