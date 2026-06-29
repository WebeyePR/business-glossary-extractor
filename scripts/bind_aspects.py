import argparse
import json
import time
from google.cloud import dataplex_v1
from google.api_core.exceptions import AlreadyExists

def robust_call(func, *args, **kwargs):
    for attempt in range(3):
        try:
            return func(*args, **kwargs)
        except AlreadyExists:
            raise
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Deep bind Aspects and Definition Links for Glossary Terms.")
    parser.add_argument("--project_id", required=True, help="GCP Project ID")
    parser.add_argument("--project_num", required=True, help="GCP Project Number")
    parser.add_argument("--location", default="us", help="Dataplex Location")
    parser.add_argument("--glossary_id", required=True, help="Glossary ID")
    parser.add_argument("--json_file", required=True, help="Path to Extracted JSON")
    parser.add_argument("--dataset", required=True, help="BigQuery Dataset containing related tables")
    args = parser.parse_args()

    client = dataplex_v1.CatalogServiceClient(transport="rest")
    
    with open(args.json_file, 'r', encoding='utf-8') as f:
        terms_data = json.load(f)
        
    term_mapping = {}
    for i, item in enumerate(terms_data):
        display_name = item.get("term", "").strip()
        term_id = f"term-v3-{i+1:03d}"
        entry_name = f"projects/{args.project_num}/locations/{args.location}/entryGroups/@dataplex/entries/projects/{args.project_num}/locations/{args.location}/glossaries/{args.glossary_id}/terms/{term_id}"
        term_mapping[display_name] = entry_name

    for i, item in enumerate(terms_data):
        display_name = item.get("term", "").strip()
        term_id = f"term-v3-{i+1:03d}"
        entry_name = term_mapping[display_name]
        
        print(f"\nProcessing [{display_name}]...")
        
        # 1. Attach Aspects
        aspects_to_update = {}
        
        desc_parts = [f"**定义**: {item.get('definition', '')}"]
        if item.get('calculation_logic'):
            desc_parts.append(f"**计算逻辑**:\n```sql\n{item.get('calculation_logic')}\n```")
            
        overview_aspect = dataplex_v1.Aspect()
        overview_aspect.aspect_type = "dataplex-types:overview"
        overview_aspect.data = {"content": "\n\n".join(desc_parts)}
        aspects_to_update["dataplex-types.global.overview"] = overview_aspect
        
        custom_aspect_key = f"{args.project_num}.{args.location}.retail-business-logic"
        data = {}
        if item.get("calculation_logic"): data["calculation_logic"] = item.get("calculation_logic")
        if item.get("related_tables") and item.get("related_tables") != ["*"]: data["related_tables"] = item.get("related_tables")
        if item.get("related_columns"): data["related_columns"] = item.get("related_columns")
        if item.get("stewards"): data["stewards"] = item.get("stewards")
        if item.get("sensitivity"): data["sensitivity"] = item.get("sensitivity")
        if item.get("lifecycle_status"): data["lifecycle_status"] = item.get("lifecycle_status")
        
        if data:
            custom_aspect = dataplex_v1.Aspect()
            custom_aspect.aspect_type = f"projects/{args.project_num}/locations/{args.location}/aspectTypes/retail-business-logic"
            custom_aspect.data = data
            aspects_to_update[custom_aspect_key] = custom_aspect

        try:
            entry = dataplex_v1.Entry()
            entry.name = entry_name
            entry.aspects = aspects_to_update
            req = dataplex_v1.UpdateEntryRequest(entry=entry, update_mask={"paths": ["aspects"]})
            robust_call(client.update_entry, request=req)
            print("  [+] Aspects updated")
        except Exception as e:
            print(f"  [-] Failed to update aspects: {e}")

        # 2. Definition Links
        related_tables = item.get("related_tables", [])
        related_columns = item.get("related_columns", [])
        if related_tables and related_tables != ["*"]:
            for table in related_tables:
                table = table.strip()
                if not table: continue
                
                table_entry = f"projects/{args.project_num}/locations/{args.location}/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/{args.project_id}/datasets/{args.dataset}/tables/{table}"
                link_id = f"def-v3-{term_id}-bq-{table.encode('utf-8').hex()[:8]}"
                
                link = dataplex_v1.EntryLink(
                    entry_link_type="projects/dataplex-types/locations/global/entryLinkTypes/definition",
                    entry_references=[
                        dataplex_v1.EntryLink.EntryReference(
                            name=table_entry,
                            type_=dataplex_v1.EntryLink.EntryReference.Type.SOURCE
                        ),
                        dataplex_v1.EntryLink.EntryReference(
                            name=entry_name,
                            type_=dataplex_v1.EntryLink.EntryReference.Type.TARGET
                        )
                    ]
                )
                
                try:
                    robust_call(client.create_entry_link, request=dataplex_v1.CreateEntryLinkRequest(
                        parent=f"projects/{args.project_num}/locations/{args.location}/entryGroups/@bigquery",
                        entry_link_id=link_id,
                        entry_link=link
                    ))
                    print(f"  [+] Definition Link created -> {table}")
                except AlreadyExists:
                    print(f"  [ℹ️] Definition Link already exists -> {table}")
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"  [ℹ️] Definition Link already exists -> {table}")
                    elif "not found" in str(e).lower() and "bigquery" in str(e).lower():
                         print(f"  [-] BigQuery table entry not found -> {table}")
                    else:
                         print(f"  [-] Failed to link table {table}: {e}")
                
                # --- NEW LOGIC: Bidirectional Column Aspect Binding ---
                if related_columns and related_columns != ["*"]:
                    try:
                        print(f"  [+] Injecting Business Context into BigQuery Columns for {table}...")
                        bq_entry = client.get_entry(name=table_entry)
                        
                        col_aspects_to_update = {}
                        if bq_entry.aspects:
                            col_aspects_to_update = dict(bq_entry.aspects)
                            
                        col_updated = False
                        for col in related_columns:
                            col = col.strip()
                            if not col: continue
                            
                            aspect_key = f"dataplex-types.global.overview@{col}"
                            col_aspect = dataplex_v1.Aspect()
                            col_aspect.aspect_type = "dataplex-types:overview"
                            col_aspect.data = {
                                "content": f"**关联业务术语 (Business Term)**: {display_name}\n\n**计算逻辑 (Calculation Logic)**:\n```sql\n{item.get('calculation_logic', 'N/A')}\n```"
                            }
                            col_aspects_to_update[aspect_key] = col_aspect
                            col_updated = True
                            
                        if col_updated:
                            update_bq_req = dataplex_v1.UpdateEntryRequest(
                                entry=dataplex_v1.Entry(name=table_entry, aspects=col_aspects_to_update),
                                update_mask={"paths": ["aspects"]}
                            )
                            robust_call(client.update_entry, request=update_bq_req)
                            print(f"      -> Injected business context into {len(related_columns)} columns of {table}.")
                    except Exception as e:
                        print(f"      [-] Failed to inject column aspects into BigQuery table {table}: {e}")

if __name__ == "__main__":
    main()
