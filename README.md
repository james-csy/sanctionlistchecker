# sanctionlistchecker

Building a tool to check if companies/people within an uploaded Excel file are on the US Sanction list


```mermaid
timeline
    title Product Development
    July 12th 2023: Created Repo: Extract Names from Sanction List: Create a form ("/searchName") to take in name input: Form returns Sanctioned List names with highest similarity scores
    July 17th 2023: Created new pages for large text search
    July 18th 2023: Array Data - carried out sanction search for each value in array: Data can be displayed in order on a table: String input converted into array (separated by white space)
    July 19th 2023: Added flag/not flagged functionality: Excel Input from files
    July 20th 2023: Started on removing common words in search (e.g. incorporation, company)
    July 21-25th 2023: Added common word screening as a second search filter: Read and write to Excel file implemented
    July 26th 2023: Added Excel Header Input: Excel File Upload is functional: Implemented spaCy (NLP) to extract names, organizations, and locations: Names & Organizations (from descriptions) are searched
    July 27th 2023: implemented bootstrap so UI is more intuitive: excel search basic functionality working
    July 28th 2023: Started description search tool: Implementing description visualization (display)
    August 8th 2023: Implemented on company server: Added OFAC list updating
    To-Do - : Create Algo to search sanction list locations: add address and country cross-referencing: Add description visualization to excel search: Update logs: research class structure
```
# Product Breakdown
Sanction Search
-
The sanction search currently uses fuzzy matching and only references the **OFAC list (not updated)**.

Moving forward:
1. Referencing multiple sanction lists: US (OFAC), UN, EU, UK, etc.
2. Automatic updating of lists

Named Entity Recognition (Extraction from Descriptions)
-
Currently using spaCy's default English library to extract People/Names/Orgs out of descriptions to later be searched using the sanction search algorithm.

Moving forward:
1. Training custom dataset built from existing claims data and maybe the sanctions lists too.
2. Also update displacy visualization to only highlight searched terms and not all entities

Extra things to implement
-
1. Implement some kind of logging system to track searches
2. Updates page to reflect when new sanction lists have been updated
