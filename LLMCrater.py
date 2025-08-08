import nbformat
import sys
import json
import os
import requests
from rocrate.rocrate import ROCrate


from RAG import RAG
from prompts import PROMPT_TEMPLATE

# Zenodo Sandbox API configuration (can be replaced with production API)
ACCESS_TOKEN = "API_TOKEN"

# For sandbox testing
ZENODO_URL = "https://sandbox.zenodo.org/api/deposit/depositions"

# For production use
# ZENODO_URL = "https://zenodo.org/api/deposit/depositions"

# Zenodo information
PUBLISHER = "Doe, John"
PROJECT_NAME = "Sample RO-Crate (Sandbox)"
DESCRIPTION = "This is a test RO-Crate uploaded to the Zenodo sandbox via Python."

# Headers for Zenodo API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}


class LLMCrater:
    def __init__(self, directory_path):
        self.rag = RAG()
        self.directory_path = directory_path
        self.output_filepath = directory_path + "/ro-crate-metadata.json"

    def read_notebook(self):
        # Look for the first Jupyter notebook file in the directory
        file_path = None
        for filename in os.listdir(self.directory_path):
            if filename.endswith(".ipynb"):
                file_path = os.path.join(self.directory_path, filename)
                break

        if not file_path:
            raise FileNotFoundError(
                "No Jupyter notebook (.ipynb) found in the directory."
            )

        # Read the notebook file
        print(f" - Reading notebook from {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            self.notebook = nbformat.read(f, as_version=4)

    def gather_directory_content(self):
        """
        Gather all files in the directory and return their paths.
        """
        file_paths = []

        # Walk through the directory and collect file paths
        for root, _, files in os.walk(self.directory_path):
            for filename in files:
                file_paths.append(os.path.join(root, filename))
        self.files = file_paths

    def generate_metadata(self):
        """
        Generate RO-Crate metadata using the RAG system.
        """
        content_parts = []

        # Read the notebook content
        for cell in self.notebook.cells:
            if cell.cell_type == "markdown":
                content_parts.append(cell["source"])

        # Add the code cells content
        content = "\n".join(content_parts)

        # Invoke the RAG system to generate the RO-Crate metadata
        print(" - Generating RO-Crate metadata...")
        prompt = PROMPT_TEMPLATE.replace("{notebook_content}", content).replace(
            "{files}", str(self.files)
        )
        return self.rag.ask(prompt)["result"]

    def save_metadata(self, crate):
        """
        Save the generated RO-Crate metadata to a file.
        """
        if not crate:
            print("No crate generated. Exiting.")
            return

        # Remove the first and last lines from the crate string
        crate = crate[crate.find("\n") + 1 : crate.rfind("\n")]

        try:
            # Verify that the output is valid JSON
            json_obj = json.loads(crate)

            # Write the JSON-LD to a file
            with open(self.output_filepath, "w", encoding="utf-8") as f:
                json.dump(json_obj, f, indent=2)

            # Let the user know where the output was saved
            print(f" - RO-Crate JSON-LD written to {self.output_filepath}")
            return True

        except json.JSONDecodeError:
            print("Generated output is not valid JSON-LD.")
            return False

    def verify_ro_crate(self, crate_path):
        """
        Verify the RO-Crate by loading it and checking its root dataset.
        """
        try:
            crate = ROCrate(crate_path)
            print(f" - RO-Crate verified successfully. RID: {crate.root_dataset.id}")
            return True

        except Exception as e:
            print(f"Failed to load or parse RO-Crate: {e}")
            return False

    def pack_crate(self):
        """
        Pack the RO-Crate into a zip file.
        """
        # Open the directory as a ROCrate
        crate = ROCrate(self.directory_path)

        # Write the RO-Crate to a zip file
        crate.write_zip("ro_crate.zip")

        # Remove the ro-crate-metadata.json file from the directory
        os.remove(self.directory_path + "/ro-crate-metadata.json")

        print(f" - RO-Crate packed into ro_crate.zip")

    def parse_crate(self):
        """
        Parse the directory and generate a RO-Crate.
        """
        print("\n* RO-Crate creation routine started...")

        # Read the notebook content
        self.read_notebook()

        # Gather directory content
        self.gather_directory_content()

        # Generate metadata
        crate = self.generate_metadata()

        if not self.save_metadata(crate):
            print("Failed to save RO-Crate metadata. Exiting.")
            sys.exit(1)

        # # Verify the RO-Crate
        if not self.verify_ro_crate(self.directory_path):
            print("RO-Crate verification failed. Exiting.")
            sys.exit(1)

        # Pack the RO-Crate into a zip file
        self.pack_crate()

    def upload_to_zenodo(self, publish=False):
        """
        Upload the RO-Crate to Zenodo.
        If `publish` is True, the deposition will be published.
        """
        print("\n* Uploading RO-Crate to Zenodo...")

        # Create a new deposition
        r = requests.post(ZENODO_URL, headers=HEADERS, json={})
        r.raise_for_status()
        deposition_id = r.json()["id"]
        print(f" - Created Zenodo deposition with ID: {deposition_id}")

        # Upload the RO-Crate zip file
        print(f" - Uploading ro_crate.zip to Zenodo deposition {deposition_id}...")
        upload_url = f"{ZENODO_URL}/{deposition_id}/files"
        with open("ro_crate.zip", "rb") as f:
            r = requests.post(
                upload_url,
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
                files={"file": (os.path.basename("ro_crate.zip"), f)},
            )
            r.raise_for_status()

        # Add metadata to the deposition
        print(" - Adding metadata to the deposition...")
        metadata = {
            "metadata": {
                "title": PROJECT_NAME,
                "upload_type": "dataset",
                "description": DESCRIPTION,
                "creators": [{"name": PUBLISHER}],
            }
        }
        r = requests.put(
            f"{ZENODO_URL}/{deposition_id}", headers=HEADERS, data=json.dumps(metadata)
        )
        r.raise_for_status()

        print(" - Metadata updated successfully.")
        print(" - RO-Crate uploaded to Zenodo successfully.")

        # If publish is requested, publish the deposition
        if publish:
            r = requests.post(
                f"{ZENODO_URL}/{deposition_id}/actions/publish", headers=HEADERS
            )
            r.raise_for_status()
            print("** Published successfully to Zenodo. DOI:", r.json()["doi"], "**")


if __name__ == "__main__":
    # Parameter validation
    if len(sys.argv) < 2:
        print("Usage: python LLMCrater.py <directory_path> [--upload] [--publish]")
        sys.exit(1)

    # Get the directory path from command line arguments
    directory_path = sys.argv[1]

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"Error: The directory '{directory_path}' does not exist.")
        sys.exit(1)

    # Optional flags for upload and publish
    upload = False
    publish = False

    # Parse optional flags
    if len(sys.argv) > 2:
        upload = "--upload" in sys.argv[2:]
        publish = "--publish" in sys.argv[2:]

    # Construct the LLMCrater object
    llm_crater = LLMCrater(directory_path)

    # Parse the directory and generate a RO-Crate
    llm_crater.parse_crate()

    # If upload is requested, handle the upload logic here
    if upload:
        llm_crater.upload_to_zenodo(publish=publish)
