# Step 1: Choose a base image
FROM python:3.8

# Step 2: Set up the working directory
WORKDIR /app

# Step 3: Install dependencies
RUN pip install streamlit

# Step 4: Copy the script and any required files
COPY code_tools.py /app/
COPY logo.jpg /app/
COPY code_tools.png /app/

# Step 5: Expose the necessary ports
EXPOSE 8501

# Step 6: Set environment variables
ENV AZURE_OPENAI_KEY=e485bd8596704f41b8de8f6ab0cec75a
ENV AZURE_OPENAI_ENDPOINT=https://aiprojectamplify.openai.azure.com/

# Step 7: Specify the command to run the script
ENTRYPOINT ["streamlit", "run", "code_tools.py"]
