import gradio as gr
import requests

# Base URL for your FastAPI application
BASE_URL = "http://127.0.0.1:8000"  # Replace with the actual URL where your FastAPI app is running

# Health Check Function
def check_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.json()
    except Exception as e:
        return {"status": 500, "message": str(e)}

# Get Prompt Template Function
def get_prompt_template():
    try:
        response = requests.get(f"{BASE_URL}/prompt_template")
        return response.json()
    except Exception as e:
        return {"status": 500, "message": str(e)}

# Jira Authentication Function
def jira_authenticate(username, api_token, jira_url):
    headers = {
        "username": username,
        "api-token": api_token,
        "jira-url": jira_url
    }
    try:
        response = requests.post(f"{BASE_URL}/jira_authenticate", headers=headers)
        return response.json()
    except Exception as e:
        return {"status": 500, "message": str(e)}

def estimate_story_ui(story_id, username, api_token, jira_url, prompt_template=None):
    """
    Fetch the story estimate and display subtasks in an editable table.
    """
    headers = {
        "username": username,
        "api-token": api_token,
        "jira-url": jira_url
    }
    data = {"story_id": story_id}
    params = {"prompt_template": prompt_template} if prompt_template else {}

    try:
        # Call FastAPI to get story estimate
        response = requests.post(f"{BASE_URL}/story_id", headers=headers, json=data, params=params)
        result = response.json()

        if result.get("status") == 200:
            # Extract subtasks and format them for display
            subtasks = result.get("subtasks", [])
            table_data = [
                [subtask.get("subtask", ""), subtask.get("estimation", 0)]
                for subtask in subtasks
            ]
            # Extract story description
            story_description = result.get("description", "No description available.")

            # Return table data, story description, and the full response as state
            return (
                gr.update(value=table_data, visible=True),  # Show table
                gr.update(value=story_description),  # Update story description
                gr.update(value="Story fetched successfully!"),  # Success message
                result  # Pass the original response as state
            )
        else:
            return (
                gr.update(visible=False),  # Hide table
                gr.update(value=""),  # Clear story description
                gr.update(value=f"Error: {result.get('message', 'Unknown error')}"),
                None  # No state to pass
            )

    except Exception as e:
        return (
            gr.update(visible=False),  # Hide table
            gr.update(value=""),  # Clear story description
            gr.update(value=f"Error: {str(e)}"),
            None  # No state to pass
        )

def create_subtasks_ui(updated_table, original_response, username, api_token, jira_url):
    """
    Update subtasks in the original JSON and send them to FastAPI's /create_subtasks endpoint.
    """
    if not original_response:
        return "Error: No story data available to update subtasks."

    # Convert updated_table to a list of lists (if it is a DataFrame)
    if hasattr(updated_table, "values"):
        updated_table = updated_table.values.tolist()

    new_subtasks = []
    for element in updated_table:
        new_subtasks.append({"subtask": element[0], "estimation": element[1]})
    
    original_response["subtasks"] = new_subtasks

    # Prepare the payload for the /create_subtasks endpoint
    payload = {
        "status": 200,  # Add the required `status` field
        "story_id": original_response.get("story_id"),
        "description": original_response.get("description"),
        "subtasks": original_response.get("subtasks")
    }

    headers = {
        "username": username,
        "api-token": api_token,
        "jira-url": jira_url
    }

    try:
        # Call FastAPI to create subtasks
        response = requests.post(f"{BASE_URL}/create_subtasks", headers=headers, json=payload)
        result = response.json()

        if result.get("status") == 200:
            return f"Subtasks status update : {result.get('message', 'Success')}"
        else:
            return f"Error: {result.get('message', 'Unknown error')}"

    except Exception as e:
        return f"Error: {str(e)}"

# Create Subtasks Function
def create_subtasks_for_story(story_estimate, username, api_token, jira_url):
    headers = {
        "username": username,
        "api_token": api_token,
        "jira_url": jira_url
    }
    try:
        response = requests.post(f"{BASE_URL}/create_subtasks", headers=headers, json=story_estimate)
        return response.json()
    except Exception as e:
        return {"status": 500, "message": str(e)}

