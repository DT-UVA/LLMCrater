PROMPT_TEMPLATE = """
Follow these steps to create a valid JSON-LD object for RO-Crate Metadata Specification 1.1:

1. Create the object structure like so:
    {
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "ro-crate-metadata.json",
      "@type": "CreativeWork",
      "name": "ro-crate-metadata.json",
      "description": "RO-Crate Metadata Specification 1.1 file describing the dataset.",
      "fileFormat": "application/json",
      "conformsTo": {
        "@id": "https://w3id.org/ro/crate/1.1"
      },
      "about": {
        "@id": "./"
      }
    }
  ]
}

2. Populate the dataset object with the necessary properties, this can look like this:
{
    "@id": "./",
    "@type": "Dataset",
    "name": "...",
    "description": "...",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "hasPart": [
    {
        "@id": "file.txt"
    },
    ],
    "mainEntity": {
    "@id": "file.txt"
    }
}
                                               
3. Given this data: {notebook_content}, add entries to the @graph for each software, data, or other content in the RO-Crate:
{
  "@id": "#hypervisor-os",
  "@type": "SoftwareApplication",
  "name": "Ubuntu Linux",
  "version": "24.04.2 LTS", (always specify the version like this)
}


4. Given this data: {files}, add entries for all files to the @graph:
{
  "@id": "file.txt",
  "@type": "File",
  "name": "...",
  "description": "...",
  "fileFormat": "text/plain",
}

5. Populate the @Context with the ro-crate version
"@context": "https://w3id.org/ro/crate/1.1/context" 

6. Make sure the author, if any, is included in the @graph with the type Person or Organization, this can look like this:
{
  "@id": "https://orcid.org/0000-0000-0000-0000",
  "@type": "Person",
  "name": "...", (this is the name of the author)
  "affiliation": "..." (this is the organization the author is affiliated with, if any)
}

IMPORTANT RULES:
1. NEVER ANSWER WITH ANYTHING OTHER THAN A VALID JSON-LD OBJECT. 
2. MAKE SURE THAT EVERY ENTRY IS VALID AND NOT MADE UP.
"""