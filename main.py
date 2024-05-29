import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)


def main():
    while True:
        struts_file_location = input("Enter the location of the struts.xml file: ")
        if os.path.isfile(struts_file_location):
            break
        else:
            print("Invalid file path. Please try again.")

    with open(struts_file_location, "r") as file:
        struts_xml_content = file.read()

    while True:
        actions_folder_location = input(
            "Enter the location of the Struts actions folder: "
        )
        if os.path.isdir(actions_folder_location):
            break
        else:
            print("Invalid folder path. Please try again.")

    # TODO: modify directory search to fetch files in subdirectories
    action_files = []
    for file in os.listdir(actions_folder_location):
        if file.endswith(".java"):
            action_files.append(
                {
                    "file_name": file,
                    "file_path": os.path.join(actions_folder_location, file),
                }
            )

    while True:
        controller_folder_location = input(
            "Enter the location of the Spring controller folder: "
        )
        if os.path.isdir(controller_folder_location):
            break
        else:
            print("Invalid folder path. Please try again.")

    print("Converting Struts actions to Spring controllers...")
    for action_file in action_files:
        with open(action_file["file_path"], "r") as file:
            code = file.read()
        section_divider = "\n -------- \n"
        with open("prompt.txt", "r") as file:
            initial_message = file.read()
        prompt = (
            initial_message
            + section_divider
            + "struts.xml: \n"
            + struts_xml_content
            + section_divider
            + action_file["file_name"]
            + ": \n"
            + code
        )

        completion = client.chat.completions.create(
            model=os.environ["DEPLOYMENT_NAME"],
            messages=[{"role": "user", "content": prompt}],
        )

        content = completion.choices[0].message.content

        filename_start = content.find("Filename - ") + len("Filename - ")
        filename_end = content.find("\n", filename_start)
        filename = content[filename_start:filename_end]

        code_start = content.find("```java\n") + len("```java\n")
        code_end = content.find("```\n", code_start)
        code = content[code_start:code_end]

        # write completion content to file
        with open(controller_folder_location + "/" + filename, "w") as file:
            file.write(code)
    print("Conversion complete.")


def get_completion(messages):
    completion = client.chat.completions.create(
        model=os.environ["DEPLOYMENT_NAME"], messages=messages
    )

    return completion.choices[0].message.content


def configure_chat():

    # Get system prompt
    with open("user_prompt.txt", "r") as file:
        # Read the content of the file
        content = file.read()

    # Get
    completion = get_completion(
        [
            {"role": "user", "content": content},
        ]
    )

    print(completion)


if __name__ == "__main__":
    main()