def update_row_selection(table_data):
    """
    Update the row selection options based on the current table data.
    """
    if hasattr(table_data, "values"):  # If it's a DataFrame
        table_data = table_data.values.tolist()
    
    # Generate options as row indices with a preview of the subtask description
    options = [f"Row {idx + 1}: {row[0]}" for idx, row in enumerate(table_data)]
    return gr.update(choices=options, value=[])

import re

def delete_selected_rows(current_table, selected_rows):
    """
    Delete rows selected by the user from the table.
    """
    if hasattr(current_table, "values"):  # If it's a DataFrame
        current_table = current_table.values.tolist()

    try:
        # Extract indices of rows to delete
        indices_to_delete = [
            int(re.search(r'\d+', choice).group()) - 1  # Extract the row index using regex
            for choice in selected_rows
        ]

        # Remove rows based on the extracted indices
        updated_table = [
            row for idx, row in enumerate(current_table) if idx not in indices_to_delete
        ]

        return gr.update(value=updated_table), gr.update(choices=[], value=[])
    except Exception as e:
        return gr.update(value=current_table), f"Error: {str(e)}"


# Gradio Interface
def main():
    with gr.Blocks() as demo:
        gr.Markdown("# Mr. AGILE - Gradio Interface")

        # Health Check
        with gr.Tab("Health Check"):
            health_button = gr.Button("Check Health")
            health_output = gr.Textbox(label="Health Status")
            health_button.click(check_health, outputs=health_output)

        # Get Prompt Template
        with gr.Tab("Prompt Template"):
            prompt_button = gr.Button("Get Prompt Template")
            prompt_output = gr.Textbox(label="Prompt Template")
            prompt_button.click(get_prompt_template, outputs=prompt_output)

        # Jira Authentication
        with gr.Tab("Jira Authentication"):
            username = gr.Textbox(label="Username")
            api_token = gr.Textbox(label="API Token")
            jira_url = gr.Textbox(label="Jira URL")
            auth_button = gr.Button("Authenticate")
            auth_output = gr.Textbox(label="Authentication Status")
            auth_button.click(jira_authenticate, inputs=[username, api_token, jira_url], outputs=auth_output)

        # Gradio Tab for "Estimate Story"
        with gr.Tab("Estimate Story"):
            # Input fields
            story_id = gr.Textbox(label="Story ID", placeholder="Enter the Jira Story ID")
            est_username = gr.Textbox(label="Username", placeholder="Enter your Jira username")
            est_api_token = gr.Textbox(label="API Token", placeholder="Enter your Jira API token")
            est_jira_url = gr.Textbox(label="Jira URL", placeholder="Enter your Jira instance URL")
            prompt_template = gr.Textbox(label="Prompt Template (Optional)", placeholder="Enter a prompt template if needed")

            # Action buttons
            estimate_button = gr.Button("Get Estimate")
            save_button = gr.Button("Update Subtasks in JIRA")
            delete_row_button = gr.Button("Delete Selected Rows")  # Button to delete selected rows

            # Outputs
            story_description_output = gr.Textbox(
                label="Story Description",
                interactive=False,
                placeholder="Story description will appear here.",
                visible=True,
                lines=3
            )
            
            table_output = gr.Dataframe(
                headers=["Subtasks", "Estimation"],
                datatype=["str", "number"],
                interactive=True,
                visible=False,
                label="Editable Subtask Table"
            )

            row_selection = gr.CheckboxGroup(label="Select Rows to Delete", visible=True)  # Selection for rows to delete
            output_message = gr.Textbox(label="Message", interactive=False)

            # State to store the original response
            story_state = gr.State()

            # Bind functions to buttons
            estimate_button.click(
                estimate_story_ui,
                inputs=[story_id, est_username, est_api_token, est_jira_url, prompt_template],
                outputs=[table_output, story_description_output, output_message, story_state]
            )

            delete_row_button.click(
                delete_selected_rows,
                inputs=[table_output, row_selection],
                outputs=[table_output, row_selection]
            )

            table_output.change(
                update_row_selection,
                inputs=[table_output],
                outputs=[row_selection]
            )

            save_button.click(
                create_subtasks_ui,
                inputs=[table_output, story_state, est_username, est_api_token, est_jira_url],
                outputs=output_message
            )

    return demo

# Run the Gradio app
if __name__ == "__main__":
    app = main()
    app.launch()
